"""Gate result models for the pipeline validation engine."""

from __future__ import annotations

from dataclasses import dataclass, field


# Canonical verdict taxonomy — these are the ONLY allowed verdict strings.
VERDICTS = frozenset({
    "SOURCE_OF_TRUTH_PROVEN_ONLY",
    "DATA_FLOW_PROTOTYPE_ONLY",
    "BLOCKED_SOURCE_OF_TRUTH",
    "BLOCKED_FIXTURE_DISCOVERY",
    "BLOCKED_SCENARIO_PLANNING",
    "BLOCKED_GENERATION",
    "BLOCKED_RESTORE_FAILED",
    "BLOCKED_BUILD_FAILED",
    "BLOCKED_RUN_FAILED",
    "BLOCKED_OUTPUT_VALIDATION_FAILED",
    "BLOCKED_REVIEWER_UNAVAILABLE",
    "BLOCKED_REVIEWER_FAILED",
    "BLOCKED_NO_PUBLISHABLE_EXAMPLES",
    "PARTIAL_PR_DRY_RUN_READY",
    "PARTIAL_PR_READY",
    "PR_DRY_RUN_READY",
    "PR_READY",
    "FULL_E2E_PASSED",
})

# Canonical status values for gate results.
GATE_STATUSES = frozenset({
    "passed",
    "failed",
    "blocked",
    "skipped",
    "degraded",
    "not_applicable",
})


@dataclass
class GateResult:
    """Result of a single pipeline gate check."""

    gate_id: str
    name: str
    status: str  # One of GATE_STATUSES
    required: bool
    evidence_files: list[str] = field(default_factory=list)
    failure_reason: str | None = None
    downstream_blocked: list[str] = field(default_factory=list)
    stage_name: str = ""


@dataclass
class GateVerdict:
    """Aggregate verdict from all gate checks."""

    gates: list[GateResult] = field(default_factory=list)
    verdict: str = "DATA_FLOW_PROTOTYPE_ONLY"
    publishable: bool = False
    all_required_passed: bool = False
    blocking_gates: list[str] = field(default_factory=list)
