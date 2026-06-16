"""Pipeline orchestrator — chains all 13 modules into a gate-driven execution flow."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any

from plugin_examples.observability import bind_context as _bind_obs_context  # noqa: E402
from plugin_examples.observability import get_logger


def _now_utc() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Core types
# ---------------------------------------------------------------------------


@dataclass
class StageResult:
    """Result of a single pipeline stage."""

    name: str
    order: int
    status: str = "pending"  # success | failed | degraded | skipped
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
    # Stages completed so far during the loop (updated after each stage appends).
    # Used by _stage_publisher to evaluate gates before the post-loop block runs.
    _completed_stages: list = field(default_factory=list)
    # Lifecycle registry — tracks every planned example through all stages.
    lifecycle_registry: Any = None
    # Agent metrics collector — optional, set when --metrics is enabled.
    metrics_collector: Any = None
    # Healing intelligence loader — loaded at generation stage for advisory constraints.
    healing_intelligence: Any = None
    # Non-LowCode fallback candidates — set by _stage_fallback_registry_lookup().
    # Only PROBE_CONFIRMED and VERIFIED_PUBLISHABLE entries are included.
    fallback_candidates: list | None = None
    # Strict output validation — when True, advisory_no_output and advisory_failed
    # block publication instead of being advisory-only.
    strict_output_validation: bool = False


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


def _write_catalog_hash_evidence(result, evidence_dir: Path) -> None:
    """Write catalog-hash-validation.json evidence."""
    import json as _json
    from datetime import datetime

    out = evidence_dir / "latest" / "catalog-hash-validation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = result.to_dict()
    data["validated_at"] = datetime.now(UTC).isoformat()
    out.write_text(_json.dumps(data, indent=2), encoding="utf-8")


def _write_fixture_strategy_plan(planning, evidence_dir: Path) -> None:
    """Write fixture-strategy-plan.json evidence."""
    import json as _json

    scenarios = []
    for s in planning.ready_scenarios + planning.blocked_scenarios:
        scenarios.append(
            {
                "scenario_id": s.scenario_id,
                "required_input_formats": [getattr(s, "required_input_format", "")]
                if getattr(s, "required_input_format", "")
                else [],
                "input_strategy": getattr(s, "input_strategy", "none"),
                "input_files": getattr(s, "input_files", []),
                "strategy_status": s.status if s.status.startswith("blocked") else "ready",
                "blocked_reason": s.blocked_reason,
            }
        )
    out = evidence_dir / "latest" / "fixture-strategy-plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        _json.dumps(
            {
                "total_scenarios": len(scenarios),
                "ready": sum(1 for s in scenarios if s["strategy_status"] == "ready"),
                "blocked": sum(1 for s in scenarios if s["strategy_status"] != "ready"),
                "strategies": {
                    "generated_fixture_file": sum(
                        1 for s in scenarios if s["input_strategy"] == "generated_fixture_file"
                    ),
                    "existing_fixture": sum(1 for s in scenarios if s["input_strategy"] == "existing_fixture"),
                    "programmatic_input": sum(1 for s in scenarios if s["input_strategy"] == "programmatic_input"),
                    "none": sum(1 for s in scenarios if s["input_strategy"] == "none"),
                    "no_valid_input_strategy": sum(
                        1 for s in scenarios if s["input_strategy"] == "no_valid_input_strategy"
                    ),
                },
                "scenarios": scenarios,
            },
            indent=2,
        )
    )


def _write_scenario_input_format_map(planning, evidence_dir: Path) -> None:
    """Write scenario-input-format-map.json evidence using FormatContract authority."""
    import json as _json

    entries = []
    for s in planning.ready_scenarios:
        type_name = s.target_type.split(".")[-1]
        input_fmt = getattr(s, "required_input_format", ".xlsx")
        output_fmt = getattr(s, "required_output_contract", "")
        source = "format_contract"
        contract_id = getattr(s, "format_contract_id", "")
        contract_hash = getattr(s, "format_contract_hash", "")

        if not output_fmt:
            try:
                from plugin_examples.format_authority.store import get_contract

                _fam = s.scenario_id.split("-", 1)[0] if s.scenario_id else ""
                if _fam:
                    fc = get_contract(_fam, type_name)
                    output_fmt = fc.canonical_output_format
                    contract_id = fc.contract_id
                    contract_hash = fc.contract_hash
            except (KeyError, ImportError):
                from plugin_examples.scenario_planner.planner import _infer_output_format

                output_fmt = _infer_output_format(type_name)
                source = "planner_map_deprecated"

        entries.append(
            {
                "scenario_id": s.scenario_id,
                "workflow_type": type_name,
                "selected_input_format": input_fmt,
                "selected_output_format": output_fmt,
                "source": source,
                "contract_id": contract_id,
                "contract_hash": contract_hash,
                "confidence": "high" if source == "format_contract" else "medium",
                "blocked_if_unclear": False,
            }
        )
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
            patterns.append(
                {
                    "scenario_id": proj["scenario_id"],
                    "uses_basedir": has_basedir,
                    "validates_input": has_file_check,
                    "validates_output": has_output_check,
                    "no_interactive_input": no_readkey and no_readline,
                    "input_strategy": proj.get("input_strategy", "none"),
                }
            )

    out = evidence_dir / "latest" / "llm-fewshot-patterns.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        _json.dumps(
            {
                "total_patterns": len(patterns),
                "verified_passing": 0,  # Updated after validation
                "patterns": patterns,
            },
            indent=2,
        )
    )


def _fixture_sources_to_dicts(sources) -> list[dict]:
    """Convert list[FixtureSource] dataclasses to list[dict]."""
    return [{"type": s.type, "owner": s.owner, "repo": s.repo, "branch": s.branch, "paths": s.paths} for s in sources]


def _fixture_registry_to_dict(registry) -> dict | None:
    """Convert FixtureRegistry to dict for plan_scenarios (expects dict|None)."""
    if registry is None:
        return None
    return {
        "fixtures": [{"filename": f.filename, "available": f.available} for f in registry.fixtures],
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
        return sorted(f.name for f in d.iterdir() if f.is_file() and f.name != ".gitkeep")

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
            name=name,
            order=order,
            status="success",
            duration_ms=duration,
            artifacts=artifacts or {},
        )
    except Exception as e:
        duration = (time.time() - start) * 1000
        logger.error("Stage %s failed: %s", name, e)
        return StageResult(
            name=name,
            order=order,
            status="failed",
            duration_ms=duration,
            error=str(e),
        )


# ---------------------------------------------------------------------------
# Stage implementations
# ---------------------------------------------------------------------------


def _stage_load_config(ctx: PipelineContext) -> dict:
    import hashlib as _hashlib
    import re as _re

    from plugin_examples.family_config import load_family_config

    # Allow CLI override via --family-config
    override = getattr(ctx, "_family_config_path", None)
    if override:
        config_path = Path(override)
    else:
        config_path = ctx.repo_root / "pipeline" / "configs" / "families" / f"{ctx.family}.yml"
        # Check disabled directory as fallback
        if not config_path.exists():
            disabled_path = ctx.repo_root / "pipeline" / "configs" / "families" / "disabled" / f"{ctx.family}.yml"
            if disabled_path.exists():
                config_path = disabled_path
    ctx.config = load_family_config(config_path)
    if ctx.config.status == "experimental" and not getattr(ctx, "_allow_experimental", False):
        raise RuntimeError(
            f"Family '{ctx.family}' is experimental. " "Use --allow-experimental to run experimental families."
        )
    if ctx.config.status == "discovery_only":
        has_fallback = getattr(ctx.config.plugin_detection, "fallback_strategy", None)
        if not has_fallback:
            raise RuntimeError(
                f"Family '{ctx.family}' is discovery_only. "
                "Use 'discover-lowcode' to run source-of-truth discovery. "
                "Generation is not allowed for discovery_only families without fallback_strategy."
            )
        logger.info(
            "Family '%s' is discovery_only with fallback_strategy=%s — proceeding via non-LowCode path",
            ctx.family,
            has_fallback,
        )
    # Compute config/constraints hashes for replay integrity checks (non-fatal if unavailable)
    artifacts: dict = {"family": ctx.config.family, "package_id": ctx.config.nuget.package_id}
    try:
        if config_path.exists():
            raw_text = config_path.read_text(encoding="utf-8")
            artifacts["config_hash"] = _hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
            m = _re.search(r"per_type_constraints\s*:(.+?)(?=\n\S|\Z)", raw_text, _re.DOTALL)
            constraints_text = m.group(1) if m else ""
            artifacts["constraints_hash"] = _hashlib.sha256(constraints_text.encode("utf-8")).hexdigest()
    except (OSError, ValueError):
        logger.debug("Config hash computation skipped (non-fatal)", exc_info=True)

    # Discovery freshness gate (Wave 25 Lane C) — mode-aware
    try:
        from plugin_examples.website_catalog.drift_detector import is_discovery_stale

        discovery_mode = getattr(ctx.config, "discovery_mode", "dry_run") or "dry_run"
        evidence_path = ctx.repo_root / "workspace" / "verification" / "latest" / "all-family-lowcode-discovery.json"
        if evidence_path.exists():
            import json as _json

            _evidence = _json.loads(evidence_path.read_text(encoding="utf-8"))
            _meta = _evidence.get("discovery_metadata", {})
            if _meta and is_discovery_stale(_meta):
                if discovery_mode == "publication":
                    raise RuntimeError(
                        f"DISCOVERY_EVIDENCE_STALE — expires_at={_meta.get('expires_at')}. "
                        "Run discovery sweep to refresh before publication mode."
                    )
                else:
                    logger.warning(
                        "Discovery evidence is stale (expires_at=%s). " "Mode=%s — continuing with warning.",
                        _meta.get("expires_at"),
                        discovery_mode,
                    )
                    artifacts["discovery_freshness"] = "STALE_WARNING"
            else:
                artifacts["discovery_freshness"] = "FRESH"
    except RuntimeError:
        raise
    except (OSError, json.JSONDecodeError, KeyError, ImportError):
        logger.debug("Freshness check skipped (non-fatal)", exc_info=True)

    return artifacts


def _stage_nuget_fetch(ctx: PipelineContext) -> dict:
    from plugin_examples.nuget_fetcher import fetch_package

    cfg = ctx.config.nuget
    ctx.download_manifest = fetch_package(
        cfg.package_id,
        cfg.version_policy,
        pinned_version=cfg.pinned_version,
        allow_prerelease=cfg.allow_prerelease,
        run_dir=ctx.run_dir,
        family=ctx.family,
    )
    return {
        "version": ctx.download_manifest["version"],
        "sha256": ctx.download_manifest["sha256"],
        "cached_path": ctx.download_manifest["cached_path"],
    }


def _stage_version_drift_preflight(ctx: PipelineContext) -> dict:
    """Warn early when the fetched package version differs from the denominator's source_version.

    This check runs immediately after nuget_fetch so catalog hash mismatches are
    anticipated *before* the expensive reflection/detection stages run.  A drift
    is not a hard stop — the operator may be intentionally testing a new package
    version prior to updating the denominator — but the warning is actionable and
    surfaced at the top of the run log rather than buried inside scenario_planning.

    Returns a dict with keys:
        fetched_version      — version resolved by NuGet
        denominator_version  — source_version from the denominator file (or None)
        drift_detected       — bool
        action_required      — human-readable next step when drift is detected
    """
    import json as _json

    fetched = ctx.download_manifest["version"] if ctx.download_manifest else None
    denom_path = ctx.repo_root / "pipeline" / "configs" / "denominators" / f"{ctx.family}.json"
    denominator_version: str | None = None
    if denom_path.exists():
        try:
            denom = _json.loads(denom_path.read_text(encoding="utf-8"))
            denominator_version = denom.get("source_version")
        except (OSError, json.JSONDecodeError, KeyError):
            logger.debug("Failed to read denominator version for %s", ctx.family, exc_info=True)

    drift = bool(fetched and denominator_version and fetched != denominator_version)
    action = (
        f"Update pipeline/configs/denominators/{ctx.family}.json — set "
        f"source_version to '{fetched}' and refresh api_catalog_sha256 after "
        f"running a fresh reflection pass."
        if drift
        else "none"
    )

    discovery_mode = getattr(ctx.config, "discovery_mode", None) or "dry_run"

    if drift:
        # Write mismatch evidence
        mismatch_evidence = {
            "family": ctx.family,
            "pinned": denominator_version,
            "live": fetched,
            "detected_at": _now_utc(),
        }
        try:
            import json as _json2

            _mismatch_path = ctx.run_dir / "version-mismatch-alert.json"
            _mismatch_path.write_text(_json2.dumps(mismatch_evidence, indent=2), encoding="utf-8")
        except OSError:
            logger.debug("Failed to write mismatch alert (non-fatal)", exc_info=True)

        if discovery_mode == "publication":
            accept_drift = os.environ.get("ACCEPT_VERSION_DRIFT") == "1"
            if not accept_drift:
                raise RuntimeError(
                    f"PINNED_VERSION_OUTDATED — family '{ctx.family}': "
                    f"pinned={denominator_version} but live={fetched}. "
                    "Set ACCEPT_VERSION_DRIFT=1 to proceed in publication mode."
                )
            else:
                # Write drift acceptance record for audit trail
                try:
                    import json as _json3

                    acceptance = {
                        "family": ctx.family,
                        "accepted_at": _now_utc(),
                        "accepted_pinned": denominator_version,
                        "accepted_live": fetched,
                        "env_gate": "ACCEPT_VERSION_DRIFT=1",
                    }
                    (ctx.run_dir / "drift-acceptance-record.json").write_text(
                        _json3.dumps(acceptance, indent=2), encoding="utf-8"
                    )
                except OSError:
                    logger.debug("Failed to write drift acceptance record (non-fatal)", exc_info=True)
                logger.warning(
                    "VERSION DRIFT ACCEPTED via ACCEPT_VERSION_DRIFT=1 for family '%s': " "pinned=%s, live=%s",
                    ctx.family,
                    denominator_version,
                    fetched,
                )
        else:
            logger.warning(
                "VERSION DRIFT DETECTED for family '%s': fetched=%s, denominator=%s. "
                "The catalog hash check will likely fail at scenario_planning. %s",
                ctx.family,
                fetched,
                denominator_version,
                action,
            )

    return {
        "fetched_version": fetched,
        "denominator_version": denominator_version,
        "drift_detected": drift,
        "action_required": action,
        "discovery_mode": discovery_mode,
    }


def _stage_dependency_resolution(ctx: PipelineContext) -> dict:
    from plugin_examples.nuget_fetcher import resolve_dependencies
    from plugin_examples.nuget_fetcher.dependency_resolver import (
        update_package_lock,
        write_dependency_manifest,
    )

    cfg = ctx.config.nuget
    assert ctx.download_manifest is not None, "download_manifest must be set before dependency resolution"
    nupkg_path = Path(ctx.download_manifest["cached_path"])

    if not cfg.dependency_resolution.enabled:
        ctx.deps = []
        return {"dependency_count": 0, "skipped": True}

    ctx.deps = resolve_dependencies(
        nupkg_path,
        target_frameworks=cfg.target_framework_preference,
        max_depth=cfg.dependency_resolution.max_depth,
        run_dir=ctx.run_dir,
        family=ctx.family,
        include_all_tfm_groups=cfg.dependency_resolution.include_all_tfm_groups,
    )
    write_dependency_manifest(ctx.deps, ctx.run_dir, ctx.family)
    update_package_lock(ctx.download_manifest, ctx.deps, ctx.evidence_dir)
    return {"dependency_count": len(ctx.deps)}


def _stage_extraction(ctx: PipelineContext) -> dict:
    from plugin_examples.nupkg_extractor import extract_package

    assert ctx.download_manifest is not None, "download_manifest must be set before extraction"
    nupkg_path = Path(ctx.download_manifest["cached_path"])
    dep_paths = [Path(d["cached_path"]) for d in (ctx.deps or []) if d.get("status") == "ok" and d.get("cached_path")]
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

    assert ctx.extraction is not None, "extraction must be set before reflection"
    dep_dll_paths = [Path(p) for p in ctx.extraction.get("dependency_dll_paths", []) if p]

    ctx.catalog = build_catalog(
        dll_path=Path(ctx.extraction["dll_path"]),
        output_path=output_path,
        xml_path=Path(ctx.extraction["xml_path"]) if ctx.extraction.get("xml_path") else None,
        dependency_paths=dep_dll_paths or None,
        namespace_filter=ctx.config.plugin_detection.namespace_patterns,
    )
    ctx.catalog_path = output_path
    assert ctx.catalog is not None, "catalog must be set after build_catalog"
    ns_count = len(ctx.catalog.get("namespaces", []))
    return {"catalog_path": str(output_path), "namespace_count": ns_count}


def _check_namespace_drift(ctx: PipelineContext) -> None:
    """Detect new namespaces in DLL and check if expected_namespace has arrived."""
    expected_ns = getattr(ctx.config.plugin_detection, "expected_namespace", "")
    if not expected_ns and not ctx.catalog:
        return
    if ctx.catalog is None:
        return

    current_namespaces = {ns["namespace"] for ns in ctx.catalog.get("namespaces", [])}
    if not current_namespaces:
        return

    if expected_ns and expected_ns in current_namespaces:
        logger.warning(
            "EXPECTED_NAMESPACE_ARRIVED: '%s' detected in %s DLL — "
            "classification_override may be removable",
            expected_ns,
            ctx.family,
        )

    # Compare against last-known namespaces from proof file
    proof_path = getattr(ctx, "proof_path", None)
    if not proof_path:
        return
    import json

    proof_file = Path(proof_path)
    if not proof_file.exists():
        return
    try:
        with open(proof_file) as f:
            proof = json.load(f)
        previous_ns = set(proof.get("catalog_namespaces", []))
        if previous_ns:
            new_ns = current_namespaces - previous_ns
            if new_ns:
                logger.info(
                    "NAMESPACE_DRIFT_DETECTED in %s: new namespaces %s",
                    ctx.family,
                    sorted(new_ns),
                )
    except (json.JSONDecodeError, OSError):
        pass


def _stage_plugin_detection(ctx: PipelineContext) -> dict:
    from plugin_examples.plugin_detector import (
        assert_source_of_truth_eligible,
        detect_plugin_namespaces,
        write_product_inventory,
        write_source_of_truth_proof,
    )
    from plugin_examples.plugin_detector.proof_reporter import (
        assert_nonlowcode_source_of_truth_eligible,
        write_nonlowcode_source_of_truth_proof,
    )

    assert ctx.catalog is not None, "catalog must be set before plugin detection"
    assert ctx.download_manifest is not None, "download_manifest must be set before plugin detection"
    assert ctx.extraction is not None, "extraction must be set before plugin detection"

    ctx.detection = detect_plugin_namespaces(
        ctx.catalog,
        ctx.config.plugin_detection.namespace_patterns,
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

    # Namespace drift detection: check if expected namespace has arrived
    _check_namespace_drift(ctx)

    # Gate: assert source-of-truth eligible
    has_fallback = getattr(ctx.config.plugin_detection, "fallback_strategy", None)
    if has_fallback and not ctx.detection.is_eligible:
        # Non-LowCode: write and assert non-LowCode SOT proof from registry
        registry_entries = _load_registry_entries(ctx)
        ctx.nonlowcode_proof_path = write_nonlowcode_source_of_truth_proof(
            family=ctx.family,
            registry_entries=registry_entries,
            verification_dir=ctx.evidence_dir,
        )
        assert_nonlowcode_source_of_truth_eligible(str(ctx.nonlowcode_proof_path))
        logger.info("Non-LowCode SOT gate passed for '%s'", ctx.family)
    else:
        assert_source_of_truth_eligible(str(ctx.proof_path))

    matched_ns = [m.namespace for m in ctx.detection.matched_namespaces]
    return {
        "eligible": ctx.detection.is_eligible,
        "matched_namespaces": matched_ns,
        "plugin_type_count": ctx.detection.public_plugin_type_count,
        "plugin_method_count": ctx.detection.public_plugin_method_count,
    }


_FALLBACK_USABLE_STATUSES = frozenset(
    {
        "PROBE_CANDIDATE",
        "PROBE_CONFIRMED",
        "VERIFIED_PUBLISHABLE",
    }
)

_FALLBACK_EXCLUDED_STATUSES = frozenset(
    {
        "PROBE_FAILED",
        "STATIC_MAPPING_REQUIRED",
        "BLOCKED_PACKAGE_UNAVAILABLE",
        "BLOCKED_REFLECTION_FAILED",
        "BLOCKED_LICENSE_RESTRICTED",
        "REJECTED_BY_VALIDATOR",
        "WEBSITE_DISCOVERED",
        "REFLECTION_CANDIDATE",
        "AI_DRAFT",
    }
)


def _load_registry_entries(ctx: PipelineContext) -> list[dict]:
    """Load all entries from the capability registry YAML for this family.

    Shared helper used by SOT proof, scenario planning, and fallback lookup.
    Returns empty list if no registry file exists or on load error.
    """
    import yaml

    registry_path = ctx.repo_root / "pipeline" / "plugin-capability-registry" / f"{ctx.family}.yaml"
    if not registry_path.exists():
        logger.debug("No capability registry file for '%s'", ctx.family)
        return []

    try:
        with open(registry_path, encoding="utf-8") as fh:
            registry_data = yaml.safe_load(fh)
    except Exception:  # noqa: BLE001
        logger.warning("Failed to load capability registry for '%s'", ctx.family, exc_info=True)
        return []

    if not isinstance(registry_data, dict):
        return []

    entries = registry_data.get("entries", [])
    return [e for e in entries if isinstance(e, dict)]


def _stage_fallback_registry_lookup(ctx: PipelineContext) -> dict:
    """Soft stage: load usable entries from the plugin-capability-registry.

    Usable statuses: PROBE_CANDIDATE, PROBE_CONFIRMED, VERIFIED_PUBLISHABLE.
    Excluded statuses: PROBE_FAILED, STATIC_MAPPING_REQUIRED, BLOCKED_*, REJECTED_BY_VALIDATOR.

    Skips when:
    - fallback_strategy is None (LowCode pipeline only)
    - A LowCode namespace was detected (ctx.detection.is_eligible)
    - No registry YAML file exists for this family

    Never hard-stops. Never writes to format-authority.

    .. note:: Data flow clarification
        This stage populates ``ctx.fallback_candidates`` for evidence/audit
        purposes. The live generation path in ``_stage_generation`` uses
        ``ctx.planning.ready_scenarios`` (from ``_stage_scenario_planning``)
        and does NOT read ``ctx.fallback_candidates``. The candidates JSON
        written here serves as an evidence artifact only.
    Writes fallback_candidates.json to ctx.run_dir as a dry-run artifact.
    """
    import json

    strategy = getattr(ctx.config.plugin_detection, "fallback_strategy", None)
    if strategy is None:
        return {"status": "SKIPPED", "reason": "fallback_strategy is None"}

    if ctx.detection is not None and ctx.detection.is_eligible:
        return {"status": "SKIPPED", "reason": "LowCode namespace found; fallback not needed"}

    registry_path = ctx.repo_root / "pipeline" / "plugin-capability-registry" / f"{ctx.family}.yaml"
    if not registry_path.exists():
        return {"status": "SKIPPED", "reason": f"no registry file for {ctx.family}"}

    try:
        import yaml

        with open(registry_path, encoding="utf-8") as fh:
            registry_data = yaml.safe_load(fh)
    except Exception as exc:  # noqa: BLE001
        return {"status": "SKIPPED", "reason": f"registry load error: {exc}"}

    if not isinstance(registry_data, dict):
        return {"status": "SKIPPED", "reason": "registry file is not a mapping"}

    entries = registry_data.get("entries", [])
    if not isinstance(entries, list):
        entries = []

    usable = [e for e in entries if isinstance(e, dict) and e.get("status") in _FALLBACK_USABLE_STATUSES]
    excluded = [e for e in entries if isinstance(e, dict) and e.get("status") not in _FALLBACK_USABLE_STATUSES]
    candidate_count = len(usable)

    # Only PROBE_CONFIRMED and VERIFIED_PUBLISHABLE feed generation.
    # PROBE_CANDIDATE requires probe validation first and must not enter the generation stage.
    _GENERATION_READY_STATUSES = frozenset({"PROBE_CONFIRMED", "VERIFIED_PUBLISHABLE"})
    generation_ready = [e for e in usable if e.get("status") in _GENERATION_READY_STATUSES]

    status_counts: dict[str, int] = {}
    for e in entries:
        if isinstance(e, dict):
            s = e.get("status", "UNKNOWN")
            status_counts[s] = status_counts.get(s, 0) + 1

    artifact_path = ctx.run_dir / "fallback_candidates.json"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with open(artifact_path, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "family": ctx.family,
                "strategy": strategy,
                "total_registry_entries": len(entries),
                "usable_entries": candidate_count,
                "generation_ready_entries": len(generation_ready),
                "excluded_entries": len(excluded),
                "status_counts": status_counts,
                "exclusion_reason": "statuses not in PROBE_CANDIDATE/PROBE_CONFIRMED/VERIFIED_PUBLISHABLE",
                "generation_exclusion_reason": "PROBE_CANDIDATE excluded from generation (requires probe validation first)",
                "candidates": usable,
            },
            fh,
            indent=2,
        )

    # Populate ctx.fallback_candidates with PluginCandidate objects for the generation stage.
    if generation_ready:
        from plugin_examples.fixture_factory.shared_downstream_executor import PluginCandidate

        ctx.fallback_candidates = [
            PluginCandidate(
                slug=e.get("plugin_slug") or e.get("slug", "unknown"),
                family=ctx.family,
                namespace_source="NON_LOWCODE_PLUGIN",
                discovery_method="capability_registry_fallback",
                metadata={k: v for k, v in e.items() if k not in ("plugin_slug", "slug")},
            )
            for e in generation_ready
        ]
        logger.info(
            "Non-LowCode fallback: %d generation-ready candidates for %s (PROBE_CONFIRMED/VERIFIED_PUBLISHABLE)",
            len(ctx.fallback_candidates),
            ctx.family,
        )
    else:
        ctx.fallback_candidates = []
        if usable:
            logger.info(
                "Non-LowCode fallback: %d usable entries for %s, but none are generation-ready "
                "(all are PROBE_CANDIDATE — probe validation required first)",
                len(usable),
                ctx.family,
            )

    return {
        "status": "OK",
        "candidate_count": candidate_count,
        "generation_ready": len(generation_ready),
        "fallback_mode": True,
    }


def _stage_api_delta(ctx: PipelineContext) -> dict:
    from plugin_examples.api_delta import compute_delta
    from plugin_examples.api_delta.delta_engine import write_delta_report

    assert ctx.catalog is not None, "catalog must be set before API delta computation"
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
    # Non-LowCode: plan scenarios from capability registry entries
    has_fallback = getattr(ctx.config.plugin_detection, "fallback_strategy", None)
    if has_fallback and not ctx.detection.is_eligible:
        from plugin_examples.scenario_planner import (
            plan_scenarios_from_registry,
            write_blocked_scenarios,
            write_scenario_catalog,
        )

        registry_entries = _load_registry_entries(ctx)
        nonlowcode_proof_path = getattr(ctx, "nonlowcode_proof_path", None)
        ctx.planning = plan_scenarios_from_registry(
            family=ctx.family,
            registry_entries=registry_entries,
            source_of_truth_proof_path=str(nonlowcode_proof_path) if nonlowcode_proof_path else None,
            min_examples=getattr(getattr(ctx.config, "generation", None), "min_examples_per_family", 3),
        )
        write_scenario_catalog(ctx.planning, ctx.evidence_dir)
        if ctx.planning.blocked_scenarios:
            write_blocked_scenarios(ctx.planning, ctx.evidence_dir)

        return {
            "status": "REGISTRY_PLANNED",
            "ready_count": ctx.planning.ready_count,
            "blocked_count": ctx.planning.blocked_count,
            "planning_source": "capability_registry",
            "total_types_classified": ctx.planning.ready_count + ctx.planning.blocked_count,
            "standalone_types": ctx.planning.ready_count,
            "completeness_gate_status": "registry_planned",
        }

    from plugin_examples.scenario_planner import (
        plan_scenarios,
        write_blocked_scenarios,
        write_scenario_catalog,
    )
    from plugin_examples.scenario_planner.consumer_mapper import (
        build_consumer_map,
        write_consumer_relationships,
    )
    from plugin_examples.scenario_planner.entrypoint_scorer import (
        score_entrypoint,
        write_entrypoint_scores,
    )
    from plugin_examples.scenario_planner.type_classifier import (
        classify_catalog,
        write_type_role_classification,
    )

    assert ctx.catalog is not None, "catalog must be set before scenario planning"

    matched_ns = [m.namespace for m in ctx.detection.matched_namespaces]
    fixture_dict = _fixture_registry_to_dict(getattr(ctx, "_fixture_registry", None))

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
            scores.append(score_entrypoint(type_info, r, consumer_map, fixture_available=fixture_avail))
    write_entrypoint_scores(scores, ctx.evidence_dir)

    # Catalog hash validation (B-013) — strict enforcement (F-1 closure)
    from plugin_examples.scenario_planner.planner import (
        CatalogHashMismatchError,
        validate_catalog_hash,
    )

    catalog_hash_result = validate_catalog_hash(
        ctx.family,
        ctx.catalog,
        ctx.repo_root,
    )
    _write_catalog_hash_evidence(catalog_hash_result, ctx.evidence_dir)
    # Evidence is written first; now enforce strict blocking on mismatch
    if catalog_hash_result.match is False:
        _current = catalog_hash_result.current_hash or ""
        _denom = catalog_hash_result.denominator_hash or ""
        raise CatalogHashMismatchError(
            f"Catalog hash MISMATCH for {ctx.family}: "
            f"current={_current[:16]}... "
            f"denominator={_denom[:16]}... "
            f"The API catalog has changed since the denominator was created. "
            f"Update the denominator file to proceed."
        )

    ctx.planning = plan_scenarios(
        family=ctx.family,
        catalog=ctx.catalog,
        plugin_namespaces=matched_ns,
        fixture_registry=fixture_dict,
        min_examples=ctx.config.generation.min_examples_per_family,
        source_of_truth_proof_path=str(ctx.proof_path),
        default_fixture_extension=fixture_ext,
        allowed_types=ctx.config.generation.allowed_types or None,
        preferred_methods_per_type=ctx.config.generation.preferred_methods_per_type or None,
        repo_root=ctx.repo_root,
    )
    write_scenario_catalog(ctx.planning, ctx.evidence_dir)
    write_blocked_scenarios(ctx.planning, ctx.evidence_dir)

    # Write fixture strategy plan evidence
    _write_fixture_strategy_plan(ctx.planning, ctx.evidence_dir)

    # Write scenario input format map evidence
    _write_scenario_input_format_map(ctx.planning, ctx.evidence_dir)

    # Write fixture resolution evidence (Lane B-4)
    from plugin_examples.scenario_planner.planner import build_fixture_resolution_evidence

    _family_config = None
    if ctx.config and hasattr(ctx.config, "_raw_yaml"):
        _family_config = ctx.config._raw_yaml
    _fixture_resolution = build_fixture_resolution_evidence(ctx.planning, _family_config)
    import json as _json_fr

    _fr_path = ctx.evidence_dir / "scenario-fixture-resolution.json"
    _fr_path.write_text(_json_fr.dumps(_fixture_resolution, indent=2), encoding="utf-8")
    logger.info("Fixture resolution evidence written: %s", _fr_path)

    # Completeness gate — verify denominator equation after planning
    import json as _json

    from plugin_examples.gates.completeness_gate import (
        check_completeness,
        write_completeness_gate_result,
    )

    _denom_path = ctx.repo_root / "pipeline" / "configs" / "denominators" / f"{ctx.family}.json"
    _denominator: dict = {}
    if _denom_path.exists():
        try:
            _denominator = _json.loads(_denom_path.read_text(encoding="utf-8"))
        except Exception as _e:
            logger.warning("Could not load denominator for completeness gate: %s", _e)

    # Unknown types: in matched namespaces but not in any planning result
    _accounted_types = {s.target_type for s in ctx.planning.ready_scenarios} | {
        s.target_type for s in ctx.planning.blocked_scenarios
    }
    _unknown_count = sum(
        1 for r in roles if any(r.full_name.startswith(ns) for ns in matched_ns) and r.full_name not in _accounted_types
    )

    _completeness_result = check_completeness(
        ctx.family,
        _denominator,
        ctx.planning,
        dry_run=ctx.dry_run,
        unknown_type_count=_unknown_count,
    )
    write_completeness_gate_result(_completeness_result, ctx.evidence_dir)

    standalone_roles = sum(1 for r in roles if r.role in {"workflow_root", "operation_facade"})
    return {
        "ready_count": ctx.planning.ready_count,
        "blocked_count": ctx.planning.blocked_count,
        "total_types_classified": len(roles),
        "standalone_types": standalone_roles,
        "completeness_gate_status": _completeness_result.status,
    }


def _stage_llm_preflight(ctx: PipelineContext) -> dict:
    from plugin_examples.llm_router import LLMRouter
    from plugin_examples.llm_router.router import write_preflight_report

    ctx.llm_router = LLMRouter(
        provider_order=ctx.config.llm.provider_order,
        metrics_collector=ctx.metrics_collector,
    )
    preflight = ctx.llm_router.run_preflight()
    ctx.llm_available = ctx.llm_router.selected_provider is not None
    write_preflight_report(preflight, ctx.llm_router.selected_provider, ctx.evidence_dir)

    if not ctx.llm_available and ctx.require_llm:
        raise RuntimeError("No LLM provider available and --require-llm is set")

    return {
        "selected_provider": ctx.llm_router.selected_provider,
        "llm_available": ctx.llm_available,
    }


def _generate_nonlowcode_examples(ctx: PipelineContext) -> dict:
    """LEGACY: Non-LowCode generation path via SharedDownstreamExecutor.

    .. deprecated::
        This function is no longer called by the main pipeline. Non-LowCode
        generation now goes through _stage_generation with registry-based
        scenario planning (plan_scenarios_from_registry) and template code
        generation (generate_code_from_registry). Retained for backward
        compatibility with existing integration tests and artifact-contract
        validation use cases.
    """
    import json as _json

    from plugin_examples.fixture_factory.shared_downstream_executor import SharedDownstreamExecutor

    candidates = ctx.fallback_candidates or []
    if not candidates:
        return {"examples_generated": 0, "reason": "no generation-ready fallback candidates"}

    executor = SharedDownstreamExecutor(strict=False)
    batch_result = executor.execute_batch(candidates)

    # Convert DownstreamResult records to the project-dict format used by subsequent stages
    for r in batch_result.results:
        ctx.generated_projects.append(
            {
                "slug": r.slug,
                "family": r.family,
                "namespace_source": r.namespace_source,
                "discovery_method": r.discovery_method,
                "artifact_contract": r.artifact_contract,
                "pr_packet": r.pr_packet,
                "publication_state": r.publication_state,
                "evidence": r.evidence,
                "errors": r.errors,
            }
        )

    summary = {
        "candidates": batch_result.candidates,
        "passed": batch_result.passed,
        "failed": batch_result.failed,
    }
    summary_path = ctx.run_dir / "nonlowcode-generation-summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(_json.dumps(summary, indent=2), encoding="utf-8")

    logger.info(
        "Non-LowCode generation: %d candidates, %d passed, %d failed",
        batch_result.candidates,
        batch_result.passed,
        batch_result.failed,
    )
    return {
        "examples_generated": batch_result.candidates,
        "generation_mode": "nonlowcode_executor",
        "parity": "NON_LOWCODE_PLUGIN",
        "passed": batch_result.passed,
        "failed": batch_result.failed,
    }


def _stage_generation(ctx: PipelineContext) -> dict:
    from plugin_examples.gates.example_lifecycle import ExampleLifecycleRegistry
    from plugin_examples.generator import (
        build_packet,
        generate_example,
        generate_project,
        write_example_index,
    )

    # Initialize lifecycle registry before early return so blocked scenarios are
    # always tracked even when ready_count == 0.
    if ctx.lifecycle_registry is None:
        ctx.lifecycle_registry = ExampleLifecycleRegistry(
            family=ctx.family,
            run_id=ctx.run_id,
        )

    # Register blocked/excluded scenarios in lifecycle so they are never silently
    # dropped from evidence.  Each gets a lifecycle record with EXCLUDED_BY_SCOPE.
    if ctx.planning:
        for blocked in ctx.planning.blocked_scenarios:
            rec = ctx.lifecycle_registry.create_record(blocked.scenario_id)
            reason = getattr(blocked, "blocked_reason", None) or getattr(blocked, "status", "blocked")
            rec.mark_excluded(reason)
            rec.final_verdict = "EXCLUDED_BY_SCOPE"

    # If no scenarios are ready (including from registry planning), nothing to generate
    if not ctx.planning or ctx.planning.ready_count == 0:
        return {"examples_generated": 0, "reason": "no ready scenarios"}

    # Load healing intelligence registries (advisory layer — does not override config)
    healing_evidence: dict[str, Any] = {"loaded": False, "registries": {}, "constraints_applied": []}
    if ctx.healing_intelligence is None:
        try:
            from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

            hi = HealingIntelligenceLoader(
                ctx.repo_root / "workspace" / "verification" / "latest" / "healing-intelligence"
            )
            hi.load()
            ctx.healing_intelligence = hi
            healing_evidence["loaded"] = True
            healing_evidence["registries"] = hi.registries_present()
            logger.info("Healing intelligence loaded: %s", hi.summary())
        except Exception as e:
            logger.warning("Healing intelligence load failed (non-blocking): %s", e)

    # LLM wrapper to bridge signature mismatch
    llm_fn = None
    if ctx.llm_available and not ctx.template_mode:
        llm_fn = lambda p, s: ctx.llm_router.generate(p, system_prompt=s)

    # Determine generation mode
    _is_nonlowcode = bool(
        getattr(ctx.config.plugin_detection, "fallback_strategy", None)
        and ctx.detection
        and not ctx.detection.is_eligible
    )
    gen_mode = "llm" if llm_fn else "template"
    if _is_nonlowcode:
        gen_mode = "registry_llm" if llm_fn else "registry_template"
    output_dir = ctx.run_dir / "generated" / ctx.family

    # Pre-load registry entries for non-LowCode code generation
    _registry_entries_by_slug: dict[str, dict] = {}
    if _is_nonlowcode:
        from plugin_examples.generator.registry_code_generator import generate_code_from_registry

        for entry in _load_registry_entries(ctx):
            slug = entry.get("plugin_slug") or entry.get("slug", "")
            if slug:
                _registry_entries_by_slug[slug] = entry

    for scenario in ctx.planning.ready_scenarios:
        scenario_dict = scenario_to_dict(scenario)
        # Create lifecycle record for every planned scenario
        lifecycle_rec = ctx.lifecycle_registry.create_record(scenario.scenario_id)
        lifecycle_rec.update_stage("generation_attempted")
        try:
            # Non-LowCode: use registry code generator
            if _is_nonlowcode:
                # Find matching registry entry for this scenario
                _slug = scenario.scenario_id.replace(f"{ctx.family}-", "", 1)
                _reg_entry = _registry_entries_by_slug.get(_slug, {})
                _pkg_id = ctx.config.nuget.package_id

                if llm_fn and not ctx.template_mode:
                    # LLM with registry metadata as prompt context
                    hints = {"family": ctx.family}
                    _ptc = getattr(ctx.config, "per_type_constraints", {}) if ctx.config else {}
                    packet = build_packet(
                        scenario_dict,
                        ctx.catalog or {},
                        template_hints=hints,
                        per_type_constraints=_ptc,
                    )
                    example = generate_example(packet, llm_generate=llm_fn)
                else:
                    # Template mode: generate from registry selected_api_mapping
                    example = generate_code_from_registry(scenario, _reg_entry, _pkg_id)
            else:
                # LowCode path: existing behavior
                hints = {}
                if ctx.config and hasattr(ctx.config, "template_hints"):
                    from dataclasses import asdict as _asdict

                    hints = _asdict(ctx.config.template_hints)
                # Inject family into hints for FormatContract lookup in codegen
                hints["family"] = ctx.family
                _ptc = getattr(ctx.config, "per_type_constraints", {}) if ctx.config else {}

                # Merge healing intelligence advisory constraints (additive only)
                if ctx.healing_intelligence and ctx.healing_intelligence.is_loaded():
                    type_short = scenario_dict.get("target_type", "").split(".")[-1]
                    hi_constraints = ctx.healing_intelligence.get_steering_constraints(
                        ctx.family,
                        type_short,
                    )
                    hi_required = hi_constraints.get("required", []) + hi_constraints.get("global_required", [])
                    hi_forbidden = hi_constraints.get("forbidden", []) + hi_constraints.get("global_forbidden", [])
                    if hi_required or hi_forbidden:
                        existing = dict(_ptc.get(type_short, {}))
                        existing.setdefault("REQUIRED", []).extend(
                            r for r in hi_required if r not in existing.get("REQUIRED", [])
                        )
                        existing.setdefault("FORBIDDEN", []).extend(
                            f for f in hi_forbidden if f not in existing.get("FORBIDDEN", [])
                        )
                        _ptc = dict(_ptc)
                        _ptc[type_short] = existing
                        healing_evidence["constraints_applied"].append(
                            {
                                "scenario_id": scenario.scenario_id,
                                "type": type_short,
                                "hi_required": hi_required,
                                "hi_forbidden": hi_forbidden,
                            }
                        )

                assert ctx.catalog is not None, "catalog must be set before generation"
                packet = build_packet(
                    scenario_dict,
                    ctx.catalog,
                    template_hints=hints,
                    per_type_constraints=_ptc,
                )
                example = generate_example(packet, llm_generate=llm_fn)
            if example.status == "failed" or not example.code.strip():
                reason = example.failure_reason or "empty code"
                logger.warning("Generation failed for %s: %s", scenario.scenario_id, reason)
                lifecycle_rec.mark_generation_failed(reason)
                continue
            lifecycle_rec.mark_generated()
            project = generate_project(
                example,
                package_id=ctx.config.nuget.package_id,
                package_version=(ctx.download_manifest or {}).get("version", "*"),
                target_framework="net8.0",
                output_dir=output_dir,
                input_strategy=getattr(scenario, "input_strategy", "none"),
                input_files=getattr(scenario, "input_files", []),
            )
            # Store constraints for build repair re-injection (all families).
            # The packet is not available in _stage_validation, so we persist here.
            # Non-LowCode template path does not create a packet — use empty defaults.
            if _is_nonlowcode and not llm_fn:
                project["pdf_constraints"] = []
                project["family_name"] = ctx.family
                project["type_short"] = (scenario.target_type or "").split(".")[-1].lower()
                project["type_constraints"] = {}
            else:
                project["pdf_constraints"] = [c for c in packet.constraints if "REQUIRED:" in c or "FORBIDDEN:" in c]
                project["family_name"] = ctx.family
                _type_name_ptc = packet.target_type.split(".")[-1] if packet.target_type else ""
                project["type_short"] = _type_name_ptc.lower()
                project["type_constraints"] = _ptc.get(_type_name_ptc, {}) if _ptc else {}
            ctx.generated_projects.append(project)
        except Exception as e:
            logger.warning("Generation failed for %s: %s", scenario.scenario_id, e)
            lifecycle_rec.mark_generation_failed(str(e))

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
                all_fixtures.append(
                    GeneratedFixture(
                        path=fp,
                        format=p.suffix,
                        created_by="fixture_factory",
                        validity_check=f"file_exists_and_size_{p.stat().st_size}",
                        size_bytes=p.stat().st_size,
                        ready=True,
                    )
                )
    if all_fixtures:
        write_generated_fixtures_evidence(all_fixtures, ctx.evidence_dir)

    # Write few-shot patterns evidence
    _write_fewshot_patterns(ctx.generated_projects, ctx.evidence_dir)

    # Write healing intelligence evidence
    if healing_evidence.get("loaded"):
        import json as _json

        hi_path = ctx.evidence_dir / "latest" / "healing-intelligence-usage.json"
        hi_path.parent.mkdir(parents=True, exist_ok=True)
        hi_path.write_text(_json.dumps(healing_evidence, indent=2), encoding="utf-8")
        logger.info(
            "Healing intelligence evidence written: %d constraints applied",
            len(healing_evidence.get("constraints_applied", [])),
        )

    # Write generation decision audit (per-scenario strategy tracking)
    try:
        from plugin_examples.generator.decision_audit import write_generation_decision_audit

        write_generation_decision_audit(ctx)
    except Exception:
        logger.debug("Generation decision audit skipped (non-critical)", exc_info=True)

    # TC-P5-02: Map generation mode to explicit quality tier label
    _tier_map = {
        "registry_template": "TEMPLATE_REGISTRY",
        "registry_llm": "LLM_REGISTRY",
        "llm": "LLM_CATALOG",
        "template": "TEMPLATE_CATALOG",
    }

    return {
        "examples_generated": len(ctx.generated_projects),
        "generation_mode": gen_mode,
        "generation_quality_tier": _tier_map.get(gen_mode, gen_mode.upper()),
        "fixtures_generated": len(all_fixtures),
        "healing_intelligence_loaded": healing_evidence.get("loaded", False),
    }


def _stage_validation(ctx: PipelineContext) -> dict:
    from plugin_examples.generator.code_generator import _extract_code, _validate_code, _validate_code_from_constraints
    from plugin_examples.verifier_bridge import run_dotnet_validation
    from plugin_examples.verifier_bridge.dotnet_runner import ValidationResult, write_validation_results

    if not ctx.generated_projects:
        return {"validated": 0, "reason": "no generated projects"}

    # TC-P5-01: Dotnet SDK preflight — detect once, label degradation explicitly
    from plugin_examples.health.doctor import check_dotnet_sdk
    _sdk_check = check_dotnet_sdk()
    _sdk_available = _sdk_check.status == "PASS"
    if not _sdk_available:
        logger.warning(
            "Dotnet SDK not available (%s) — validation will degrade to "
            "artifact-contract-only for projects without --skip-run",
            _sdk_check.detail,
        )

    max_build_repairs = 2 if (ctx.llm_available and not ctx.template_mode) else 0
    max_runtime_repairs = 1 if (ctx.llm_available and not ctx.template_mode) else 0
    repairs_done = 0
    runtime_repairs_done = 0
    repair_log: list[dict] = []

    # Repairable runtime failure classifications
    repairable_classifications = {
        "interactive_console_call",
        "wrong_input_format",
        "invalid_api_usage",
        "blocked_invalid_operation",
        "blocked_null_argument",
        "missing_options_input",
        "null_options_passed",
        "blocked_runtime_context_required",
    }

    from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure

    # Healing intelligence: pre-load failure/repair patterns for this family
    hi_failure_hints: dict[str, list[dict]] = {}  # scenario_id -> known failures
    hi_repair_hints: dict[str, str] = {}  # scenario_id -> repair guidance
    if ctx.healing_intelligence and ctx.healing_intelligence.is_loaded():
        for proj in ctx.generated_projects:
            if "scenario_id" not in proj:
                continue
            type_short = proj.get("type_short", "")
            failures = ctx.healing_intelligence.get_failures_for_type(ctx.family, type_short)
            if failures:
                hi_failure_hints[proj["scenario_id"]] = failures
                # Find repair pattern for first known failure
                for fp in failures:
                    rp = ctx.healing_intelligence.get_repair_for_failure(fp.get("id", ""))
                    if rp and rp.get("strategy"):
                        hi_repair_hints[proj["scenario_id"]] = rp["strategy"]
                        break

    nonlowcode_limited = 0
    sdk_degraded = 0
    for proj in ctx.generated_projects:
        # Safety net: projects without project_dir get LIMITED_VALIDATION
        # (artifact contract only). With Phase 3 routing, non-LowCode projects
        # SHOULD have project_dir and flow through normal dotnet validation.
        if "project_dir" not in proj:
            _proj_id = proj.get("slug", proj.get("scenario_id", "unknown"))
            logger.warning(
                "Project '%s' has no project_dir — LIMITED_VALIDATION "
                "(artifact contract only)",
                _proj_id,
            )
            ctx.validation_results.append(ValidationResult(
                scenario_id=_proj_id,
                passed=False,
                failure_stage="no_project_dir",
            ))
            nonlowcode_limited += 1
            continue

        # TC-P5-01: If dotnet SDK not available, skip dotnet validation with
        # explicit VALIDATION_DEGRADED_NO_SDK label (never a silent skip).
        if not _sdk_available and not ctx.skip_run:
            _proj_id = proj.get("scenario_id", "unknown")
            logger.warning(
                "Project '%s' — VALIDATION_DEGRADED_NO_SDK "
                "(dotnet SDK not found, skipping restore/build/run)",
                _proj_id,
            )
            ctx.validation_results.append(ValidationResult(
                scenario_id=_proj_id,
                passed=False,
                failure_stage="no_sdk",
            ))
            sdk_degraded += 1
            continue

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
            # Re-inject PDF-specific packet constraints so LLM cannot fall back to
            # semantically wrong but compilable code (e.g. File.Copy).
            pdf_constraints = proj.get("pdf_constraints", [])
            pdf_constraint_reminder = ""
            if pdf_constraints:
                pdf_constraint_reminder = "\n\nREQUIRED CONSTRAINTS (must be satisfied in fixed code):\n" + "\n".join(
                    f"- {c}" for c in pdf_constraints
                )
            # Healing intelligence: inject known repair strategy if available
            hi_hint = ""
            scenario_repair = hi_repair_hints.get(proj["scenario_id"], "")
            if scenario_repair:
                hi_hint = f"\n\nKNOWN REPAIR STRATEGY: {scenario_repair}"
            # RISK-07/08: sanitize compiler output before prompt construction
            from plugin_examples.llm_router.sanitizer import sanitize_llm_input, scrub_secrets

            _clean_build_stdout = sanitize_llm_input(build_stdout)
            _clean_build_stderr = sanitize_llm_input(build_stderr)
            repair_prompt = (
                f"The following C# code fails to compile. Fix it.\n\n"
                f"Compiler stdout:\n{_clean_build_stdout}\n\n"
                f"Compiler stderr:\n{_clean_build_stderr}\n\n"
                f"Code:\n```csharp\n{current_code}\n```\n\n"
                f"RULES: Do NOT use Console.ReadKey() or Console.ReadLine(). "
                f"Do NOT use try/catch to hide errors. "
                f"Return ONLY the fixed C# code in a ```csharp code block."
                f"{pdf_constraint_reminder}"
                f"{hi_hint}"
            )
            repair_prompt = scrub_secrets(repair_prompt)
            _prompt_hash = hashlib.sha256(repair_prompt.encode("utf-8")).hexdigest()
            try:
                response = ctx.llm_router.generate(
                    repair_prompt,
                    system_prompt=(
                        "You are an expert C# developer. Fix the compilation errors. "
                        "FORBIDDEN: Console.ReadKey(), Console.ReadLine(), TODO, NotImplementedException. "
                        "Return ONLY the corrected code in a single ```csharp code block."
                    ),
                )
                fixed_code = _extract_code(response)
                _code_hash = hashlib.sha256(fixed_code.encode("utf-8")).hexdigest() if fixed_code else ""
                # RISK-01: Repair diff cap — reject repairs that rewrite >60% of code
                if fixed_code and current_code:
                    from difflib import SequenceMatcher

                    _similarity = SequenceMatcher(None, current_code, fixed_code).ratio()
                    if _similarity < 0.4:  # >60% changed
                        logger.warning(
                            "Build repair attempt %d for %s rejected: diff too large (similarity=%.2f, threshold=0.40)",
                            attempt,
                            proj["scenario_id"],
                            _similarity,
                        )
                        repair_log.append(
                            {
                                "scenario_id": proj["scenario_id"],
                                "repair_type": "build",
                                "attempt": attempt,
                                "success": False,
                                "rejection_reason": "repair_diff_cap_exceeded",
                                "similarity": round(_similarity, 3),
                                "output_hash": _code_hash,
                                "prompt_hash": _prompt_hash,
                            }
                        )
                        break
                if fixed_code and fixed_code != current_code:
                    # Semantic validation before writing — PDF-specific check + per-type constraints
                    proj_family = proj.get("family_name", "pdf" if pdf_constraints else "")
                    proj_type_short = proj.get("type_short", "")
                    semantic_issues = _validate_code(fixed_code, family=proj_family, type_short=proj_type_short)
                    proj_type_constraints = proj.get("type_constraints", {})
                    if proj_type_constraints:
                        semantic_issues.extend(_validate_code_from_constraints(fixed_code, proj_type_constraints))
                    if semantic_issues:
                        logger.warning(
                            "Build repair attempt %d for %s produced semantically invalid code: %s",
                            attempt,
                            proj["scenario_id"],
                            semantic_issues,
                        )
                        repair_log.append(
                            {
                                "scenario_id": proj["scenario_id"],
                                "repair_type": "build",
                                "attempt": attempt,
                                "success": False,
                                "semantic_issues": semantic_issues,
                                "output_hash": _code_hash,
                                "prompt_hash": _prompt_hash,
                            }
                        )
                        # Do NOT write the invalid code — continue to next attempt or stop
                        break
                    program_path.write_text(fixed_code, encoding="utf-8")
                    vr = run_dotnet_validation(
                        Path(proj["project_dir"]),
                        proj["scenario_id"],
                        skip_run=ctx.skip_run,
                    )
                    repairs_done += 1
                    repair_log.append(
                        {
                            "scenario_id": proj["scenario_id"],
                            "repair_type": "build",
                            "attempt": attempt,
                            "success": vr.passed or (vr.build and vr.build.success),
                            "output_hash": _code_hash,
                            "prompt_hash": _prompt_hash,
                        }
                    )
                    logger.info(
                        "Build repair attempt %d for %s: %s",
                        attempt,
                        proj["scenario_id"],
                        "passed" if vr.passed else "still failing",
                    )
                else:
                    break
            except Exception as e:
                logger.warning("Build repair failed for %s: %s", proj["scenario_id"], e)
                break

        # Runtime-repair cycle: fix repairable runtime failures
        rt_attempt = 0
        while not vr.passed and vr.failure_stage == "run" and rt_attempt < max_runtime_repairs and vr.run:
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
            # Re-inject PDF-specific packet constraints so LLM cannot regress to
            # semantically wrong but runnable code (e.g. replacing LowCode API with core API).
            rt_pdf_constraints = proj.get("pdf_constraints", [])
            rt_pdf_constraint_reminder = ""
            if rt_pdf_constraints:
                rt_pdf_constraint_reminder = (
                    "\n\nREQUIRED CONSTRAINTS (must be satisfied in fixed code):\n"
                    + "\n".join(f"- {c}" for c in rt_pdf_constraints)
                )
                logger.info(
                    "Runtime repair attempt %d for %s: re-injecting %d pdf_constraints",
                    rt_attempt,
                    proj["scenario_id"],
                    len(rt_pdf_constraints),
                )
            rt_type_constraints = proj.get("type_constraints", {})
            rt_type_constraint_reminder = ""
            if rt_type_constraints:
                required_lines = [c for c in rt_type_constraints.get("REQUIRED", [])]
                forbidden_lines = [c for c in rt_type_constraints.get("FORBIDDEN", [])]
                if required_lines or forbidden_lines:
                    parts = []
                    if required_lines:
                        parts.append("REQUIRED:\n" + "\n".join(f"  - {c}" for c in required_lines))
                    if forbidden_lines:
                        parts.append("FORBIDDEN:\n" + "\n".join(f"  - {c}" for c in forbidden_lines))
                    rt_type_constraint_reminder = "\n\nPER-TYPE CONSTRAINTS (must be respected):\n" + "\n".join(parts)
                    logger.info(
                        "Runtime repair attempt %d for %s: re-injecting type_constraints "
                        "(%d required, %d forbidden)",
                        rt_attempt,
                        proj["scenario_id"],
                        len(required_lines),
                        len(forbidden_lines),
                    )
            # RISK-07/08: sanitize runtime output before prompt construction
            _clean_run_stdout = sanitize_llm_input(run_stdout)
            _clean_run_stderr = sanitize_llm_input(run_stderr)
            repair_prompt = (
                f"The following C# code compiles but fails at runtime.\n\n"
                f"Runtime classification: {rc.classification}\n"
                f"Runtime stdout:\n{_clean_run_stdout}\n\n"
                f"Runtime stderr:\n{_clean_run_stderr}\n\n"
                f"Code:\n```csharp\n{current_code}\n```\n\n"
                f"RULES: Do NOT use Console.ReadKey() or Console.ReadLine(). "
                f"Do NOT use try/catch to hide errors. "
                f"Validate input file exists before API call. "
                f"Return ONLY the fixed C# code in a ```csharp code block."
                f"{rt_pdf_constraint_reminder}"
                f"{rt_type_constraint_reminder}"
                f"{hi_repair_hints.get(proj['scenario_id'], '') and ('\n\nKNOWN REPAIR STRATEGY: ' + hi_repair_hints[proj['scenario_id']]) or ''}"
            )
            repair_prompt = scrub_secrets(repair_prompt)
            _prompt_hash = hashlib.sha256(repair_prompt.encode("utf-8")).hexdigest()
            try:
                response = ctx.llm_router.generate(
                    repair_prompt,
                    system_prompt=(
                        "You are an expert C# developer. Fix the runtime error. "
                        "FORBIDDEN: Console.ReadKey(), Console.ReadLine(). "
                        "Return ONLY the corrected code in a single ```csharp code block."
                    ),
                )
                fixed_code = _extract_code(response)
                _code_hash = hashlib.sha256(fixed_code.encode("utf-8")).hexdigest() if fixed_code else ""
                # RISK-01: Repair diff cap — reject repairs that rewrite >60% of code
                if fixed_code and current_code:
                    from difflib import SequenceMatcher

                    _similarity = SequenceMatcher(None, current_code, fixed_code).ratio()
                    if _similarity < 0.4:  # >60% changed
                        logger.warning(
                            "Runtime repair attempt %d for %s rejected: diff too large (similarity=%.2f, threshold=0.40)",
                            rt_attempt,
                            proj["scenario_id"],
                            _similarity,
                        )
                        repair_log.append(
                            {
                                "scenario_id": proj["scenario_id"],
                                "repair_type": "runtime",
                                "classification": rc.classification,
                                "attempt": rt_attempt,
                                "success": False,
                                "rejection_reason": "repair_diff_cap_exceeded",
                                "similarity": round(_similarity, 3),
                                "output_hash": _code_hash,
                                "prompt_hash": _prompt_hash,
                            }
                        )
                        break
                if fixed_code and fixed_code != current_code:
                    # Semantic validation before writing — PDF-specific check + per-type constraints
                    rt_proj_family = proj.get("family_name", "pdf" if rt_pdf_constraints else "")
                    rt_proj_type_short = proj.get("type_short", "")
                    rt_semantic_issues = _validate_code(
                        fixed_code, family=rt_proj_family, type_short=rt_proj_type_short
                    )
                    if rt_type_constraints:
                        rt_semantic_issues.extend(_validate_code_from_constraints(fixed_code, rt_type_constraints))
                    if rt_semantic_issues:
                        logger.warning(
                            "Runtime repair attempt %d for %s produced semantically invalid code: %s",
                            rt_attempt,
                            proj["scenario_id"],
                            rt_semantic_issues,
                        )
                        repair_log.append(
                            {
                                "scenario_id": proj["scenario_id"],
                                "repair_type": "runtime",
                                "classification": rc.classification,
                                "attempt": rt_attempt,
                                "success": False,
                                "semantic_issues": rt_semantic_issues,
                                "output_hash": _code_hash,
                                "prompt_hash": _prompt_hash,
                            }
                        )
                        # Do NOT write the invalid code — continue to next attempt or stop
                        break
                    program_path.write_text(fixed_code, encoding="utf-8")
                    vr = run_dotnet_validation(
                        Path(proj["project_dir"]),
                        proj["scenario_id"],
                        skip_run=ctx.skip_run,
                    )
                    runtime_repairs_done += 1
                    repair_log.append(
                        {
                            "scenario_id": proj["scenario_id"],
                            "repair_type": "runtime",
                            "classification": rc.classification,
                            "attempt": rt_attempt,
                            "success": vr.passed,
                            "output_hash": _code_hash,
                            "prompt_hash": _prompt_hash,
                        }
                    )
                    logger.info(
                        "Runtime repair attempt %d for %s (%s): %s",
                        rt_attempt,
                        proj["scenario_id"],
                        rc.classification,
                        "passed" if vr.passed else "still failing",
                    )
                else:
                    break
            except Exception as e:
                logger.warning("Runtime repair failed for %s: %s", proj["scenario_id"], e)
                break

        ctx.validation_results.append(vr)

        # Update lifecycle record with validation outcome
        if ctx.lifecycle_registry:
            rec = ctx.lifecycle_registry.get_record(proj["scenario_id"])
            if rec:
                if vr.build and vr.build.success:
                    if repairs_done > 0:
                        rec.mark_build_repaired(repairs_done)
                    else:
                        rec.mark_build_passed()
                elif vr.failure_stage == "build":
                    rec.mark_build_failed(
                        (vr.build.stderr or vr.build.stdout or "unknown")[:200] if vr.build else "unknown"
                    )
                if vr.run and vr.run.success:
                    if runtime_repairs_done > 0:
                        rec.mark_run_repaired(runtime_repairs_done)
                    else:
                        rec.mark_run_passed()
                elif vr.failure_stage == "run":
                    run_err = (vr.run.stderr or vr.run.stdout or "unknown")[:200] if vr.run else "unknown"
                    rec.mark_run_failed(run_err)

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

        repair_path.write_text(
            _json.dumps(
                {
                    "total_build_repairs": repairs_done,
                    "total_runtime_repairs": runtime_repairs_done,
                    "attempts": repair_log,
                },
                indent=2,
            )
        )

    # Backlog failed examples with root cause and recommended fix
    if ctx.lifecycle_registry:
        for rec in ctx.lifecycle_registry.records:
            if rec.generation_status == "failed":
                rec.mark_backlogged(
                    root_cause=rec.generation_failure_reason or "generation_failed",
                    recommended_fix="Review LLM constraints and few-shot patterns for this scenario",
                    priority="high",
                )
            elif rec.build_status == "failed":
                rec.mark_backlogged(
                    root_cause=rec.build_failure_reason or "build_failed",
                    recommended_fix="Feed compiler errors to LLM with stronger constraints",
                    priority="high",
                )
            elif rec.run_status == "failed":
                rec.mark_backlogged(
                    root_cause=rec.run_failure_reason or "run_failed",
                    recommended_fix="Classify runtime failure and add to repairable set or fix constraints",
                    priority="medium",
                )
            elif rec.build_status in ("passed", "repaired") and rec.run_status in ("passed", "repaired"):
                rec.mark_pr_candidate()

    passed = sum(1 for v in ctx.validation_results if v.passed)
    failed = len(ctx.validation_results) - passed

    if failed > 0 and ctx.require_validation:
        raise RuntimeError(
            f"Validation failed for {failed}/{len(ctx.validation_results)} examples " "and --require-validation is set"
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
        "nonlowcode_limited": nonlowcode_limited,
        "sdk_available": _sdk_available,
        "sdk_degraded": sdk_degraded,
    }


_REVIEWER_MAX_REPAIR_ATTEMPTS = 2

# Retryable reviewer errors — transient or code-fixable failures.
# Non-retryable: infrastructure errors, timeout, unavailable.
_REVIEWER_RETRYABLE_KEYWORDS = (
    "compilation error",
    "build error",
    "CS0",
    "CS1",
    "missing using",
    "syntax error",
    "type mismatch",
    "namespace",
    "undeclared",
    "does not contain",
)


def _is_reviewer_failure_retryable(result) -> bool:
    """Classify whether a reviewer failure is retryable (code-fixable)."""
    if not result.available:
        return False
    err = (result.error or "").lower()
    if "timeout" in err or "timed out" in err:
        return False
    for kw in _REVIEWER_RETRYABLE_KEYWORDS:
        if kw.lower() in err:
            return True
    # Check details for structured feedback
    if result.details and isinstance(result.details, dict):
        errors = result.details.get("errors", [])
        for e in errors:
            msg = str(e).lower()
            for kw in _REVIEWER_RETRYABLE_KEYWORDS:
                if kw.lower() in msg:
                    return True
    return False


def _stage_reviewer(ctx: PipelineContext) -> dict:
    from plugin_examples.verifier_bridge.bridge import (
        ReviewerResult,
        ReviewerUnavailableError,
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

    # Gate-triggered reviewer repair loop: retry retryable failures up to max attempts
    repair_attempts = 0
    repair_log: list[dict] = []
    while (
        not result.passed
        and result.available
        and repair_attempts < _REVIEWER_MAX_REPAIR_ATTEMPTS
        and _is_reviewer_failure_retryable(result)
    ):
        repair_attempts += 1
        logger.info(
            "Reviewer repair attempt %d/%d for %s (error: %s)",
            repair_attempts,
            _REVIEWER_MAX_REPAIR_ATTEMPTS,
            ctx.family,
            result.error,
        )
        repair_log.append(
            {
                "attempt": repair_attempts,
                "prior_error": result.error,
                "retryable": True,
            }
        )
        try:
            result = run_example_reviewer(
                family=ctx.family,
                workspace_dir=ctx.run_dir,
            )
        except ReviewerUnavailableError:
            result = ReviewerResult(available=False, error="Lost during repair")
            break

    write_reviewer_results(result, ctx.evidence_dir)

    # Update lifecycle records with reviewer outcome
    if ctx.lifecycle_registry:
        for rec in ctx.lifecycle_registry.pr_candidates:
            if not result.available:
                rec.mark_reviewer_unavailable()
            elif result.passed and repair_attempts > 0:
                rec.mark_reviewer_repaired(repair_attempts)
            elif result.passed:
                rec.mark_reviewer_passed()
            else:
                rec.mark_reviewer_failed(result.error or "reviewer_failed")
                rec.mark_backlogged(
                    root_cause="reviewer_failed",
                    recommended_fix="Address reviewer feedback and regenerate",
                    priority="high",
                )

    # G-1: Auto-learn from run failures (additive CANDIDATE only — never promotes CONFIRMED).
    try:
        from plugin_examples.healing_intelligence.loader import auto_learn_from_run

        registry_dir = ctx.repo_root / "workspace" / "verification" / "latest" / "healing-intelligence"
        registry_path = registry_dir / "failure-pattern-registry.json"
        learn_result = auto_learn_from_run(ctx.run_dir, ctx.family, registry_path)
        logger.info(
            "Healing auto-learn: +%d new, %d incremented, %d skipped for %s",
            learn_result["added"],
            learn_result["incremented"],
            learn_result["skipped"],
            ctx.family,
        )
    except Exception as _e:  # noqa: BLE001
        logger.warning("Healing auto-learn failed (non-blocking): %s", _e)

    return {
        "available": result.available,
        "passed": result.passed,
        "preflight_ready": preflight.overall_ready,
        "repair_attempts": repair_attempts,
        "repair_log": repair_log,
    }


def _stage_publisher(ctx: PipelineContext) -> dict:
    from plugin_examples.gates.evaluator import evaluate_gates
    from plugin_examples.publisher import publish_examples
    from plugin_examples.publisher.publisher import write_publishing_report

    # Pre-evaluate gates from stages completed before the publisher runs.
    # The post-loop gate evaluation (which writes gate-results.json) runs after
    # the stage loop ends, so ctx.gate_verdict is None here. We compute it now
    # from ctx._completed_stages (stages 1-16) so the publisher can use the
    # verdict directly without depending on gate-results.json existing on disk.
    if ctx.gate_verdict is None:
        ctx.gate_verdict = evaluate_gates(ctx._completed_stages, ctx)

    examples = ctx.generated_projects or []
    result = publish_examples(
        family=ctx.family,
        run_id=ctx.run_id,
        examples=examples,
        verification_dir=ctx.evidence_dir,
        dry_run=ctx.dry_run,
        gate_verdict=ctx.gate_verdict,
        family_config=ctx.config,
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
    skipped = sum(1 for s in stages if s.status in ("skipped", "skipped_replayed"))

    hard_stopped = any(s.status == "failed" for s in stages[:7])

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
        "delta_status": ("initial_run" if stages[7].artifacts.get("initial_run", True) else "diff")
        if len(stages) > 7
        else "unknown",
        "fixture_count": stages[9].artifacts.get("fixture_count", 0) if len(stages) > 9 else 0,
        "mined_example_count": stages[10].artifacts.get("mined_total", 0) if len(stages) > 10 else 0,
        "ready_scenario_count": plan_stage.artifacts.get("ready_count", 0) if plan_stage else 0,
        "blocked_scenario_count": plan_stage.artifacts.get("blocked_count", 0) if plan_stage else 0,
        "llm_preflight_result": llm_stage.artifacts.get("selected_provider", "no_provider") if llm_stage else "skipped",
        "generation_mode": gen_stage.artifacts.get("generation_mode", "skipped") if gen_stage else "skipped",
        "examples_generated_count": gen_stage.artifacts.get("examples_generated", 0) if gen_stage else 0,
        "dotnet_restore_passed": sum(1 for v in ctx.validation_results if v.restore and v.restore.success)
        if ctx.validation_results
        else 0,
        "dotnet_build_passed": sum(1 for v in ctx.validation_results if v.build and v.build.success)
        if ctx.validation_results
        else 0,
        "dotnet_run_passed": sum(1 for v in ctx.validation_results if v.run and v.run.success)
        if ctx.validation_results
        else 0,
        "reviewer_available": rev_stage.artifacts.get("available", False) if rev_stage else False,
        "reviewer_result": "passed" if (rev_stage and rev_stage.artifacts.get("passed")) else "unavailable",
        "publisher_status": pub_stage.artifacts.get("status", "skipped") if pub_stage else "skipped",
        "skipped_stages": [s.name for s in stages if s.status in ("skipped", "skipped_replayed")],
        "replayed_stages": [s.name for s in stages if s.status == "skipped_replayed"],
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
    ("version_drift_preflight", 2, _stage_version_drift_preflight),
    ("dependency_resolution", 3, _stage_dependency_resolution),
    ("extraction", 4, _stage_extraction),
    ("reflection", 5, _stage_reflection),
    ("plugin_detection", 6, _stage_plugin_detection),
    ("source_of_truth_gate", 7, None),  # combined into plugin_detection
    ("fallback_registry_lookup", 7, _stage_fallback_registry_lookup),  # soft stage; skips for LowCode families
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
HARD_STOP_STAGES = {
    "load_config",
    "nuget_fetch",
    "dependency_resolution",
    "extraction",
    "reflection",
    "plugin_detection",
    "scenario_planning",
}


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
    compare_run: str | None = None,
    replay_from: str | None = None,
    reuse_run_id: str | None = None,
    metrics_collector: Any = None,
    metrics_config: Any = None,
    metrics_post: bool = False,
    metrics_job_type: str | None = None,
    metrics_strict: bool = False,
    metrics_force_repost: bool = False,
    family_config_path: str | None = None,
) -> dict:
    """Run the full pipeline and return a structured report dict."""
    # Verify stage I/O contracts are consistent at startup (advisory — logs warnings only)
    from plugin_examples.contracts.stage_contracts import check_contract_consistency
    _contract_errors = check_contract_consistency()
    if _contract_errors:
        for _err in _contract_errors:
            logger.warning("stage_contract_violation", extra={"error": _err})

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
        metrics_collector=metrics_collector,
    )
    ctx._allow_experimental = allow_experimental
    ctx._family_config_path = family_config_path

    # Bind structured-log context so every downstream logger emits run_id + family
    _bind_obs_context(run_id=run_id, family=family)
    logger.info("pipeline_start run_id=%s family=%s dry_run=%s", run_id, family, dry_run)

    # ---------------------------------------------------------------------------
    # Replay setup (fail-closed; runs before any stage)
    # ---------------------------------------------------------------------------
    _replay_skip: frozenset = frozenset()
    _reuse_run_id: str | None = None

    if replay_from:
        from plugin_examples.replay import (  # noqa: PLC0415
            ReplayIntegrityError,
            check_replay_integrity,
            copy_reviewer_evidence,
            find_prior_run,
            restore_catalog,
            restore_generated_projects,
            restore_validation_results,
            stages_to_skip,
            write_replay_manifest,
        )

        _reuse_run_id = reuse_run_id or find_prior_run(family, repo_root)
        if not _reuse_run_id:
            raise RuntimeError(
                f"--replay-from {replay_from!r} requires a prior pilot run; "
                f"none found for family '{family}' in workspace/runs/. "
                "Run the pipeline at least once normally before replaying."
            )
        _prior_run_dir = repo_root / "workspace" / "runs" / _reuse_run_id
        if not _prior_run_dir.is_dir():
            raise RuntimeError(f"--reuse-run '{_reuse_run_id}' does not exist at {_prior_run_dir}")

        logger.info("replay: starting %r replay from run '%s'", replay_from, _reuse_run_id)

        # Integrity checks (writes stale-artifact-check.json; raises on hard fail)
        _integrity = check_replay_integrity(
            family=family,
            replay_from=replay_from,
            prior_run_dir=_prior_run_dir,
            repo_root=repo_root,
        )

        # Restore catalog (used by plugin_detection → scenario_planning which re-run)
        ctx.catalog, ctx.catalog_path = restore_catalog(_prior_run_dir, family)

        # Restore download_manifest from prior run's nuget_fetch artifacts
        # (plugin_detection reads version/sha256 even when nuget_fetch is skipped)
        _prior_report = _prior_run_dir / "pilot-report.json"
        if _prior_report.exists():
            import json as _json

            _prior_data = _json.loads(_prior_report.read_text(encoding="utf-8"))
            _nf_stage = next(
                (s for s in _prior_data.get("stages", []) if s.get("name") == "nuget_fetch"),
                None,
            )
            if _nf_stage and _nf_stage.get("artifacts"):
                ctx.download_manifest = dict(_nf_stage["artifacts"])

        # Point ctx.extraction at prior extracted dir (plugin_detection uses dll_path)
        _prior_extracted = _prior_run_dir / "extracted" / family
        ctx.extraction = {
            "dll_path": str(_prior_extracted / "primary"),
            "xml_path": str(_prior_extracted / "primary"),
            "selected_framework": "",
        }

        # Restore generated_projects for validation / reviewer / publisher modes
        if replay_from in {"validation", "reviewer", "publisher"}:
            ctx.generated_projects = restore_generated_projects(_prior_run_dir, family, repo_root)

        # Restore validation_results (typed) for reviewer / publisher modes
        if replay_from in {"reviewer", "publisher"}:
            ctx.validation_results = restore_validation_results(_prior_run_dir)

        # Copy prior reviewer evidence into current run for publisher mode
        if replay_from == "publisher":
            copy_reviewer_evidence(_prior_run_dir, evidence_dir, family)

        _replay_skip = stages_to_skip(replay_from)
        logger.info(
            "replay: skipping stages %s; scenario_planning will re-run for denominator safety",
            sorted(_replay_skip),
        )

    # Before snapshot
    before = _snapshot_workspace(manifests_dir, verification_dir)

    start_time = datetime.now(UTC).isoformat()
    pipeline_start = time.time()

    # Tier-to-stage mapping
    tier_max_stage = {0: 0, 1: 6, 2: 12, 3: 14, 4: 16, 5: 17}
    max_stage_order = tier_max_stage.get(max_tier, 17)

    # Execute stages
    stages: list[StageResult] = []
    hard_stopped = False

    # Effective stage list (stage 7 = source_of_truth_gate is combined into stage 6)
    effective_stages = [(name, order, fn) for name, order, fn in STAGE_DEFINITIONS if fn is not None]

    for name, order, fn in effective_stages:
        if hard_stopped:
            r = StageResult(name=name, order=order, status="skipped")
            stages.append(r)
            ctx._completed_stages = list(stages)
            continue

        if order > max_stage_order:
            r = StageResult(name=name, order=order, status="skipped", error=f"Skipped: max tier {max_tier}")
            stages.append(r)
            ctx._completed_stages = list(stages)
            continue

        # Replay: skip stages whose artifacts are reused from a prior run
        if _replay_skip and name in _replay_skip:
            r = StageResult(
                name=name,
                order=order,
                status="skipped_replayed",
                artifacts={"reuse_run_id": _reuse_run_id, "replay_from": replay_from},
            )
            stages.append(r)
            ctx._completed_stages = list(stages)
            continue

        result = _run_stage(name, order, fn, ctx)

        # Determine if failure is hard stop or degraded.
        # Only degrade stages with explicit optional semantics.
        # All other failures stay "failed" for honest reporting.
        if result.status == "failed":
            if name in HARD_STOP_STAGES:
                hard_stopped = True
            elif name == "llm_preflight" and not ctx.require_llm or name == "validation" and not ctx.require_validation or name == "reviewer" and not ctx.require_reviewer:
                result.status = "degraded"
            # All other failures stay "failed" — no blanket degradation

        stages.append(result)
        ctx._completed_stages = list(stages)

    pipeline_end = time.time()
    end_time = datetime.now(UTC).isoformat()
    total_ms = (pipeline_end - pipeline_start) * 1000

    # Write replay manifest (only when replay mode was active)
    if replay_from and _reuse_run_id:
        try:
            from plugin_examples.replay import write_replay_manifest  # noqa: PLC0415

            write_replay_manifest(
                evidence_dir=evidence_dir,
                replay_from=replay_from,
                reuse_run_id=_reuse_run_id,
                new_run_id=run_id,
                family=family,
                skipped_stages=_replay_skip,
                integrity_result=_integrity,
            )
        except Exception as _rme:
            logger.warning("replay: failed to write replay manifest: %s", _rme)

    # Per-example gate evaluation and partitioning
    from plugin_examples.gates.example_gates import (
        build_pr_candidate_manifest,
        build_scenario_feedback,
        compute_aggregate_gates,
        compute_partitioned_verdict,
        evaluate_example_gates,
        write_aggregate_gate_results,
        write_example_gate_results,
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
        contract_blocking_mode=True,
    )
    write_example_gate_results(example_gates, evidence_dir)

    aggregate = compute_aggregate_gates(example_gates)
    write_aggregate_gate_results(aggregate, evidence_dir)

    pr_manifest = build_pr_candidate_manifest(example_gates, dry_run=dry_run)
    scenario_fb = build_scenario_feedback(example_gates)
    write_scenario_feedback(scenario_fb, evidence_dir)

    global_manifest_path = verification_dir / "latest" / "pr-candidate-manifest.json"
    write_pr_candidate_manifest(
        pr_manifest,
        evidence_dir,
        prior_manifest_path=global_manifest_path,
        scenario_feedback=scenario_fb,
    )

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

    # Write lifecycle evidence and update per-family backlog
    if ctx.lifecycle_registry:
        from plugin_examples.gates.example_lifecycle import (
            update_backlog_from_lifecycle,
            write_lifecycle_evidence,
        )

        write_lifecycle_evidence(ctx.lifecycle_registry, evidence_dir)
        backlog_dir = verification_dir / "latest"
        update_backlog_from_lifecycle(ctx.lifecycle_registry, backlog_dir)

    # Run-to-run comparison (only when --compare-run is provided)
    comparison_result = None
    if compare_run and ctx.lifecycle_registry:
        from plugin_examples.gates.example_lifecycle import (
            compare_with_prior_run,
            write_comparison_evidence,
        )

        comparison_result = compare_with_prior_run(
            ctx.lifecycle_registry,
            compare_run,
            repo_root,
        )
        write_comparison_evidence(comparison_result, evidence_dir)
        # Re-write lifecycle evidence with comparison fields populated
        write_lifecycle_evidence(ctx.lifecycle_registry, evidence_dir)
        if comparison_result.regression_detected:
            logger.warning(
                "RUN-TO-RUN REGRESSION DETECTED: %d scenario(s) regressed vs %s",
                comparison_result.regressed_count,
                compare_run,
            )
        else:
            logger.info(
                "Run-to-run comparison vs %s: %s",
                compare_run,
                comparison_result.verdict,
            )

    # After snapshot
    after = _snapshot_workspace(manifests_dir, verification_dir)

    # Add run-scoped evidence listing
    after["run_evidence_files"] = (
        sorted(f.name for f in (evidence_dir / "latest").iterdir() if f.is_file())
        if (evidence_dir / "latest").exists()
        else []
    )

    report = _build_report(
        ctx,
        stages,
        before,
        after,
        start_time,
        end_time,
        total_ms,
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

        from plugin_examples.evidence_layout import promote_family_evidence

        src_latest = evidence_dir / "latest"
        # Promote to families/{family}/ (primary) and verification/latest/ (compat alias)
        promote_family_evidence(src_latest, verification_dir, family, run_id)

        # Promote manifests (package-lock, fixture-registry, etc.)
        dst_manifests = manifests_dir
        dst_manifests.mkdir(parents=True, exist_ok=True)
        manifest_files = [
            "package-lock.json",
            "fixture-registry.json",
            "existing-examples-index.json",
            "scenario-catalog.json",
            "example-index.json",
        ]
        for mf in manifest_files:
            src_mf = evidence_dir / mf
            if src_mf.exists():
                shutil.copy2(src_mf, dst_manifests / mf)
        logger.info("Manifests promoted to %s", dst_manifests)

    # Metrics finalization (only when metrics_collector is set)
    if metrics_collector and metrics_config:
        try:
            from plugin_examples.metrics.config import is_agent_metrics_production_enabled
            from plugin_examples.metrics.pipeline_hook import finalize_metrics

            metrics_result = finalize_metrics(
                ctx=ctx,
                config=metrics_config,
                report=report,
                command=command or "run",
                dry_run=not metrics_post,
                post=metrics_post,
                job_type_override=metrics_job_type,
                force_repost=metrics_force_repost,
                strict=metrics_strict,
                test_only_sprint=not is_agent_metrics_production_enabled(),
            )
            report["_metrics_result"] = metrics_result
        except Exception as exc:
            logger.error("Metrics finalization failed: %s", exc)
            if metrics_strict:
                raise

    return report
