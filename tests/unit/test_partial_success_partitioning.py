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
    merge_pr_candidate_manifests,
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
        run=_MockDotnetResult(
            "run", False, exit_code=1, stderr="System.IO.FileNotFoundException: Could not find file 'input.xlsx'"
        ),
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
    return [
        {"scenario_id": sid, "project_dir": f"/gen/{sid}", "program_path": f"/gen/{sid}/Program.cs"} for sid in sids
    ]


# --- Test 1: Partial runtime success must not be global run pass ---


class TestPartialRuntimeSuccessNotGlobalRunPass:
    def test_partial_runtime_success_not_global_run_pass(self):
        """When 3/9 examples pass runtime, aggregate run status must be passed_partial."""
        sids = [f"ex-{i}" for i in range(9)]
        vrs = [_make_passed_vr(sid) for sid in sids[:3]]
        vrs += [_make_build_passed_run_failed_vr(sid) for sid in sids[3:]]
        rcs = [
            _MockRuntimeClassification(sid, classification="blocked_missing_fixture", detail="File not found")
            for sid in sids[3:]
        ]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)
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
        rcs = [_MockRuntimeClassification(sid, classification="blocked_missing_fixture") for sid in sids[3:]]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)
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
        rcs = [_MockRuntimeClassification(sid, classification="blocked_missing_fixture") for sid in sids]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)
        agg = compute_aggregate_gates(eg)
        verdict = compute_partitioned_verdict(agg, _MockCtx(dry_run=True), gen_mode="llm")

        assert verdict == "BLOCKED_NO_PUBLISHABLE_EXAMPLES"


# --- Test 3: PR candidate manifest excludes failed runtime ---


class TestPRCandidateManifest:
    def test_pr_candidate_manifest_excludes_failed_runtime(self):
        """Failed runtime examples must not appear in included_examples."""
        sids = ["pass-1", "pass-2", "fail-1", "fail-2"]
        vrs = [
            _make_passed_vr("pass-1"),
            _make_passed_vr("pass-2"),
            _make_build_passed_run_failed_vr("fail-1"),
            _make_build_passed_run_failed_vr("fail-2"),
        ]
        rcs = [
            _MockRuntimeClassification("fail-1", classification="blocked_missing_fixture"),
            _MockRuntimeClassification("fail-2", classification="blocked_missing_fixture"),
        ]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)
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
        vrs = [
            _make_passed_vr("ok-1"),
            _make_build_failed_vr("fail-build"),
            _make_build_passed_run_failed_vr("fail-run"),
        ]
        rcs = [_MockRuntimeClassification("fail-run", classification="blocked_missing_fixture")]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)
        manifest = build_pr_candidate_manifest(eg)

        assert manifest["publishable_candidate_count"] == 1
        assert manifest["included_examples"][0]["scenario_id"] == "ok-1"
        assert len(manifest["excluded_examples"]) == 2


# --- Test 5: Blocked examples preserved in report ---


class TestBlockedExamplesPreservedInReport:
    def test_blocked_examples_preserved_in_report(self):
        """All blocked examples must appear in example-gate-results with their reasons."""
        sids = ["ok-1", "fail-1", "fail-2"]
        vrs = [
            _make_passed_vr("ok-1"),
            _make_build_passed_run_failed_vr("fail-1"),
            _make_build_passed_run_failed_vr("fail-2"),
        ]
        rcs = [
            _MockRuntimeClassification(
                "fail-1", classification="blocked_missing_fixture", detail="Could not find file"
            ),
            _MockRuntimeClassification("fail-2", classification="blocked_runtime_context_required", detail="NullRef"),
        ]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)

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
        vrs = [
            _make_passed_vr("ok-1"),
            _make_build_passed_run_failed_vr("fail-1"),
            _make_build_passed_run_failed_vr("fail-2"),
        ]
        rcs = [
            _MockRuntimeClassification("fail-1", classification="blocked_missing_fixture"),
            _MockRuntimeClassification("fail-2", classification="blocked_missing_fixture"),
        ]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)
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
        eg2 = evaluate_example_gates(vrs_mixed, _make_projects(sids), runtime_classifications=rcs)
        agg2 = compute_aggregate_gates(eg2)
        assert compute_partitioned_verdict(agg2, _MockCtx(dry_run=True), "llm") == "PARTIAL_PR_DRY_RUN_READY"


