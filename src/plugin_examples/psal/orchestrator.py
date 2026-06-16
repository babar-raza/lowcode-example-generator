"""PSAL orchestrator — never-stop multi-family autonomous execution loop.

Iterates over ALL non-LowCode families. Each family gets up to max_iterations
of pipeline execution + governance classification. The outer loop NEVER stops
until every family reaches a terminal state.

Three-level exception barrier ensures no single family failure can halt the run.
"""

from __future__ import annotations

import datetime
import logging
import time
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plugin_examples.psal.evidence import AllFamiliesReport, FamilyExecutionRecord

logger = logging.getLogger(__name__)


class FamilyTerminalState(StrEnum):
    ACCEPTED = "ACCEPTED"
    ACCEPTED_WITH_LIMITATIONS = "ACCEPTED_WITH_LIMITATIONS"
    BLOCKED_EXTERNAL = "BLOCKED_EXTERNAL"
    ESCALATED = "ESCALATED"
    ERROR_TERMINAL = "ERROR_TERMINAL"


# Governance next_stage -> terminal state mapping
_TERMINAL_STAGE_MAP = {
    "ACCEPT": FamilyTerminalState.ACCEPTED,
    "ESCALATE": FamilyTerminalState.ESCALATED,
}

# Non-LowCode families ordered by tier (TC-PSAL-21):
NON_LOWCODE_FAMILIES = [
    # Tier 1: proven (enabled, PROBE_CONFIRMED entries exist)
    "barcode", "imaging", "zip", "cad", "font", "tasks",
    # Tier 2: enabled, may have reflection blockers
    "ocr", "psd",
    # Tier 3A: disabled, reflection succeeded, entries exist, no dep issues
    "drawing", "finance", "page", "omr",
    # Tier 3B: disabled, reflection succeeded, dependency resolved manually
    "html", "svg",
    # Tier 3C: disabled, reflection succeeded, license/dep complications
    "threed", "gis",
    # Tier 4: disabled, reflection deferred (large DLL)
    "note", "tex",
    # Tier 5: permanently blocked (no NuGet package)
    "epub",
]


def run_all_families(
    *,
    families: list[str] | None = None,
    max_iterations: int = 3,
    dry_run: bool = True,
    template_mode: bool = False,
    repo_root: Path | None = None,
) -> dict:
    """Run the PSAL orchestrator over all target families.

    Args:
        families: Override list of family slugs. Defaults to NON_LOWCODE_FAMILIES.
        max_iterations: Max governance loop iterations per family.
        dry_run: Pass through to run_pipeline.
        template_mode: Pass through to run_pipeline.
        repo_root: Repository root.

    Returns:
        AllFamiliesReport as a dict (JSON-serializable).
    """
    from plugin_examples.psal.evidence import (
        AllFamiliesReport,
        FamilyExecutionRecord,
        write_aggregate_evidence,
        write_family_evidence,
    )

    target_families = families or list(NON_LOWCODE_FAMILIES)
    resolved_root = (repo_root or Path(".")).resolve()
    evidence_dir = resolved_root / ".local" / "psal" / "evidence"

    report = AllFamiliesReport(
        started_at=datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
    )

    for family in target_families:
        # Level 1: family-level exception barrier
        try:
            record = _execute_family_loop(
                family=family,
                max_iterations=max_iterations,
                dry_run=dry_run,
                template_mode=template_mode,
                repo_root=resolved_root,
            )
        except Exception as exc:
            logger.error("Family %s crashed at top level: %s", family, exc, exc_info=True)
            record = FamilyExecutionRecord(
                family=family,
                terminal_state=FamilyTerminalState.ERROR_TERMINAL,
                error=f"{type(exc).__name__}: {exc}",
            )

        report.records[family] = record

        # Write per-family evidence immediately (incremental checkpoint)
        try:
            write_family_evidence(record, evidence_dir)
        except Exception as exc:
            logger.error("Failed to write evidence for %s: %s", family, exc)

        logger.info(
            "Family %s: %s (iterations=%d)",
            family, record.terminal_state, record.iterations,
        )

    report.completed_at = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")

    # Write aggregate evidence
    try:
        write_aggregate_evidence(report, target_families, evidence_dir)
    except Exception as exc:
        logger.error("Failed to write aggregate evidence: %s", exc)

    return _report_to_dict(report, target_families)


