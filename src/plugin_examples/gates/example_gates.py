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
    code_contract_validation_status: str = "not_evaluated"  # advisory — never blocks
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


def _get_contract_output_kind(project_dir: str, scenario_id: str) -> str:
    """Get contract output_kind from manifest or store (returns 'file' as default)."""
    import json as _json_inner
    manifest_path = Path(project_dir) / "example.manifest.json"
    if manifest_path.exists():
        try:
            manifest = _json_inner.loads(manifest_path.read_text(encoding="utf-8"))
            kind = manifest.get("contract_output_kind", "")
            if kind:
                return kind
        except Exception:
            pass
    # Fallback: infer from scenario_id
    sid_lower = scenario_id.lower()
    if "textextractor" in sid_lower or "text-extractor" in sid_lower:
        return "stdout"
    return "file"


def _advisory_output_validation(project_dir: str, scenario_id: str) -> str:
    """Check output files in advisory mode (never blocks).

    Returns one of: advisory_passed, advisory_failed, advisory_no_output,
    advisory_not_applicable, or passed (fallback).
    Uses FormatContract output_kind from manifest when available.
    """
    project_path = Path(project_dir)
    if not project_path.is_dir():
        return "passed"

    # Get contract output kind — contract-first, fallback to heuristic
    output_kind = _get_contract_output_kind(project_dir, scenario_id)

    # stdout types produce no output file
    if output_kind == "stdout":
        return "advisory_not_applicable"

    # directory types produce an output directory
    if output_kind == "directory":
        output_dirs = [
            d for d in project_path.iterdir()
            if d.is_dir() and d.name.startswith("output")
        ]
        if output_dirs:
            return "advisory_passed"
        return "advisory_no_output"

    # file, collection, generated_sequence types — look for output files
    output_files = (
        list(project_path.glob("output.*"))
        + list(project_path.glob("output_*.*"))
        + list(project_path.glob("result.*"))
        + list(project_path.glob("report.*"))
    )

    if not output_files:
        return "advisory_no_output"

    # Try semantic validation if available
    try:
        from plugin_examples.verifier_bridge.output_validator import (
            validate_output_file_semantic,
        )
        for out_file in output_files:
            result = validate_output_file_semantic(out_file)
            if not result.get("valid", True):
                logger.warning(
                    "Advisory output validation failed for %s: %s",
                    out_file, result.get("reason", "unknown"),
                )
                return "advisory_failed"
        return "advisory_passed"
    except (ImportError, Exception) as exc:
        logger.debug("Advisory output validation skipped: %s", exc)
        return "passed"


def _advisory_code_contract_validation(project_dir: str, scenario_id: str) -> str:
    """Validate generated Program.cs against FormatContract in advisory mode (never blocks).

    Returns one of: advisory_passed, advisory_failed, advisory_no_code,
    advisory_no_contract, or not_evaluated.
    """
    from pathlib import Path as _Path
    project_path = _Path(project_dir)
    program_cs = project_path / "Program.cs"

    if not program_cs.exists():
        return "advisory_no_code"

    # Load contract from manifest if available
    manifest_path = project_path / "example.manifest.json"
    contract_dict: dict = {}
    if manifest_path.exists():
        try:
            import json as _json
            manifest = _json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("contract_id"):
                contract_dict = {
                    "canonical_output_format": manifest.get("contract_output_format", ""),
                    "input_format": manifest.get("contract_input_format", ""),
                    "output_kind": manifest.get("contract_output_kind", "file"),
                    "output_cardinality": manifest.get("contract_output_cardinality", "single"),
                    "operation_kind": manifest.get("contract_operation_kind", ""),
                    "contract_id": manifest.get("contract_id", ""),
                }
        except Exception:
            pass

    if not contract_dict:
        # Fall back to store lookup by scenario_id
        try:
            parts = scenario_id.split("-", 1) if scenario_id else []
            if len(parts) >= 2:
                _fam = parts[0]
                _slug = parts[1]
                _type_guess = "".join(p.capitalize() for p in _slug.split("-"))
                from plugin_examples.format_authority.store import get_contract
                fc = get_contract(_fam, _type_guess)
                contract_dict = fc.to_dict()
        except Exception:
            return "advisory_no_contract"

    try:
        code = program_cs.read_text(encoding="utf-8")
        from plugin_examples.gates.code_contract_validator import validate_code_against_contract
        result = validate_code_against_contract(code, contract_dict)
        if result.valid:
            return "advisory_passed"
        failed = [c["check"] for c in result.checks if not c["passed"]]
        logger.warning(
            "Advisory contract validation failed for %s: %s",
            scenario_id, failed,
        )
        return "advisory_failed"
    except Exception as exc:
        logger.debug("Advisory code contract validation skipped: %s", exc)
        return "not_evaluated"


