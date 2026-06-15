"""Tests for sprint_governance.taskcard_fsm — state machine transitions."""

from __future__ import annotations

import pytest

from plugin_examples.sprint_governance.models import Taskcard, TaskcardState
from plugin_examples.sprint_governance.taskcard_fsm import (
    TERMINAL_STATES,
    VALID_TRANSITIONS,
    has_passed_through,
    transition,
    validate_acceptance,
)


class TestValidTransitions:
    """Test all valid state transitions succeed."""

    @pytest.mark.parametrize(
        "from_state,to_state",
        [
            (TaskcardState.PROPOSED, TaskcardState.READY),
            (TaskcardState.PROPOSED, TaskcardState.BLOCKED),
            (TaskcardState.PROPOSED, TaskcardState.DEFERRED_WITH_REASON),
            (TaskcardState.READY, TaskcardState.IN_PROGRESS),
            (TaskcardState.IN_PROGRESS, TaskcardState.IMPLEMENTED),
            (TaskcardState.IN_PROGRESS, TaskcardState.BLOCKED),
            (TaskcardState.IN_PROGRESS, TaskcardState.REROUTED),
            (TaskcardState.IMPLEMENTED, TaskcardState.VERIFIED),
            (TaskcardState.IMPLEMENTED, TaskcardState.REROUTED),
            (TaskcardState.VERIFIED, TaskcardState.SCORED),
            (TaskcardState.VERIFIED, TaskcardState.REROUTED),
            (TaskcardState.SCORED, TaskcardState.ACCEPTED),
            (TaskcardState.SCORED, TaskcardState.ACCEPTED_WITH_LIMITATIONS),
            (TaskcardState.SCORED, TaskcardState.REROUTED),
            (TaskcardState.REROUTED, TaskcardState.REWORKING),
            (TaskcardState.REROUTED, TaskcardState.BLOCKED_EXTERNAL),
            (TaskcardState.REWORKING, TaskcardState.REWORKED),
            (TaskcardState.REWORKED, TaskcardState.VERIFIED),
            (TaskcardState.BLOCKED, TaskcardState.READY),
            (TaskcardState.BLOCKED, TaskcardState.BLOCKED_EXTERNAL),
        ],
    )
    def test_valid_transition(self, from_state, to_state):
        card = Taskcard(id="TC-1", title="Test", state=from_state)
        result = transition(card, to_state)
        assert result.state == to_state
        assert len(result.history) == 1
        assert result.history[0]["from"] == str(from_state)
        assert result.history[0]["to"] == str(to_state)


class TestInvalidTransitions:
    """Test all invalid transitions raise ValueError."""

    @pytest.mark.parametrize(
        "from_state,to_state",
        [
            # Terminal states cannot transition
            (TaskcardState.ACCEPTED, TaskcardState.IN_PROGRESS),
            (TaskcardState.ACCEPTED, TaskcardState.PROPOSED),
            (TaskcardState.BLOCKED_EXTERNAL, TaskcardState.READY),
            (TaskcardState.DEFERRED_WITH_REASON, TaskcardState.READY),
            # Cannot skip states
            (TaskcardState.PROPOSED, TaskcardState.IMPLEMENTED),
            (TaskcardState.PROPOSED, TaskcardState.ACCEPTED),
            (TaskcardState.READY, TaskcardState.VERIFIED),
            (TaskcardState.READY, TaskcardState.ACCEPTED),
            # Backwards transitions not allowed
            (TaskcardState.IN_PROGRESS, TaskcardState.PROPOSED),
            (TaskcardState.IMPLEMENTED, TaskcardState.IN_PROGRESS),
            (TaskcardState.VERIFIED, TaskcardState.IMPLEMENTED),
            (TaskcardState.SCORED, TaskcardState.VERIFIED),
            # REROUTED cannot go directly to ACCEPTED
            (TaskcardState.REROUTED, TaskcardState.ACCEPTED),
            (TaskcardState.REWORKING, TaskcardState.ACCEPTED),
        ],
    )
    def test_invalid_transition_raises(self, from_state, to_state):
        card = Taskcard(id="TC-1", title="Test", state=from_state)
        with pytest.raises(ValueError, match="Invalid transition"):
            transition(card, to_state)


class TestTerminalStates:
    def test_terminal_states_have_no_outgoing(self):
        for state in TERMINAL_STATES:
            assert VALID_TRANSITIONS[state] == frozenset()

    def test_terminal_state_set(self):
        assert TaskcardState.ACCEPTED in TERMINAL_STATES
        assert TaskcardState.BLOCKED_EXTERNAL in TERMINAL_STATES
        assert TaskcardState.DEFERRED_WITH_REASON in TERMINAL_STATES


class TestHistoryTracking:
    def test_multiple_transitions_build_history(self):
        card = Taskcard(id="TC-1", title="Test", state=TaskcardState.PROPOSED)
        transition(card, TaskcardState.READY)
        transition(card, TaskcardState.IN_PROGRESS)
        transition(card, TaskcardState.IMPLEMENTED)
        assert len(card.history) == 3

    def test_has_passed_through(self):
        card = Taskcard(id="TC-1", title="Test", state=TaskcardState.PROPOSED)
        transition(card, TaskcardState.READY)
        transition(card, TaskcardState.IN_PROGRESS)
        assert has_passed_through(card, TaskcardState.READY) is True
        assert has_passed_through(card, TaskcardState.PROPOSED) is True
        assert has_passed_through(card, TaskcardState.IN_PROGRESS) is True
        assert has_passed_through(card, TaskcardState.ACCEPTED) is False


class TestAcceptanceValidation:
    def test_accepted_with_verified_and_scored(self):
        card = Taskcard(id="TC-1", title="Test", state=TaskcardState.PROPOSED)
        transition(card, TaskcardState.READY)
        transition(card, TaskcardState.IN_PROGRESS)
        transition(card, TaskcardState.IMPLEMENTED)
        transition(card, TaskcardState.VERIFIED)
        transition(card, TaskcardState.SCORED)
        transition(card, TaskcardState.ACCEPTED)
        errors = validate_acceptance(card)
        assert errors == []

    def test_accepted_without_verified_detected(self):
        card = Taskcard(
            id="TC-1",
            title="Test",
            state=TaskcardState.ACCEPTED,
            history=[],
        )
        errors = validate_acceptance(card)
        assert any("VERIFIED" in e for e in errors)
        assert any("SCORED" in e for e in errors)
