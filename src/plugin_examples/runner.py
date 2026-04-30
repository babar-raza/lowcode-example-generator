"""Pipeline orchestrator — chains all 13 modules into a gate-driven execution flow."""

from __future__ import annotations

import json
import logging
import platform
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------

@dataclass
class StageResult:
    """Result of a single pipeline stage."""
    name: str
    order: int
    status: str = "pending"       # success | failed | degraded | skipped
    duration_ms: float = 0.0
    error: str | None = None
    artifacts: dict = field(default_factory=dict)


@dataclass
class PipelineContext:
    """Mutable state threaded through all stages."""
    family: str
    run_id: str
    dry_run: bool
    skip_run: bool
    template_mode: bool
    require_llm: bool
    require_validation: bool
    require_reviewer: bool
    repo_root: Path
    run_dir: Path
    evidence_dir: Path

    # Set by stages
    config: Any = None
    download_manifest: dict | None = None
    deps: list[dict] | None = None
    extraction: dict | None = None
    catalog: dict | None = None
    catalog_path: Path | None = None
    detection: Any = None
    proof_path: Path | None = None
    planning: Any = None
    llm_router: Any = None
    llm_available: bool = False
    generated_projects: list[dict] = field(default_factory=list)
    validation_results: list = field(default_factory=list)
    gate_verdict: Any = None


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def scenario_to_dict(s) -> dict:
    """Convert a Scenario dataclass to a plain dict for build_packet.

    Does not import the private _scenario_to_dict from scenario_catalog.
    """
    return {
        "scenario_id": s.scenario_id,
        "title": s.title,
        "target_type": s.target_type,
        "target_namespace": s.target_namespace,
        "target_methods": s.target_methods,
        "required_symbols": s.required_symbols,
        "required_fixtures": s.required_fixtures,
        "output_plan": s.output_plan,
        "validation_plan": s.validation_plan,
        "status": s.status,
        "blocked_reason": s.blocked_reason,
        "input_strategy": getattr(s, "input_strategy", "none"),
        "input_files": getattr(s, "input_files", []),
        "required_input_format": getattr(s, "required_input_format", ""),
    }


def _write_fixture_strategy_plan(planning, evidence_dir: Path) -> None:
    """Write fixture-strategy-plan.json evidence."""
    import json as _json
    scenarios = []
    for s in (planning.ready_scenarios + planning.blocked_scenarios):
        scenarios.append({
            "scenario_id": s.scenario_id,
            "required_input_formats": [getattr(s, "required_input_format", "")] if getattr(s, "required_input_format", "") else [],
            "input_strategy": getattr(s, "input_strategy", "none"),
            "input_files": getattr(s, "input_files", []),
            "strategy_status": s.status if s.status.startswith("blocked") else "ready",
            "blocked_reason": s.blocked_reason,
        })
    out = evidence_dir / "latest" / "fixture-strategy-plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps({
        "total_scenarios": len(scenarios),
        "ready": sum(1 for s in scenarios if s["strategy_status"] == "ready"),
        "blocked": sum(1 for s in scenarios if s["strategy_status"] != "ready"),
        "strategies": {
            "generated_fixture_file": sum(1 for s in scenarios if s["input_strategy"] == "generated_fixture_file"),
            "existing_fixture": sum(1 for s in scenarios if s["input_strategy"] == "existing_fixture"),
            "programmatic_input": sum(1 for s in scenarios if s["input_strategy"] == "programmatic_input"),
            "none": sum(1 for s in scenarios if s["input_strategy"] == "none"),
            "no_valid_input_strategy": sum(1 for s in scenarios if s["input_strategy"] == "no_valid_input_strategy"),
        },
        "scenarios": scenarios,
    }, indent=2))


def _write_scenario_input_format_map(planning, evidence_dir: Path) -> None:
    """Write scenario-input-format-map.json evidence."""
    import json as _json
    from plugin_examples.scenario_planner.planner import (
        _infer_input_format, _infer_output_format,
    )
    entries = []
    for s in planning.ready_scenarios:
        type_name = s.target_type.split(".")[-1]
        input_fmt = getattr(s, "required_input_format", ".xlsx")
        output_fmt = _infer_output_format(type_name)
        entries.append({
            "scenario_id": s.scenario_id,
            "workflow_type": type_name,
            "selected_input_format": input_fmt,
            "selected_output_format": output_fmt,
            "reason": f"Inferred from type name {type_name}",
            "source": "input_format_map",
            "confidence": "high" if type_name.lower() in {
                "textconverter", "jsonconverter", "htmlconverter",
                "pdfconverter", "spreadsheetmerger", "spreadsheetsplitter",
                "spreadsheetlocker", "spreadsheetconverter", "imageconverter",
            } else "medium",
            "blocked_if_unclear": False,
        })
    out = evidence_dir / "latest" / "scenario-input-format-map.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps({"scenarios": entries}, indent=2))


def _write_fewshot_patterns(generated_projects: list[dict], evidence_dir: Path) -> None:
    """Write llm-fewshot-patterns.json from generated projects."""
    import json as _json
    patterns = []
    for proj in generated_projects:
        program_path = Path(proj.get("program_path", ""))
        if program_path.exists():
            code = program_path.read_text(encoding="utf-8")
            # Extract key patterns
            has_basedir = "AppContext.BaseDirectory" in code
            has_file_check = "File.Exists" in code
            has_output_check = "output" in code.lower()
            no_readkey = "Console.ReadKey" not in code
            no_readline = "Console.ReadLine" not in code
            patterns.append({
                "scenario_id": proj["scenario_id"],
                "uses_basedir": has_basedir,
                "validates_input": has_file_check,
                "validates_output": has_output_check,
                "no_interactive_input": no_readkey and no_readline,
                "input_strategy": proj.get("input_strategy", "none"),
            })

    out = evidence_dir / "latest" / "llm-fewshot-patterns.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_json.dumps({
        "total_patterns": len(patterns),
        "verified_passing": 0,  # Updated after validation
        "patterns": patterns,
    }, indent=2))


