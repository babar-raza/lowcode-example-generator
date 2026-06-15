"""Integration tests for the full sprint governance loop.

Proves the P1->P2->P3->decide loop on fixture data:
- ACCEPT path (high quality)
- REWORK path (low quality loops back)
- ESCALATE path (max iterations)
"""

from __future__ import annotations

from pathlib import Path

import yaml

from plugin_examples.sprint_governance.evidence_bundle import (
    create_bundle_manifest,
    validate_bundle,
)
from plugin_examples.sprint_governance.loop_controller import (
    classify_and_decide,
    load_loop_state,
    save_loop_state,
)
from plugin_examples.sprint_governance.models import (
    ExecutionSummary,
    Issue,
    IssueLevel,
    IssueSeverity,
    LoopStage,
    LoopState,
    QualityEvaluation,
    QualityScore,
    SummaryClassification,
    Taskcard,
    TaskcardState,
)
from plugin_examples.sprint_governance.quality_scorer import (
    REQUIRED_DIMENSIONS,
    score_taskcard,
)
from plugin_examples.sprint_governance.summary_parser import (
    classify_summary,
    parse_summary,
)
from plugin_examples.sprint_governance.taskcard_fsm import transition


def _create_all_green_summary() -> ExecutionSummary:
    """Create a fully passing execution summary."""
    scores = [QualityScore(dimension=d, score=5) for d in REQUIRED_DIMENSIONS]
    return ExecutionSummary(
        timestamp="2026-06-15T12:00:00Z",
        verdict="EXECUTION_COMPLETE_VERIFIED",
        taskcards_attempted=1,
        taskcards_completed=1,
        taskcards_blocked=0,
        taskcards_rerouted=0,
        quality_evaluations=[
            QualityEvaluation(taskcard_id="TC-001", scores=scores, accepted=True),
        ],
        evidence_path="/tmp/evidence",
    )


def _create_failing_summary() -> ExecutionSummary:
    """Create a summary with a failing score."""
    scores = [QualityScore(dimension="requirement_correctness", score=3)]
    return ExecutionSummary(
        timestamp="2026-06-15T12:00:00Z",
        verdict="EXECUTION_REROUTED_REWORK_REQUIRED",
        taskcards_attempted=1,
        taskcards_completed=0,
        taskcards_blocked=0,
        taskcards_rerouted=1,
        quality_evaluations=[
            QualityEvaluation(taskcard_id="TC-001", scores=scores, rerouted=True),
        ],
        evidence_path="/tmp/evidence",
    )


class TestFullLoopAcceptPath:
    """Prove the ACCEPT path: high quality -> loop accepts."""

    def test_accept_path(self, tmp_path):
        state = LoopState(sprint_name="accept-test")

        # Simulate P3 output
        summary = _create_all_green_summary()

        # Loop controller decides
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.ACCEPT
        assert decision.summary_classification == SummaryClassification.STRUCTURED_ALL_GREEN

        # Persist state
        state.decisions.append(decision)
        state_path = tmp_path / "state.json"
        save_loop_state(state, state_path)

        loaded = load_loop_state(state_path)
        assert loaded.sprint_name == "accept-test"
        assert len(loaded.decisions) == 1
        assert loaded.decisions[0].next_stage == LoopStage.ACCEPT


class TestFullLoopReworkPath:
    """Prove the REWORK path: low quality -> loops back to HARDEN."""

    def test_rework_path(self):
        state = LoopState(sprint_name="rework-test")

        # Simulate P3 output with failing scores
        summary = _create_failing_summary()

        # Loop controller decides
        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.HARDEN
        assert decision.summary_classification == SummaryClassification.STRUCTURED_NOT_GREEN

        # Second iteration with all-green
        state.iteration += 1
        state.decisions.append(decision)
        summary2 = _create_all_green_summary()
        decision2 = classify_and_decide(summary2, state)
        assert decision2.next_stage == LoopStage.ACCEPT