def _execute_family_loop(
    *,
    family: str,
    max_iterations: int,
    dry_run: bool,
    template_mode: bool,
    repo_root: Path,
) -> FamilyExecutionRecord:
    """Execute the pipeline + governance loop for a single family."""
    from plugin_examples.psal.config_patcher import ensure_runnable_config
    from plugin_examples.psal.evidence import FamilyExecutionRecord
    from plugin_examples.psal.report_bridge import (
        build_crash_summary,
        pipeline_report_to_summary,
    )
    from plugin_examples.sprint_governance.loop_controller import classify_and_decide
    from plugin_examples.sprint_governance.models import LoopState

    start_time = time.monotonic()

    # TC-PSAL-20: epub early-exit — no NuGet package, skip pipeline entirely
    original_config = _read_original_config(family, repo_root)
    if original_config.get("status") == "discovery_blocked":
        return FamilyExecutionRecord(
            family=family,
            terminal_state=FamilyTerminalState.BLOCKED_EXTERNAL,
            iterations=0,
            duration_ms=int((time.monotonic() - start_time) * 1000),
            diagnostic_category="NO_NUGET_PACKAGE",
            suggested_action=f"No action possible. {family} package not available on NuGet.org.",
        )

    config_path = ensure_runnable_config(family, repo_root)

    state = LoopState()
    state.sprint_name = f"psal-{family}"
    state.max_iterations = max_iterations

    decisions: list[dict] = []
    last_verdict = ""
    last_sufficiency = ""
    last_ready = 0
    last_blocked = 0
    last_total = 0

    for iteration in range(max_iterations):
        # Level 2: iteration-level exception barrier
        try:
            pipeline_report = _run_pipeline_safe(
                family=family,
                dry_run=dry_run,
                template_mode=template_mode,
                repo_root=repo_root,
                config_path=config_path,
            )
        except Exception as exc:
            logger.error("Pipeline crashed for %s iter %d: %s", family, iteration, exc)
            pipeline_report = {"verdict": "PIPELINE_CRASH", "stages": {}, "error": str(exc)}

        # Level 3: governance-level exception barrier
        try:
            summary = pipeline_report_to_summary(pipeline_report, family)
            decision = classify_and_decide(summary, state)
        except Exception as exc:
            logger.error("Governance crashed for %s iter %d: %s", family, iteration, exc)
            crash_summary = build_crash_summary(family, exc)
            decision = classify_and_decide(crash_summary, state)

        state.iteration += 1
        state.decisions.append(decision)
        decisions.append(decision.to_dict())

        last_verdict = pipeline_report.get("verdict", "")
        # Extract sufficiency and scenario counts from pipeline report
        # stages is a list of {name, status, artifacts, ...} dicts
        raw_stages = pipeline_report.get("stages", [])
        planning = {}
        if isinstance(raw_stages, list):
            for s in raw_stages:
                if isinstance(s, dict) and s.get("name") == "scenario_planning":
                    planning = s.get("artifacts", {}) if isinstance(s.get("artifacts"), dict) else s
                    break
        elif isinstance(raw_stages, dict):
            planning = raw_stages.get("scenario_planning", {})
        if isinstance(planning, dict):
            last_sufficiency = planning.get("sufficiency_status", last_sufficiency)
            last_ready = planning.get("ready_count", last_ready)
            last_blocked = planning.get("blocked_count", last_blocked)
            last_total = planning.get("total_registry_entries", last_total)
        # Also check comparison for scenario counts
        comparison = pipeline_report.get("comparison", {})
        if isinstance(comparison, dict):
            if comparison.get("ready_scenario_count"):
                last_ready = comparison["ready_scenario_count"]
            if comparison.get("blocked_scenario_count"):
                last_blocked = comparison["blocked_scenario_count"]

        # Check if decision is terminal
        next_stage = str(decision.next_stage)
        if next_stage in _TERMINAL_STAGE_MAP:
            terminal = _TERMINAL_STAGE_MAP[next_stage]
            # Distinguish ACCEPTED vs ACCEPTED_WITH_LIMITATIONS
            if terminal == FamilyTerminalState.ACCEPTED and last_sufficiency not in ("SUFFICIENT", ""):
                terminal = FamilyTerminalState.ACCEPTED_WITH_LIMITATIONS
            return FamilyExecutionRecord(
                family=family,
                terminal_state=terminal,
                iterations=iteration + 1,
                verdict=last_verdict,
                sufficiency_status=last_sufficiency,
                ready_scenarios=last_ready,
                blocked_scenarios=last_blocked,
                total_registry_entries=last_total,
                duration_ms=int((time.monotonic() - start_time) * 1000),
                decisions=decisions,
            )

        logger.info(
            "Family %s iter %d: next_stage=%s, continuing loop",
            family, iteration, next_stage,
        )

    # Max iterations reached without terminal — escalate with diagnostics
    diag_cat, diag_action, reg_summary = _diagnose_family(family, repo_root)
    return FamilyExecutionRecord(
        family=family,
        terminal_state=FamilyTerminalState.ESCALATED,
        iterations=max_iterations,
        verdict=last_verdict,
        sufficiency_status=last_sufficiency,
        ready_scenarios=last_ready,
        blocked_scenarios=last_blocked,
        total_registry_entries=last_total,
        error=f"Max iterations ({max_iterations}) reached without terminal state",
        duration_ms=int((time.monotonic() - start_time) * 1000),
        decisions=decisions,
        diagnostic_category=diag_cat,
        suggested_action=diag_action,
        registry_summary=reg_summary,
    )