def _fixture_sources_to_dicts(sources) -> list[dict]:
    """Convert list[FixtureSource] dataclasses to list[dict]."""
    return [
        {"type": s.type, "owner": s.owner, "repo": s.repo,
         "branch": s.branch, "paths": s.paths}
        for s in sources
    ]


def _fixture_registry_to_dict(registry) -> dict | None:
    """Convert FixtureRegistry to dict for plan_scenarios (expects dict|None)."""
    if registry is None:
        return None
    return {
        "fixtures": [
            {"filename": f.filename, "available": f.available}
            for f in registry.fixtures
        ],
    }


def _find_type_in_catalog(catalog: dict, full_name: str) -> dict | None:
    """Find a type dict in the catalog by full_name."""
    for ns in catalog.get("namespaces", []):
        for t in ns.get("types", []):
            if t.get("full_name") == full_name:
                return t
    return None


# ---------------------------------------------------------------------------
# Workspace snapshot
# ---------------------------------------------------------------------------

def _snapshot_workspace(manifests_dir: Path, verification_dir: Path) -> dict:
    """List non-.gitkeep files in manifests and verification/latest."""
    def _list_files(d: Path) -> list[str]:
        if not d.exists():
            return []
        return sorted(
            f.name for f in d.iterdir()
            if f.is_file() and f.name != ".gitkeep"
        )

    latest = verification_dir / "latest"
    return {
        "manifests_files": _list_files(manifests_dir),
        "verification_files": _list_files(latest),
    }


# ---------------------------------------------------------------------------
# Stage runner
# ---------------------------------------------------------------------------

def _run_stage(
    name: str,
    order: int,
    fn: Callable[[PipelineContext], dict],
    ctx: PipelineContext,
) -> StageResult:
    """Execute a stage, capturing timing and errors."""
    start = time.time()
    try:
        artifacts = fn(ctx)
        duration = (time.time() - start) * 1000
        return StageResult(
            name=name, order=order, status="success",
            duration_ms=duration, artifacts=artifacts or {},
        )
    except Exception as e:
        duration = (time.time() - start) * 1000
        logger.error("Stage %s failed: %s", name, e)
        return StageResult(
            name=name, order=order, status="failed",
            duration_ms=duration, error=str(e),
        )


# ---------------------------------------------------------------------------
# Stage implementations
# ---------------------------------------------------------------------------

def _stage_load_config(ctx: PipelineContext) -> dict:
    from plugin_examples.family_config import load_family_config
    config_path = ctx.repo_root / "pipeline" / "configs" / "families" / f"{ctx.family}.yml"
    # Check disabled directory as fallback
    if not config_path.exists():
        disabled_path = ctx.repo_root / "pipeline" / "configs" / "families" / "disabled" / f"{ctx.family}.yml"
        if disabled_path.exists():
            config_path = disabled_path
    ctx.config = load_family_config(config_path)
    if ctx.config.status == "experimental" and not getattr(ctx, "_allow_experimental", False):
        raise RuntimeError(
            f"Family '{ctx.family}' is experimental. "
            "Use --allow-experimental to run experimental families."
        )
    return {"family": ctx.config.family, "package_id": ctx.config.nuget.package_id}


def _stage_nuget_fetch(ctx: PipelineContext) -> dict:
    from plugin_examples.nuget_fetcher import fetch_package
    cfg = ctx.config.nuget
    ctx.download_manifest = fetch_package(
        cfg.package_id, cfg.version_policy,
        pinned_version=cfg.pinned_version,
        allow_prerelease=cfg.allow_prerelease,
        run_dir=ctx.run_dir, family=ctx.family,
    )
    return {
        "version": ctx.download_manifest["version"],
        "sha256": ctx.download_manifest["sha256"],
        "cached_path": ctx.download_manifest["cached_path"],
    }


def _stage_dependency_resolution(ctx: PipelineContext) -> dict:
    from plugin_examples.nuget_fetcher import resolve_dependencies
    from plugin_examples.nuget_fetcher.dependency_resolver import (
        write_dependency_manifest,
        update_package_lock,
    )
    cfg = ctx.config.nuget
    nupkg_path = Path(ctx.download_manifest["cached_path"])

    if not cfg.dependency_resolution.enabled:
        ctx.deps = []
        return {"dependency_count": 0, "skipped": True}

    ctx.deps = resolve_dependencies(
        nupkg_path,
        target_frameworks=cfg.target_framework_preference,
        max_depth=cfg.dependency_resolution.max_depth,
        run_dir=ctx.run_dir, family=ctx.family,
    )
    write_dependency_manifest(ctx.deps, ctx.run_dir, ctx.family)
    update_package_lock(ctx.download_manifest, ctx.deps, ctx.evidence_dir)
    return {"dependency_count": len(ctx.deps)}


def _stage_extraction(ctx: PipelineContext) -> dict:
    from plugin_examples.nupkg_extractor import extract_package
    nupkg_path = Path(ctx.download_manifest["cached_path"])
    dep_paths = [
        Path(d["cached_path"]) for d in (ctx.deps or [])
        if d.get("status") == "ok" and d.get("cached_path")
    ]
    ctx.extraction = extract_package(
        nupkg_path,
        package_id=ctx.config.nuget.package_id,
        family=ctx.family,
        target_framework_preference=ctx.config.nuget.target_framework_preference,
        run_dir=ctx.run_dir,
        dependency_nupkgs=dep_paths or None,
    )
    return {
        "selected_framework": ctx.extraction["selected_framework"],
        "dll_path": ctx.extraction["dll_path"],
        "xml_path": ctx.extraction.get("xml_path"),
    }


