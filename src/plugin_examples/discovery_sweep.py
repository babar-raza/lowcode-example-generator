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
        all_families: If True, discover all enabled families.
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
        # Scan enabled family configs
        for yml in sorted(configs_dir.glob("*.yml")):
            family_names.append(yml.stem)

    results: list[dict] = []

    for family in family_names:
        result = _discover_family(family, repo_root, allow_experimental)
        results.append(result)

    # Build summary
    eligible_count = sum(1 for r in results if r["status"] == "eligible_lowcode_found")
    summary = {
        "total_families": len(results),
        "eligible_count": eligible_count,
        "families": results,
    }

    # Write evidence
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    evidence_path = latest / "all-family-lowcode-discovery.json"
    evidence_path.write_text(json.dumps(summary, indent=2))
    logger.info("Discovery sweep evidence written: %s", evidence_path)

    return summary


def _discover_family(family: str, repo_root: Path, allow_experimental: bool) -> dict:
    """Discover LowCode namespaces for a single family."""
    result: dict = {
        "family": family,
        "status": "unknown",
        "package_id": None,
        "resolved_version": None,
        "namespace_count": 0,
        "lowcode_namespaces": [],
        "plugin_type_count": 0,
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

        if config.status == "experimental" and not allow_experimental:
            result["status"] = "experimental_skipped"
            return result

        result["package_id"] = config.nuget.package_id

        # Resolve NuGet package
        from plugin_examples.nuget_fetcher import fetch_package
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

        # Extract DLLs
        from plugin_examples.nupkg_extractor import extract_package
        extraction = extract_package(
            Path(manifest["cached_path"]),
            package_id=config.nuget.package_id,
            family=family,
            target_framework_preference=config.nuget.target_framework_preference,
            run_dir=run_dir,
        )

        # Build catalog
        from plugin_examples.reflection_catalog import build_catalog
        catalog_dir = run_dir / "catalog" / family
        catalog_dir.mkdir(parents=True, exist_ok=True)
        catalog = build_catalog(
            dll_path=Path(extraction["dll_path"]),
            output_path=catalog_dir / "api-catalog.json",
            xml_path=Path(extraction["xml_path"]) if extraction.get("xml_path") else None,
            namespace_filter=config.plugin_detection.namespace_patterns,
        )

        # Detect namespaces
        from plugin_examples.plugin_detector import detect_plugin_namespaces
        detection = detect_plugin_namespaces(
            catalog, config.plugin_detection.namespace_patterns,
        )

        matched = [m.namespace for m in detection.matched_namespaces]
        result["namespace_count"] = len(matched)
        result["lowcode_namespaces"] = matched
        result["plugin_type_count"] = detection.public_plugin_type_count

        if matched:
            result["status"] = "eligible_lowcode_found"
        else:
            result["status"] = "not_eligible_no_namespace"

    except Exception as e:
        logger.warning("Discovery failed for %s: %s", family, e)
        result["status"] = "blocked_reflection_failed"
        result["error"] = str(e)

    return result
