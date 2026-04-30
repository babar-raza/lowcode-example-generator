"""Honest verdict evaluator for the pipeline gate engine."""

from __future__ import annotations

from plugin_examples.gates.models import GateResult, GateVerdict


# Hard-stop stage names (pipeline halts on failure).
_HARD_STOP_STAGES = frozenset({
    "load_config", "nuget_fetch", "dependency_resolution",
    "extraction", "reflection", "plugin_detection",
})


def evaluate_gates(
    stages: list,
    ctx,
    validation_results: list | None = None,
    reviewer_result=None,
) -> GateVerdict:
    """Evaluate all pipeline gates and produce an honest verdict.

    Args:
        stages: List of StageResult from the pipeline run.
        ctx: PipelineContext with run configuration.
        validation_results: List of ValidationResult (optional).
        reviewer_result: ReviewerResult (optional).

    Returns:
        GateVerdict with honest assessment.
    """
    gates: list[GateResult] = []
    blocking: list[str] = []

    # --- Hard gate: source of truth ---
    hard_failed = [s for s in stages if s.name in _HARD_STOP_STAGES and s.status == "failed"]
    if hard_failed:
        gate = GateResult(
            gate_id="gate_source_of_truth",
            name="Source of Truth",
            status="failed",
            required=True,
            failure_reason=f"Hard-stop stage(s) failed: {', '.join(s.name for s in hard_failed)}",
            downstream_blocked=["gate_scenarios", "gate_generation", "gate_build", "gate_run",
                                "gate_output_validation", "gate_reviewer", "gate_publish"],
            stage_name=hard_failed[0].name,
        )
        gates.append(gate)
        blocking.append(gate.gate_id)

    # --- Scenario planning gate ---
    plan_stage = _find_stage(stages, "scenario_planning")
    if plan_stage:
        ready_count = plan_stage.artifacts.get("ready_count", 0) if plan_stage.status == "success" else 0
        gate = GateResult(
            gate_id="gate_scenarios",
            name="Scenario Planning",
            status="passed" if ready_count > 0 else ("failed" if plan_stage.status == "failed" else "blocked"),
            required=True,
            failure_reason=None if ready_count > 0 else "No ready scenarios",
            stage_name="scenario_planning",
        )
        if gate.status != "passed":
            blocking.append(gate.gate_id)
        gates.append(gate)

    # --- Generation gate ---
    gen_stage = _find_stage(stages, "generation")
    gen_count = 0
    gen_mode = "template"
    if gen_stage:
        gen_count = gen_stage.artifacts.get("examples_generated", 0)
        gen_mode = gen_stage.artifacts.get("generation_mode", "template")
        gate = GateResult(
            gate_id="gate_generation",
            name="Example Generation",
            status="passed" if gen_count > 0 else ("failed" if gen_stage.status == "failed" else "blocked"),
            required=True,
            failure_reason=None if gen_count > 0 else "No examples generated",
            stage_name="generation",
        )
        if gate.status != "passed":
            blocking.append(gate.gate_id)
        gates.append(gate)

    # --- Build gate ---
    val_stage = _find_stage(stages, "validation")
    build_passed = 0
    build_total = 0
    run_passed = 0
    if val_stage and val_stage.status not in ("skipped",):
        build_passed = val_stage.artifacts.get("build_passed", val_stage.artifacts.get("passed", 0))
        build_total = val_stage.artifacts.get("total", 0)
        run_passed = val_stage.artifacts.get("run_passed", val_stage.artifacts.get("passed", 0))

        # Build gate
        gate = GateResult(
            gate_id="gate_build",
            name="Build Validation",
            status="passed" if build_passed > 0 else "failed",
            required=True,
            failure_reason=None if build_passed > 0 else f"0/{build_total} examples passed build",
            evidence_files=["validation-results.json"],
            stage_name="validation",
        )
        if gate.status != "passed":
            blocking.append(gate.gate_id)
        gates.append(gate)

    # --- Run gate (aggregate-aware) ---
    run_total = build_total  # Only examples that built can run
    if ctx.skip_run:
        gate = GateResult(
            gate_id="gate_run",
            name="Runtime Validation",
            status="skipped",
            required=False,
            failure_reason="Runtime skipped via --skip-run",
            stage_name="validation",
        )
        gates.append(gate)
    elif val_stage and val_stage.status not in ("skipped",) and build_passed > 0:
        vr = validation_results or ctx.validation_results
        if vr:
            run_passed = sum(1 for v in vr if v.run and v.run.success)
            run_total = sum(1 for v in vr if v.build and v.build.success)

        # Determine aggregate run status
        if run_passed == run_total and run_total > 0:
            agg_run = "passed_all"
        elif run_passed > 0:
            agg_run = "passed_partial"
        elif run_total > 0:
            agg_run = "failed_all"
        else:
            agg_run = "blocked"

        run_failure_reason = None
        if agg_run == "failed_all":
            run_failure_reason = "No examples passed runtime"
        elif agg_run == "passed_partial":
            run_failure_reason = f"{run_passed}/{run_total} examples passed runtime"

        gate = GateResult(
            gate_id="gate_run",
            name="Runtime Validation",
            status="passed" if run_passed > 0 else "failed",
            required=True,
            failure_reason=run_failure_reason,
            stage_name="validation",
        )
        if gate.status != "passed":
            blocking.append(gate.gate_id)
        gates.append(gate)
    elif build_passed == 0 and gen_count > 0:
        gate = GateResult(
            gate_id="gate_run",
            name="Runtime Validation",
            status="blocked",
            required=True,
            failure_reason="Build failed — runtime cannot execute",
            stage_name="validation",
        )
        blocking.append(gate.gate_id)
        gates.append(gate)

    # --- Reviewer gate ---
    rev_stage = _find_stage(stages, "reviewer")
    publish_path = not ctx.dry_run
    if rev_stage:
        if rev_stage.status == "skipped":
            rev_status = "skipped"
        elif rev_stage.status in ("failed", "degraded"):
            rev_available = rev_stage.artifacts.get("available", False)
            if not rev_available:
                rev_status = "failed" if publish_path else "skipped"
            else:
                rev_passed = rev_stage.artifacts.get("passed", False)
                rev_status = "passed" if rev_passed else "failed"
        else:
            rev_passed = rev_stage.artifacts.get("passed", False)
            rev_status = "passed" if rev_passed else "failed"

        gate = GateResult(
            gate_id="gate_reviewer",
            name="Example Reviewer",
            status=rev_status,
            required=publish_path or ctx.require_reviewer,
            failure_reason=None if rev_status == "passed" else (
                "Reviewer unavailable" if not rev_stage.artifacts.get("available", False)
                else "Reviewer returned failure"
            ),
            stage_name="reviewer",
        )
        if gate.required and gate.status not in ("passed",):
            blocking.append(gate.gate_id)
        gates.append(gate)

    # Determine publishability and verdict
    all_required_passed = all(
        g.status == "passed" for g in gates if g.required
    )

    verdict = _compute_verdict(
        stages=stages,
        ctx=ctx,
        gates=gates,
        blocking=blocking,
        gen_count=gen_count,
        gen_mode=gen_mode,
        build_passed=build_passed,
        run_passed=run_passed,
        all_required_passed=all_required_passed,
    )

    publishable = is_publishable_verdict(verdict)

    return GateVerdict(
        gates=gates,
        verdict=verdict,
        publishable=publishable,
        all_required_passed=all_required_passed,
        blocking_gates=blocking,
    )