def _stage_reflection(ctx: PipelineContext) -> dict:
    from plugin_examples.reflection_catalog import build_catalog
    catalog_dir = ctx.run_dir / "catalog" / ctx.family
    catalog_dir.mkdir(parents=True, exist_ok=True)
    output_path = catalog_dir / "api-catalog.json"

    dep_dll_paths = [Path(p) for p in ctx.extraction.get("dependency_dll_paths", []) if p]

    ctx.catalog = build_catalog(
        dll_path=Path(ctx.extraction["dll_path"]),
        output_path=output_path,
        xml_path=Path(ctx.extraction["xml_path"]) if ctx.extraction.get("xml_path") else None,
        dependency_paths=dep_dll_paths or None,
        namespace_filter=ctx.config.plugin_detection.namespace_patterns,
    )
    ctx.catalog_path = output_path
    ns_count = len(ctx.catalog.get("namespaces", []))
    return {"catalog_path": str(output_path), "namespace_count": ns_count}


def _stage_plugin_detection(ctx: PipelineContext) -> dict:
    from plugin_examples.plugin_detector import (
        detect_plugin_namespaces,
        write_source_of_truth_proof,
        write_product_inventory,
        assert_source_of_truth_eligible,
    )
    ctx.detection = detect_plugin_namespaces(
        ctx.catalog, ctx.config.plugin_detection.namespace_patterns,
    )

    # Write product inventory
    write_product_inventory(
        family=ctx.family,
        package_id=ctx.config.nuget.package_id,
        resolved_version=ctx.download_manifest["version"],
        detection_result=ctx.detection,
        manifests_dir=ctx.evidence_dir,
    )

    # Write source-of-truth proof
    ctx.proof_path = write_source_of_truth_proof(
        family=ctx.family,
        package_id=ctx.config.nuget.package_id,
        resolved_version=ctx.download_manifest["version"],
        nupkg_sha256=ctx.download_manifest.get("sha256"),
        selected_target_framework=ctx.extraction.get("selected_framework"),
        dll_path=ctx.extraction.get("dll_path"),
        xml_path=ctx.extraction.get("xml_path"),
        xml_warning=ctx.extraction.get("xml_warning"),
        dependency_count=len(ctx.deps or []),
        dependency_paths=[d.get("cached_path", "") for d in (ctx.deps or [])],
        api_catalog_path=str(ctx.catalog_path) if ctx.catalog_path else None,
        detection_result=ctx.detection,
        verification_dir=ctx.evidence_dir,
    )

    # Gate: assert eligible
    assert_source_of_truth_eligible(str(ctx.proof_path))

    matched_ns = [m.namespace for m in ctx.detection.matched_namespaces]
    return {
        "eligible": ctx.detection.is_eligible,
        "matched_namespaces": matched_ns,
        "plugin_type_count": ctx.detection.public_plugin_type_count,
        "plugin_method_count": ctx.detection.public_plugin_method_count,
    }


def _stage_api_delta(ctx: PipelineContext) -> dict:
    from plugin_examples.api_delta import compute_delta
    from plugin_examples.api_delta.delta_engine import write_delta_report
    ctx.delta = compute_delta(ctx.catalog, old_catalog=None)
    write_delta_report(ctx.delta, ctx.evidence_dir)
    return {
        "initial_run": ctx.delta.initial_run,
        "total_changes": ctx.delta.total_changes,
    }


def _stage_impact_mapping(ctx: PipelineContext) -> dict:
    from plugin_examples.api_delta import map_impact
    from plugin_examples.api_delta.impact_mapper import write_impact_report
    impact = map_impact(ctx.delta, existing_examples_index=None)
    write_impact_report(impact, ctx.evidence_dir)
    return {"new_api_needed": len(impact.new_api_examples_needed)}


def _stage_fixture_registry(ctx: PipelineContext) -> dict:
    from plugin_examples.fixture_registry.registry import (
        build_fixture_registry,
        write_fixture_registry,
    )
    sources = _fixture_sources_to_dicts(ctx.config.fixtures.sources)
    registry = build_fixture_registry(ctx.family, sources)
    write_fixture_registry(registry, ctx.evidence_dir)
    ctx._fixture_registry = registry
    return {"fixture_count": len(registry.fixtures)}


def _stage_example_mining(ctx: PipelineContext) -> dict:
    from plugin_examples.example_miner import mine_examples
    from plugin_examples.example_miner.miner import write_examples_index, write_stale_report
    sources = _fixture_sources_to_dicts(ctx.config.existing_examples.sources)
    mining = mine_examples(ctx.family, sources, catalog=ctx.catalog)
    write_examples_index(mining, ctx.evidence_dir)
    write_stale_report(mining, ctx.evidence_dir)
    return {"mined_total": mining.total, "stale_count": mining.stale_count}


