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

# Non-LowCode families ordered by tier:
# Tier 1: proven (enabled, discovery_only, have registry entries)
# Tier 2: enabled but blocked (ocr, psd)
# Tier 3: disabled with registry
# Tier 4: disabled without registry
# Tier 5: epub (discovery_blocked)
NON_LOWCODE_FAMILIES = [
    # Tier 1: proven
    "barcode", "imaging", "zip", "cad", "font", "tasks",
    # Tier 2: enabled, may be blocked
    "ocr", "psd",
    # Tier 3: disabled, have registries
    "drawing", "finance", "gis", "html", "note", "omr", "page", "svg", "tex", "threed",
    # Tier 5: epub
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

    # Max iterations reached without terminal — escalate
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
