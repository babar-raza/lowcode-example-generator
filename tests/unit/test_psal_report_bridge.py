"""Tests for PSAL report bridge — pipeline output to governance input translation."""

from __future__ import annotations

import pytest

from plugin_examples.psal.report_bridge import (
    _auto_score_pipeline_run,
    _map_verdict,
    build_crash_summary,
    pipeline_report_to_summary,
)
from plugin_examples.sprint_governance.models import Issue, IssueSeverity

# ---------------------------------------------------------------------------
# pipeline_report_to_summary
# ---------------------------------------------------------------------------


class TestPipelineReportToSummary:
    """Test the main bridge function."""

    def _make_report(self, *, verdict="DRY_RUN_BUILD_PASS", stages=None, comparison=None):
        return {
            "verdict": verdict,
            "stages": stages or {
                "load_config": {"status": "PASS"},
                "nuget_fetch": {"status": "PASS"},
                "reflection": {"status": "PASS"},
                "plugin_detection": {"status": "PASS"},
                "scenario_planning": {"status": "PASS", "sufficiency_status": "SUFFICIENT"},
            },
            "comparison": comparison or {"ready_scenario_count": 3, "examples_generated_count": 3},
            "gate_summary": {},
        }

    def test_successful_dry_run(self):
        report = self._make_report()
        summary = pipeline_report_to_summary(report, "barcode")

        assert summary.verdict == "EXECUTION_COMPLETE_VERIFIED"
        assert summary.taskcards_attempted == 3
        assert summary.taskcards_completed == 3
        assert len(summary.quality_evaluations) == 1
        assert summary.quality_evaluations[0].accepted is True

    def test_below_minimum_verdict(self):
        report = self._make_report(
            stages={
                "load_config": {"status": "PASS"},
                "scenario_planning": {"status": "PASS", "sufficiency_status": "BELOW_MINIMUM"},
            },
            comparison={"ready_scenario_count": 1, "examples_generated_count": 1},
        )
        summary = pipeline_report_to_summary(report, "imaging")

        assert summary.verdict == "EXECUTION_PARTIAL_BELOW_MINIMUM"

    def test_registry_incomplete_verdict(self):
        report = self._make_report(
            stages={
                "load_config": {"status": "PASS"},
                "scenario_planning": {"status": "PASS", "sufficiency_status": "REGISTRY_INCOMPLETE"},
            },
        )
        summary = pipeline_report_to_summary(report, "imaging")

        assert summary.verdict == "EXECUTION_PARTIAL_REGISTRY_INCOMPLETE"

    def test_hard_stopped_pipeline(self):
        report = self._make_report(
            verdict="HARD_STOPPED_AT_reflection",
            stages={
                "load_config": {"status": "PASS"},
                "reflection": {"status": "FAIL", "error": "dep missing", "hard_stop": True},
            },
        )
        summary = pipeline_report_to_summary(report, "psd")

        assert summary.verdict == "EXECUTION_BLOCKED"
        assert len(summary.issues) == 1
        assert summary.issues[0].blocker is True

    def test_failed_stage_creates_issue(self):
        report = self._make_report(
            stages={
                "load_config": {"status": "PASS"},
                "nuget_fetch": {"status": "FAIL", "error": "404"},
            },
        )
        summary = pipeline_report_to_summary(report, "test")

        assert len(summary.issues) == 1
        assert summary.issues[0].severity == IssueSeverity.HIGH

    def test_raw_report_preserved(self):
        report = self._make_report()
        summary = pipeline_report_to_summary(report, "barcode")

        assert summary.raw == report


# ---------------------------------------------------------------------------
# build_crash_summary
# ---------------------------------------------------------------------------


class TestBuildCrashSummary:
    def test_crash_summary_has_blocker_issue(self):
        summary = build_crash_summary("psd", RuntimeError("segfault"))

        assert summary.verdict == "PIPELINE_CRASH"
        assert len(summary.issues) == 1
        assert summary.issues[0].blocker is True
        assert "RuntimeError" in summary.issues[0].description

    def test_crash_scores_all_minimum(self):
        summary = build_crash_summary("ocr", ValueError("bad config"))

        for eval_ in summary.quality_evaluations:
            for score in eval_.scores:
                assert score.score == 1
            assert eval_.accepted is False


# ---------------------------------------------------------------------------
# _auto_score_pipeline_run
# ---------------------------------------------------------------------------


class TestAutoScore:
    def test_all_green_scores(self):
        scores = _auto_score_pipeline_run(
            verdict="DRY_RUN_BUILD_PASS",
            total_stages=18,
            passed_stages=18,
            taskcards_attempted=5,
            taskcards_completed=5,
            sufficiency="SUFFICIENT",
        )
        score_map = {s.dimension: s.score for s in scores}

        assert score_map["requirement_correctness"] == 5
        assert score_map["integration_completeness"] == 5
        assert score_map["rollback_safety"] == 5
        assert all(s.passes for s in scores)

    def test_below_minimum_penalizes_requirement(self):
        scores = _auto_score_pipeline_run(
            verdict="DRY_RUN_BUILD_PASS",
            total_stages=18,
            passed_stages=18,
            taskcards_attempted=1,
            taskcards_completed=1,
            sufficiency="BELOW_MINIMUM",
        )
        score_map = {s.dimension: s.score for s in scores}

        assert score_map["requirement_correctness"] == 2
        assert not score_map["requirement_correctness"] >= 4

    def test_registry_incomplete_moderate_penalty(self):
        scores = _auto_score_pipeline_run(
            verdict="DRY_RUN_BUILD_PASS",
            total_stages=18,
            passed_stages=18,
            taskcards_attempted=1,
            taskcards_completed=1,
            sufficiency="REGISTRY_INCOMPLETE",
        )
        score_map = {s.dimension: s.score for s in scores}

        assert score_map["requirement_correctness"] == 3

    def test_zero_stages_handled(self):
        scores = _auto_score_pipeline_run(
            verdict="UNKNOWN",
            total_stages=0,
            passed_stages=0,
            taskcards_attempted=0,
            taskcards_completed=0,
            sufficiency="UNKNOWN",
        )
        score_map = {s.dimension: s.score for s in scores}

        assert score_map["pipeline_compatibility"] == 1
        assert all(1 <= s.score <= 5 for s in scores)


# ---------------------------------------------------------------------------
# _map_verdict
# ---------------------------------------------------------------------------


class TestMapVerdict:
    def test_pass_sufficient(self):
        assert _map_verdict("DRY_RUN_BUILD_PASS", "SUFFICIENT", []) == "EXECUTION_COMPLETE_VERIFIED"

    def test_pass_below_minimum(self):
        assert _map_verdict("DRY_RUN_BUILD_PASS", "BELOW_MINIMUM", []) == "EXECUTION_PARTIAL_BELOW_MINIMUM"

    def test_blocker_overrides_pass(self):
        issues = [Issue(id="x", level="L1", severity="critical", title="t", blocker=True)]
        assert _map_verdict("DRY_RUN_BUILD_PASS", "SUFFICIENT", issues) == "EXECUTION_BLOCKED"

    def test_hard_stop(self):
        assert _map_verdict("HARD_STOPPED_AT_reflection", "UNKNOWN", []) == "EXECUTION_HARD_STOPPED"
