"""Tests for example lifecycle tracking and per-family backlog."""

import json
from pathlib import Path

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


class TestExampleLifecycleRecord:
    """Test ExampleLifecycleRecord state transitions."""

    def test_initial_state_is_planned(self):
        rec = ExampleLifecycleRecord(scenario_id="pdf-merger", family="pdf", run_id="run-001")
        assert rec.current_stage == "planned"
        assert rec.final_verdict == "PENDING"
        assert rec.pr_candidate is False
        assert rec.backlogged is False

    def test_mark_generation_failed_sets_stage_and_verdict(self):
        rec = ExampleLifecycleRecord(scenario_id="pdf-merger", family="pdf", run_id="run-001")
        rec.mark_generation_failed("LLM returned empty code")
        assert rec.current_stage == "generation_failed"
        assert rec.generation_status == "failed"
        assert rec.generation_failure_reason == "LLM returned empty code"
        assert rec.final_verdict == "EXAMPLE_BLOCKED_GENERATION_FAILED"
        assert rec.pr_candidate is False

    def test_full_success_lifecycle(self):
        rec = ExampleLifecycleRecord(scenario_id="pdf-merger", family="pdf", run_id="run-001")
        rec.mark_generated()
        rec.mark_build_passed()
        rec.mark_run_passed()
        rec.mark_pr_candidate()
        assert rec.current_stage == "pr_candidate"
        assert rec.pr_candidate is True
        assert rec.final_verdict == "EXAMPLE_READY_FOR_PR_DRY_RUN"

    def test_build_failure_triggers_backlog(self):
        rec = ExampleLifecycleRecord(scenario_id="pdf-merger", family="pdf", run_id="run-001")
        rec.mark_generated()
        rec.mark_build_failed("CS0246: type not found")
        rec.mark_backlogged(
            root_cause="CS0246: type not found",
            recommended_fix="Add missing using directive",
            priority="high",
        )
        assert rec.backlogged is True
        assert rec.backlog_root_cause == "CS0246: type not found"
        assert rec.backlog_priority == "high"
        assert rec.pr_candidate is False

    def test_reviewer_failure_updates_lifecycle(self):
        rec = ExampleLifecycleRecord(scenario_id="pdf-merger", family="pdf", run_id="run-001")
        rec.mark_generated()
        rec.mark_build_passed()
        rec.mark_run_passed()
        rec.mark_pr_candidate()
        rec.mark_reviewer_failed("Uses deprecated API")
        assert rec.reviewer_status == "failed"
        assert rec.final_verdict == "EXAMPLE_BLOCKED_REVIEWER_FAILED"


class TestExampleLifecycleRegistry:
    """Test registry for collecting lifecycle records."""

    def test_create_record_adds_to_registry(self):
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-001")
        rec = reg.create_record("pdf-merger")
        assert reg.total == 1
        assert rec.scenario_id == "pdf-merger"
        assert rec.family == "pdf"

    def test_get_record_by_scenario_id(self):
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-001")
        reg.create_record("pdf-merger")
        reg.create_record("pdf-text-extractor")
        found = reg.get_record("pdf-text-extractor")
        assert found is not None
        assert found.scenario_id == "pdf-text-extractor"

    def test_get_record_returns_none_for_missing(self):
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-001")
        assert reg.get_record("nonexistent") is None

    def test_summary_counts_all_stages(self):
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-001")
        rec1 = reg.create_record("pdf-merger")
        rec1.mark_generated()
        rec1.mark_build_passed()
        rec1.mark_run_passed()
        rec1.mark_pr_candidate()

        rec2 = reg.create_record("pdf-splitter")
        rec2.mark_generation_failed("timeout")

        summary = reg.summary()
        assert summary["total_planned"] == 2
        assert summary["generation_passed"] == 1
        assert summary["generation_failed"] == 1
        assert summary["pr_candidates"] == 1

    def test_generation_failed_not_silently_dropped(self):
        """Core contract: failed generation is tracked, never invisible."""
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-001")
        rec = reg.create_record("pdf-optimizer")
        rec.mark_generation_failed("LLM timeout")
        # The record is still in the registry — not dropped
        assert reg.total == 1
        assert len(reg.generation_failed) == 1
        assert reg.generation_failed[0].scenario_id == "pdf-optimizer"


