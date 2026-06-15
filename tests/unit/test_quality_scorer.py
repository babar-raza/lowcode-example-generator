"""Tests for sprint_governance.quality_scorer — quality rubric and scoring."""

from __future__ import annotations

import pytest

from plugin_examples.sprint_governance.models import QualityScore
from plugin_examples.sprint_governance.quality_scorer import (
    ACCEPTANCE_THRESHOLD,
    QUALITY_DIMENSIONS,
    REQUIRED_DIMENSIONS,
    check_acceptance,
    score_taskcard,
)


class TestQualityDimensions:
    def test_has_15_dimensions(self):
        assert len(QUALITY_DIMENSIONS) == 15

    def test_required_dimensions_subset(self):
        assert REQUIRED_DIMENSIONS.issubset(set(QUALITY_DIMENSIONS))

    def test_has_10_required_dimensions(self):
        assert len(REQUIRED_DIMENSIONS) == 10

    def test_acceptance_threshold_is_4(self):
        assert ACCEPTANCE_THRESHOLD == 4


class TestScoreTaskcard:
    def test_all_passing(self):
        scores = {dim: 5 for dim in REQUIRED_DIMENSIONS}
        ev = score_taskcard("TC-001", scores)
        assert ev.accepted is True
        assert ev.rerouted is False

    def test_one_failing_required(self):
        scores = {dim: 5 for dim in REQUIRED_DIMENSIONS}
        scores["requirement_correctness"] = 3
        ev = score_taskcard("TC-001", scores)
        assert ev.accepted is False
        assert ev.rerouted is True

    def test_boundary_score_exactly_4(self):
        scores = {dim: 4 for dim in REQUIRED_DIMENSIONS}
        ev = score_taskcard("TC-001", scores)
        assert ev.accepted is True

    def test_optional_dimension_below_threshold_accepted(self):
        scores = {dim: 5 for dim in REQUIRED_DIMENSIONS}
        scores["idempotency"] = 2  # Optional dimension
        ev = score_taskcard("TC-001", scores)
        assert ev.accepted is True

    def test_empty_scores(self):
        ev = score_taskcard("TC-001", {})
        assert ev.accepted is True  # No required dimensions present to fail

    def test_scores_objects_created(self):
        scores = {"requirement_correctness": 5, "idempotency": 3}
        ev = score_taskcard("TC-001", scores)
        assert len(ev.scores) == 2


class TestCheckAcceptance:
    def test_all_pass(self):
        from plugin_examples.sprint_governance.models import QualityEvaluation

        ev = QualityEvaluation(
            taskcard_id="TC-1",
            scores=[
                QualityScore(dimension="requirement_correctness", score=5),
                QualityScore(dimension="implementation_correctness", score=4),
            ],
        )
        assert check_acceptance(ev) is True

    def test_one_fail(self):
        from plugin_examples.sprint_governance.models import QualityEvaluation

        ev = QualityEvaluation(
            taskcard_id="TC-1",
            scores=[
                QualityScore(dimension="requirement_correctness", score=3),
            ],
        )
        assert check_acceptance(ev) is False