def _stage_scenario_planning(ctx: PipelineContext) -> dict:
    from plugin_examples.scenario_planner import (
        plan_scenarios,
        write_scenario_catalog,
        write_blocked_scenarios,
    )
    from plugin_examples.scenario_planner.type_classifier import (
        classify_catalog,
        write_type_role_classification,
    )
    from plugin_examples.scenario_planner.consumer_mapper import (
        build_consumer_map,
        write_consumer_relationships,
    )
    from plugin_examples.scenario_planner.entrypoint_scorer import (
        score_entrypoint,
        write_entrypoint_scores,
    )
    matched_ns = [m.namespace for m in ctx.detection.matched_namespaces]
    fixture_dict = _fixture_registry_to_dict(
        getattr(ctx, "_fixture_registry", None)
    )

    fixture_ext = ".xlsx"
    if ctx.config and hasattr(ctx.config, "template_hints"):
        fixture_ext = ctx.config.template_hints.default_fixture_extension

    # Type role classification evidence
    roles = classify_catalog(ctx.catalog, matched_ns)
    write_type_role_classification(roles, ctx.evidence_dir)

    # Consumer relationship evidence
    consumer_map = build_consumer_map(ctx.catalog, matched_ns)
    write_consumer_relationships(consumer_map, ctx.evidence_dir)

    # Entrypoint scoring evidence
    scores = []
    for r in roles:
        type_info = _find_type_in_catalog(ctx.catalog, r.full_name)
        if type_info:
            fixture_avail = bool(fixture_dict and fixture_dict.get("fixtures"))
            scores.append(score_entrypoint(type_info, r, consumer_map,
                                           fixture_available=fixture_avail))
    write_entrypoint_scores(scores, ctx.evidence_dir)

    ctx.planning = plan_scenarios(
        family=ctx.family,
        catalog=ctx.catalog,
        plugin_namespaces=matched_ns,
        fixture_registry=fixture_dict,
        min_examples=ctx.config.generation.min_examples_per_family,
        source_of_truth_proof_path=str(ctx.proof_path),
        default_fixture_extension=fixture_ext,
    )
    write_scenario_catalog(ctx.planning, ctx.evidence_dir)
    write_blocked_scenarios(ctx.planning, ctx.evidence_dir)

    # Write fixture strategy plan evidence
    _write_fixture_strategy_plan(ctx.planning, ctx.evidence_dir)

    # Write scenario input format map evidence
    _write_scenario_input_format_map(ctx.planning, ctx.evidence_dir)

    standalone_roles = sum(1 for r in roles if r.role in {"workflow_root", "operation_facade"})
    return {
        "ready_count": ctx.planning.ready_count,
        "blocked_count": ctx.planning.blocked_count,
        "total_types_classified": len(roles),
        "standalone_types": standalone_roles,
    }


def _stage_llm_preflight(ctx: PipelineContext) -> dict:
    from plugin_examples.llm_router import LLMRouter
    from plugin_examples.llm_router.router import write_preflight_report
    ctx.llm_router = LLMRouter(provider_order=ctx.config.llm.provider_order)
    preflight = ctx.llm_router.run_preflight()
    ctx.llm_available = ctx.llm_router.selected_provider is not None
    write_preflight_report(preflight, ctx.llm_router.selected_provider, ctx.evidence_dir)

    if not ctx.llm_available and ctx.require_llm:
        raise RuntimeError("No LLM provider available and --require-llm is set")

    return {
        "selected_provider": ctx.llm_router.selected_provider,
        "llm_available": ctx.llm_available,
    }


def _stage_generation(ctx: PipelineContext) -> dict:
    from plugin_examples.generator import (
        build_packet,
        generate_example,
        generate_project,
        write_example_index,
    )

    if not ctx.planning or ctx.planning.ready_count == 0:
        return {"examples_generated": 0, "reason": "no ready scenarios"}

    # LLM wrapper to bridge signature mismatch
    llm_fn = None
    if ctx.llm_available and not ctx.template_mode:
        llm_fn = lambda p, s: ctx.llm_router.generate(p, system_prompt=s)

    gen_mode = "llm" if llm_fn else "template"
    output_dir = ctx.run_dir / "generated" / ctx.family

    for scenario in ctx.planning.ready_scenarios:
        scenario_dict = scenario_to_dict(scenario)
        try:
            hints = {}
            if ctx.config and hasattr(ctx.config, "template_hints"):
                from dataclasses import asdict as _asdict
                hints = _asdict(ctx.config.template_hints)
            packet = build_packet(scenario_dict, ctx.catalog, template_hints=hints)
            example = generate_example(packet, llm_generate=llm_fn)
            if example.status == "failed" or not example.code.strip():
                logger.warning("Skipping project for %s: %s", scenario.scenario_id,
                               example.failure_reason or "empty code")
                continue
            project = generate_project(
                example,
                package_id=ctx.config.nuget.package_id,
                package_version=ctx.download_manifest.get("version", "*"),
                target_framework="net8.0",
                output_dir=output_dir,
                input_strategy=getattr(scenario, "input_strategy", "none"),
                input_files=getattr(scenario, "input_files", []),
            )
            ctx.generated_projects.append(project)
        except Exception as e:
            logger.warning("Generation failed for %s: %s", scenario.scenario_id, e)

    write_example_index(ctx.generated_projects, ctx.evidence_dir)

    # Write generated fixtures evidence
    from plugin_examples.fixture_registry.fixture_factory import (
        GeneratedFixture,
        write_generated_fixtures_evidence,
    )
    all_fixtures: list[GeneratedFixture] = []
    for proj in ctx.generated_projects:
        placed = proj.get("placed_fixtures", [])
        for fp in placed:
            p = Path(fp)
            if p.exists():
                all_fixtures.append(GeneratedFixture(
                    path=fp, format=p.suffix, created_by="fixture_factory",
                    validity_check=f"file_exists_and_size_{p.stat().st_size}",
                    size_bytes=p.stat().st_size, ready=True,
                ))
    if all_fixtures:
        write_generated_fixtures_evidence(all_fixtures, ctx.evidence_dir)

    # Write few-shot patterns evidence
    _write_fewshot_patterns(ctx.generated_projects, ctx.evidence_dir)

    return {
        "examples_generated": len(ctx.generated_projects),
        "generation_mode": gen_mode,
        "fixtures_generated": len(all_fixtures),
    }


