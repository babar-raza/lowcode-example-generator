"""Tests for sprint_governance.summary_parser — parsing and classification."""

from __future__ import annotations

import pytest

from plugin_examples.sprint_governance.models import (
    ExecutionSummary,
    Issue,
    IssueLevel,
    IssueSeverity,
    QualityEvaluation,
    QualityScore,
    SummaryClassification,
)
from plugin_examples.sprint_governance.summary_parser import (
    classify_raw_text,
    classify_summary,
    parse_summary,
    validate_summary_schema,
)

VALID_YAML = """\
verdict: EXECUTION_COMPLETE_VERIFIED
taskcards_attempted: 5
taskcards_completed: 5
taskcards_blocked: 0
taskcards_rerouted: 0
quality_evaluations:
  - taskcard_id: TC-001
    scores:
      - dimension: requirement_correctness
        score: 5
    accepted: true
    rerouted: false
evidence_path: /tmp/evidence
"""


class TestParseSummary:
    def test_valid_yaml(self):
        summary = parse_summary(VALID_YAML)
        assert summary is not None
        assert summary.verdict == "EXECUTION_COMPLETE_VERIFIED"
        assert summary.taskcards_attempted == 5

    def test_none_input(self):
        assert parse_summary(None) is None

    def test_empty_input(self):
        assert parse_summary("") is None
        assert parse_summary("  ") is None

    def test_invalid_yaml(self):
        with pytest.raises(ValueError, match="Invalid YAML"):
            parse_summary("{{invalid yaml")

    def test_non_mapping_yaml(self):
        with pytest.raises(ValueError, match="must be a YAML mapping"):
            parse_summary("- item1\n- item2")

    def test_missing_required_fields(self):
        with pytest.raises(ValueError, match="Missing required field"):
            parse_summary("verdict: OK\n")


class TestValidateSummarySchema:
    def test_valid_data(self):
        data = {
            "verdict": "OK",
            "taskcards_attempted": 5,
            "taskcards_completed": 5,
            "taskcards_blocked": 0,
            "taskcards_rerouted": 0,
            "quality_evaluations": [],
            "evidence_path": "/tmp/ev",
        }
        errors = validate_summary_schema(data)
        assert errors == []

    def test_missing_fields(self):
        errors = validate_summary_schema({})
        assert len(errors) >= 7  # All required fields missing

    def test_non_integer_field(self):
        data = {
            "verdict": "OK",
            "taskcards_attempted": "five",
            "taskcards_completed": 0,
            "taskcards_blocked": 0,
            "taskcards_rerouted": 0,
            "quality_evaluations": [],
            "evidence_path": "/tmp",
        }
        errors = validate_summary_schema(data)
        assert any("integer" in e for e in errors)

    def test_negative_count(self):
        data = {
            "verdict": "OK",
            "taskcards_attempted": -1,
            "taskcards_completed": 0,
            "taskcards_blocked": 0,
            "taskcards_rerouted": 0,
            "quality_evaluations": [],
            "evidence_path": "/tmp",
        }
        errors = validate_summary_schema(data)
        assert any("non-negative" in e for e in errors)

    def test_score_out_of_range(self):
        data = {
            "verdict": "OK",
            "taskcards_attempted": 1,
            "taskcards_completed": 1,
            "taskcards_blocked": 0,
            "taskcards_rerouted": 0,
            "quality_evaluations": [
                {"taskcard_id": "TC-1", "scores": [{"dimension": "x", "score": 6}]},
            ],
            "evidence_path": "/tmp",
        }
        errors = validate_summary_schema(data)
        assert any("outside 1-5" in e for e in errors)


class TestClassifySummary:
    def test_missing(self):
        assert classify_summary(None) == SummaryClassification.MISSING

    def test_blocked_external(self):
        s = ExecutionSummary(verdict="BLOCKED_EXTERNAL", evidence_path="/tmp")
        assert classify_summary(s) == SummaryClassification.BLOCKED_EXTERNAL

    def test_evidence_missing(self):
        s = ExecutionSummary(verdict="OK", evidence_path="")
        assert classify_summary(s) == SummaryClassification.EVIDENCE_MISSING

    def test_scores_missing(self):
        s = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            quality_evaluations=[],
        )
        assert classify_summary(s) == SummaryClassification.SCORES_MISSING

    def test_taskcards_incomplete(self):
        s = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=5,
            taskcards_completed=3,
            taskcards_blocked=0,
            taskcards_rerouted=0,
            quality_evaluations=[QualityEvaluation(taskcard_id="TC-1", scores=[QualityScore(dimension="x", score=5)])],
        )
        assert classify_summary(s) == SummaryClassification.TASKCARDS_INCOMPLETE

    def test_contradictory(self):
        s = ExecutionSummary(
            verdict="EXECUTION_COMPLETE_VERIFIED",
            evidence_path="/tmp",
            taskcards_attempted=1,
            taskcards_completed=1,
            quality_evaluations=[QualityEvaluation(taskcard_id="TC-1", scores=[QualityScore(dimension="x", score=5)])],
            reroute_log=[{"reason": "test"}],
        )
        assert classify_summary(s) == SummaryClassification.CONTRADICTORY

    def test_structured_not_green_rerouted(self):
        s = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=2,
            taskcards_completed=1,
            taskcards_rerouted=1,
            quality_evaluations=[QualityEvaluation(taskcard_id="TC-1", scores=[QualityScore(dimension="x", score=5)])],
        )
        assert classify_summary(s) == SummaryClassification.STRUCTURED_NOT_GREEN

    def test_structured_not_green_failing_score(self):
        s = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=1,
            taskcards_completed=1,
            quality_evaluations=[
                QualityEvaluation(
                    taskcard_id="TC-1",
                    scores=[QualityScore(dimension="requirement_correctness", score=3)],
                ),
            ],
        )
        assert classify_summary(s) == SummaryClassification.STRUCTURED_NOT_GREEN

    def test_structured_all_green(self):
        s = ExecutionSummary(
            verdict="OK",
            evidence_path="/tmp",
            taskcards_attempted=1,
            taskcards_completed=1,
            quality_evaluations=[
                QualityEvaluation(
                    taskcard_id="TC-1",
                    scores=[QualityScore(dimension="requirement_correctness", score=5)],
                ),
            ],
        )
        assert classify_summary(s) == SummaryClassification.STRUCTURED_ALL_GREEN


class TestClassifyRawText:
    def test_empty(self):
        assert classify_raw_text("") == SummaryClassification.MISSING
        assert classify_raw_text(None) == SummaryClassification.MISSING

    def test_prose_only(self):
        assert classify_raw_text("This is just prose text.") == SummaryClassification.PROSE_ONLY

    def test_valid_yaml(self):
        result = classify_raw_text(VALID_YAML)
        assert result == SummaryClassification.STRUCTURED_ALL_GREEN
