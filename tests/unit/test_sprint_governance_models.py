"""Tests for sprint_governance.models — enums, dataclasses, serialization."""

from __future__ import annotations

import json

import pytest

from plugin_examples.sprint_governance.models import (
    ClaimClassification,
    EvidenceVerdict,
    ExecutionSummary,
    Issue,
    IssueLevel,
    IssueSeverity,
    LoopDecision,
    LoopStage,
    LoopState,
    QualityEvaluation,
    QualityScore,
    SprintVerdict,
    SummaryClassification,
    Taskcard,
    TaskcardState,
)


class TestEnumMembership:
    def test_issue_severity_values(self):
        assert set(IssueSeverity) == {"critical", "high", "medium", "low"}

    def test_issue_level_values(self):
        assert set(IssueLevel) == {"L1", "L2", "L3"}

    def test_claim_classification_values(self):
        assert len(ClaimClassification) == 9

    def test_taskcard_state_values(self):
        assert len(TaskcardState) == 14

    def test_loop_stage_values(self):
        assert set(LoopStage) == {"AUDIT", "HARDEN", "EXECUTE", "DECIDE", "ACCEPT", "ESCALATE"}

    def test_summary_classification_values(self):
        assert len(SummaryClassification) == 9

    def test_evidence_verdict_values(self):
        assert len(EvidenceVerdict) == 5

    def test_sprint_verdict_values(self):
        assert len(SprintVerdict) == 7


class TestIssueRoundtrip:
    def test_to_dict_from_dict(self):
        issue = Issue(
            id="L1-001",
            level=IssueLevel.L1,
            severity=IssueSeverity.HIGH,
            title="Test issue",
            root_cause="Root cause here",
            blocker=True,
        )
        d = issue.to_dict()
        restored = Issue.from_dict(d)
        assert restored.id == "L1-001"
        assert restored.level == IssueLevel.L1
        assert restored.severity == IssueSeverity.HIGH
        assert restored.root_cause == "Root cause here"
        assert restored.blocker is True

    def test_from_dict_defaults(self):
        issue = Issue.from_dict({"issue_id": "X", "title": "T"})
        assert issue.id == "X"
        assert issue.level == IssueLevel.L1
        assert issue.severity == IssueSeverity.MEDIUM
        assert issue.claim == ClaimClassification.UNVERIFIED


class TestQualityScore:
    def test_valid_score(self):
        qs = QualityScore(dimension="test", score=4)
        assert qs.passes is True

    def test_below_threshold(self):
        qs = QualityScore(dimension="test", score=3)
        assert qs.passes is False

    def test_boundary_score(self):
        qs = QualityScore(dimension="test", score=4, threshold=4)
        assert qs.passes is True

    def test_invalid_score_too_low(self):
        with pytest.raises(ValueError, match="Score must be 1-5"):
            QualityScore(dimension="test", score=0)

    def test_invalid_score_too_high(self):
        with pytest.raises(ValueError, match="Score must be 1-5"):
            QualityScore(dimension="test", score=6)

    def test_roundtrip(self):
        qs = QualityScore(dimension="test_cov", score=5, comment="Great")
        d = qs.to_dict()
        restored = QualityScore.from_dict(d)
        assert restored.dimension == "test_cov"
        assert restored.score == 5
        assert restored.passes is True


class TestTaskcardRoundtrip:
    def test_to_dict_from_dict(self):
        tc = Taskcard(
            id="TC-001",
            title="Fix bug",
            state=TaskcardState.READY,
            source_issue_id="L1-001",
        )
        d = tc.to_dict()
        restored = Taskcard.from_dict(d)
        assert restored.id == "TC-001"
        assert restored.state == TaskcardState.READY


class TestLoopStateRoundtrip:
    def test_to_dict_from_dict(self):
        state = LoopState(
            iteration=2,
            sprint_name="test-sprint",
            stage=LoopStage.EXECUTE,
        )
        d = state.to_dict()
        restored = LoopState.from_dict(d)
        assert restored.iteration == 2
        assert restored.sprint_name == "test-sprint"
        assert restored.stage == LoopStage.EXECUTE

    def test_save_load(self, tmp_path):
        state = LoopState(iteration=1, sprint_name="s1")
        path = tmp_path / "state.json"
        state.save(path)
        loaded = LoopState.load(path)
        assert loaded.iteration == 1
        assert loaded.sprint_name == "s1"

    def test_load_missing_file(self, tmp_path):
        loaded = LoopState.load(tmp_path / "missing.json")
        assert loaded.iteration == 0

    def test_load_corrupt_file(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("not json", encoding="utf-8")
        loaded = LoopState.load(path)
        assert loaded.iteration == 0


class TestExecutionSummaryRoundtrip:
    def test_to_dict_from_dict(self):
        summary = ExecutionSummary(
            verdict="EXECUTION_COMPLETE_VERIFIED",
            taskcards_attempted=5,
            taskcards_completed=5,
        )
        d = summary.to_dict()
        restored = ExecutionSummary.from_dict(d)
        assert restored.verdict == "EXECUTION_COMPLETE_VERIFIED"
        assert restored.taskcards_attempted == 5


class TestLoopDecisionRoundtrip:
    def test_to_dict_from_dict(self):
        decision = LoopDecision(
            current_stage=LoopStage.DECIDE,
            next_stage=LoopStage.ACCEPT,
            reason="All green",
        )
        d = decision.to_dict()
        assert d["next_stage"] == "ACCEPT"
        restored = LoopDecision.from_dict(d)
        assert restored.next_stage == LoopStage.ACCEPT
