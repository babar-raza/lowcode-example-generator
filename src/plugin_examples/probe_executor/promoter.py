"""Registry promoter: write probe results back to capability registry YAMLs.

After a probe run, the promoter updates the entry's status from
REFLECTION_CANDIDATE/WEBSITE_DISCOVERED to PROBE_CONFIRMED or PROBE_FAILED,
along with evidence paths and metadata.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Mapping from failure taxonomy to next_action.
_FAILURE_NEXT_ACTION: dict[str, str] = {
    "PROBE_FAILED_BUILD": "NEEDS_API_MAPPING_FIX",
    "PROBE_FAILED_API": "NEEDS_RUNTIME_FIX",
    "PROBE_FAILED_LICENSE": "BLOCKED_LICENSE_RESTRICTED",
    "PROBE_FAILED_RESTORE": "NEEDS_DEPENDENCY_FIX",
    "PROBE_FAILED_TIMEOUT": "NEEDS_TIMEOUT_INCREASE",
}


def promote_entry(
    family: str,
    plugin_slug: str,
    new_status: str,
    probe_evidence_path: str,
    failure_taxonomy: str | None,
    repo_root: Path,
) -> dict:
    """Promote a single registry entry based on probe results.

    Args:
        family: Family slug.
        plugin_slug: Plugin slug to find in the registry.
        new_status: Target status (PROBE_CONFIRMED or PROBE_FAILED_*).
        probe_evidence_path: Path to probe evidence JSON.
        failure_taxonomy: Failure taxonomy code (None if confirmed).
        repo_root: Repository root path.

    Returns:
        Updated entry dict.

    Raises:
        ValueError: If entry not found in registry.
    """
    import yaml

    registry_path = repo_root / "pipeline" / "plugin-capability-registry" / f"{family}.yaml"
    if not registry_path.exists():
        raise ValueError(f"Registry file not found: {registry_path}")

    text = registry_path.read_text(encoding="utf-8")
    data = yaml.safe_load(text) or {}
    entries = data.get("entries", [])

    target = None
    for entry in entries:
        if entry.get("plugin_slug") == plugin_slug:
            target = entry
            break

    if target is None:
        raise ValueError(
            f"Entry '{plugin_slug}' not found in {registry_path}. "
            f"Available: {[e.get('plugin_slug') for e in entries]}"
        )

    if new_status == "PROBE_CONFIRMED":
        target["status"] = "PROBE_CONFIRMED"
        target["probe_evidence"] = probe_evidence_path
        current_score = target.get("confidence_score", 0.50)
        target["confidence_score"] = min(0.95, current_score + 0.20)
        target["next_action"] = "READY_FOR_EXAMPLE_GENERATION"
        target["blocker_type"] = None
        target["failure_taxonomy"] = None
        target["bootstrap_status"] = "PROBE_CONFIRMED"
    else:
        target["status"] = "PROBE_FAILED"
        target["probe_evidence"] = probe_evidence_path
        target["failure_taxonomy"] = failure_taxonomy or new_status
        target["next_action"] = _FAILURE_NEXT_ACTION.get(
            new_status, "NEEDS_INVESTIGATION"
        )

    with registry_path.open("w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    logger.info("Promoted %s/%s -> %s", family, plugin_slug, new_status)
    return target


def promote_family(
    family: str,
    outcomes: list,
    repo_root: Path,
) -> dict:
    """Promote all entries for a family based on probe outcomes.

    Args:
        family: Family slug.
        outcomes: List of ProbeOutcome objects.
        repo_root: Repository root path.

    Returns:
        Summary dict with promoted/failed counts.
    """
    promoted = 0
    failed = 0

    for outcome in outcomes:
        try:
            promote_entry(
                family=family,
                plugin_slug=outcome.plugin_slug,
                new_status=outcome.new_status,
                probe_evidence_path=outcome.probe_evidence_path,
                failure_taxonomy=getattr(outcome, "error", None)
                or (outcome.probe_result.failure_taxonomy if outcome.probe_result else outcome.new_status),
                repo_root=repo_root,
            )
            if outcome.new_status == "PROBE_CONFIRMED":
                promoted += 1
            else:
                failed += 1
        except Exception as exc:
            logger.error("Failed to promote %s/%s: %s", family, outcome.plugin_slug, exc)
            failed += 1

    return {"family": family, "promoted": promoted, "failed": failed, "total": promoted + failed}
