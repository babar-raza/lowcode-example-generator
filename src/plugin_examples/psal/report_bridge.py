"""Report bridge — translate pipeline output to governance ExecutionSummary.

Bridges the gap between run_pipeline() dict output and the sprint governance
classify_and_decide() input format (ExecutionSummary).
"""

from __future__ import annotations

import datetime
import logging

from plugin_examples.sprint_governance.models import (
    ExecutionSummary,
    Issue,
    IssueLevel,
    IssueSeverity,
    QualityEvaluation,
    QualityScore,
)

logger = logging.getLogger(__name__)

# Required quality dimensions from sprint-governance-schema.yaml
_REQUIRED_DIMENSIONS = [
    "requirement_correctness",
    "implementation_correctness",
    "integration_completeness",
    "pipeline_compatibility",
    "governance_compliance",
    "evidence_completeness",
    "test_coverage",
    "repeatability",
    "rollback_safety",
    "production_readiness",
]


def pipeline_report_to_summary(
    report: dict,
    family: str,
) -> ExecutionSummary:
    """Convert a pipeline run_pipeline() report dict to an ExecutionSummary.

    Args:
        report: Dict returned by run_pipeline() with keys:
            stages, gate_summary, verdict, comparison, etc.
        family: Family slug.

    Returns:
        ExecutionSummary suitable for classify_and_decide().
    """
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    verdict = report.get("verdict", "UNKNOWN")
    raw_stages = report.get("stages", [])
    comparison = report.get("comparison", {})
    gate_summary = report.get("gate_summary", {})

    # Normalize stages: pipeline returns a list of {name, status, ...} dicts.
    # Convert to a dict keyed by stage name for easier lookup.
    stages_by_name: dict[str, dict] = {}
    if isinstance(raw_stages, list):
        for s in raw_stages:
            if isinstance(s, dict) and "name" in s:
                stages_by_name[s["name"]] = s
    elif isinstance(raw_stages, dict):
        stages_by_name = raw_stages

    # Status values: pipeline uses "success"/"skipped"/"error"/"hard_stop"
    _PASS_STATUSES = frozenset({"success", "skipped", "PASS", "SKIP"})
    _FAIL_STATUSES = frozenset({"error", "hard_stop", "FAIL"})

    total_stages = len(stages_by_name)
    passed_stages = sum(
        1 for s in stages_by_name.values()
        if isinstance(s, dict) and s.get("status") in _PASS_STATUSES
    )

    # Taskcard counts from comparison or gate_summary
    # attempted = ready + blocked (total scenarios in the registry)
    ready_count = comparison.get("ready_scenario_count", 0)
    blocked_count = comparison.get("blocked_scenario_count", 0)
    taskcards_attempted = ready_count + blocked_count
    if not taskcards_attempted:
        taskcards_attempted = gate_summary.get("scenarios_planned", 0)
    taskcards_completed = comparison.get("examples_generated_count", 0)
    taskcards_blocked = blocked_count

    # Sufficiency status from planning stage artifacts
    sufficiency = "UNKNOWN"
    planning_data = stages_by_name.get("scenario_planning", {})
    if isinstance(planning_data, dict):
        artifacts = planning_data.get("artifacts", {})
        if isinstance(artifacts, dict):
            sufficiency = artifacts.get("sufficiency_status", "UNKNOWN")
        # Also check direct key (test compatibility)
        if sufficiency == "UNKNOWN":
            sufficiency = planning_data.get("sufficiency_status", "UNKNOWN")

    # Build issues from failed stages
    hard_stop_stages = {"load_config", "nuget_fetch", "dependency_resolution",
                        "extraction", "reflection", "plugin_detection", "scenario_planning"}
    issues: list[Issue] = []
    for stage_name, stage_data in stages_by_name.items():
        if isinstance(stage_data, dict) and stage_data.get("status") in _FAIL_STATUSES:
            is_hard_stop = stage_name in hard_stop_stages or stage_data.get("status") == "hard_stop"
            issues.append(Issue(
                id=f"{family}-{stage_name}-fail",
                level=IssueLevel.L1,
                severity=IssueSeverity.HIGH if stage_name in hard_stop_stages else IssueSeverity.MEDIUM,
                title=f"Stage {stage_name} failed for {family}",
                description=str(stage_data.get("error", "")),
                blocker=is_hard_stop,
            ))

    # Auto-score quality from pipeline metrics
    scores = _auto_score_pipeline_run(
        verdict=verdict,
        total_stages=total_stages,
        passed_stages=passed_stages,
        taskcards_attempted=taskcards_attempted,
        taskcards_completed=taskcards_completed,
        sufficiency=sufficiency,
    )

    quality_eval = QualityEvaluation(
        taskcard_id=f"{family}-pipeline-run",
        scores=scores,
        accepted=all(s.passes for s in scores),
        rerouted=not all(s.passes for s in scores),
    )

    # Map pipeline verdict to governance verdict
    gov_verdict = _map_verdict(verdict, sufficiency, issues)

    # Extract evidence path from pipeline metadata
    evidence_path = ""
    meta = report.get("meta", {})
    if isinstance(meta, dict):
        evidence_path = meta.get("evidence_dir", "") or meta.get("run_dir", "")
    if not evidence_path:
        evidence_files = report.get("run_evidence_files", [])
        if isinstance(evidence_files, list) and evidence_files:
            evidence_path = str(evidence_files[0]) if evidence_files else ""
    # Fallback: if pipeline ran at all, use a synthetic path
    if not evidence_path and total_stages > 0:
        evidence_path = f"psal/{family}/pipeline-evidence"

    return ExecutionSummary(
        timestamp=timestamp,
        verdict=gov_verdict,
        taskcards_attempted=taskcards_attempted,
        taskcards_completed=taskcards_completed,
        taskcards_blocked=taskcards_blocked,
        taskcards_rerouted=0,
        issues=issues,
        quality_evaluations=[quality_eval],
        evidence_path=evidence_path,
        raw=report,
    )


