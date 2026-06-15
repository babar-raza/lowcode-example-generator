"""Taskcard finite state machine — enforces valid state transitions."""

from __future__ import annotations

from datetime import UTC, datetime

from plugin_examples.sprint_governance.models import Taskcard, TaskcardState

TERMINAL_STATES: frozenset[TaskcardState] = frozenset({
    TaskcardState.ACCEPTED,
    TaskcardState.ACCEPTED_WITH_LIMITATIONS,
    TaskcardState.BLOCKED_EXTERNAL,
    TaskcardState.DEFERRED_WITH_REASON,
})

VALID_TRANSITIONS: dict[TaskcardState, frozenset[TaskcardState]] = {
    TaskcardState.PROPOSED: frozenset({
        TaskcardState.READY,
        TaskcardState.BLOCKED,
        TaskcardState.DEFERRED_WITH_REASON,
    }),
    TaskcardState.READY: frozenset({
        TaskcardState.IN_PROGRESS,
        TaskcardState.BLOCKED,
        TaskcardState.DEFERRED_WITH_REASON,
    }),
    TaskcardState.IN_PROGRESS: frozenset({
        TaskcardState.IMPLEMENTED,
        TaskcardState.BLOCKED,
        TaskcardState.REROUTED,
    }),
    TaskcardState.IMPLEMENTED: frozenset({
        TaskcardState.VERIFIED,
        TaskcardState.REROUTED,
        TaskcardState.BLOCKED,
    }),
    TaskcardState.VERIFIED: frozenset({
        TaskcardState.SCORED,
        TaskcardState.REROUTED,
    }),
    TaskcardState.SCORED: frozenset({
        TaskcardState.ACCEPTED,
        TaskcardState.ACCEPTED_WITH_LIMITATIONS,
        TaskcardState.REROUTED,
    }),
    TaskcardState.REROUTED: frozenset({
        TaskcardState.REWORKING,
        TaskcardState.BLOCKED_EXTERNAL,
        TaskcardState.DEFERRED_WITH_REASON,
    }),
    TaskcardState.REWORKING: frozenset({
        TaskcardState.REWORKED,
        TaskcardState.BLOCKED,
        TaskcardState.BLOCKED_EXTERNAL,
    }),
    TaskcardState.REWORKED: frozenset({
        TaskcardState.VERIFIED,
        TaskcardState.REROUTED,
    }),
    TaskcardState.BLOCKED: frozenset({
        TaskcardState.READY,
        TaskcardState.BLOCKED_EXTERNAL,
        TaskcardState.DEFERRED_WITH_REASON,
    }),
    # Terminal states — no outgoing transitions
    TaskcardState.ACCEPTED: frozenset(),
    TaskcardState.ACCEPTED_WITH_LIMITATIONS: frozenset(),
    TaskcardState.BLOCKED_EXTERNAL: frozenset(),
    TaskcardState.DEFERRED_WITH_REASON: frozenset(),
}


def transition(card: Taskcard, new_state: TaskcardState) -> Taskcard:
    """Transition a taskcard to a new state.

    Raises ValueError if the transition is invalid.
    Returns the updated taskcard (mutated in place).
    """
    current = card.state
    allowed = VALID_TRANSITIONS.get(current, frozenset())

    if new_state not in allowed:
        msg = (
            f"Invalid transition: {current} -> {new_state}. "
            f"Allowed from {current}: {sorted(str(s) for s in allowed)}"
        )
        raise ValueError(msg)

    card.history.append({
        "from": str(current),
        "to": str(new_state),
        "timestamp": datetime.now(UTC).isoformat(),
    })
    card.state = new_state
    return card


def has_passed_through(card: Taskcard, state: TaskcardState) -> bool:
    """Check if a taskcard has passed through a given state in its history."""
    if card.state == state:
        return True
    return any(
        entry.get("to") == str(state) or entry.get("from") == str(state)
        for entry in card.history
    )


def validate_acceptance(card: Taskcard) -> list[str]:
    """Validate that a taskcard in ACCEPTED state went through VERIFIED and SCORED."""
    errors: list[str] = []
    if card.state in {TaskcardState.ACCEPTED, TaskcardState.ACCEPTED_WITH_LIMITATIONS}:
        if not has_passed_through(card, TaskcardState.VERIFIED):
            errors.append(
                f"Taskcard {card.id}: ACCEPTED without passing through VERIFIED"
            )
        if not has_passed_through(card, TaskcardState.SCORED):
            errors.append(
                f"Taskcard {card.id}: ACCEPTED without passing through SCORED"
            )
    return errors