class TestFullLoopEscalatePath:
    """Prove the ESCALATE path: max iterations -> escalates."""

    def test_escalate_path(self):
        state = LoopState(sprint_name="escalate-test", iteration=3, max_iterations=3)

        # Still failing at max iterations
        summary = _create_failing_summary()

        decision = classify_and_decide(summary, state)
        assert decision.next_stage == LoopStage.ESCALATE


class TestTaskcardLifecycle:
    """Prove full taskcard lifecycle through the FSM."""

    def test_full_happy_path(self):
        card = Taskcard(id="TC-001", title="Fix bug", state=TaskcardState.PROPOSED)
        transition(card, TaskcardState.READY)
        transition(card, TaskcardState.IN_PROGRESS)
        transition(card, TaskcardState.IMPLEMENTED)
        transition(card, TaskcardState.VERIFIED)
        transition(card, TaskcardState.SCORED)
        transition(card, TaskcardState.ACCEPTED)

        assert card.state == TaskcardState.ACCEPTED
        assert len(card.history) == 6

    def test_reroute_rework_cycle(self):
        card = Taskcard(id="TC-002", title="Fix bug", state=TaskcardState.PROPOSED)
        transition(card, TaskcardState.READY)
        transition(card, TaskcardState.IN_PROGRESS)
        transition(card, TaskcardState.IMPLEMENTED)
        transition(card, TaskcardState.VERIFIED)
        transition(card, TaskcardState.SCORED)
        # Score below 4 -> reroute
        transition(card, TaskcardState.REROUTED)
        transition(card, TaskcardState.REWORKING)
        transition(card, TaskcardState.REWORKED)
        transition(card, TaskcardState.VERIFIED)
        transition(card, TaskcardState.SCORED)
        transition(card, TaskcardState.ACCEPTED)

        assert card.state == TaskcardState.ACCEPTED
        assert len(card.history) == 11


class TestEvidenceBundleValidation:
    """Prove evidence bundle validation."""

    def test_valid_stage3_bundle(self, tmp_path):
        for artifact in [
            "stage3-final-sprint-summary.yaml",
            "stage3-quality-evaluations.yaml",
            "stage3-taskcard-status.yaml",
            "stage3-evidence-manifest.yaml",
        ]:
            (tmp_path / artifact).write_text("content: true\n", encoding="utf-8")

        valid, errors = validate_bundle(tmp_path, "stage3")
        assert valid is True
        assert errors == []

    def test_incomplete_bundle(self, tmp_path):
        (tmp_path / "stage3-final-sprint-summary.yaml").write_text("x: 1\n", encoding="utf-8")
        valid, errors = validate_bundle(tmp_path, "stage3")
        assert valid is False
        assert len(errors) == 3  # 3 missing artifacts

    def test_manifest_creation(self, tmp_path):
        (tmp_path / "file1.yaml").write_text("x: 1\n", encoding="utf-8")
        (tmp_path / "file2.md").write_text("# Test\n", encoding="utf-8")
        manifest = create_bundle_manifest(tmp_path)
        assert manifest["total_files"] == 2
        assert len(manifest["files"]) == 2


class TestYamlParsePilot:
    """Prove YAML parsing works end-to-end with fixture data."""

    def test_parse_fixture_summary(self):
        yaml_text = yaml.dump({
            "verdict": "EXECUTION_COMPLETE_VERIFIED",
            "taskcards_attempted": 3,
            "taskcards_completed": 3,
            "taskcards_blocked": 0,
            "taskcards_rerouted": 0,
            "quality_evaluations": [
                {
                    "taskcard_id": "TC-001",
                    "scores": [{"dimension": "requirement_correctness", "score": 5}],
                    "accepted": True,
                    "rerouted": False,
                },
            ],
            "evidence_path": "/tmp/evidence",
        })
        summary = parse_summary(yaml_text)
        assert summary is not None
        assert summary.taskcards_completed == 3
        classification = classify_summary(summary)
        assert classification == SummaryClassification.STRUCTURED_ALL_GREEN
