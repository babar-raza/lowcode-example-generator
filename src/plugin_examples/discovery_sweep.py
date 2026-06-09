"""Discovery-only sweep for all families — no LLM, no generation, no publish.

Resolves NuGet packages, extracts DLLs, builds reflection catalogs, and
detects LowCode/Plugin namespaces. Writes a family inventory without
generating any examples.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Families with this status are always included in the discovery sweep without
# requiring --allow-experimental. They are excluded from the generation pipeline.
DISCOVERY_ONLY_STATUS = "discovery_only"


def run_discovery_sweep(
    *,
    families: list[str] | None = None,
    all_families: bool = False,
    promote_latest: bool = False,
    allow_experimental: bool = False,
    repo_root: Path | None = None,
) -> dict:
    """Run a discovery-only sweep across families.

    This does NOT generate examples, call LLM, or publish anything.
    It only resolves packages, reflects APIs, and detects namespaces.

    Args:
        families: Specific family names to discover.
        all_families: If True, discover all enabled families (including discovery_only).
        promote_latest: If True, copy results to verification/latest/.
        allow_experimental: If True, include experimental families.
        repo_root: Repository root path.

    Returns:
        Dict with discovery results per family.
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]

    configs_dir = repo_root / "pipeline" / "configs" / "families"
    verification_dir = repo_root / "workspace" / "verification"

    # Collect family names to discover
    family_names: list[str] = []
    if families:
        family_names = list(families)
    elif all_families:
        # Scan enabled family configs (includes discovery_only families)
        for yml in sorted(configs_dir.glob("*.yml")):
            family_names.append(yml.stem)

    results: list[dict] = []

    for family in family_names:
        result = _discover_family(family, repo_root, allow_experimental, verification_dir)
        results.append(result)

    # Build summary
    eligible_count = sum(1 for r in results if r["status"] == "eligible_lowcode_found")

    # Discovery metadata — freshness tracking (Wave 25 Lane C)
    from plugin_examples.website_catalog.drift_detector import make_discovery_metadata
    discovery_metadata = make_discovery_metadata()

    summary = {
        "total_families": len(results),
        "eligible_count": eligible_count,
        "families": results,
        "discovery_metadata": discovery_metadata,
    }

    # Write evidence
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    evidence_path = latest / "all-family-lowcode-discovery.json"
    evidence_path.write_text(json.dumps(summary, indent=2))
    logger.info(
        "Discovery sweep evidence written: %s (run_id=%s, expires_at=%s)",
        evidence_path,
        discovery_metadata["run_id"],
        discovery_metadata["expires_at"],
    )

    return summary


