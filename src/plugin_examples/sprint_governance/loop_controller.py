"""Loop controller — classifies summaries and decides next stage automatically."""

from __future__ import annotations

import json
from pathlib import Path

from plugin_examples.sprint_governance.models import (
    ExecutionSummary,
    LoopDecision,
    LoopStage,
    LoopState,
    SummaryClassification,
)
from plugin_examples.sprint_governance.summary_parser import classify_summary

# Invalid final states — the controller must never return these.
INVALID_FINAL_STATES: frozenset[str] = frozenset({
    "NEXT_PROMPT_NEEDED",
    "HUMAN_REVIEW_NEEDED_BEFORE_AGENT_REVIEW",
    "PROSE_ONLY_ACCEPTED",
    "SUMMARY_MISSING_ACCEPTED",
    "SCORE_BELOW_4_ACCEPTED",
    "EVIDENCE_PACKAGE_MISSING_ACCEPTED",
    "PLAN_UPDATED_NOT_EXECUTED",
    "EXECUTED_NOT_EVALUATED",
    "PROMPT_ASSETS_DISCONNECTED",
    "TASKCARDS_MISSING_ACCEPTED",
})

# Mapping from summary classification to next stage
_CLASSIFICATION_TO_STAGE: dict[SummaryClassification, LoopStage] = {
    SummaryClassification.MISSING: LoopStage.AUDIT,
    SummaryClassification.PROSE_ONLY: LoopStage.HARDEN,
    SummaryClassification.STRUCTURED_NOT_GREEN: LoopStage.HARDEN,
    SummaryClassification.CONTRADICTORY: LoopStage.HARDEN,
    SummaryClassification.SCORES_MISSING: LoopStage.EXECUTE,
    SummaryClassification.EVIDENCE_MISSING: LoopStage.EXECUTE,
    SummaryClassification.TASKCARDS_INCOMPLETE: LoopStage.HARDEN,
    SummaryClassification.BLOCKED_EXTERNAL: LoopStage.ESCALATE,
    SummaryClassification.STRUCTURED_ALL_GREEN: LoopStage.ACCEPT,
}


def classify_and_decide(
    summary: ExecutionSummary | None,
    state: LoopState,
) -> LoopDecision:
    """Classify the summary and decide the next loop stage.

    Args:
        summary: Parsed execution summary (None if missing).
        state: Current loop state.

    Returns:
        LoopDecision with next_stage and reason.
    """
    classification = classify_summary(summary)

    # Check max iterations
    if (
        state.iteration >= state.max_iterations
        and classification != SummaryClassification.STRUCTURED_ALL_GREEN
    ):
        return LoopDecision(
            current_stage=LoopStage.DECIDE,
            next_stage=LoopStage.ESCALATE,
            reason=f"Max iterations ({state.max_iterations}) exceeded without all-green",
            iteration=state.iteration,
            summary_classification=classification,
        )

    next_stage = _CLASSIFICATION_TO_STAGE.get(classification, LoopStage.HARDEN)

    reason = _build_reason(classification, next_stage)

    return LoopDecision(
        current_stage=LoopStage.DECIDE,
        next_stage=next_stage,
        reason=reason,
        iteration=state.iteration,
        summary_classification=classification,
    )


def _build_reason(
    classification: SummaryClassification,
    next_stage: LoopStage,
) -> str:
    """Build a human-readable reason for the decision."""
    reasons: dict[SummaryClassification, str] = {
        SummaryClassification.MISSING: "No summary found; full audit required",
        SummaryClassification.PROSE_ONLY: "Summary is prose-only; plan hardening required",
        SummaryClassification.STRUCTURED_NOT_GREEN: "Open issues remain; plan hardening required",
        SummaryClassification.CONTRADICTORY: "Summary contradicts issue/reroute state; plan hardening required",
        SummaryClassification.SCORES_MISSING: "Quality scores missing; re-execute scoring lane",
        SummaryClassification.EVIDENCE_MISSING: "Evidence bundle missing; re-execute evidence lane",
        SummaryClassification.TASKCARDS_INCOMPLETE: "Taskcards not all terminal; plan update required",
        SummaryClassification.BLOCKED_EXTERNAL: "External blocker prevents progress",
        SummaryClassification.STRUCTURED_ALL_GREEN: "All gates passed; sprint accepted",
    }
    return reasons.get(classification, f"Classification {classification} -> {next_stage}")


def validate_decision(decision: LoopDecision) -> list[str]:
    """Validate that a decision does not use an invalid final state."""
    errors: list[str] = []
    if str(decision.next_stage) in INVALID_FINAL_STATES:
        errors.append(
            f"Invalid final state: {decision.next_stage}"
        )
    return errors


def save_loop_state(state: LoopState, path: Path) -> None:
    """Persist loop state to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state.to_dict(), indent=2), encoding="utf-8")


def load_loop_state(path: Path) -> LoopState:
    """Load loop state from a JSON file. Returns fresh state if file missing."""
    return LoopState.load(path)