def evaluate_example_gates(
    validation_results: list,
    generated_projects: list[dict],
    runtime_classifications: list | None = None,
    reviewer_available: bool = False,
    reviewer_passed: bool = False,
    skip_run: bool = False,
    contract_blocking_mode: bool = True,
) -> list[ExampleGateResult]:
    """Evaluate gates for each individual example.

    Args:
        validation_results: List of ValidationResult from dotnet_runner.
        generated_projects: List of generated project dicts.
        runtime_classifications: Optional runtime failure classifications.
        reviewer_available: Whether reviewer is available.
        reviewer_passed: Whether reviewer passed.
        skip_run: Whether runtime was skipped.
        contract_blocking_mode: When True (default), advisory_failed contract/output
            validation blocks PR_DRY_RUN_READY. Set to False for legacy advisory mode.

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

        # Output validation (advisory or blocking depending on mode)
        eg.output_validation_status = _advisory_output_validation(epath, sid)

        # Code contract validation (advisory or blocking depending on mode)
        eg.code_contract_validation_status = _advisory_code_contract_validation(epath, sid)

        # Contract blocking gate (promotes advisory → blocking when contract_blocking_mode=True)
        if contract_blocking_mode:
            if eg.code_contract_validation_status == "advisory_failed":
                eg.final_example_verdict = "EXAMPLE_BLOCKED_CODE_CONTRACT_FAILED"
                eg.blocked_reason = "Code contract validation failed (blocking mode)"
                results.append(eg)
                continue
            if eg.output_validation_status == "advisory_failed":
                eg.final_example_verdict = "EXAMPLE_BLOCKED_OUTPUT_CONTRACT_FAILED"
                eg.blocked_reason = "Output contract validation failed (blocking mode)"
                results.append(eg)
                continue

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


def _compute_manifest_counts(included: list[dict], excluded: list[dict]) -> dict:
    """Compute safe candidate counts with integrity breakdown.

    publishable_candidate_count is SAFE: it equals live_publishable_count, which
    counts only current_run and replay_validated candidates. Prior-run preserved
    candidates are included in the manifest but are NOT live-publishable without
    a replay or current-run pass — they are tracked separately.
    """
    current_run = [
        e for e in included
        if e.get("candidate_integrity_status", "current_run") == "current_run"
    ]
    replay_validated = [
        e for e in included
        if e.get("candidate_integrity_status") == "replay_validated"
    ]
    prior_run_preserved = [
        e for e in included
        if e.get("candidate_integrity_status") in (
            "prior_run_preserved_not_reattempted",
            "prior_run_preserved_regression_protected",
        )
    ]
    quarantined = [
        e for e in excluded
        if e.get("candidate_integrity_status") == "demoted_quarantined"
    ]
    live_publishable = current_run + replay_validated
    return {
        "included_manifest_candidate_count": len(included),
        "current_run_pr_eligible_count": len(current_run),
        "replay_validated_pr_eligible_count": len(replay_validated),
        "prior_run_preserved_count": len(prior_run_preserved),
        "replay_required_count": len(prior_run_preserved),
        "quarantined_count": len(quarantined),
        "live_publishable_count": len(live_publishable),
        "approval_blocked_count": len(live_publishable),
        # SAFE: publishable_candidate_count = live-publishable only (current_run + replay_validated)
        # Prior-run preserved candidates do NOT count as publishable.
        "publishable_candidate_count": len(live_publishable),
        "blocked_candidate_count": len(excluded),
    }


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

    # In the initial build all included examples are current_run by definition
    counts = _compute_manifest_counts(included, excluded)
    return {
        "included_examples": included,
        "excluded_examples": excluded,
        "exclusion_reasons": exclusion_reasons,
        "dry_run": dry_run,
        "live_publish_attempted": not dry_run,
        **counts,
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


def merge_pr_candidate_manifests(
    existing: dict,
    new_manifest: dict,
    demoted_scenario_ids: set[str] | None = None,
) -> dict:
    """Merge a new run's PR candidate manifest into an existing one.

    Merge strategy:
    - New run's PASSES always overwrite their scenario's entry (upgrade),
      and also clear any prior quarantine for that scenario.
    - Old pass entries are PRESERVED for scenarios absent from the new run
      (scenarios not re-attempted are not demoted).
    - New run's FAILURES only overwrite if the scenario was NOT previously passing.
    - Demoted scenarios (in demoted_scenario_ids) are ALWAYS quarantined regardless
      of prior passing state — a demotion in the latest run supersedes any old pass.
    - PERSISTED QUARANTINES: scenarios already marked demoted_quarantined in the
      existing manifest (excluded_examples) remain quarantined in future runs
      even when the current run does not explicitly demote them.  Only a new
      current_run PASS can clear a persisted quarantine.

    The demoted_scenario_ids set should be populated from scenario_feedback_updates.json
    for the current run.  Any scenario explicitly demoted (e.g. blocked_missing_fixture)
    must not appear as a PR candidate even if it passed in an older run.
    """
    _demoted: set[str] = set(demoted_scenario_ids or set())

    # Accumulate persisted quarantines from the prior manifest's excluded_examples.
    # These are scenarios previously quarantined (demoted_quarantined) and stored in
    # excluded_examples of the existing manifest.  They remain quarantined in this
    # merge UNLESS the current run produces a current_run PASS for them (which clears
    # the quarantine).  Unlike _demoted (current-run demotion), a current-run pass
    # CAN override _prior_quarantined.
    _prior_quarantined: set[str] = set()
    _prior_quarantined_entries: dict[str, dict] = {}
    for e in existing.get("excluded_examples", []):
        if e.get("candidate_integrity_status") == "demoted_quarantined":
            sid = e["scenario_id"]
            _prior_quarantined.add(sid)
            _prior_quarantined_entries[sid] = e

    existing_included = {
        e["scenario_id"]: e
        for e in existing.get("included_examples", [])
    }

    new_included = {
        e["scenario_id"]: e
        for e in new_manifest.get("included_examples", [])
    }

    # All scenario_ids attempted in the new run (pass or fail)
    new_run_attempted = set(
        e["scenario_id"] for e in new_manifest.get("included_examples", [])
    ) | set(
        e["scenario_id"] for e in new_manifest.get("excluded_examples", [])
    )

    # Start with new passes — annotate as current-run candidates.
    # current_run PASS clears prior quarantine (_prior_quarantined), but
    # current-run DEMOTION (_demoted) blocks even a new pass.
    merged_included: dict[str, dict] = {}
    for sid, entry in new_included.items():
        if sid in _demoted:
            continue  # Current-run demotion wins over a new pass — keep quarantined
        merged_included[sid] = {**entry, "candidate_integrity_status": "current_run"}

    # Preserve old passes for scenarios NOT attempted (or not re-passed) in new run.
    # Both current-run demotions and persisted prior-run quarantines block preservation.
    _all_blocked = _demoted | (_prior_quarantined - set(merged_included.keys()))
    for sid, entry in existing_included.items():
        if sid in _all_blocked:
            continue  # Quarantined — do not preserve
        if sid not in new_run_attempted:
            # Not re-attempted — preserve prior passing state
            merged_included[sid] = {**entry, "candidate_integrity_status": "prior_run_preserved_not_reattempted"}
        elif sid not in merged_included:
            # Re-attempted but failed in new run and NOT demoted — PRESERVE old pass
            # (regression protection for probabilistic failures)
            merged_included[sid] = {**entry, "candidate_integrity_status": "prior_run_preserved_regression_protected"}

    # Excluded = new run's excluded entries whose scenarios aren't in merged_included
    # Also add demoted scenarios that were in existing as quarantined excluded entries
    merged_excluded = [
        e for e in new_manifest.get("excluded_examples", [])
        if e["scenario_id"] not in merged_included
    ]
    # Add quarantined demoted scenarios from prior runs (existing_included entries demoted now)
    for sid in _demoted:
        if sid in existing_included and sid not in merged_included:
            entry = existing_included[sid]
            merged_excluded.append({
                **entry,
                "final_example_verdict": "EXAMPLE_BLOCKED_DEMOTED_IN_LATEST_RUN",
                "blocked_reason": "Scenario was demoted in scenario_feedback_updates for the latest run",
                "candidate_integrity_status": "demoted_quarantined",
            })
    # Carry forward persisted quarantines not cleared by a current_run pass
    already_in_excluded_ids = {e["scenario_id"] for e in merged_excluded}
    for sid, entry in _prior_quarantined_entries.items():
        if sid not in merged_included and sid not in already_in_excluded_ids:
            merged_excluded.append({
                **entry,
                "candidate_integrity_status": "demoted_quarantined",
            })

    exclusion_reasons: dict[str, list[str]] = {}
    for e in merged_excluded:
        reason = e.get("final_example_verdict", "unknown")
        exclusion_reasons.setdefault(reason, []).append(e["scenario_id"])

    included_list = list(merged_included.values())
    counts = _compute_manifest_counts(included_list, merged_excluded)
    return {
        "included_examples": included_list,
        "excluded_examples": merged_excluded,
        "exclusion_reasons": exclusion_reasons,
        "dry_run": new_manifest.get("dry_run", True),
        "live_publish_attempted": new_manifest.get("live_publish_attempted", False),
        **counts,
    }


def write_pr_candidate_manifest(
    manifest: dict,
    verification_dir: Path,
    merge_existing: bool = True,
    prior_manifest_path: Path | None = None,
    scenario_feedback: dict | None = None,
) -> Path:
    """Write PR candidate manifest.

    When merge_existing=True (default), reads any existing manifest and merges
    using merge_pr_candidate_manifests() — preserving previously-passing candidates
    that were not re-attempted or regressed in the current run.

    The merge looks up the prior manifest from (in order):
    1. verification_dir / "latest" / "pr-candidate-manifest.json" (run-local evidence)
    2. prior_manifest_path (e.g. the global workspace/verification/latest/ path)

    When merge_existing=False, overwrites the existing manifest (legacy behavior).

    scenario_feedback: optional dict from scenario_feedback_updates.json for the current
        run.  Demoted scenarios in this dict are quarantined from the merged manifest
        regardless of prior passing state, preventing stale candidates from being included.
    """
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "pr-candidate-manifest.json"

    # Extract demoted scenario IDs from current-run feedback
    demoted_ids: set[str] = set()
    if scenario_feedback:
        for update in scenario_feedback.get("updates", []):
            new_status = update.get("new_status", "")
            if new_status.startswith("blocked") or new_status in (
                "demoted", "quarantined", "failed", "excluded"
            ):
                sid = update.get("scenario_id")
                if sid:
                    demoted_ids.add(sid)

    # Determine the prior manifest to merge from: run-local first, then global fallback
    prior_path = path if path.exists() else (prior_manifest_path if prior_manifest_path and prior_manifest_path.exists() else None)

    final_manifest = manifest
    if merge_existing and prior_path is not None:
        try:
            with open(prior_path) as f:
                existing = json.load(f)
            final_manifest = merge_pr_candidate_manifests(existing, manifest, demoted_scenario_ids=demoted_ids)
            logger.info(
                "PR candidate manifest merged from %s: %d included (%d current_run, %d prior_run_preserved, %d demoted/quarantined)",
                prior_path,
                final_manifest.get("included_manifest_candidate_count", len(final_manifest.get("included_examples", []))),
                final_manifest.get("current_run_pr_eligible_count", 0),
                final_manifest.get("prior_run_preserved_count", 0),
                len(demoted_ids),
            )
        except (json.JSONDecodeError, OSError, KeyError) as exc:
            logger.warning("Failed to merge existing manifest (overwriting): %s", exc)
            final_manifest = manifest

    with open(path, "w") as f:
        json.dump(final_manifest, f, indent=2)

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