def build_crash_summary(family: str, exc: Exception) -> ExecutionSummary:
    """Build an ExecutionSummary from a pipeline crash.

    Args:
        family: Family slug.
        exc: The exception that crashed the pipeline.

    Returns:
        ExecutionSummary with a single blocker issue.
    """
    timestamp = datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
    issue = Issue(
        id=f"{family}-pipeline-crash",
        level=IssueLevel.L1,
        severity=IssueSeverity.CRITICAL,
        title=f"Pipeline crashed for {family}",
        description=f"{type(exc).__name__}: {exc}",
        blocker=True,
    )

    # All scores at minimum (1)
    scores = [
        QualityScore(dimension=dim, score=1, threshold=4, comment="Pipeline crashed")
        for dim in _REQUIRED_DIMENSIONS
    ]

    return ExecutionSummary(
        timestamp=timestamp,
        verdict="PIPELINE_CRASH",
        taskcards_attempted=0,
        taskcards_completed=0,
        taskcards_blocked=1,
        issues=[issue],
        quality_evaluations=[
            QualityEvaluation(
                taskcard_id=f"{family}-crash",
                scores=scores,
                accepted=False,
                rerouted=True,
            )
        ],
        raw={"error": str(exc), "error_type": type(exc).__name__},
    )


def _auto_score_pipeline_run(
    *,
    verdict: str,
    total_stages: int,
    passed_stages: int,
    taskcards_attempted: int,
    taskcards_completed: int,
    sufficiency: str,
) -> list[QualityScore]:
    """Derive quality scores from pipeline metrics."""
    stage_ratio = passed_stages / max(total_stages, 1)
    completion_ratio = taskcards_completed / max(taskcards_attempted, 1)

    # requirement_correctness: penalized when BELOW_MINIMUM or REGISTRY_INCOMPLETE
    req_score = 5 if sufficiency == "SUFFICIENT" else 3 if sufficiency == "REGISTRY_INCOMPLETE" else 2

    # implementation_correctness: based on build/run success
    _pass_verdicts = {"DRY_RUN_BUILD_PASS", "DATA_FLOW_PROTOTYPE_ONLY", "FULL_E2E_PASSED"}
    impl_score = 5 if verdict in _pass_verdicts else 3 if "PARTIAL" in verdict.upper() else 2

    # integration_completeness: stages passed ratio
    integ_score = max(1, min(5, round(stage_ratio * 5)))

    # pipeline_compatibility: if pipeline ran at all
    pipeline_score = 5 if total_stages > 0 else 1

    # governance_compliance: always 4 (PSAL is running governance)
    gov_score = 4

    # evidence_completeness: based on stages producing artifacts
    evidence_score = max(1, min(5, round(stage_ratio * 5)))

    # test_coverage: based on completion ratio
    test_score = max(1, min(5, round(completion_ratio * 5)))

    # repeatability: 4 if pipeline passed, 3 otherwise
    repeat_score = 4 if verdict in _pass_verdicts else 3

    # rollback_safety: 5 for dry_run (no side effects)
    rollback_score = 5

    # production_readiness: derived from verdict + sufficiency
    prod_score = 4 if verdict in _pass_verdicts and sufficiency == "SUFFICIENT" else 3

    dimension_scores = {
        "requirement_correctness": req_score,
        "implementation_correctness": impl_score,
        "integration_completeness": integ_score,
        "pipeline_compatibility": pipeline_score,
        "governance_compliance": gov_score,
        "evidence_completeness": evidence_score,
        "test_coverage": test_score,
        "repeatability": repeat_score,
        "rollback_safety": rollback_score,
        "production_readiness": prod_score,
    }

    return [
        QualityScore(dimension=dim, score=score, threshold=4)
        for dim, score in dimension_scores.items()
    ]


def _map_verdict(verdict: str, sufficiency: str, issues: list[Issue]) -> str:
    """Map pipeline verdict + sufficiency to governance verdict string."""
    has_blockers = any(i.blocker for i in issues)

    if has_blockers:
        return "EXECUTION_BLOCKED"

    # Verdicts that indicate pipeline completed successfully
    _PASS_VERDICTS = {"DRY_RUN_BUILD_PASS", "DATA_FLOW_PROTOTYPE_ONLY", "FULL_E2E_PASSED"}

    if verdict in _PASS_VERDICTS:
        if sufficiency == "SUFFICIENT":
            return "EXECUTION_COMPLETE_VERIFIED"
        if sufficiency == "REGISTRY_INCOMPLETE":
            return "EXECUTION_PARTIAL_REGISTRY_INCOMPLETE"
        return "EXECUTION_PARTIAL_BELOW_MINIMUM"

    if "HARD_STOP" in verdict.upper():
        return "EXECUTION_HARD_STOPPED"

    return f"EXECUTION_UNKNOWN_{verdict}"