def _stage_validation(ctx: PipelineContext) -> dict:
    from plugin_examples.verifier_bridge import run_dotnet_validation
    from plugin_examples.verifier_bridge.dotnet_runner import write_validation_results
    from plugin_examples.generator.code_generator import _extract_code

    if not ctx.generated_projects:
        return {"validated": 0, "reason": "no generated projects"}

    max_build_repairs = 2 if (ctx.llm_available and not ctx.template_mode) else 0
    max_runtime_repairs = 1 if (ctx.llm_available and not ctx.template_mode) else 0
    repairs_done = 0
    runtime_repairs_done = 0
    repair_log: list[dict] = []

    # Repairable runtime failure classifications
    repairable_classifications = {
        "interactive_console_call", "wrong_input_format", "invalid_api_usage",
        "blocked_invalid_operation", "blocked_null_argument",
        "missing_options_input", "null_options_passed",
        "blocked_runtime_context_required",
    }

    from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure

    for proj in ctx.generated_projects:
        vr = run_dotnet_validation(
            Path(proj["project_dir"]),
            proj["scenario_id"],
            skip_run=ctx.skip_run,
        )

        # Build-repair cycle: feed compiler errors back to LLM
        attempt = 0
        while not vr.passed and vr.failure_stage == "build" and attempt < max_build_repairs:
            attempt += 1
            build_stdout = (vr.build.stdout or "") if vr.build else ""
            build_stderr = (vr.build.stderr or "") if vr.build else ""
            build_errors = build_stderr or build_stdout
            if not build_errors:
                break
            program_path = Path(proj["program_path"])
            current_code = program_path.read_text(encoding="utf-8")
            repair_prompt = (
                f"The following C# code fails to compile. Fix it.\n\n"
                f"Compiler stdout:\n{build_stdout[:800]}\n\n"
                f"Compiler stderr:\n{build_stderr[:800]}\n\n"
                f"Code:\n```csharp\n{current_code}\n```\n\n"
                f"RULES: Do NOT use Console.ReadKey() or Console.ReadLine(). "
                f"Do NOT use try/catch to hide errors. "
                f"Return ONLY the fixed C# code in a ```csharp code block."
            )
            try:
                response = ctx.llm_router.generate(repair_prompt, system_prompt=(
                    "You are an expert C# developer. Fix the compilation errors. "
                    "FORBIDDEN: Console.ReadKey(), Console.ReadLine(), TODO, NotImplementedException. "
                    "Return ONLY the corrected code in a single ```csharp code block."
                ))
                fixed_code = _extract_code(response)
                if fixed_code and fixed_code != current_code:
                    program_path.write_text(fixed_code, encoding="utf-8")
                    vr = run_dotnet_validation(
                        Path(proj["project_dir"]),
                        proj["scenario_id"],
                        skip_run=ctx.skip_run,
                    )
                    repairs_done += 1
                    repair_log.append({
                        "scenario_id": proj["scenario_id"],
                        "repair_type": "build",
                        "attempt": attempt,
                        "success": vr.passed or (vr.build and vr.build.success),
                    })
                    logger.info("Build repair attempt %d for %s: %s",
                                attempt, proj["scenario_id"],
                                "passed" if vr.passed else "still failing")
                else:
                    break
            except Exception as e:
                logger.warning("Build repair failed for %s: %s", proj["scenario_id"], e)
                break

        # Runtime-repair cycle: fix repairable runtime failures
        rt_attempt = 0
        while (not vr.passed and vr.failure_stage == "run"
               and rt_attempt < max_runtime_repairs
               and vr.run):
            rt_attempt += 1
            rc = classify_runtime_failure(
                proj["scenario_id"],
                vr.run.exit_code,
                vr.run.stdout or "",
                vr.run.stderr or "",
            )
            if rc.classification not in repairable_classifications:
                break

            program_path = Path(proj["program_path"])
            current_code = program_path.read_text(encoding="utf-8")
            run_stdout = vr.run.stdout or ""
            run_stderr = vr.run.stderr or ""
            repair_prompt = (
                f"The following C# code compiles but fails at runtime.\n\n"
                f"Runtime classification: {rc.classification}\n"
                f"Runtime stdout:\n{run_stdout[:600]}\n\n"
                f"Runtime stderr:\n{run_stderr[:600]}\n\n"
                f"Code:\n```csharp\n{current_code}\n```\n\n"
                f"RULES: Do NOT use Console.ReadKey() or Console.ReadLine(). "
                f"Do NOT use try/catch to hide errors. "
                f"Validate input file exists before API call. "
                f"Return ONLY the fixed C# code in a ```csharp code block."
            )
            try:
                response = ctx.llm_router.generate(repair_prompt, system_prompt=(
                    "You are an expert C# developer. Fix the runtime error. "
                    "FORBIDDEN: Console.ReadKey(), Console.ReadLine(). "
                    "Return ONLY the corrected code in a single ```csharp code block."
                ))
                fixed_code = _extract_code(response)
                if fixed_code and fixed_code != current_code:
                    program_path.write_text(fixed_code, encoding="utf-8")
                    vr = run_dotnet_validation(
                        Path(proj["project_dir"]),
                        proj["scenario_id"],
                        skip_run=ctx.skip_run,
                    )
                    runtime_repairs_done += 1
                    repair_log.append({
                        "scenario_id": proj["scenario_id"],
                        "repair_type": "runtime",
                        "classification": rc.classification,
                        "attempt": rt_attempt,
                        "success": vr.passed,
                    })
                    logger.info("Runtime repair attempt %d for %s (%s): %s",
                                rt_attempt, proj["scenario_id"], rc.classification,
                                "passed" if vr.passed else "still failing")
                else:
                    break
            except Exception as e:
                logger.warning("Runtime repair failed for %s: %s", proj["scenario_id"], e)
                break

        ctx.validation_results.append(vr)

    write_validation_results(ctx.validation_results, ctx.evidence_dir)

    # Classify runtime failures for feedback
    from plugin_examples.scenario_planner.runtime_feedback import (
        classify_validation_results,
        write_runtime_failure_classifications,
    )
    runtime_failures = classify_validation_results(ctx.validation_results)
    if runtime_failures:
        write_runtime_failure_classifications(runtime_failures, ctx.evidence_dir)

    # Write repair attempts evidence
    if repair_log:
        repair_path = ctx.evidence_dir / "latest" / "repair-attempts.json"
        repair_path.parent.mkdir(parents=True, exist_ok=True)
        import json as _json
        repair_path.write_text(_json.dumps({
            "total_build_repairs": repairs_done,
            "total_runtime_repairs": runtime_repairs_done,
            "attempts": repair_log,
        }, indent=2))

    passed = sum(1 for v in ctx.validation_results if v.passed)
    failed = len(ctx.validation_results) - passed

    if failed > 0 and ctx.require_validation:
        raise RuntimeError(
            f"Validation failed for {failed}/{len(ctx.validation_results)} examples "
            "and --require-validation is set"
        )

    build_passed = sum(1 for v in ctx.validation_results if v.build and v.build.success)
    run_passed = sum(1 for v in ctx.validation_results if v.run and v.run.success)
    runtime_classified = len(runtime_failures)

    return {
        "total": len(ctx.validation_results),
        "passed": passed,
        "failed": failed,
        "build_passed": build_passed,
        "run_passed": run_passed,
        "build_repairs": repairs_done,
        "runtime_repairs": runtime_repairs_done,
        "runtime_failures_classified": runtime_classified,
    }