def _compute_verdict(
    *,
    stages: list,
    ctx,
    gates: list[GateResult],
    blocking: list[str],
    gen_count: int,
    gen_mode: str,
    build_passed: int,
    run_passed: int,
    all_required_passed: bool,
) -> str:
    """Compute the canonical verdict string."""
    # Hard gate failures
    if "gate_source_of_truth" in blocking:
        return "BLOCKED_SOURCE_OF_TRUTH"

    # Scenario planning blocked
    plan_stage = _find_stage(stages, "scenario_planning")
    if plan_stage and plan_stage.status == "failed":
        return "BLOCKED_SCENARIO_PLANNING"

    # No ready scenarios — source of truth proven but nothing to generate
    if plan_stage and plan_stage.status == "success":
        ready = plan_stage.artifacts.get("ready_count", 0)
        if ready == 0:
            return "SOURCE_OF_TRUTH_PROVEN_ONLY"

    # Generation failed or produced nothing
    if gen_count == 0:
        gen_stage = _find_stage(stages, "generation")
        if gen_stage and gen_stage.status == "skipped":
            return "SOURCE_OF_TRUTH_PROVEN_ONLY"
        return "BLOCKED_GENERATION"

    # Template mode or skip-run: max is DATA_FLOW_PROTOTYPE_ONLY
    if ctx.template_mode or ctx.skip_run:
        return "DATA_FLOW_PROTOTYPE_ONLY"

    # Build failures
    if build_passed == 0:
        return "BLOCKED_BUILD_FAILED"

    # Run failures (only if not skip_run)
    if not ctx.skip_run and run_passed == 0:
        return "BLOCKED_RUN_FAILED"

    # Reviewer gate
    rev_gate = next((g for g in gates if g.gate_id == "gate_reviewer"), None)
    if rev_gate:
        if rev_gate.status == "failed" and rev_gate.required:
            if rev_gate.failure_reason and "unavailable" in rev_gate.failure_reason.lower():
                return "BLOCKED_REVIEWER_UNAVAILABLE"
            return "BLOCKED_REVIEWER_FAILED"

    # Partitioned verdict: check if ALL or PARTIAL examples passed
    partial_runtime = (run_passed > 0 and run_passed < build_passed)

    if all_required_passed and gen_mode == "llm" and build_passed > 0 and run_passed > 0:
        if partial_runtime:
            if ctx.dry_run:
                return "PARTIAL_PR_DRY_RUN_READY"
            return "PARTIAL_PR_READY"
        if not ctx.dry_run:
            return "FULL_E2E_PASSED"
        return "PR_DRY_RUN_READY"

    if all_required_passed and ctx.dry_run:
        if partial_runtime:
            return "PARTIAL_PR_DRY_RUN_READY"
        return "PR_DRY_RUN_READY"

    if all_required_passed and not ctx.dry_run:
        if partial_runtime:
            return "PARTIAL_PR_READY"
        return "PR_READY"

    # Fallback for partial success
    return "DATA_FLOW_PROTOTYPE_ONLY"


def determine_verdict(stages: list, ctx) -> str:
    """Top-level verdict determination — replaces runner._determine_verdict().

    Args:
        stages: List of StageResult from the pipeline run.
        ctx: PipelineContext.

    Returns:
        Canonical verdict string.
    """
    gate_verdict = evaluate_gates(stages, ctx)
    return gate_verdict.verdict


def is_publishable(verdict: GateVerdict) -> bool:
    """Check if a gate verdict allows publishing."""
    return verdict.publishable


def is_publishable_verdict(verdict_str: str) -> bool:
    """Check if a verdict string allows publishing."""
    return verdict_str in ("PR_READY", "FULL_E2E_PASSED")


def _find_stage(stages: list, name: str):
    """Find a stage by name."""
    return next((s for s in stages if s.name == name), None)
