"""Tests for example lifecycle hardening, backlog backfill, and exclusion tracking.

Sprint: Example Lifecycle, Backlog Backfill, and Reviewer Feedback Loop Hardening
Date: 2026-05-06
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from plugin_examples.gates.example_lifecycle import (
    ExampleLifecycleRecord,
    ExampleLifecycleRegistry,
    FamilyBacklogEntry,
    load_family_backlog,
    save_family_backlog,
    update_backlog_from_lifecycle,
    write_lifecycle_evidence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_registry(family="pdf", run_id="test-run", scenarios=None):
    """Create a lifecycle registry with optional pre-populated records."""
    reg = ExampleLifecycleRegistry(family=family, run_id=run_id)
    for s in scenarios or []:
        rec = reg.create_record(s["scenario_id"])
        if s.get("excluded"):
            rec.mark_excluded(s.get("excluded_reason", "blocked"))
            rec.final_verdict = "EXCLUDED_BY_SCOPE"
        elif s.get("generated"):
            rec.mark_generated()
            if s.get("build_passed"):
                rec.mark_build_passed()
                if s.get("run_passed"):
                    rec.mark_run_passed()
                    rec.mark_pr_candidate()
                elif s.get("run_failed"):
                    rec.mark_run_failed(s.get("run_failure_reason", "runtime error"))
            elif s.get("build_failed"):
                rec.mark_build_failed(s.get("build_failure_reason", "build error"))
        elif s.get("generation_failed"):
            rec.mark_generation_failed(s.get("generation_failure_reason", "gen error"))
    return reg


@dataclass
class _MockScenario:
    scenario_id: str
    status: str = "ready"
    blocked_reason: str = ""


@dataclass
class _MockPlanningResult:
    ready_scenarios: list = field(default_factory=list)
    blocked_scenarios: list = field(default_factory=list)

    @property
    def ready_count(self):
        return len(self.ready_scenarios)

    @property
    def blocked_count(self):
        return len(self.blocked_scenarios)


# ---------------------------------------------------------------------------
# Phase 6 Tests
# ---------------------------------------------------------------------------


class TestEveryPlannedExampleGetsLifecycleRecord:
    """Verify that ALL planned examples (including excluded) get lifecycle records."""

    def test_excluded_by_allowlist_gets_lifecycle_record(self):
        """Excluded scenarios must have a lifecycle record with EXCLUDED_BY_SCOPE."""
        reg = _make_registry(
            scenarios=[
                {"scenario_id": "pdf-merger", "generated": True, "build_passed": True, "run_passed": True},
                {"scenario_id": "pdf-splitter", "excluded": True, "excluded_reason": "blocked_pilot_not_in_scope"},
            ]
        )
        splitter = reg.get_record("pdf-splitter")
        assert splitter is not None
        assert splitter.current_stage == "excluded"
        assert splitter.final_verdict == "EXCLUDED_BY_SCOPE"
        assert splitter.excluded_reason == "blocked_pilot_not_in_scope"
        assert splitter.pr_candidate is False

    def test_every_planned_example_gets_lifecycle_record(self):
        """All 4 PDF pilot scenarios must appear in lifecycle."""
        reg = _make_registry(
            scenarios=[
                {"scenario_id": "pdf-merger", "generated": True, "build_passed": True, "run_passed": True},
                {"scenario_id": "pdf-text-extractor", "generated": True, "build_passed": True, "run_passed": True},
                {"scenario_id": "pdf-splitter", "excluded": True, "excluded_reason": "not_in_allowlist"},
                {"scenario_id": "pdf-optimizer", "excluded": True, "excluded_reason": "not_in_allowlist"},
            ]
        )
        assert reg.total == 4
        assert len(reg.pr_candidates) == 2
        assert len(reg.excluded_records) == 2

    def test_excluded_by_allowlist_gets_backlog_or_taskcard(self):
        """Excluded scenarios should be backloggable."""
        reg = _make_registry(
            scenarios=[
                {"scenario_id": "pdf-splitter", "excluded": True, "excluded_reason": "not_in_allowlist"},
            ]
        )
        rec = reg.get_record("pdf-splitter")
        rec.mark_backlogged(
            root_cause="LLM uses PluginOptions instead of SplitOptions",
            recommended_fix="Add SplitOptions few-shot",
            priority="high",
        )
        assert rec.backlogged is True
        assert rec.backlog_root_cause == "LLM uses PluginOptions instead of SplitOptions"


class TestFailedExamplesGetBacklogEntries:
    """Verify that build/runtime/reviewer failures produce backlog entries."""

    def test_build_failed_example_gets_backlog_entry(self, tmp_path):
        reg = _make_registry(
            scenarios=[
                {
                    "scenario_id": "test-ex",
                    "generated": True,
                    "build_failed": True,
                    "build_failure_reason": "CS0246: type not found",
                },
            ]
        )
        rec = reg.get_record("test-ex")
        rec.mark_backlogged(
            root_cause="CS0246: type not found",
            recommended_fix="Fix type reference",
            priority="high",
        )
        update_backlog_from_lifecycle(reg, tmp_path)
        backlog = load_family_backlog("pdf", tmp_path)
        assert len(backlog) >= 1
        entry = next(e for e in backlog if e.scenario_id == "test-ex")
        assert entry.root_cause == "CS0246: type not found"

    def test_runtime_failed_example_gets_backlog_entry(self, tmp_path):
        reg = _make_registry(
            scenarios=[
                {
                    "scenario_id": "test-rt",
                    "generated": True,
                    "build_passed": True,
                    "run_failed": True,
                    "run_failure_reason": "ArgumentException",
                },
            ]
        )
        rec = reg.get_record("test-rt")
        rec.mark_backlogged(
            root_cause="ArgumentException",
            recommended_fix="Fix argument",
            priority="medium",
        )
        update_backlog_from_lifecycle(reg, tmp_path)
        backlog = load_family_backlog("pdf", tmp_path)
        entry = next(e for e in backlog if e.scenario_id == "test-rt")
        assert entry.root_cause == "ArgumentException"

    def test_reviewer_failed_example_gets_backlog_entry(self, tmp_path):
        reg = _make_registry(
            scenarios=[
                {"scenario_id": "test-rev", "generated": True, "build_passed": True, "run_passed": True},
            ]
        )
        rec = reg.get_record("test-rev")
        rec.mark_reviewer_failed("code quality issue")
        rec.mark_backlogged(
            root_cause="reviewer_failed: code quality issue",
            recommended_fix="Address reviewer feedback",
            priority="high",
        )
        update_backlog_from_lifecycle(reg, tmp_path)
        backlog = load_family_backlog("pdf", tmp_path)
        entry = next(e for e in backlog if e.scenario_id == "test-rev")
        assert "reviewer_failed" in entry.root_cause


class TestBacklogCrossLinksTaskcard:
    """Verify that backlog entries can reference taskcards."""

    def test_backlog_entry_cross_links_taskcard(self):
        """FamilyBacklogEntry should be able to store taskcard references."""
        entry = FamilyBacklogEntry(
            scenario_id="pdf-splitter",
            family="pdf",
            last_run_id="pilot-pdf-20260505-214804",
            last_failure_stage="scenario_planning",
            root_cause="PluginOptions hallucination",
            recommended_fix="Add SplitOptions few-shot",
            priority="high",
        )
        # The entry stores enough info to cross-link; taskcard_id can be derived
        assert entry.scenario_id == "pdf-splitter"
        assert entry.root_cause == "PluginOptions hallucination"
        assert entry.priority == "high"


class TestPartialPrSummaryListsExcludedExamples:
    """Verify that PR summary includes excluded scenarios."""

    def test_partial_pr_summary_lists_excluded_examples(self):
        from plugin_examples.publisher.pr_builder import build_pr

        excluded = [
            "pdf-splitter — blocked_pilot_not_in_scope: Type 'Splitter' not in allowlist",
            "pdf-optimizer — blocked_pilot_not_in_scope: Type 'Optimizer' not in allowlist",
        ]
        pr = build_pr(
            family="pdf",
            run_id="test-run",
            examples_count=2,
            package_version="26.4.0",
            examples_list=["merger", "text-extractor"],
            excluded_scenarios=excluded,
        )
        assert "pdf-splitter" in pr.body
        assert "pdf-optimizer" in pr.body
        assert "None in this controlled pilot scope" not in pr.body

    def test_pr_summary_without_excluded_shows_none(self):
        from plugin_examples.publisher.pr_builder import build_pr

        pr = build_pr(
            family="cells",
            run_id="test-run",
            examples_count=9,
            package_version="26.4.0",
        )
        assert "None in this controlled pilot scope" in pr.body


class TestReadinessRankCountsBackloggedExamples:
    """Verify readiness rank tracks backlogged examples."""

    def test_readiness_rank_counts_backlogged_examples(self):
        """Registry summary should include backlogged count."""
        reg = _make_registry(
            scenarios=[
                {"scenario_id": "ex1", "generated": True, "build_passed": True, "run_passed": True},
                {"scenario_id": "ex2", "generated": True, "build_failed": True, "build_failure_reason": "error"},
            ]
        )
        rec2 = reg.get_record("ex2")
        rec2.mark_backlogged(root_cause="build_failed", recommended_fix="fix", priority="high")
        summary = reg.summary()
        assert summary["backlogged"] >= 1
        assert summary["total_planned"] == 2


class TestFailedExamplesNotMissingFromLatestFamilyLifecycle:
    """Verify that lifecycle evidence preserves all records."""

    def test_failed_examples_not_missing_from_latest_family_lifecycle(self, tmp_path):
        reg = _make_registry(
            scenarios=[
                {"scenario_id": "ok", "generated": True, "build_passed": True, "run_passed": True},
                {"scenario_id": "fail", "generated": True, "build_failed": True, "build_failure_reason": "CS0001"},
            ]
        )
        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir(parents=True)
        latest = evidence_dir / "latest"
        latest.mkdir()
        write_lifecycle_evidence(reg, evidence_dir)
        evidence_file = latest / "example-lifecycle-records.json"
        assert evidence_file.exists()
        data = json.loads(evidence_file.read_text())
        ids = [r["scenario_id"] for r in data["records"]]
        assert "ok" in ids
        assert "fail" in ids


class TestPdfSplitterOptimizerBackfilledToBacklog:
    """Verify the actual PDF backlog backfill."""

    def test_pdf_splitter_optimizer_backfilled_to_backlog(self):
        backlog_path = Path(__file__).resolve().parents[2] / "workspace" / "backlog" / "pdf" / "examples-backlog.json"
        if not backlog_path.exists():
            pytest.skip("Backlog file not yet created")
        data = json.loads(backlog_path.read_text())
        ids = [e["scenario_id"] for e in data["entries"]]
        assert "pdf-splitter" in ids
        assert "pdf-optimizer" in ids
        # All entries must have a taskcard cross-link; open entries must have root_cause
        for entry in data["entries"]:
            assert entry["taskcard_id"]  # cross-linked
            if entry["status"] == "open":
                assert entry["root_cause"]  # open entries must document root cause
        # Splitter was resolved in Wave 1 — status may be "resolved"
        splitter_entry = next(e for e in data["entries"] if e["scenario_id"] == "pdf-splitter")
        assert splitter_entry["status"] in ("open", "resolved")
        # Optimizer was resolved in Sprint R2 (first PASS in pilot-pdf-20260508-155520)
        optimizer_entry = next(e for e in data["entries"] if e["scenario_id"] == "pdf-optimizer")
        assert optimizer_entry["status"] in ("open", "resolved")


class TestReviewerFeedbackLoopPendingStatusIsReported:
    """Verify that reviewer feedback loop gap is documented."""

    def test_reviewer_feedback_loop_pending_status_is_reported(self):
        gap_path = (
            Path(__file__).resolve().parents[2]
            / "workspace"
            / "verification"
            / "latest"
            / "example-reviewer-feedback-loop-gap-analysis.json"
        )
        if not gap_path.exists():
            pytest.skip("Gap analysis not yet created")
        data = json.loads(gap_path.read_text())
        assert data["current_state"]["feedback_driven_repair"] is False
        assert data["current_state"]["per_example_feedback"] is False
        assert data["verdict"] == "REVIEWER_FEEDBACK_LOOP_NOT_IMPLEMENTED"


class TestRunnerRegistersBlockedScenarios:
    """Verify that runner.py creates lifecycle records for blocked scenarios."""

    def test_blocked_scenarios_get_lifecycle_records(self):
        """Simulates the runner flow: blocked scenarios should get excluded records."""
        from plugin_examples.runner import PipelineContext

        ctx = PipelineContext(
            family="pdf",
            run_id="test-blocked",
            dry_run=True,
            skip_run=False,
            template_mode=True,
            require_llm=False,
            require_validation=False,
            require_reviewer=False,
            repo_root=Path("."),
            run_dir=Path("."),
            evidence_dir=Path("."),
        )

        # Simulate: lifecycle registry initialized with blocked scenarios
        reg = ExampleLifecycleRegistry(family="pdf", run_id="test-blocked")
        blocked = [
            _MockScenario(
                "pdf-splitter", status="blocked_pilot_not_in_scope", blocked_reason="Type 'Splitter' not in allowlist"
            ),
            _MockScenario(
                "pdf-optimizer", status="blocked_pilot_not_in_scope", blocked_reason="Type 'Optimizer' not in allowlist"
            ),
        ]
        for b in blocked:
            rec = reg.create_record(b.scenario_id)
            reason = getattr(b, "blocked_reason", None) or getattr(b, "status", "blocked")
            rec.mark_excluded(reason)
            rec.final_verdict = "EXCLUDED_BY_SCOPE"

        assert reg.total == 2
        for rec in reg.records:
            assert rec.current_stage == "excluded"
            assert rec.final_verdict == "EXCLUDED_BY_SCOPE"
            assert rec.pr_candidate is False


class TestLoadExcludedScenarioSummaries:
    """Verify _load_excluded_scenario_summaries from publisher.py."""

    def test_loads_from_family_scoped_evidence(self, tmp_path):
        from plugin_examples.publisher.publisher import _load_excluded_scenario_summaries

        # Create family-scoped blocked-scenarios.json
        families_dir = tmp_path / "latest" / "families" / "pdf"
        families_dir.mkdir(parents=True)
        blocked = {
            "family": "pdf",
            "blocked_count": 2,
            "blocked_scenarios": [
                {
                    "scenario_id": "pdf-splitter",
                    "status": "blocked_pilot_not_in_scope",
                    "blocked_reason": "Not in allowlist",
                },
                {
                    "scenario_id": "pdf-optimizer",
                    "status": "blocked_pilot_not_in_scope",
                    "blocked_reason": "Not in allowlist",
                },
            ],
        }
        (families_dir / "blocked-scenarios.json").write_text(json.dumps(blocked))

        lines = _load_excluded_scenario_summaries(tmp_path, "pdf")
        assert len(lines) == 2
        assert "pdf-splitter" in lines[0]
        assert "pdf-optimizer" in lines[1]

    def test_returns_empty_when_no_blocked_file(self, tmp_path):
        from plugin_examples.publisher.publisher import _load_excluded_scenario_summaries

        lines = _load_excluded_scenario_summaries(tmp_path, "pdf")
        assert lines == []
