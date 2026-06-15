"""Quality scoring for sprint governance taskcards."""

from __future__ import annotations

from plugin_examples.sprint_governance.models import (
    QualityEvaluation,
    QualityScore,
)

QUALITY_DIMENSIONS: list[str] = [
    "requirement_correctness",
    "implementation_correctness",
    "integration_completeness",
    "pipeline_compatibility",
    "governance_compliance",
    "evidence_completeness",
    "test_coverage",
    "validator_coverage",
    "repeatability",
    "idempotency",
    "downstream_consumer_readiness",
    "agentic_consumption_quality",
    "rollback_safety",
    "documentation_sync",
    "production_readiness",
]

REQUIRED_DIMENSIONS: frozenset[str] = frozenset({
    "requirement_correctness",
    "implementation_correctness",
    "integration_completeness",
    "pipeline_compatibility",
    "governance_compliance",
    "evidence_completeness",
    "test_coverage",
    "repeatability",
    "rollback_safety",
    "production_readiness",
})

ACCEPTANCE_THRESHOLD = 4


def score_taskcard(
    taskcard_id: str,
    dimension_scores: dict[str, int],
    threshold: int = ACCEPTANCE_THRESHOLD,
) -> QualityEvaluation:
    """Score a taskcard across provided dimensions.

    Args:
        taskcard_id: The taskcard being scored.
        dimension_scores: Mapping of dimension name to score (1-5).
        threshold: Minimum score for acceptance (default 4).

    Returns:
        QualityEvaluation with acceptance/reroute status.
    """
    scores: list[QualityScore] = []
    for dim, value in dimension_scores.items():
        dim_threshold = threshold if dim in REQUIRED_DIMENSIONS else 1
        scores.append(QualityScore(
            dimension=dim,
            score=value,
            threshold=dim_threshold,
        ))

    accepted = check_acceptance_from_scores(scores)
    rerouted = not accepted

    return QualityEvaluation(
        taskcard_id=taskcard_id,
        scores=scores,
        accepted=accepted,
        rerouted=rerouted,
    )


def check_acceptance(evaluation: QualityEvaluation) -> bool:
    """Check if a quality evaluation meets acceptance criteria.

    All required dimensions must score >= threshold.
    """
    return check_acceptance_from_scores(evaluation.scores)


def check_acceptance_from_scores(scores: list[QualityScore]) -> bool:
    """Check if all required dimension scores meet their thresholds."""
    return all(
        score.passes
        for score in scores
        if score.dimension in REQUIRED_DIMENSIONS
    )
