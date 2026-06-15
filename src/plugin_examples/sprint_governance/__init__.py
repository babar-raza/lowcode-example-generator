"""Sprint governance: autonomous post-sprint control loop machinery.

Provides summary parsing, quality scoring, taskcard state machine,
loop controller, evidence bundle validation, and project adapter.
"""

from __future__ import annotations

from plugin_examples.sprint_governance.evidence_bundle import (
    create_bundle_manifest,
    validate_bundle,
    validate_manifest_vs_contents,
)
from plugin_examples.sprint_governance.loop_controller import (
    classify_and_decide,
    load_loop_state,
    save_loop_state,
)
from plugin_examples.sprint_governance.models import (
    ClaimClassification,
    EvidenceVerdict,
    ExecutionSummary,
    Issue,
    IssueLevel,
    IssueSeverity,
    LoopDecision,
    LoopStage,
    LoopState,
    QualityEvaluation,
    QualityScore,
    SprintVerdict,
    SummaryClassification,
    Taskcard,
    TaskcardState,
)
from plugin_examples.sprint_governance.quality_scorer import (
    QUALITY_DIMENSIONS,
    check_acceptance,
    score_taskcard,
)
from plugin_examples.sprint_governance.summary_parser import (
    classify_summary,
    parse_summary,
    validate_summary_schema,
)
from plugin_examples.sprint_governance.taskcard_fsm import (
    TERMINAL_STATES,
    VALID_TRANSITIONS,
    transition,
)

__all__ = [
    "QUALITY_DIMENSIONS",
    "TERMINAL_STATES",
    "VALID_TRANSITIONS",
    "ClaimClassification",
    "EvidenceVerdict",
    "ExecutionSummary",
    "Issue",
    "IssueLevel",
    "IssueSeverity",
    "LoopDecision",
    "LoopStage",
    "LoopState",
    "QualityEvaluation",
    "QualityScore",
    "SprintVerdict",
    "SummaryClassification",
    "Taskcard",
    "TaskcardState",
    "check_acceptance",
    "classify_and_decide",
    "classify_summary",
    "create_bundle_manifest",
    "load_loop_state",
    "parse_summary",
    "save_loop_state",
    "score_taskcard",
    "transition",
    "validate_bundle",
    "validate_manifest_vs_contents",
    "validate_summary_schema",
]