# --- Test 8: No publishable examples blocks PR ready ---


class TestNoPublishableExamplesBlocksPRReady:
    def test_no_publishable_examples_blocks_pr_ready(self):
        """If all examples fail runtime, verdict must be BLOCKED_NO_PUBLISHABLE_EXAMPLES."""
        sids = [f"ex-{i}" for i in range(3)]
        vrs = [_make_build_passed_run_failed_vr(sid) for sid in sids]
        rcs = [_MockRuntimeClassification(sid, classification="blocked_missing_fixture") for sid in sids]

        eg = evaluate_example_gates(vrs, _make_projects(sids), runtime_classifications=rcs)
        agg = compute_aggregate_gates(eg)
        verdict = compute_partitioned_verdict(agg, _MockCtx(dry_run=True), "llm")

        assert verdict == "BLOCKED_NO_PUBLISHABLE_EXAMPLES"
        assert agg.total_pr_candidates == 0


# --- Evidence file writing tests ---


class TestEvidenceWriters:
    def test_write_example_gate_results(self, tmp_path):
        eg = [
            ExampleGateResult(
                scenario_id="s1",
                example_path="/p",
                publish_candidate=True,
                final_example_verdict="EXAMPLE_READY_FOR_PR_DRY_RUN",
            )
        ]
        path = write_example_gate_results(eg, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["total_examples"] == 1
        assert data["publish_candidates"] == 1

    def test_write_aggregate_gate_results(self, tmp_path):
        agg = AggregateGateResult(
            total_generated=9,
            total_built=9,
            total_runtime_passed=3,
            total_runtime_blocked=6,
            total_pr_candidates=3,
            total_excluded=6,
            aggregate_run_status="passed_partial",
        )
        path = write_aggregate_gate_results(agg, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["aggregate_run_status"] == "passed_partial"

    def test_write_pr_candidate_manifest(self, tmp_path):
        manifest = {
            "included_examples": [],
            "excluded_examples": [],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 0,
            "blocked_candidate_count": 0,
        }
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
            "s1", classification="blocked_missing_fixture", detail="Could not find file 'input.xlsx'"
        )
        vr = _make_build_passed_run_failed_vr("s1")

        eg = evaluate_example_gates([vr], _make_projects(["s1"]), runtime_classifications=[rc])
        assert eg[0].final_example_verdict == "EXAMPLE_BLOCKED_MISSING_FIXTURE"
        assert not eg[0].publish_candidate

    def test_runtime_missing_input_demotes_ready_scenario(self):
        """Runtime missing input must demote scenario from ready to blocked."""
        vr = _make_build_passed_run_failed_vr("s1")
        rc = _MockRuntimeClassification("s1", classification="blocked_missing_fixture")
        eg = evaluate_example_gates([vr], _make_projects(["s1"]), runtime_classifications=[rc])
        feedback = build_scenario_feedback(eg)
        assert feedback["demoted_scenarios"] == 1
        assert feedback["updates"][0]["new_status"] == "blocked_missing_fixture"

    def test_blocked_missing_fixture_excluded_from_pr_candidates(self):
        """Blocked missing fixture examples must not be PR candidates."""
        vrs = [_make_passed_vr("ok"), _make_build_passed_run_failed_vr("fail")]
        rcs = [_MockRuntimeClassification("fail", classification="blocked_missing_fixture")]
        eg = evaluate_example_gates(vrs, _make_projects(["ok", "fail"]), runtime_classifications=rcs)
        manifest = build_pr_candidate_manifest(eg)
        assert manifest["publishable_candidate_count"] == 1
        assert manifest["blocked_candidate_count"] == 1
        assert manifest["excluded_examples"][0]["scenario_id"] == "fail"


# --- Manifest merge tests (Sprint 8: cross-run candidate preservation) ---


def _make_manifest(included_ids: list[str], excluded_ids: list[str]) -> dict:
    """Build a minimal manifest dict for merge tests."""
    included = [
        {"scenario_id": s, "example_path": f"/path/{s}", "final_example_verdict": "EXAMPLE_READY_FOR_PR_DRY_RUN"}
        for s in included_ids
    ]
    excluded = [
        {
            "scenario_id": s,
            "example_path": f"/path/{s}",
            "final_example_verdict": "EXAMPLE_BLOCKED_BUILD_FAILED",
            "blocked_reason": "build failed",
        }
        for s in excluded_ids
    ]
    return {
        "included_examples": included,
        "excluded_examples": excluded,
        "exclusion_reasons": {"EXAMPLE_BLOCKED_BUILD_FAILED": excluded_ids} if excluded_ids else {},
        "dry_run": True,
        "live_publish_attempted": False,
        "publishable_candidate_count": len(included),
        "blocked_candidate_count": len(excluded),
    }


class TestMergePrCandidateManifests:
    def test_preserves_old_passes_not_in_new_run(self):
        """Scenarios not re-attempted in the new run keep their old pass state."""
        old = _make_manifest(["xls-converter", "doc-converter"], [])
        new = _make_manifest(["html"], [])  # xls-converter not re-attempted
        merged = merge_pr_candidate_manifests(old, new)
        ids = {e["scenario_id"] for e in merged["included_examples"]}
        assert "xls-converter" in ids, "xls-converter (not re-attempted) must be preserved"
        assert "doc-converter" in ids, "doc-converter (not re-attempted) must be preserved"
        assert "html" in ids, "html (new pass) must be in merged"
        # included_manifest_candidate_count = all 3 included (current_run + prior_run_preserved)
        assert merged["included_manifest_candidate_count"] == 3
        # prior_run_preserved: xls-converter + doc-converter (not reattempted)
        assert merged["prior_run_preserved_count"] == 2
        # publishable_candidate_count = SAFE = only current_run (html)
        assert (
            merged["publishable_candidate_count"] == 1
        ), "publishable_candidate_count must only count current_run candidates, not prior_run_preserved"

    def test_preserves_old_pass_when_new_run_fails_same_scenario(self):
        """When a new run re-attempts a scenario and FAILS, the old pass is preserved (no regression demotion)."""
        old = _make_manifest(["xls-converter"], [])
        new = _make_manifest([], ["xls-converter"])  # xls-converter failed in new run
        merged = merge_pr_candidate_manifests(old, new)
        ids = {e["scenario_id"] for e in merged["included_examples"]}
        assert "xls-converter" in ids, "xls-converter pass must survive new-run regression"
        # xls-converter is regression_protected (prior_run_preserved) — NOT live-publishable
        assert merged["included_manifest_candidate_count"] == 1
        assert merged["prior_run_preserved_count"] == 1
        assert (
            merged["publishable_candidate_count"] == 0
        ), "regression_protected prior_run candidate must not count as publishable"

    def test_new_pass_upgrades_old_pass(self):
        """A new pass for a scenario always replaces the old pass entry."""
        old_entry = {
            "scenario_id": "doc",
            "example_path": "/old/path",
            "final_example_verdict": "EXAMPLE_READY_FOR_PR_DRY_RUN",
        }
        new_entry = {
            "scenario_id": "doc",
            "example_path": "/new/path",
            "final_example_verdict": "EXAMPLE_READY_FOR_PR_DRY_RUN",
        }
        old = {
            "included_examples": [old_entry],
            "excluded_examples": [],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 0,
        }
        new = {
            "included_examples": [new_entry],
            "excluded_examples": [],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 1,
            "blocked_candidate_count": 0,
        }
        merged = merge_pr_candidate_manifests(old, new)
        included = {e["scenario_id"]: e for e in merged["included_examples"]}
        assert included["doc"]["example_path"] == "/new/path", "new pass must overwrite old pass path"

    def test_new_pass_not_in_old_adds_to_included(self):
        """A brand-new pass scenario gets added to included_examples."""
        old = _make_manifest(["a"], [])
        new = _make_manifest(["a", "b"], [])
        merged = merge_pr_candidate_manifests(old, new)
        ids = {e["scenario_id"] for e in merged["included_examples"]}
        assert "a" in ids and "b" in ids
        assert merged["publishable_candidate_count"] == 2

    def test_excluded_only_shows_non_previously_passing(self):
        """Excluded list only contains scenarios that weren't passing before."""
        old = _make_manifest(["good"], [])
        new = _make_manifest([], ["good", "bad"])  # good regressed, bad is new failure
        merged = merge_pr_candidate_manifests(old, new)
        excluded_ids = {e["scenario_id"] for e in merged["excluded_examples"]}
        assert "good" not in excluded_ids, "previously-passing good must not appear in excluded"
        assert "bad" in excluded_ids, "newly-failed bad must appear in excluded"

    def test_write_manifest_merges_on_second_write(self, tmp_path):
        """write_pr_candidate_manifest with merge_existing=True merges on second write."""
        m1 = _make_manifest(["xls-converter"], [])
        write_pr_candidate_manifest(m1, tmp_path, merge_existing=False)
        m2 = _make_manifest(["html"], ["xls-converter"])  # xls-converter fails in run 2
        write_pr_candidate_manifest(m2, tmp_path, merge_existing=True)
        saved = json.loads((tmp_path / "latest" / "pr-candidate-manifest.json").read_text())
        ids = {e["scenario_id"] for e in saved["included_examples"]}
        assert "xls-converter" in ids, "xls-converter must survive run-2 regression via merge"
        assert "html" in ids, "html must be in merged manifest"
        assert saved["included_manifest_candidate_count"] == 2
        assert saved["prior_run_preserved_count"] == 1, "xls-converter is regression_protected"
        assert saved["publishable_candidate_count"] == 1, "only html (current_run) is live-publishable"

    def test_write_manifest_overwrite_when_merge_false(self, tmp_path):
        """write_pr_candidate_manifest with merge_existing=False overwrites (legacy behavior)."""
        m1 = _make_manifest(["xls-converter"], [])
        write_pr_candidate_manifest(m1, tmp_path, merge_existing=False)
        m2 = _make_manifest(["html"], [])
        write_pr_candidate_manifest(m2, tmp_path, merge_existing=False)
        saved = json.loads((tmp_path / "latest" / "pr-candidate-manifest.json").read_text())
        ids = {e["scenario_id"] for e in saved["included_examples"]}
        assert "xls-converter" not in ids, "overwrite must drop xls-converter"
        assert "html" in ids
        assert saved["publishable_candidate_count"] == 1

    def test_write_manifest_merges_from_global_path(self, tmp_path):
        """write_pr_candidate_manifest merges from prior_manifest_path when run-local is empty."""
        # Simulate global workspace/verification/latest/ having a prior manifest
        global_dir = tmp_path / "global"
        m_global = _make_manifest(["tiff"], [])
        write_pr_candidate_manifest(m_global, global_dir, merge_existing=False)
        global_manifest_path = global_dir / "latest" / "pr-candidate-manifest.json"

        # New run-local evidence dir (fresh, no prior manifest)
        run_dir = tmp_path / "run_local"
        m_new = _make_manifest(["merger"], ["tiff"])  # tiff fails in new run
        write_pr_candidate_manifest(m_new, run_dir, merge_existing=True, prior_manifest_path=global_manifest_path)

        saved = json.loads((run_dir / "latest" / "pr-candidate-manifest.json").read_text())
        ids = {e["scenario_id"] for e in saved["included_examples"]}
        assert "tiff" in ids, "tiff must be preserved from global manifest via Rule 3 (prior pass, new run fails)"
        assert "merger" in ids, "merger must be included from new run"
        assert saved["included_manifest_candidate_count"] == 2
        assert saved["prior_run_preserved_count"] == 1, "tiff is regression_protected prior_run"
        assert saved["publishable_candidate_count"] == 1, "only merger (current_run) is live-publishable"


# ---------------------------------------------------------------------------
# Sprint 17 Lane A — Manifest count semantics safety tests
# ---------------------------------------------------------------------------


class TestManifestCountSemantics:
    """Verify that publishable_candidate_count is SAFE (current_run only)."""

    def test_prior_run_preserved_not_counted_as_publishable(self):
        """prior_run_preserved_not_reattempted candidates are included but NOT publishable."""
        old = _make_manifest(["doc-converter"], [])
        new = _make_manifest(["merger"], [])  # doc-converter not reattempted
        merged = merge_pr_candidate_manifests(old, new)
        # doc-converter is prior_run_preserved_not_reattempted
        doc_entry = next(e for e in merged["included_examples"] if e["scenario_id"] == "doc-converter")
        assert doc_entry["candidate_integrity_status"] == "prior_run_preserved_not_reattempted"
        # It IS in included_manifest_candidate_count
        assert merged["included_manifest_candidate_count"] == 2
        # It is NOT in publishable_candidate_count
        assert (
            merged["publishable_candidate_count"] == 1
        ), "prior_run_preserved_not_reattempted must not count as publishable"
        assert merged["prior_run_preserved_count"] == 1
        assert merged["live_publishable_count"] == 1

    def test_current_run_candidate_is_live_publishable(self):
        """A current_run candidate contributes to publishable_candidate_count and live_publishable_count."""
        old = _make_manifest([], [])
        new = _make_manifest(["merger"], [])
        merged = merge_pr_candidate_manifests(old, new)
        merger_entry = next(e for e in merged["included_examples"] if e["scenario_id"] == "merger")
        assert merger_entry["candidate_integrity_status"] == "current_run"
        assert merged["publishable_candidate_count"] == 1
        assert merged["live_publishable_count"] == 1
        assert merged["current_run_pr_eligible_count"] == 1
        assert merged["prior_run_preserved_count"] == 0

    def test_quarantined_candidate_excluded_and_not_publishable(self):
        """A demoted_quarantined candidate is excluded and never publishable."""
        old = _make_manifest(["png"], [])
        new = _make_manifest(["merger"], ["png"])
        merged = merge_pr_candidate_manifests(old, new, demoted_scenario_ids={"png"})
        included_ids = {e["scenario_id"] for e in merged["included_examples"]}
        excluded_ids = {e["scenario_id"] for e in merged["excluded_examples"]}
        assert "png" not in included_ids
        assert "png" in excluded_ids
        assert merged["quarantined_count"] == 1
        assert merged["publishable_candidate_count"] == 1  # only merger
        assert merged["live_publishable_count"] == 1

    def test_root_and_family_counts_agree(self):
        """included_manifest_candidate_count == len(included_examples)."""
        old = _make_manifest(["a", "b"], [])
        new = _make_manifest(["c"], [])
        merged = merge_pr_candidate_manifests(old, new)
        assert merged["included_manifest_candidate_count"] == len(merged["included_examples"])
        assert merged["blocked_candidate_count"] == len(merged["excluded_examples"])

    def test_mixed_integrity_counts_are_correct(self):
        """With current_run + prior_run_preserved + quarantined, all counts are correct."""
        # Prior: doc-converter, xls-converter, png (quarantined)
        prior_quarantined = {
            "scenario_id": "png",
            "example_path": "old/path",
            "final_example_verdict": "EXAMPLE_BLOCKED_DEMOTED_IN_LATEST_RUN",
            "blocked_reason": "Demoted",
            "candidate_integrity_status": "demoted_quarantined",
        }
        existing = {
            "included_examples": [
                {
                    "scenario_id": "doc-converter",
                    "example_path": "old/path",
                    "final_example_verdict": "EXAMPLE_READY_FOR_PR_DRY_RUN",
                },
                {
                    "scenario_id": "xls-converter",
                    "example_path": "old/path",
                    "final_example_verdict": "EXAMPLE_READY_FOR_PR_DRY_RUN",
                },
            ],
            "excluded_examples": [prior_quarantined],
            "exclusion_reasons": {},
            "dry_run": True,
            "live_publish_attempted": False,
            "publishable_candidate_count": 2,
            "blocked_candidate_count": 1,
        }
        # New run: merger (current_run), doc-converter and xls-converter not reattempted
        new_run = _make_manifest(["merger"], [])
        merged = merge_pr_candidate_manifests(existing, new_run, demoted_scenario_ids=None)
        # 3 included: merger(current_run) + doc-converter + xls-converter (prior_run_preserved)
        assert merged["included_manifest_candidate_count"] == 3
        assert merged["current_run_pr_eligible_count"] == 1
        assert merged["prior_run_preserved_count"] == 2
        assert merged["live_publishable_count"] == 1
        assert merged["publishable_candidate_count"] == 1
        assert merged["quarantined_count"] == 1
        assert merged["blocked_candidate_count"] == 1  # png in excluded