def _discover_family(
    family: str,
    repo_root: Path,
    allow_experimental: bool,
    verification_dir: Path | None = None,
) -> dict:
    """Discover LowCode namespaces for a single family."""
    if verification_dir is None:
        verification_dir = repo_root / "workspace" / "verification"

    result: dict = {
        "family": family,
        "status": "unknown",
        "package_id": None,
        "resolved_version": None,
        "dependency_count": 0,
        "dependency_paths": [],
        "selected_target_framework": None,
        "namespace_count": 0,
        "lowcode_namespaces": [],
        "plugin_type_count": 0,
        "plugin_method_count": 0,
        "catalog_path": None,
        "eligibility_status": None,
        "error": None,
    }

    try:
        from plugin_examples.family_config import load_family_config

        config_path = repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
        if not config_path.exists():
            disabled = repo_root / "pipeline" / "configs" / "families" / "disabled" / f"{family}.yml"
            if disabled.exists():
                result["status"] = "disabled"
                return result
            result["status"] = "blocked_config_not_found"
            return result

        config = load_family_config(config_path)

        if not config.enabled:
            result["status"] = "disabled"
            return result

        # discovery_only families are always included in the discovery sweep.
        # experimental families require --allow-experimental.
        if config.status == "experimental" and not allow_experimental:
            result["status"] = "experimental_skipped"
            return result
        # discovery_only: proceed (no guard needed — discovery is exactly what this status allows)

        result["package_id"] = config.nuget.package_id

        # Resolve NuGet package
        from plugin_examples.nuget_fetcher import fetch_package, resolve_dependencies
        from datetime import datetime

        run_dir = repo_root / "workspace" / "runs" / f"discovery-{family}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        run_dir.mkdir(parents=True, exist_ok=True)

        manifest = fetch_package(
            config.nuget.package_id,
            config.nuget.version_policy,
            pinned_version=config.nuget.pinned_version,
            allow_prerelease=config.nuget.allow_prerelease,
            run_dir=run_dir,
            family=family,
        )
        result["resolved_version"] = manifest["version"]

        # Resolve package dependencies (mirrors runner.py stage 3).
        # Without dependency DLLs, DllReflector fails for assemblies with
        # external dependencies (e.g. System.Drawing.Common for Aspose.Cells).
        nupkg_path = Path(manifest["cached_path"])
        dep_cfg = config.nuget.dependency_resolution
        deps: list[dict] = []
        if dep_cfg.enabled:
            deps = resolve_dependencies(
                nupkg_path,
                target_frameworks=config.nuget.target_framework_preference,
                max_depth=dep_cfg.max_depth,
                run_dir=run_dir,
                family=family,
                include_all_tfm_groups=True,
            )
            logger.info(
                "Discovery resolved %d dependencies for %s", len(deps), family
            )
        result["dependency_count"] = len(deps)

        dep_nupkg_paths = [
            Path(d["cached_path"])
            for d in deps
            if d.get("status") == "ok" and d.get("cached_path")
        ]

        # Download any extra_packages declared in the family config for reflection.
        # These are packages whose assemblies the primary DLL references but which
        # are not declared in any nuspec TFM group (e.g. Aspose.Drawing.Common for
        # Aspose.OCR).  We download the latest stable version of each.
        if dep_cfg.extra_packages:
            from plugin_examples.nuget_fetcher.fetcher import (
                resolve_latest_stable,
                _download_nupkg,
            )
            from plugin_examples.nuget_fetcher.cache import check_cache
            extra_deps_dir = run_dir / "packages" / family / "deps"
            extra_deps_dir.mkdir(parents=True, exist_ok=True)
            for extra_pkg_id in dep_cfg.extra_packages:
                try:
                    extra_version = resolve_latest_stable(extra_pkg_id)
                    extra_path = extra_deps_dir / f"{extra_pkg_id}.{extra_version}.nupkg"
                    if not check_cache(extra_path):
                        _download_nupkg(extra_pkg_id, extra_version, extra_path)
                    dep_nupkg_paths.append(extra_path)
                    logger.info(
                        "Extra package for reflection: %s %s",
                        extra_pkg_id, extra_version,
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed to download extra_package %s for %s: %s",
                        extra_pkg_id, family, exc,
                    )
                    result["error"] = (
                        f"extra_package download failed: {extra_pkg_id}: {exc}"
                    )

        # Extract DLLs (pass dependency nupkgs so dep DLLs are co-extracted)
        from plugin_examples.nupkg_extractor import extract_package
        extraction = extract_package(
            nupkg_path,
            package_id=config.nuget.package_id,
            family=family,
            target_framework_preference=config.nuget.target_framework_preference,
            run_dir=run_dir,
            dependency_nupkgs=dep_nupkg_paths or None,
        )

        result["selected_target_framework"] = extraction.get("selected_framework")

        # Collect extracted dependency DLL paths for the reflector
        dep_dll_paths = [
            Path(p) for p in extraction.get("dependency_dll_paths", []) if p
        ]

        # Deduplicate by assembly simple name — prevents FileLoadException in
        # MetadataLoadContext when two NuGet packages provide the same DLL name.
        from plugin_examples.dependencies.assembly_identity import deduplicate_assemblies
        _dedup = deduplicate_assemblies(dep_dll_paths)
        if _dedup.excluded:
            logger.info(
                "Assembly deduplication: %d kept, %d excluded for %s",
                len(_dedup.kept), len(_dedup.excluded), family,
            )
        dep_dll_paths = _dedup.kept
        result["dependency_paths"] = [str(p) for p in dep_dll_paths]
        result["dedup_excluded_count"] = len(_dedup.excluded)

        # Write dedup report to verification/latest/{family}-dependency-dedup-report.json
        latest_dir = verification_dir / "latest"
        latest_dir.mkdir(parents=True, exist_ok=True)
        dedup_report = {
            "family": family,
            "total_input_paths": len(_dedup.kept) + len(_dedup.excluded),
            "kept_count": len(_dedup.kept),
            "excluded_count": len(_dedup.excluded),
            "dedup_by": _dedup.dedup_by,
            "kept": [str(p) for p in _dedup.kept],
            "excluded": _dedup.excluded,
            "conflicts": _dedup.conflicts,
        }
        import json as _json
        (latest_dir / f"{family}-dependency-dedup-report.json").write_text(
            _json.dumps(dedup_report, indent=2)
        )

        # Build catalog (pass dependency_paths so DllReflector can load them)
        from plugin_examples.reflection_catalog import build_catalog
        catalog_dir = run_dir / "catalog" / family
        catalog_dir.mkdir(parents=True, exist_ok=True)
        catalog_path = catalog_dir / "api-catalog.json"
        catalog = build_catalog(
            dll_path=Path(extraction["dll_path"]),
            output_path=catalog_path,
            xml_path=Path(extraction["xml_path"]) if extraction.get("xml_path") else None,
            dependency_paths=dep_dll_paths or None,
            namespace_filter=config.plugin_detection.namespace_patterns,
        )
        result["catalog_path"] = str(catalog_path)

        # Detect namespaces
        from plugin_examples.plugin_detector import detect_plugin_namespaces, write_source_of_truth_proof
        detection = detect_plugin_namespaces(
            catalog, config.plugin_detection.namespace_patterns,
        )

        matched = [m.namespace for m in detection.matched_namespaces]
        result["namespace_count"] = len(matched)
        result["lowcode_namespaces"] = matched
        result["plugin_type_count"] = detection.public_plugin_type_count
        result["plugin_method_count"] = detection.public_plugin_method_count
        result["eligibility_status"] = "eligible" if detection.is_eligible else "not_eligible"

        # Write per-family source-of-truth proof (mirrors runner stage 6)
        proof_path = write_source_of_truth_proof(
            family=family,
            package_id=config.nuget.package_id,
            resolved_version=manifest["version"],
            nupkg_sha256=manifest.get("sha256"),
            selected_target_framework=extraction.get("selected_framework"),
            dll_path=extraction.get("dll_path"),
            xml_path=extraction.get("xml_path"),
            xml_warning=extraction.get("xml_warning"),
            dependency_count=len(deps),
            dependency_paths=[d.get("cached_path", "") for d in deps],
            api_catalog_path=str(catalog_path),
            detection_result=detection,
            verification_dir=verification_dir,
        )
        logger.info("Source-of-truth proof written: %s", proof_path)

        if matched:
            result["status"] = "eligible_lowcode_found"
        else:
            result["status"] = "not_eligible_no_namespace"

    except Exception as e:
        logger.warning("Discovery failed for %s: %s", family, e)
        result["status"] = "blocked_reflection_failed"
        result["eligibility_status"] = "blocked"
        result["error"] = str(e)

    return result