def _stage_reviewer(ctx: PipelineContext) -> dict:
    from plugin_examples.verifier_bridge.bridge import (
        ReviewerUnavailableError,
        ReviewerResult,
        run_example_reviewer,
        write_reviewer_results,
    )
    from plugin_examples.verifier_bridge.reviewer_preflight import (
        run_reviewer_preflight,
        write_reviewer_preflight,
    )

    # Write preflight evidence regardless of outcome
    preflight = run_reviewer_preflight()
    write_reviewer_preflight(preflight, ctx.evidence_dir)

    try:
        result = run_example_reviewer(
            family=ctx.family,
            workspace_dir=ctx.run_dir,
        )
    except ReviewerUnavailableError:
        result = ReviewerResult(available=False, error="Not installed")
        if ctx.require_reviewer:
            write_reviewer_results(result, ctx.evidence_dir)
            raise RuntimeError("Reviewer unavailable and --require-reviewer is set")

    write_reviewer_results(result, ctx.evidence_dir)
    return {
        "available": result.available,
        "passed": result.passed,
        "preflight_ready": preflight.overall_ready,
    }


def _stage_publisher(ctx: PipelineContext) -> dict:
    from plugin_examples.publisher import publish_examples
    from plugin_examples.publisher.publisher import write_publishing_report

    examples = ctx.generated_projects or []
    result = publish_examples(
        family=ctx.family,
        run_id=ctx.run_id,
        examples=examples,
        verification_dir=ctx.evidence_dir,
        dry_run=ctx.dry_run,
    )
    write_publishing_report(result, ctx.evidence_dir)
    return {
        "status": result.status,
        "evidence_verified": result.evidence_verified,
        "files_included": len(result.files_included),
    }


# ---------------------------------------------------------------------------
# Verdict determination
# ---------------------------------------------------------------------------

