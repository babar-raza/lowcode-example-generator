"""Tests for sprint_governance.loop_controller — FSM and decision engine."""

from __future__ import annotations

import pytest

from plugin_examples.sprint_governance.loop_controller import (
    INVALID_FINAL_STATES,
    classify_and_decide,
    load_loop_state,
    save_loop_state,
    validate_decision,
)
from plugin_examples.sprint_governance.models import (
    ExecutionSummary,
    Issue,
    IssueLevel,
    IssueSeverity,
    LoopDecision,
    LoopStage,
    LoopState,
    QualityEvaluation,
    QualityScore,
    SummaryClassification,
)


class TestClassifyAndDecide:
    def test_missing_summary_goes_to_audit(self):
        state = LoopState()
        decision = classify_and_decide(None, state)
        assert decision.next_stage == LoopStage.AUDIT
        assert decision.summary_classification == SummaryClassification.MISSING

    def test_all_green_goes_to_accept(self):
        summary = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=1,
            taskcards_completed=1,
            quality_evaluations=[
                QualityEvaluation(
                    taskcard_id="TC-1",
                    scores=[QualityScore(dimension="x", score=5)],
                ),
            ],
        )
        state = LoopState()
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.ACCEPT

    def test_not_green_goes_to_harden(self):
        summary = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=2,
            taskcards_completed=1,
            taskcards_rerouted=1,
            quality_evaluations=[
                QualityEvaluation(
                    taskcard_id="TC-1",
                    scores=[QualityScore(dimension="x", score=5)],
                ),
            ],
        )
        state = LoopState()
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.HARDEN

    def test_evidence_missing_goes_to_execute(self):
        summary = ExecutionSummary(verdict="OK", evidence_path="")
        state = LoopState()
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.EXECUTE

    def test_scores_missing_goes_to_execute(self):
        summary = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            quality_evaluations=[],
        )
        state = LoopState()
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.EXECUTE

    def test_blocked_external_goes_to_escalate(self):
        summary = ExecutionSummary(
            verdict="BLOCKED_EXTERNAL",
            evidence_path="/tmp",
        )
        state = LoopState()
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.ESCALATE

    def test_max_iterations_forces_escalate(self):
        summary = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=2,
            taskcards_completed=1,
            taskcards_rerouted=1,
            quality_evaluations=[
                QualityEvaluation(
                    taskcard_id="TC-1",
                    scores=[QualityScore(dimension="x", score=5)],
                ),
            ],
        )
        state = LoopState(iteration=3, max_iterations=3)
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.ESCALATE

    def test_max_iterations_allows_accept(self):
        """Even at max iterations, all-green still gets ACCEPT."""
        summary = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=1,
            taskcards_completed=1,
            quality_evaluations=[
                QualityEvaluation(
                    taskcard_id="TC-1",
                    scores=[QualityScore(dimension="x", score=5)],
                ),
            ],
        )
        state = LoopState(iteration=3, max_iterations=3)
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.ACCEPT

    def test_contradictory_goes_to_harden(self):
        summary = ExecutionSummary(
            verdict="EXECUTION_COMPLETE_VERIFIED",
            evidence_path="/tmp",
            taskcards_attempted=1,
            taskcards_completed=1,
            quality_evaluations=[
                QualityEvaluation(
                    taskcard_id="TC-1",
                    scores=[QualityScore(dimension="x", score=5)],
                ),
            ],
            reroute_log=[{"reason": "test"}],
        )
        state = LoopState()
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.HARDEN


class TestValidateDecision:
    def test_valid_decision(self):
        decision = LoopDecision(
            current_stage=LoopStage.DECIDE,
            next_stage=LoopStage.ACCEPT,
        )
        assert validate_decision(decision) == []

    def test_invalid_final_states_are_strings(self):
        # All values in INVALID_FINAL_STATES are not valid LoopStage values
        for state in INVALID_FINAL_STATES:
            assert state not in set(LoopStage)


class TestStatePersistence:
    def test_save_and_load(self, tmp_path):
        state = LoopState(
            iteration=2,
            sprint_name="test",
            stage=LoopStage.HARDEN,
        )
        path = tmp_path / "loop.json"
        save_loop_state(state, path)
        loaded = load_loop_state(path)
        assert loaded.iteration == 2
        assert loaded.sprint_name == "test"
        assert loaded.stage == LoopStage.HARDEN

    def test_load_missing_returns_fresh(self, tmp_path):
        loaded = load_loop_state(tmp_path / "missing.json")
        assert loaded.iteration == 0
        assert loaded.stage == LoopStage.AUDIT