def compute_generation_readiness(
    discovery_results: list[dict],
    repo_root: Path,
) -> list[dict]:
    """Rank families by generation readiness using discovery evidence.

    For each family that produced a catalog, classify types and compute
    readiness metrics. Does not call LLM or generate examples.

    Args:
        discovery_results: List of family discovery result dicts.
        repo_root: Repository root.

    Returns:
        Sorted list of readiness dicts, most-ready first.
    """
    readiness_list: list[dict] = []

    for r in discovery_results:
        family = r["family"]
        status = r["status"]

        # Base entry — always included so blockers are visible
        entry: dict = {
            "family": family,
            "eligibility_status": r.get("eligibility_status"),
            "lowcode_namespace_found": status == "eligible_lowcode_found",
            "plugin_type_count": r.get("plugin_type_count", 0),
            "plugin_method_count": r.get("plugin_method_count", 0),
            "workflow_root_candidate_count": 0,
            "provider_callback_count": 0,
            "options_type_count": 0,
            "existing_examples_configured": False,
            "fixture_sources_configured": False,
            "fixture_access_status": "unknown",
            "expected_output_validation_supported": False,
            "generation_risk": "high",
            "recommended_next_action": "blocked_no_lowcode_namespace",
        }

        if status == "blocked_reflection_failed":
            entry["recommended_next_action"] = "blocked_reflection_failed"
            entry["generation_risk"] = "high"
            entry["generation_ready"] = False
            entry["generation_blocked_by"] = ["blocked_reflection_failed"]
            readiness_list.append(entry)
            continue

        if status not in ("eligible_lowcode_found", "not_eligible_no_namespace"):
            entry["recommended_next_action"] = f"blocked_{status}"
            entry["generation_ready"] = False
            entry["generation_blocked_by"] = [f"blocked_{status}"]
            readiness_list.append(entry)
            continue

        if status == "not_eligible_no_namespace":
            entry["recommended_next_action"] = "blocked_no_lowcode_namespace"
            entry["generation_ready"] = False
            entry["generation_blocked_by"] = ["no_lowcode_namespace_found"]
            readiness_list.append(entry)
            continue

        # Family has a LowCode namespace — analyze its API catalog
        catalog_path = r.get("catalog_path")
        if catalog_path and Path(catalog_path).exists():
            try:
                with open(catalog_path) as f:
                    catalog = json.load(f)

                from plugin_examples.scenario_planner.type_classifier import (
                    classify_catalog, WORKFLOW_ROOT, PROVIDER_CALLBACK, OPTIONS,
                )
                # Load config to get namespace patterns
                config_path = (
                    repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
                )
                if config_path.exists():
                    from plugin_examples.family_config import load_family_config
                    config = load_family_config(config_path)
                    ns_patterns = config.plugin_detection.namespace_patterns
                    fixture_sources = config.fixtures.sources
                    existing_sources = config.existing_examples.sources

                    entry["fixture_sources_configured"] = len(fixture_sources) > 0
                    entry["existing_examples_configured"] = len(existing_sources) > 0
                    entry["fixture_access_status"] = "configured" if fixture_sources else "none"
                else:
                    ns_patterns = r.get("lowcode_namespaces", [])

                roles = classify_catalog(catalog, r.get("lowcode_namespaces", []))
                entry["workflow_root_candidate_count"] = sum(
                    1 for role in roles if role.role == WORKFLOW_ROOT
                )
                entry["provider_callback_count"] = sum(
                    1 for role in roles if role.role == PROVIDER_CALLBACK
                )
                entry["options_type_count"] = sum(
                    1 for role in roles if role.role == OPTIONS
                )

            except Exception as catalog_err:
                logger.warning("Could not classify catalog for %s: %s", family, catalog_err)

        # Determine output validation support
        entry["expected_output_validation_supported"] = (
            entry["workflow_root_candidate_count"] > 0
        )

        # Compute generation risk
        wrc = entry["workflow_root_candidate_count"]
        pcc = entry["provider_callback_count"]
        otc = entry["options_type_count"]

        if wrc >= 3 and entry["fixture_sources_configured"]:
            entry["generation_risk"] = "low"
        elif wrc >= 1:
            entry["generation_risk"] = "medium"
        else:
            entry["generation_risk"] = "high"

        # Recommended next action
        if wrc == 0:
            entry["recommended_next_action"] = "needs_type_role_rules"
        elif pcc > 0 or otc > 0:
            entry["recommended_next_action"] = "needs_options_aware_rules"
        elif not entry["fixture_sources_configured"]:
            entry["recommended_next_action"] = "needs_fixture_strategy"
        else:
            entry["recommended_next_action"] = "generate_next"

        # Explicit generation_ready flag — prevents misreading eligibility as permission.
        # Rules:
        #   discovery_only → always False (discovery is all that is allowed).
        #   allowed_types restricted → pilot mode → False until pilot is formally expanded.
        #   wrc == 0 → no workflow roots → cannot generate → False.
        #   Otherwise → True (options_aware advisory does not block proven active families).
        _config_status = "unknown"
        _allowed_types: list[str] = []
        _generation_blocked_by: list[str] = []
        try:
            _cfg_path = repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
            if _cfg_path.exists():
                from plugin_examples.family_config import load_family_config as _lcf
                _cfg = _lcf(_cfg_path)
                _config_status = _cfg.status
                _allowed_types = list(_cfg.generation.allowed_types or [])
        except Exception:
            pass

        # Check denominator for controlled pilot approval state.
        # Rules:
        #   controlled_pilot_approved=True when published_count > 0 (pilot has run).
        #   generation_ready override applies only when published_count < allowed_pilot_count
        #   (i.e., there are still types within the pilot scope left to generate).
        #   When published_count == allowed_pilot_count, all pilot types are done;
        #   further generation requires expansion review — leave generation_ready=False.
        _denominator_published = 0
        _denominator_pilot_count = 0
        _controlled_pilot_approved = False
        _pilot_has_remaining = False
        try:
            _denom_path = repo_root / "pipeline" / "configs" / "denominators" / f"{family}.json"
            if _denom_path.exists():
                import json as _djson
                _denom = _djson.loads(_denom_path.read_text(encoding="utf-8"))
                _denominator_published = _denom.get("published_count", 0) or 0
                _denominator_pilot_count = (
                    _denom.get("allowed_pilot_count")
                    or _denom.get("runnable_scenarios")
                    or len(_allowed_types)
                    or 0
                )
                if _denominator_published > 0 and _allowed_types:
                    _controlled_pilot_approved = True
                    # Remaining pilot types = those approved but not yet published
                    _pilot_has_remaining = _denominator_published < _denominator_pilot_count
        except Exception:
            pass

        if _config_status == "discovery_only":
            _generation_blocked_by.append("family_status_is_discovery_only")
        if _config_status in ("experimental", "disabled"):
            _generation_blocked_by.append(f"family_status_is_{_config_status}")
        if _allowed_types and not _controlled_pilot_approved:
            # Non-empty allowed_types means this family is in controlled pilot mode.
            # Pilot families require explicit governance sign-off to expand generation.
            # Exception: if published_count > 0 the pilot has already run with approval.
            _generation_blocked_by.append("allowed_types_restricted_to_pilot")
        elif _allowed_types and _controlled_pilot_approved and not _pilot_has_remaining:
            # All pilot types have been published; expansion beyond the pilot scope requires
            # a separate review/approval. Block generation until review artifacts are present.
            _generation_blocked_by.append("pilot_completed_expansion_review_required")

        entry["controlled_pilot_approved"] = _controlled_pilot_approved
        if entry["recommended_next_action"] == "needs_type_role_rules":
            # No workflow root candidates found — generation cannot proceed.
            _generation_blocked_by.append("needs_type_role_rules")
        if not entry["fixture_sources_configured"] and entry["workflow_root_candidate_count"] >= 1:
            _generation_blocked_by.append("needs_fixture_strategy")

        # controlled_pilot_approved=True with remaining pilot types means the pilot already
        # ran and produced some published examples, but there are still types within the
        # allowed_types scope left to generate. The published_count>0 proof overrides live
        # classification gaps (e.g. workflow_root_candidate_count=0 due to classifier
        # precision limits). When published_count==allowed_pilot_count, all pilot types are
        # done — expansion requires separate review → leave generation_ready=False.
        if _controlled_pilot_approved and _pilot_has_remaining and not any(
            b.startswith("family_status_is_") for b in _generation_blocked_by
        ):
            entry["generation_ready"] = True
        else:
            entry["generation_ready"] = len(_generation_blocked_by) == 0
        entry["generation_blocked_by"] = _generation_blocked_by
        entry["discovery_status"] = status
        entry["reflection_status"] = "succeeded" if status == "eligible_lowcode_found" else "failed"
        entry["evidence_source"] = f"workspace/verification/latest/{family}-source-of-truth-proof.json"

        readiness_list.append(entry)

    # Sort: generate_next first, then medium risk, then blocked
    priority = {"generate_next": 0, "needs_options_aware_rules": 1,
                "needs_fixture_strategy": 2, "needs_type_role_rules": 3,
                "blocked_no_lowcode_namespace": 4, "blocked_reflection_failed": 5}
    readiness_list.sort(key=lambda x: priority.get(x.get("recommended_next_action", ""), 6))
    return readiness_list
