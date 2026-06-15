"""Parse and classify Stage 3 execution summaries."""

from __future__ import annotations

from typing import Any

import yaml

from plugin_examples.sprint_governance.models import (
    ExecutionSummary,
    SummaryClassification,
)

REQUIRED_FIELDS = frozenset({
    "verdict",
    "taskcards_attempted",
    "taskcards_completed",
    "taskcards_blocked",
    "taskcards_rerouted",
    "quality_evaluations",
    "evidence_path",
})

INTEGER_FIELDS = frozenset({
    "taskcards_attempted",
    "taskcards_completed",
    "taskcards_blocked",
    "taskcards_rerouted",
})


def validate_summary_schema(data: dict[str, Any]) -> list[str]:
    """Validate a summary dict against the expected schema.

    Returns a list of error strings (empty if valid).
    """
    errors: list[str] = []

    for field_name in REQUIRED_FIELDS:
        if field_name not in data:
            errors.append(f"Missing required field: {field_name}")

    for field_name in INTEGER_FIELDS:
        val = data.get(field_name)
        if val is not None and not isinstance(val, int):
            errors.append(f"Field {field_name} must be integer, got {type(val).__name__}")
        if isinstance(val, int) and val < 0:
            errors.append(f"Field {field_name} must be non-negative, got {val}")

    evals = data.get("quality_evaluations")
    if isinstance(evals, list):
        for i, ev in enumerate(evals):
            if isinstance(ev, dict):
                for score in ev.get("scores", []):
                    if isinstance(score, dict):
                        s = score.get("score")
                        if isinstance(s, int) and (s < 1 or s > 5):
                            errors.append(
                                f"quality_evaluations[{i}]: score {s} outside 1-5 range"
                            )

    return errors


def parse_summary(yaml_text: str | None) -> ExecutionSummary | None:
    """Parse a Stage 3 execution summary from YAML text.

    Returns None if input is None or empty.
    Raises ValueError if YAML is valid but schema validation fails.
    """
    if not yaml_text or not yaml_text.strip():
        return None

    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        msg = f"Invalid YAML: {exc}"
        raise ValueError(msg) from exc

    if not isinstance(data, dict):
        msg = "Summary must be a YAML mapping, got " + type(data).__name__
        raise ValueError(msg)

    errors = validate_summary_schema(data)
    if errors:
        msg = "Schema validation errors: " + "; ".join(errors)
        raise ValueError(msg)

    return ExecutionSummary.from_dict(data)


def classify_summary(
    summary: ExecutionSummary | None,
) -> SummaryClassification:
    """Classify a parsed execution summary."""
    if summary is None:
        return SummaryClassification.MISSING

    # Check for BLOCKED_EXTERNAL verdict
    if "BLOCKED_EXTERNAL" in (summary.verdict or ""):
        return SummaryClassification.BLOCKED_EXTERNAL

    # Check for missing evidence
    if not summary.evidence_path:
        return SummaryClassification.EVIDENCE_MISSING

    # Check for missing scores
    if not summary.quality_evaluations:
        return SummaryClassification.SCORES_MISSING

    # Check for incomplete taskcards
    accounted = (
        summary.taskcards_completed
        + summary.taskcards_blocked
        + summary.taskcards_rerouted
    )
    if summary.taskcards_attempted > 0 and accounted != summary.taskcards_attempted:
        return SummaryClassification.TASKCARDS_INCOMPLETE

    # Check for contradictions
    has_reroutes = bool(summary.reroute_log)
    has_blocker_issues = any(i.blocker for i in summary.issues)
    all_green_verdict = summary.verdict in {
        "EXECUTION_COMPLETE_VERIFIED",
        "SPRINT_ALL_GREEN_VERIFIED",
    }
    if all_green_verdict and (has_reroutes or has_blocker_issues):
        return SummaryClassification.CONTRADICTORY

    # Check for rerouted or blocked taskcards
    if summary.taskcards_rerouted > 0 or summary.taskcards_blocked > 0:
        return SummaryClassification.STRUCTURED_NOT_GREEN

    # Check if any quality score fails
    for evaluation in summary.quality_evaluations:
        for score in evaluation.scores:
            if not score.passes:
                return SummaryClassification.STRUCTURED_NOT_GREEN

    # Check for open issues
    if summary.issues:
        return SummaryClassification.STRUCTURED_NOT_GREEN

    return SummaryClassification.STRUCTURED_ALL_GREEN


def classify_raw_text(text: str | None) -> SummaryClassification:
    """Classify raw text that may or may not be valid YAML.

    Used by the loop controller when the text hasn't been parsed yet.
    """
    if not text or not text.strip():
        return SummaryClassification.MISSING

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return SummaryClassification.PROSE_ONLY

    if not isinstance(data, dict):
        return SummaryClassification.PROSE_ONLY

    # Check if it has the required structure
    missing = REQUIRED_FIELDS - set(data.keys())
    if len(missing) > len(REQUIRED_FIELDS) // 2:
        return SummaryClassification.PROSE_ONLY

    try:
        summary = ExecutionSummary.from_dict(data)
    except (KeyError, TypeError, ValueError):
        return SummaryClassification.PROSE_ONLY

    return classify_summary(summary)