def _determine_verdict(stages: list[StageResult], ctx: PipelineContext) -> str:
    """Determine the proof verdict based on stage outcomes.

    Delegates to the central gate engine for honest verdict computation.
    """
    from plugin_examples.gates.evaluator import determine_verdict
    return determine_verdict(stages, ctx)


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _build_report(
    ctx: PipelineContext,
    stages: list[StageResult],
    before: dict,
    after: dict,
    start_time: str,
    end_time: str,
    total_ms: float,
    command: str = "",
) -> dict:
    """Build the structured pilot report."""
    passed = sum(1 for s in stages if s.status == "success")
    degraded = sum(1 for s in stages if s.status == "degraded")
    failed = sum(1 for s in stages if s.status == "failed")
    skipped = sum(1 for s in stages if s.status == "skipped")

    hard_stopped = any(
        s.status == "failed" for s in stages[:7]
    )

    # Use partitioned verdict from gate_verdict if available
    verdict = ctx.gate_verdict.verdict if ctx.gate_verdict else _determine_verdict(stages, ctx)

    # Comparison section
    gen_stage = next((s for s in stages if s.name == "generation"), None)
    val_stage = next((s for s in stages if s.name == "validation"), None)
    det_stage = next((s for s in stages if s.name == "plugin_detection"), None)
    plan_stage = next((s for s in stages if s.name == "scenario_planning"), None)
    llm_stage = next((s for s in stages if s.name == "llm_preflight"), None)
    pub_stage = next((s for s in stages if s.name == "publisher"), None)
    fetch_stage = next((s for s in stages if s.name == "nuget_fetch"), None)
    rev_stage = next((s for s in stages if s.name == "reviewer"), None)
    ext_stage = next((s for s in stages if s.name == "extraction"), None)

    # Run-scoped evidence listing
    evidence_dir_latest = ctx.evidence_dir / "latest"
    run_evidence = []
    if evidence_dir_latest.exists():
        run_evidence = sorted(f.name for f in evidence_dir_latest.iterdir() if f.is_file())

    comparison = {
        "package_version_resolved": fetch_stage.artifacts.get("version") if fetch_stage else None,
        "nupkg_sha256": fetch_stage.artifacts.get("sha256") if fetch_stage else None,
        "selected_framework": ext_stage.artifacts.get("selected_framework") if ext_stage else None,
        "dll_path": ext_stage.artifacts.get("dll_path") if ext_stage else None,
        "catalog_path": stages[4].artifacts.get("catalog_path") if len(stages) > 4 else None,
        "matched_plugin_namespaces": det_stage.artifacts.get("matched_namespaces", []) if det_stage else [],
        "source_of_truth_status": "eligible" if (det_stage and det_stage.status == "success") else "failed",
        "delta_status": ("initial_run" if stages[7].artifacts.get("initial_run", True) else "diff") if len(stages) > 7 else "unknown",
        "fixture_count": stages[9].artifacts.get("fixture_count", 0) if len(stages) > 9 else 0,
        "mined_example_count": stages[10].artifacts.get("mined_total", 0) if len(stages) > 10 else 0,
        "ready_scenario_count": plan_stage.artifacts.get("ready_count", 0) if plan_stage else 0,
        "blocked_scenario_count": plan_stage.artifacts.get("blocked_count", 0) if plan_stage else 0,
        "llm_preflight_result": llm_stage.artifacts.get("selected_provider", "no_provider") if llm_stage else "skipped",
        "generation_mode": gen_stage.artifacts.get("generation_mode", "skipped") if gen_stage else "skipped",
        "examples_generated_count": gen_stage.artifacts.get("examples_generated", 0) if gen_stage else 0,
        "dotnet_restore_passed": sum(1 for v in ctx.validation_results if v.restore and v.restore.success) if ctx.validation_results else 0,
        "dotnet_build_passed": sum(1 for v in ctx.validation_results if v.build and v.build.success) if ctx.validation_results else 0,
        "dotnet_run_passed": sum(1 for v in ctx.validation_results if v.run and v.run.success) if ctx.validation_results else 0,
        "reviewer_available": rev_stage.artifacts.get("available", False) if rev_stage else False,
        "reviewer_result": "passed" if (rev_stage and rev_stage.artifacts.get("passed")) else "unavailable",
        "publisher_status": pub_stage.artifacts.get("status", "skipped") if pub_stage else "skipped",
        "skipped_stages": [s.name for s in stages if s.status == "skipped"],
        "degraded_stages": [s.name for s in stages if s.status == "degraded"],
    }

    return {
        "meta": {
            "run_id": ctx.run_id,
            "family": ctx.family,
            "dry_run": ctx.dry_run,
            "skip_run": ctx.skip_run,
            "template_mode": ctx.template_mode,
            "start_time": start_time,
            "end_time": end_time,
            "total_duration_ms": total_ms,
            "python_version": platform.python_version(),
            "platform": sys.platform,
            "command": command,
        },
        "before": before,
        "after": after,
        "comparison": comparison,
        "stages": [
            {
                "name": s.name,
                "order": s.order,
                "status": s.status,
                "duration_ms": s.duration_ms,
                "error": s.error,
                "artifacts": s.artifacts,
            }
            for s in stages
        ],
        "gate_summary": {
            "total_stages": len(stages),
            "passed": passed,
            "degraded": degraded,
            "failed": failed,
            "skipped": skipped,
            "hard_stopped": hard_stopped,
        },
        "environment": {
            "python_version": platform.python_version(),
            "platform": sys.platform,
        },
        "run_evidence_files": run_evidence,
        "pr_candidate_count": sum(1 for v in ctx.validation_results if v.passed) if ctx.validation_results else 0,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Main pipeline function
# ---------------------------------------------------------------------------

STAGE_DEFINITIONS = [
    ("load_config", 1, _stage_load_config),
    ("nuget_fetch", 2, _stage_nuget_fetch),
    ("dependency_resolution", 3, _stage_dependency_resolution),
    ("extraction", 4, _stage_extraction),
    ("reflection", 5, _stage_reflection),
    ("plugin_detection", 6, _stage_plugin_detection),
    ("source_of_truth_gate", 7, None),  # combined into plugin_detection
    ("api_delta", 8, _stage_api_delta),
    ("impact_mapping", 9, _stage_impact_mapping),
    ("fixture_registry", 10, _stage_fixture_registry),
    ("example_mining", 11, _stage_example_mining),
    ("scenario_planning", 12, _stage_scenario_planning),
    ("llm_preflight", 13, _stage_llm_preflight),
    ("generation", 14, _stage_generation),
    ("validation", 15, _stage_validation),
    ("reviewer", 16, _stage_reviewer),
    ("publisher", 17, _stage_publisher),
]

# Hard-stop stages (pipeline halts on failure)
HARD_STOP_STAGES = {"load_config", "nuget_fetch", "dependency_resolution",
                     "extraction", "reflection", "plugin_detection"}


def run_pipeline(
    *,
    family: str,
    dry_run: bool = True,
    skip_run: bool = False,
    template_mode: bool = False,
    require_llm: bool = False,
    require_validation: bool = False,
    require_reviewer: bool = False,
    run_id: str | None = None,
    repo_root: Path | None = None,
    max_tier: int = 5,
    command: str = "",
    promote_latest: bool = False,
    allow_experimental: bool = False,
) -> dict:
    """Run the full pipeline and return a structured report dict."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    if run_id is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_id = f"pilot-{family}-{ts}"

    run_dir = repo_root / "workspace" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    manifests_dir = repo_root / "workspace" / "manifests"
    verification_dir = repo_root / "workspace" / "verification"

    ctx = PipelineContext(
        family=family,
        run_id=run_id,
        dry_run=dry_run,
        skip_run=skip_run,
        template_mode=template_mode,
        require_llm=require_llm,
        require_validation=require_validation,
        require_reviewer=require_reviewer,
        repo_root=repo_root,
        run_dir=run_dir,
        evidence_dir=evidence_dir,
    )
    ctx._allow_experimental = allow_experimental

    # Before snapshot
    before = _snapshot_workspace(manifests_dir, verification_dir)

    start_time = datetime.now(timezone.utc).isoformat()
    pipeline_start = time.time()

    # Tier-to-stage mapping
    tier_max_stage = {0: 0, 1: 6, 2: 12, 3: 14, 4: 16, 5: 17}
    max_stage_order = tier_max_stage.get(max_tier, 17)

    # Execute stages
    stages: list[StageResult] = []
    hard_stopped = False

    # Effective stage list (stage 7 = source_of_truth_gate is combined into stage 6)
    effective_stages = [
        (name, order, fn) for name, order, fn in STAGE_DEFINITIONS
        if fn is not None
    ]

    for name, order, fn in effective_stages:
        if hard_stopped:
            stages.append(StageResult(name=name, order=order, status="skipped"))
            continue

        if order > max_stage_order:
            stages.append(StageResult(name=name, order=order, status="skipped",
                                       error=f"Skipped: max tier {max_tier}"))
            continue

        result = _run_stage(name, order, fn, ctx)

        # Determine if failure is hard stop or degraded.
        # Only degrade stages with explicit optional semantics.
        # All other failures stay "failed" for honest reporting.
        if result.status == "failed":
            if name in HARD_STOP_STAGES:
                hard_stopped = True
            elif name == "llm_preflight" and not ctx.require_llm:
                result.status = "degraded"
            elif name == "validation" and not ctx.require_validation:
                result.status = "degraded"
            elif name == "reviewer" and not ctx.require_reviewer:
                result.status = "degraded"
            # All other failures stay "failed" — no blanket degradation

        stages.append(result)

    pipeline_end = time.time()
    end_time = datetime.now(timezone.utc).isoformat()
    total_ms = (pipeline_end - pipeline_start) * 1000

    # Per-example gate evaluation and partitioning
    from plugin_examples.gates.example_gates import (
        evaluate_example_gates,
        compute_aggregate_gates,
        compute_partitioned_verdict,
        build_pr_candidate_manifest,
        build_scenario_feedback,
        write_example_gate_results,
        write_aggregate_gate_results,
        write_pr_candidate_manifest,
        write_scenario_feedback,
    )
    from plugin_examples.scenario_planner.runtime_feedback import (
        classify_validation_results as _classify_vr,
    )

    # Build per-example gates
    rev_stage = next((s for s in stages if s.name == "reviewer"), None)
    reviewer_avail = rev_stage.artifacts.get("available", False) if rev_stage else False
    reviewer_pass = rev_stage.artifacts.get("passed", False) if rev_stage else False
    rt_classifications = _classify_vr(ctx.validation_results) if ctx.validation_results else []

    example_gates = evaluate_example_gates(
        validation_results=ctx.validation_results,
        generated_projects=ctx.generated_projects,
        runtime_classifications=rt_classifications,
        reviewer_available=reviewer_avail,
        reviewer_passed=reviewer_pass,
        skip_run=skip_run,
    )
    write_example_gate_results(example_gates, evidence_dir)

    aggregate = compute_aggregate_gates(example_gates)
    write_aggregate_gate_results(aggregate, evidence_dir)

    pr_manifest = build_pr_candidate_manifest(example_gates, dry_run=dry_run)
    write_pr_candidate_manifest(pr_manifest, evidence_dir)

    scenario_fb = build_scenario_feedback(example_gates)
    write_scenario_feedback(scenario_fb, evidence_dir)

    # Gate evaluation — compute honest verdict (now with partitioned awareness)
    from plugin_examples.gates.evaluator import evaluate_gates
    from plugin_examples.gates.writer import write_gate_results

    ctx.gate_verdict = evaluate_gates(stages, ctx)

    # Override verdict with partitioned verdict if examples were generated
    if ctx.generated_projects and ctx.validation_results:
        gen_stage = next((s for s in stages if s.name == "generation"), None)
        gen_mode = gen_stage.artifacts.get("generation_mode", "template") if gen_stage else "template"
        ctx.gate_verdict.verdict = compute_partitioned_verdict(aggregate, ctx, gen_mode)
        ctx.gate_verdict.publishable = ctx.gate_verdict.verdict in ("PR_READY", "FULL_E2E_PASSED")

    write_gate_results(ctx.gate_verdict, evidence_dir)

    # After snapshot
    after = _snapshot_workspace(manifests_dir, verification_dir)

    # Add run-scoped evidence listing
    after["run_evidence_files"] = sorted(
        f.name for f in (evidence_dir / "latest").iterdir()
        if f.is_file()
    ) if (evidence_dir / "latest").exists() else []

    report = _build_report(
        ctx, stages, before, after,
        start_time, end_time, total_ms,
        command=command,
    )

    # Write report
    report_path = run_dir / "pilot-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    logger.info("Pilot report written: %s", report_path)

    # Promote evidence to durable paths if requested
    if promote_latest:
        import shutil
        src_latest = evidence_dir / "latest"
        dst_latest = verification_dir / "latest"
        dst_latest.mkdir(parents=True, exist_ok=True)
        if src_latest.exists():
            for f in src_latest.iterdir():
                if f.is_file() and f.name != ".gitkeep":
                    shutil.copy2(f, dst_latest / f.name)
            logger.info("Evidence promoted to %s", dst_latest)

        # Promote manifests (package-lock, fixture-registry, etc.)
        dst_manifests = manifests_dir
        dst_manifests.mkdir(parents=True, exist_ok=True)
        manifest_files = ["package-lock.json", "fixture-registry.json",
                          "existing-examples-index.json", "scenario-catalog.json",
                          "example-index.json"]
        for mf in manifest_files:
            src_mf = evidence_dir / mf
            if src_mf.exists():
                shutil.copy2(src_mf, dst_manifests / mf)
        logger.info("Manifests promoted to %s", dst_manifests)

    return report