def _run_pipeline_safe(
    *,
    family: str,
    dry_run: bool,
    template_mode: bool,
    repo_root: Path,
    config_path: Path,
) -> dict:
    """Run the pipeline, returning a report dict. Raises on crash."""
    from plugin_examples.runner import run_pipeline

    return run_pipeline(
        family=family,
        dry_run=dry_run,
        template_mode=template_mode,
        repo_root=repo_root,
        family_config_path=str(config_path),
    )


def _read_original_config(family: str, repo_root: Path) -> dict:
    """Read the original (unpatched) family config YAML."""
    import yaml

    config_path = repo_root / "pipeline" / "configs" / "families" / f"{family}.yml"
    if not config_path.exists():
        return {}
    try:
        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _diagnose_family(family: str, repo_root: Path) -> tuple[str, str, dict]:
    """Produce diagnostic category, suggested action, and registry summary.

    Returns:
        (diagnostic_category, suggested_action, registry_summary)
    """
    import yaml

    registry_path = repo_root / "pipeline" / "plugin-capability-registry" / f"{family}.yaml"
    if not registry_path.exists():
        return (
            "NO_REGISTRY",
            f"Create capability registry at pipeline/plugin-capability-registry/{family}.yaml",
            {},
        )

    try:
        data = yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return ("NO_REGISTRY", "Registry YAML is unreadable", {})

    entries = data.get("entries", [])
    if not entries:
        return ("NO_REGISTRY", "Registry exists but has no entries", {"total": 0})

    counts: dict[str, int] = {}
    for e in entries:
        status = e.get("status", "UNKNOWN")
        counts[status] = counts.get(status, 0) + 1

    summary = {"total": len(entries), **counts}

    confirmed = counts.get("PROBE_CONFIRMED", 0) + counts.get("VERIFIED_PUBLISHABLE", 0)
    failed = counts.get("PROBE_FAILED", 0)

    if confirmed > 0:
        return ("PROBED_BUT_INSUFFICIENT", f"Family has {confirmed} confirmed entries but governance did not accept", summary)

    if failed > 0 and failed == len(entries):
        return ("ALL_PROBES_FAILED", f"All {failed} probes failed. Check probe evidence for fix hints.", summary)

    # Check for dependency/reflection blockers
    blocked_entries = [e for e in entries if e.get("blocker_type")]
    if blocked_entries:
        blocker_types = {e.get("blocker_type") for e in blocked_entries}
        return (
            "DEPENDENCY_BLOCKED",
            f"Blocked by: {', '.join(sorted(blocker_types))}. Resolve dependencies first.",
            summary,
        )

    # Default: entries exist but unprobed
    return (
        "ENTRIES_UNPROBED",
        f"Run: probe-registry --family {family} --execute --promote",
        summary,
    )


def _report_to_dict(report: AllFamiliesReport, target_families: list[str]) -> dict:
    """Convert AllFamiliesReport to a JSON-serializable dict."""
    processed = sorted(report.records.keys())
    missing = sorted(set(target_families) - set(processed))

    return {
        "started_at": report.started_at,
        "completed_at": report.completed_at,
        "total_families": report.total_families,
        "accepted": report.accepted_count,
        "blocked": report.blocked_count,
        "escalated": report.escalated_count,
        "errors": report.error_count,
        "completeness": {
            "target": len(target_families),
            "processed": len(processed),
            "missing": missing,
            "passed": len(missing) == 0,
        },
        "families": {
            fam: rec.to_dict() for fam, rec in report.records.items()
        },
    }
