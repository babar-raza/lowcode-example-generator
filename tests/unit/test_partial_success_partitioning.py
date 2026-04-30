"""Tests for the Partial Success and Publish Candidate Partitioning Sprint.

Covers: per-example gates, aggregate gates, partitioned verdicts,
PR candidate manifests, scenario feedback, and publisher safety.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from plugin_examples.gates.example_gates import (
    ExampleGateResult,
    AggregateGateResult,
    evaluate_example_gates,
    compute_aggregate_gates,
    compute_partitioned_verdict,
    build_pr_candidate_manifest,
    build_scenario_feedback,
    write_example_gate_results,
    write_aggregate_gate_results,
    write_pr_candidate_manifest,
    write_scenario_feedback,
)


# --- Helpers ---

@dataclass
class _MockDotnetResult:
    operation: str
    success: bool
    exit_code: int = 0
    stdout: str = ""
    stderr: str = ""
    duration_ms: float = 100.0


@dataclass
class _MockValidationResult:
    scenario_id: str
    restore: _MockDotnetResult | None = None
    build: _MockDotnetResult | None = None
    run: _MockDotnetResult | None = None
    passed: bool = False
    failure_stage: str | None = None


@dataclass
class _MockRuntimeClassification:
    scenario_id: str
    exit_code: int = 1
    classification: str = "unknown_runtime_failure"
    detail: str = ""
    actionable: bool = False
    recommendation: str = ""


@dataclass
class _MockCtx:
    dry_run: bool = True
    skip_run: bool = False
    template_mode: bool = False


def _make_passed_vr(sid: str) -> _MockValidationResult:
    return _MockValidationResult(
        scenario_id=sid,
        restore=_MockDotnetResult("restore", True),
        build=_MockDotnetResult("build", True),
        run=_MockDotnetResult("run", True, exit_code=0),
        passed=True,
    )


def _make_build_passed_run_failed_vr(sid: str) -> _MockValidationResult:
    return _MockValidationResult(
        scenario_id=sid,
        restore=_MockDotnetResult("restore", True),
        build=_MockDotnetResult("build", True),
        run=_MockDotnetResult("run", False, exit_code=1,
                              stderr="System.IO.FileNotFoundException: Could not find file 'input.xlsx'"),
        passed=False,
        failure_stage="run",
    )


def _make_build_failed_vr(sid: str) -> _MockValidationResult:
    return _MockValidationResult(
        scenario_id=sid,
        restore=_MockDotnetResult("restore", True),
        build=_MockDotnetResult("build", False, exit_code=1),
        passed=False,
        failure_stage="build",
    )


def _make_projects(sids: list[str]) -> list[dict]:
    return [{"scenario_id": sid, "project_dir": f"/gen/{sid}", "program_path": f"/gen/{sid}/Program.cs"}
            for sid in sids]


# --- Test 1: Partial runtime success must not be global run pass ---

class TestPartialRuntimeSuccessNotGlobalRunPass:
    def test_partial_runtime_success_not_global_run_pass(self):
        """When 3/9 examples pass runtime, aggregate run status must be passed_partial."""
        sids = [f"ex-{i}" for i in range(9)]
        vrs = [_make_passed_vr(sid) for sid in sids[:3]]
        vrs += [_make_build_passed_run_failed_vr(sid) for sid in sids[3:]]
        rcs = [_MockRuntimeClassification(sid, classification="blocked_missing_fixture",
                                          detail="File not found")
               for sid in sids[3:]]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)
        agg = compute_aggregate_gates(eg)

        assert agg.aggregate_run_status == "passed_partial"
        assert agg.total_runtime_passed == 3
        assert agg.total_runtime_blocked == 6
        assert agg.total_pr_candidates == 3
        assert agg.total_excluded == 6


# --- Test 2: Partial success verdict ---

class TestPartialSuccessVerdict:
    def test_partial_success_verdict(self):
        """With partial runtime success, verdict must be PARTIAL_PR_DRY_RUN_READY."""
        sids = [f"ex-{i}" for i in range(9)]
        vrs = [_make_passed_vr(sid) for sid in sids[:3]]
        vrs += [_make_build_passed_run_failed_vr(sid) for sid in sids[3:]]
        rcs = [_MockRuntimeClassification(sid, classification="blocked_missing_fixture")
               for sid in sids[3:]]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)
        agg = compute_aggregate_gates(eg)
        verdict = compute_partitioned_verdict(agg, _MockCtx(dry_run=True), gen_mode="llm")

        assert verdict == "PARTIAL_PR_DRY_RUN_READY"

    def test_all_pass_gives_pr_dry_run_ready(self):
        """When ALL examples pass all gates, verdict must be PR_DRY_RUN_READY."""
        sids = [f"ex-{i}" for i in range(3)]
        vrs = [_make_passed_vr(sid) for sid in sids]

        eg = evaluate_example_gates(vrs, _make_projects(sids))
        agg = compute_aggregate_gates(eg)
        verdict = compute_partitioned_verdict(agg, _MockCtx(dry_run=True), gen_mode="llm")

        assert verdict == "PR_DRY_RUN_READY"

    def test_no_publishable_examples_blocks_pr_ready(self):
        """When no examples pass all gates, verdict must be BLOCKED_NO_PUBLISHABLE_EXAMPLES."""
        sids = [f"ex-{i}" for i in range(3)]
        vrs = [_make_build_passed_run_failed_vr(sid) for sid in sids]
        rcs = [_MockRuntimeClassification(sid, classification="blocked_missing_fixture")
               for sid in sids]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)
        agg = compute_aggregate_gates(eg)
        verdict = compute_partitioned_verdict(agg, _MockCtx(dry_run=True), gen_mode="llm")

        assert verdict == "BLOCKED_NO_PUBLISHABLE_EXAMPLES"


# --- Test 3: PR candidate manifest excludes failed runtime ---

class TestPRCandidateManifest:
    def test_pr_candidate_manifest_excludes_failed_runtime(self):
        """Failed runtime examples must not appear in included_examples."""
        sids = ["pass-1", "pass-2", "fail-1", "fail-2"]
        vrs = [_make_passed_vr("pass-1"), _make_passed_vr("pass-2"),
               _make_build_passed_run_failed_vr("fail-1"),
               _make_build_passed_run_failed_vr("fail-2")]
        rcs = [_MockRuntimeClassification("fail-1", classification="blocked_missing_fixture"),
               _MockRuntimeClassification("fail-2", classification="blocked_missing_fixture")]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)
        manifest = build_pr_candidate_manifest(eg, dry_run=True)

        included_ids = [e["scenario_id"] for e in manifest["included_examples"]]
        excluded_ids = [e["scenario_id"] for e in manifest["excluded_examples"]]

        assert "pass-1" in included_ids
        assert "pass-2" in included_ids
        assert "fail-1" in excluded_ids
        assert "fail-2" in excluded_ids
        assert manifest["publishable_candidate_count"] == 2
        assert manifest["blocked_candidate_count"] == 2
        assert manifest["dry_run"] is True


# --- Test 4: Publisher only includes examples with all gates passed ---

class TestPublisherOnlyIncludesAllGatesPassed:
    def test_publisher_only_includes_examples_with_all_gates_passed(self):
        """PR candidate manifest must have publish_candidate=true only for fully passing examples."""
        sids = ["ok-1", "fail-build", "fail-run"]
        vrs = [_make_passed_vr("ok-1"),
               _make_build_failed_vr("fail-build"),
               _make_build_passed_run_failed_vr("fail-run")]
        rcs = [_MockRuntimeClassification("fail-run", classification="blocked_missing_fixture")]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)
        manifest = build_pr_candidate_manifest(eg)

        assert manifest["publishable_candidate_count"] == 1
        assert manifest["included_examples"][0]["scenario_id"] == "ok-1"
        assert len(manifest["excluded_examples"]) == 2


# --- Test 5: Blocked examples preserved in report ---

class TestBlockedExamplesPreservedInReport:
    def test_blocked_examples_preserved_in_report(self):
        """All blocked examples must appear in example-gate-results with their reasons."""
        sids = ["ok-1", "fail-1", "fail-2"]
        vrs = [_make_passed_vr("ok-1"),
               _make_build_passed_run_failed_vr("fail-1"),
               _make_build_passed_run_failed_vr("fail-2")]
        rcs = [_MockRuntimeClassification("fail-1", classification="blocked_missing_fixture",
                                          detail="Could not find file"),
               _MockRuntimeClassification("fail-2", classification="blocked_runtime_context_required",
                                          detail="NullRef")]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)

        blocked = [e for e in eg if not e.publish_candidate]
        assert len(blocked) == 2
        verdicts = {e.final_example_verdict for e in blocked}
        assert "EXAMPLE_BLOCKED_MISSING_FIXTURE" in verdicts
        assert "EXAMPLE_BLOCKED_RUNTIME_CONTEXT_REQUIRED" in verdicts
        for e in blocked:
            assert e.blocked_reason is not None


# --- Test 6: Scenario feedback demotes missing fixture runtime failures ---

class TestScenarioFeedbackDemotesMissingFixture:
    def test_scenario_feedback_demotes_missing_fixture_runtime_failures(self):
        """Scenarios that fail runtime due to missing fixture must be demoted."""
        sids = ["ok-1", "fail-1", "fail-2"]
        vrs = [_make_passed_vr("ok-1"),
               _make_build_passed_run_failed_vr("fail-1"),
               _make_build_passed_run_failed_vr("fail-2")]
        rcs = [_MockRuntimeClassification("fail-1", classification="blocked_missing_fixture"),
               _MockRuntimeClassification("fail-2", classification="blocked_missing_fixture")]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)
        feedback = build_scenario_feedback(eg)

        assert feedback["total_feedback_updates"] == 2
        assert feedback["demoted_scenarios"] == 2
        for u in feedback["updates"]:
            assert u["new_status"] == "blocked_missing_fixture"
            assert u["previous_status"] == "ready"
            assert u["preserve_failed_attempt"] is True


# --- Test 7: All pass required for full PR_DRY_RUN_READY ---

class TestAllPassRequiredForFullPRDryRunReady:
    def test_all_pass_required_for_full_pr_dry_run_ready(self):
        """PR_DRY_RUN_READY requires ALL examples pass all gates."""
        # All pass → PR_DRY_RUN_READY
        sids = [f"ex-{i}" for i in range(5)]
        vrs = [_make_passed_vr(sid) for sid in sids]
        eg = evaluate_example_gates(vrs, _make_projects(sids))
        agg = compute_aggregate_gates(eg)
        assert compute_partitioned_verdict(agg, _MockCtx(dry_run=True), "llm") == "PR_DRY_RUN_READY"

        # One fails → PARTIAL_PR_DRY_RUN_READY
        vrs_mixed = [_make_passed_vr(sid) for sid in sids[:4]]
        vrs_mixed.append(_make_build_passed_run_failed_vr(sids[4]))
        rcs = [_MockRuntimeClassification(sids[4], classification="blocked_missing_fixture")]
        eg2 = evaluate_example_gates(vrs_mixed, _make_projects(sids),
                                     runtime_classifications=rcs)
        agg2 = compute_aggregate_gates(eg2)
        assert compute_partitioned_verdict(agg2, _MockCtx(dry_run=True), "llm") == "PARTIAL_PR_DRY_RUN_READY"


# --- Test 8: No publishable examples blocks PR ready ---

class TestNoPublishableExamplesBlocksPRReady:
    def test_no_publishable_examples_blocks_pr_ready(self):
        """If all examples fail runtime, verdict must be BLOCKED_NO_PUBLISHABLE_EXAMPLES."""
        sids = [f"ex-{i}" for i in range(3)]
        vrs = [_make_build_passed_run_failed_vr(sid) for sid in sids]
        rcs = [_MockRuntimeClassification(sid, classification="blocked_missing_fixture")
               for sid in sids]

        eg = evaluate_example_gates(vrs, _make_projects(sids),
                                    runtime_classifications=rcs)
        agg = compute_aggregate_gates(eg)
        verdict = compute_partitioned_verdict(agg, _MockCtx(dry_run=True), "llm")

        assert verdict == "BLOCKED_NO_PUBLISHABLE_EXAMPLES"
        assert agg.total_pr_candidates == 0


# --- Evidence file writing tests ---

class TestEvidenceWriters:
    def test_write_example_gate_results(self, tmp_path):
        eg = [ExampleGateResult(scenario_id="s1", example_path="/p",
                                publish_candidate=True,
                                final_example_verdict="EXAMPLE_READY_FOR_PR_DRY_RUN")]
        path = write_example_gate_results(eg, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["total_examples"] == 1
        assert data["publish_candidates"] == 1

    def test_write_aggregate_gate_results(self, tmp_path):
        agg = AggregateGateResult(total_generated=9, total_built=9,
                                  total_runtime_passed=3, total_runtime_blocked=6,
                                  total_pr_candidates=3, total_excluded=6,
                                  aggregate_run_status="passed_partial")
        path = write_aggregate_gate_results(agg, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["aggregate_run_status"] == "passed_partial"

    def test_write_pr_candidate_manifest(self, tmp_path):
        manifest = {"included_examples": [], "excluded_examples": [],
                     "exclusion_reasons": {}, "dry_run": True,
                     "live_publish_attempted": False,
                     "publishable_candidate_count": 0,
                     "blocked_candidate_count": 0}
        path = write_pr_candidate_manifest(manifest, tmp_path)
        assert path.exists()

    def test_write_scenario_feedback(self, tmp_path):
        feedback = {"total_feedback_updates": 0, "demoted_scenarios": 0, "updates": []}
        path = write_scenario_feedback(feedback, tmp_path)
        assert path.exists()


# --- Self-generated input strategy tests ---

class TestSelfGeneratedStrategy:
    def test_self_generated_strategy_requires_input_creation_code(self):
        """A self-generated input scenario that doesn't actually create a file
        should fail runtime with blocked_missing_fixture."""
        # This is verified by the runtime failure classification:
        # if the generated code doesn't create a valid input file, the process
        # exits with FileNotFoundException → classified as blocked_missing_fixture
        rc = _MockRuntimeClassification(
            "s1", classification="blocked_missing_fixture",
            detail="Could not find file 'input.xlsx'")
        vr = _make_build_passed_run_failed_vr("s1")

        eg = evaluate_example_gates([vr], _make_projects(["s1"]),
                                    runtime_classifications=[rc])
        assert eg[0].final_example_verdict == "EXAMPLE_BLOCKED_MISSING_FIXTURE"
        assert not eg[0].publish_candidate

    def test_runtime_missing_input_demotes_ready_scenario(self):
        """Runtime missing input must demote scenario from ready to blocked."""
        vr = _make_build_passed_run_failed_vr("s1")
        rc = _MockRuntimeClassification("s1", classification="blocked_missing_fixture")
        eg = evaluate_example_gates([vr], _make_projects(["s1"]),
                                    runtime_classifications=[rc])
        feedback = build_scenario_feedback(eg)
        assert feedback["demoted_scenarios"] == 1
        assert feedback["updates"][0]["new_status"] == "blocked_missing_fixture"

    def test_blocked_missing_fixture_excluded_from_pr_candidates(self):
        """Blocked missing fixture examples must not be PR candidates."""
        vrs = [_make_passed_vr("ok"), _make_build_passed_run_failed_vr("fail")]
        rcs = [_MockRuntimeClassification("fail", classification="blocked_missing_fixture")]
        eg = evaluate_example_gates(vrs, _make_projects(["ok", "fail"]),
                                    runtime_classifications=rcs)
        manifest = build_pr_candidate_manifest(eg)
        assert manifest["publishable_candidate_count"] == 1
        assert manifest["blocked_candidate_count"] == 1
        assert manifest["excluded_examples"][0]["scenario_id"] == "fail"