class TestFamilyBacklog:
    """Test persistent per-family backlog."""

    def test_save_and_load_backlog(self, tmp_path):
        entries = [
            FamilyBacklogEntry(
                scenario_id="pdf-splitter",
                family="pdf",
                last_run_id="run-001",
                last_failure_stage="build_failed",
                root_cause="CS0246: SplitOptions not found",
                recommended_fix="Use concrete SplitOptions class",
                priority="high",
            )
        ]
        save_family_backlog("pdf", entries, tmp_path)
        loaded = load_family_backlog("pdf", tmp_path)
        assert len(loaded) == 1
        assert loaded[0].scenario_id == "pdf-splitter"
        assert loaded[0].root_cause == "CS0246: SplitOptions not found"

    def test_load_empty_backlog_returns_empty(self, tmp_path):
        loaded = load_family_backlog("pdf", tmp_path)
        assert loaded == []

    def test_update_backlog_adds_failed_examples(self, tmp_path):
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-001")
        rec = reg.create_record("pdf-splitter")
        rec.mark_generation_failed("timeout")
        rec.mark_backlogged("timeout", "increase timeout", "high")

        entries = update_backlog_from_lifecycle(reg, tmp_path)
        assert len(entries) == 1
        assert entries[0].scenario_id == "pdf-splitter"
        assert entries[0].root_cause == "timeout"

    def test_update_backlog_resolves_passing_examples(self, tmp_path):
        # First run: failure
        entries = [
            FamilyBacklogEntry(
                scenario_id="pdf-merger",
                family="pdf",
                last_run_id="run-001",
                last_failure_stage="build_failed",
                root_cause="missing AddInput",
                recommended_fix="add few-shot",
            )
        ]
        save_family_backlog("pdf", entries, tmp_path)

        # Second run: success
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-002")
        rec = reg.create_record("pdf-merger")
        rec.mark_generated()
        rec.mark_build_passed()
        rec.mark_run_passed()
        rec.mark_pr_candidate()

        updated = update_backlog_from_lifecycle(reg, tmp_path)
        resolved = [e for e in updated if e.resolved]
        assert len(resolved) == 1
        assert resolved[0].resolved_in_run == "run-002"

    def test_update_backlog_increments_attempt_count(self, tmp_path):
        # First run: failure
        entries = [
            FamilyBacklogEntry(
                scenario_id="pdf-splitter",
                family="pdf",
                last_run_id="run-001",
                last_failure_stage="build_failed",
                root_cause="wrong class",
                recommended_fix="fix class name",
                attempt_count=1,
            )
        ]
        save_family_backlog("pdf", entries, tmp_path)

        # Second run: still failing
        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-002")
        rec = reg.create_record("pdf-splitter")
        rec.mark_generation_failed("still wrong class")
        rec.mark_backlogged("still wrong class", "stronger constraint", "high")

        updated = update_backlog_from_lifecycle(reg, tmp_path)
        splitter = [e for e in updated if e.scenario_id == "pdf-splitter"][0]
        assert splitter.attempt_count == 2
        assert splitter.last_run_id == "run-002"


class TestLifecycleEvidenceWriter:
    """Test evidence file output."""

    def test_write_lifecycle_evidence_creates_file(self, tmp_path):
        evidence_dir = tmp_path / "evidence"
        evidence_dir.mkdir()
        (evidence_dir / "latest").mkdir()

        reg = ExampleLifecycleRegistry(family="pdf", run_id="run-001")
        rec = reg.create_record("pdf-merger")
        rec.mark_generated()
        rec.mark_build_passed()
        rec.mark_run_passed()
        rec.mark_pr_candidate()

        path = write_lifecycle_evidence(reg, evidence_dir)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["family"] == "pdf"
        assert data["summary"]["pr_candidates"] == 1
        assert len(data["records"]) == 1
        assert data["records"][0]["scenario_id"] == "pdf-merger"
        assert data["records"][0]["pr_candidate"] is True


class TestRunnerLifecycleIntegration:
    """Test that the runner correctly populates lifecycle records."""

    def test_lifecycle_registry_created_during_generation(self):
        """Verify the lifecycle registry field exists on PipelineContext."""
        from plugin_examples.runner import PipelineContext
        from pathlib import Path as P

        ctx = PipelineContext(
            family="pdf",
            run_id="test",
            dry_run=True,
            skip_run=False,
            template_mode=True,
            require_llm=False,
            require_validation=False,
            require_reviewer=False,
            repo_root=P("."),
            run_dir=P("."),
            evidence_dir=P("."),
        )
        assert ctx.lifecycle_registry is None  # Initialized lazily in _stage_generation
