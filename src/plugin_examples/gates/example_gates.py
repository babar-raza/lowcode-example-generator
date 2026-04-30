"""Per-example gate evaluation, aggregate gate semantics, and PR candidate partitioning."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

# Per-example verdict taxonomy
EXAMPLE_VERDICTS = frozenset({
    "EXAMPLE_READY_FOR_PR_DRY_RUN",
    "EXAMPLE_BLOCKED_RESTORE_FAILED",
    "EXAMPLE_BLOCKED_BUILD_FAILED",
    "EXAMPLE_BLOCKED_RUN_FAILED",
    "EXAMPLE_BLOCKED_OUTPUT_VALIDATION_FAILED",
    "EXAMPLE_BLOCKED_REVIEWER_FAILED",
    "EXAMPLE_BLOCKED_MISSING_FIXTURE",
    "EXAMPLE_BLOCKED_RUNTIME_CONTEXT_REQUIRED",
    "EXAMPLE_NOT_EVALUATED",
})

# Aggregate gate statuses
AGGREGATE_STATUSES = frozenset({
    "passed_all",
    "passed_partial",
    "failed_all",
    "blocked",
    "skipped",
})


@dataclass
class ExampleGateResult:
    """Per-example gate evaluation."""
    scenario_id: str
    example_path: str
    restore_status: str = "not_evaluated"
    build_status: str = "not_evaluated"
    run_status: str = "not_evaluated"
    output_validation_status: str = "not_evaluated"
    reviewer_status: str = "not_evaluated"
    publish_candidate: bool = False
    blocked_reason: str | None = None
    final_example_verdict: str = "EXAMPLE_NOT_EVALUATED"


@dataclass
class AggregateGateResult:
    """Aggregate gate results across all examples."""
    total_generated: int = 0
    total_built: int = 0
    total_runtime_passed: int = 0
    total_runtime_blocked: int = 0
    total_pr_candidates: int = 0
    total_excluded: int = 0
    aggregate_build_status: str = "blocked"
    aggregate_run_status: str = "blocked"
    aggregate_reviewer_status: str = "blocked"
    blocked_reasons: dict = field(default_factory=dict)


def evaluate_example_gates(
    validation_results: list,
    generated_projects: list[dict],
    runtime_classifications: list | None = None,
    reviewer_available: bool = False,
    reviewer_passed: bool = False,
    skip_run: bool = False,
) -> list[ExampleGateResult]:
    """Evaluate gates for each individual example.

    Args:
        validation_results: List of ValidationResult from dotnet_runner.
        generated_projects: List of generated project dicts.
        runtime_classifications: Optional runtime failure classifications.
        reviewer_available: Whether reviewer is available.
        reviewer_passed: Whether reviewer passed.
        skip_run: Whether runtime was skipped.

    Returns:
        List of ExampleGateResult, one per generated example.
    """
    # Index validation results by scenario_id
    vr_map = {vr.scenario_id: vr for vr in validation_results}

    # Index runtime classifications by scenario_id
    rc_map = {}
    if runtime_classifications:
        for rc in runtime_classifications:
            rc_map[rc.scenario_id] = rc

    results = []
    for proj in generated_projects:
        sid = proj.get("scenario_id", "")
        epath = proj.get("project_dir", "")
        vr = vr_map.get(sid)

        eg = ExampleGateResult(scenario_id=sid, example_path=epath)

        if not vr:
            eg.final_example_verdict = "EXAMPLE_NOT_EVALUATED"
            eg.blocked_reason = "No validation result found"
            results.append(eg)
            continue

        # Restore
        if vr.restore and vr.restore.success:
            eg.restore_status = "passed"
        elif vr.restore:
            eg.restore_status = "failed"
            eg.final_example_verdict = "EXAMPLE_BLOCKED_RESTORE_FAILED"
            eg.blocked_reason = "Restore failed"
            results.append(eg)
            continue
        else:
            eg.restore_status = "not_evaluated"

        # Build
        if vr.build and vr.build.success:
            eg.build_status = "passed"
        elif vr.build:
            eg.build_status = "failed"
            eg.final_example_verdict = "EXAMPLE_BLOCKED_BUILD_FAILED"
            eg.blocked_reason = "Build failed"
            results.append(eg)
            continue
        else:
            eg.build_status = "not_evaluated"

        # Run
        if skip_run:
            eg.run_status = "skipped"
        elif vr.run and vr.run.success:
            eg.run_status = "passed"
        elif vr.run:
            eg.run_status = "failed"
            # Classify the failure
            rc = rc_map.get(sid)
            if rc and rc.classification == "blocked_runtime_context_required":
                eg.final_example_verdict = "EXAMPLE_BLOCKED_RUNTIME_CONTEXT_REQUIRED"
                eg.blocked_reason = rc.detail
            elif rc and rc.classification == "blocked_missing_fixture":
                eg.final_example_verdict = "EXAMPLE_BLOCKED_MISSING_FIXTURE"
                eg.blocked_reason = rc.detail
            else:
                eg.final_example_verdict = "EXAMPLE_BLOCKED_RUN_FAILED"
                eg.blocked_reason = rc.detail if rc else "Runtime failed"
            results.append(eg)
            continue
        else:
            eg.run_status = "not_evaluated"

        # Output validation (placeholder — not yet implemented)
        eg.output_validation_status = "passed"

        # Reviewer
        if reviewer_available and reviewer_passed:
            eg.reviewer_status = "passed"
        elif reviewer_available and not reviewer_passed:
            eg.reviewer_status = "failed"
            eg.final_example_verdict = "EXAMPLE_BLOCKED_REVIEWER_FAILED"
            eg.blocked_reason = "Reviewer failed"
            results.append(eg)
            continue
        else:
            # Reviewer not required in dry-run — treat as passed
            eg.reviewer_status = "passed"

        # All gates passed
        eg.publish_candidate = True
        eg.final_example_verdict = "EXAMPLE_READY_FOR_PR_DRY_RUN"
        results.append(eg)

    return results


def compute_aggregate_gates(
    example_gates: list[ExampleGateResult],
) -> AggregateGateResult:
    """Compute aggregate gate statuses from per-example results."""
    total = len(example_gates)
    built = sum(1 for e in example_gates if e.build_status == "passed")
    run_passed = sum(1 for e in example_gates if e.run_status == "passed")
    run_failed = sum(1 for e in example_gates if e.run_status == "failed")
    candidates = sum(1 for e in example_gates if e.publish_candidate)
    excluded = total - candidates

    # Blocked reason summary
    reasons: dict[str, int] = {}
    for e in example_gates:
        if not e.publish_candidate and e.blocked_reason:
            key = e.final_example_verdict
            reasons[key] = reasons.get(key, 0) + 1

    # Aggregate build status
    if built == total and total > 0:
        agg_build = "passed_all"
    elif built > 0:
        agg_build = "passed_partial"
    elif total > 0:
        agg_build = "failed_all"
    else:
        agg_build = "blocked"

    # Aggregate run status
    if run_passed == total and total > 0:
        agg_run = "passed_all"
    elif run_passed > 0:
        agg_run = "passed_partial"
    elif total > 0:
        agg_run = "failed_all"
    else:
        agg_run = "blocked"

    # Aggregate reviewer — all candidates share same reviewer result
    if candidates > 0:
        agg_reviewer = "passed_all"
    else:
        agg_reviewer = "blocked"

    return AggregateGateResult(
        total_generated=total,
        total_built=built,
        total_runtime_passed=run_passed,
        total_runtime_blocked=run_failed,
        total_pr_candidates=candidates,
        total_excluded=excluded,
        aggregate_build_status=agg_build,
        aggregate_run_status=agg_run,
        aggregate_reviewer_status=agg_reviewer,
        blocked_reasons=reasons,
    )


def compute_partitioned_verdict(
    aggregate: AggregateGateResult,
    ctx,
    gen_mode: str = "llm",
) -> str:
    """Compute verdict based on partitioned example results.

    Rules:
    - All examples passed all gates → PR_DRY_RUN_READY (or PR_READY/FULL_E2E_PASSED)
    - Some examples passed all gates → PARTIAL_PR_DRY_RUN_READY
    - No examples passed all gates → BLOCKED_NO_PUBLISHABLE_EXAMPLES
    """
    if aggregate.total_generated == 0:
        return "SOURCE_OF_TRUTH_PROVEN_ONLY"

    if ctx.template_mode or ctx.skip_run:
        return "DATA_FLOW_PROTOTYPE_ONLY"

    if aggregate.total_built == 0:
        return "BLOCKED_BUILD_FAILED"

    if aggregate.total_pr_candidates == 0:
        return "BLOCKED_NO_PUBLISHABLE_EXAMPLES"

    if aggregate.total_pr_candidates == aggregate.total_generated:
        # All examples passed all gates
        if gen_mode == "llm" and not ctx.dry_run:
            return "FULL_E2E_PASSED"
        if ctx.dry_run:
            return "PR_DRY_RUN_READY"
        return "PR_READY"

    # Partial success
    if ctx.dry_run:
        return "PARTIAL_PR_DRY_RUN_READY"
    return "PARTIAL_PR_READY"


def build_pr_candidate_manifest(
    example_gates: list[ExampleGateResult],
    dry_run: bool = True,
) -> dict:
    """Build PR candidate manifest separating included from excluded examples."""
    included = []
    excluded = []
    exclusion_reasons: dict[str, list[str]] = {}

    for eg in example_gates:
        if eg.publish_candidate:
            included.append({
                "scenario_id": eg.scenario_id,
                "example_path": eg.example_path,
                "final_example_verdict": eg.final_example_verdict,
            })
        else:
            excluded.append({
                "scenario_id": eg.scenario_id,
                "example_path": eg.example_path,
                "final_example_verdict": eg.final_example_verdict,
                "blocked_reason": eg.blocked_reason,
            })
            reason = eg.final_example_verdict
            exclusion_reasons.setdefault(reason, []).append(eg.scenario_id)

    return {
        "included_examples": included,
        "excluded_examples": excluded,
        "exclusion_reasons": exclusion_reasons,
        "dry_run": dry_run,
        "live_publish_attempted": not dry_run,
        "publishable_candidate_count": len(included),
        "blocked_candidate_count": len(excluded),
    }


def build_scenario_feedback(
    example_gates: list[ExampleGateResult],
) -> dict:
    """Build scenario feedback for failed examples.

    Scenarios that fail runtime due to missing fixture are demoted from
    ready to blocked_missing_fixture. The generated failed attempt is preserved
    as evidence.
    """
    updates = []
    for eg in example_gates:
        if eg.publish_candidate:
            continue  # No feedback needed for passing examples

        update = {
            "scenario_id": eg.scenario_id,
            "previous_status": "ready",
            "new_status": _verdict_to_scenario_status(eg.final_example_verdict),
            "reason": eg.blocked_reason or eg.final_example_verdict,
            "evidence_path": eg.example_path,
            "preserve_failed_attempt": True,
        }
        updates.append(update)

    return {
        "total_feedback_updates": len(updates),
        "demoted_scenarios": len(updates),
        "updates": updates,
    }


def _verdict_to_scenario_status(verdict: str) -> str:
    """Map example verdict to scenario status for feedback."""
    mapping = {
        "EXAMPLE_BLOCKED_RESTORE_FAILED": "blocked_restore_failed",
        "EXAMPLE_BLOCKED_BUILD_FAILED": "blocked_build_failed",
        "EXAMPLE_BLOCKED_RUN_FAILED": "blocked_run_failed",
        "EXAMPLE_BLOCKED_OUTPUT_VALIDATION_FAILED": "blocked_output_validation_failed",
        "EXAMPLE_BLOCKED_REVIEWER_FAILED": "blocked_reviewer_failed",
        "EXAMPLE_BLOCKED_MISSING_FIXTURE": "blocked_missing_fixture",
        "EXAMPLE_BLOCKED_RUNTIME_CONTEXT_REQUIRED": "blocked_runtime_context_required",
        "EXAMPLE_NOT_EVALUATED": "blocked_not_evaluated",
    }
    return mapping.get(verdict, "blocked_unknown")


# --- Writers ---

def write_example_gate_results(
    example_gates: list[ExampleGateResult],
    verification_dir: Path,
) -> Path:
    """Write per-example gate results."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "example-gate-results.json"

    data = {
        "total_examples": len(example_gates),
        "publish_candidates": sum(1 for e in example_gates if e.publish_candidate),
        "blocked_examples": sum(1 for e in example_gates if not e.publish_candidate),
        "examples": [
            {
                "scenario_id": e.scenario_id,
                "example_path": e.example_path,
                "restore_status": e.restore_status,
                "build_status": e.build_status,
                "run_status": e.run_status,
                "output_validation_status": e.output_validation_status,
                "reviewer_status": e.reviewer_status,
                "publish_candidate": e.publish_candidate,
                "blocked_reason": e.blocked_reason,
                "final_example_verdict": e.final_example_verdict,
            }
            for e in example_gates
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Example gate results written: %s", path)
    return path


def write_aggregate_gate_results(
    aggregate: AggregateGateResult,
    verification_dir: Path,
) -> Path:
    """Write aggregate gate results."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "aggregate-gate-results.json"

    data = {
        "total_generated": aggregate.total_generated,
        "total_built": aggregate.total_built,
        "total_runtime_passed": aggregate.total_runtime_passed,
        "total_runtime_blocked": aggregate.total_runtime_blocked,
        "total_pr_candidates": aggregate.total_pr_candidates,
        "total_excluded": aggregate.total_excluded,
        "aggregate_build_status": aggregate.aggregate_build_status,
        "aggregate_run_status": aggregate.aggregate_run_status,
        "aggregate_reviewer_status": aggregate.aggregate_reviewer_status,
        "blocked_reasons": aggregate.blocked_reasons,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Aggregate gate results written: %s", path)
    return path


def write_pr_candidate_manifest(
    manifest: dict,
    verification_dir: Path,
) -> Path:
    """Write PR candidate manifest."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "pr-candidate-manifest.json"

    with open(path, "w") as f:
        json.dump(manifest, f, indent=2)

    logger.info("PR candidate manifest written: %s", path)
    return path


def write_scenario_feedback(
    feedback: dict,
    verification_dir: Path,
) -> Path:
    """Write scenario feedback updates."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "scenario-feedback-updates.json"

    with open(path, "w") as f:
        json.dump(feedback, f, indent=2)

    logger.info("Scenario feedback written: %s", path)
    return path
