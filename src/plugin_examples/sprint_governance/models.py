"""Core data models for the sprint governance autonomy loop."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IssueSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueLevel(StrEnum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class ClaimClassification(StrEnum):
    ACCEPTED_VERIFIED = "ACCEPTED_VERIFIED"
    ACCEPTED_WITH_LIMITATIONS = "ACCEPTED_WITH_LIMITATIONS"
    PARTIAL = "PARTIAL"
    UNVERIFIED = "UNVERIFIED"
    FAILED = "FAILED"
    STALE = "STALE"
    MISLEADING = "MISLEADING"
    DAMAGED_OR_REGRESSED = "DAMAGED_OR_REGRESSED"
    EXTERNAL_BLOCKED = "EXTERNAL_BLOCKED"


class TaskcardState(StrEnum):
    PROPOSED = "PROPOSED"
    READY = "READY"
    BLOCKED = "BLOCKED"
    IN_PROGRESS = "IN_PROGRESS"
    IMPLEMENTED = "IMPLEMENTED"
    VERIFIED = "VERIFIED"
    SCORED = "SCORED"
    REROUTED = "REROUTED"
    REWORKING = "REWORKING"
    REWORKED = "REWORKED"
    ACCEPTED = "ACCEPTED"
    ACCEPTED_WITH_LIMITATIONS = "ACCEPTED_WITH_LIMITATIONS"
    BLOCKED_EXTERNAL = "BLOCKED_EXTERNAL"
    DEFERRED_WITH_REASON = "DEFERRED_WITH_REASON"


class LoopStage(StrEnum):
    AUDIT = "AUDIT"
    HARDEN = "HARDEN"
    EXECUTE = "EXECUTE"
    DECIDE = "DECIDE"
    ACCEPT = "ACCEPT"
    ESCALATE = "ESCALATE"


class SummaryClassification(StrEnum):
    STRUCTURED_ALL_GREEN = "STRUCTURED_ALL_GREEN"
    STRUCTURED_NOT_GREEN = "STRUCTURED_NOT_GREEN"
    PROSE_ONLY = "PROSE_ONLY"
    MISSING = "MISSING"
    CONTRADICTORY = "CONTRADICTORY"
    EVIDENCE_MISSING = "EVIDENCE_MISSING"
    SCORES_MISSING = "SCORES_MISSING"
    TASKCARDS_INCOMPLETE = "TASKCARDS_INCOMPLETE"
    BLOCKED_EXTERNAL = "BLOCKED_EXTERNAL"


class EvidenceVerdict(StrEnum):
    STRONG = "STRONG"
    ADEQUATE_WITH_LIMITATIONS = "ADEQUATE_WITH_LIMITATIONS"
    WEAK = "WEAK"
    INSUFFICIENT = "INSUFFICIENT"
    MISLEADING = "MISLEADING"


class SprintVerdict(StrEnum):
    SPRINT_ALL_GREEN_VERIFIED = "SPRINT_ALL_GREEN_VERIFIED"
    SPRINT_ACCEPTED_WITH_LIMITATIONS = "SPRINT_ACCEPTED_WITH_LIMITATIONS"
    SPRINT_REQUIRES_PLAN_HARDENING = "SPRINT_REQUIRES_PLAN_HARDENING"
    SPRINT_REQUIRES_REEXECUTION = "SPRINT_REQUIRES_REEXECUTION"
    SPRINT_REQUIRES_EVIDENCE_REPAIR = "SPRINT_REQUIRES_EVIDENCE_REPAIR"
    SPRINT_BLOCKED_EXTERNAL = "SPRINT_BLOCKED_EXTERNAL"
    SPRINT_SUMMARY_INSUFFICIENT = "SPRINT_SUMMARY_INSUFFICIENT"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class Issue:
    """A single audit issue from Stage 1."""

    id: str
    level: IssueLevel
    severity: IssueSeverity
    title: str
    description: str = ""
    evidence: str = ""
    missing_evidence: str = ""
    root_cause: str = ""
    affected_files: list[str] = field(default_factory=list)
    affected_components: list[str] = field(default_factory=list)
    blocker: bool = False
    recurrence_risk: str = "medium"
    recommended_next_stage: str = ""
    claim: ClaimClassification = ClaimClassification.UNVERIFIED

    def to_dict(self) -> dict[str, Any]:
        return {
            "issue_id": self.id,
            "issue_level": str(self.level),
            "severity": str(self.severity),
            "title": self.title,
            "description": self.description,
            "evidence": self.evidence,
            "missing_evidence": self.missing_evidence,
            "root_cause": self.root_cause,
            "affected_files": self.affected_files,
            "affected_components": self.affected_components,
            "blocker": self.blocker,
            "recurrence_risk": self.recurrence_risk,
            "recommended_next_stage": self.recommended_next_stage,
            "claim": str(self.claim),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Issue:
        return cls(
            id=data.get("issue_id", data.get("id", "")),
            level=IssueLevel(data.get("issue_level", data.get("level", "L1"))),
            severity=IssueSeverity(data.get("severity", "medium")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            evidence=data.get("evidence", ""),
            missing_evidence=data.get("missing_evidence", ""),
            root_cause=data.get("root_cause", ""),
            affected_files=data.get("affected_files", []),
            affected_components=data.get("affected_components", []),
            blocker=data.get("blocker", False),
            recurrence_risk=data.get("recurrence_risk", "medium"),
            recommended_next_stage=data.get("recommended_next_stage", ""),
            claim=ClaimClassification(
                data.get("claim", "UNVERIFIED"),
            ),
        )


@dataclass
class QualityScore:
    """A single dimension score for a taskcard."""

    dimension: str
    score: int
    threshold: int = 4
    comment: str = ""

    def __post_init__(self) -> None:
        if not (1 <= self.score <= 5):
            msg = f"Score must be 1-5, got {self.score}"
            raise ValueError(msg)
        if self.threshold < 1 or self.threshold > 5:
            msg = f"Threshold must be 1-5, got {self.threshold}"
            raise ValueError(msg)

    @property
    def passes(self) -> bool:
        return self.score >= self.threshold

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "score": self.score,
            "threshold": self.threshold,
            "comment": self.comment,
            "passes": self.passes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualityScore:
        return cls(
            dimension=data["dimension"],
            score=data["score"],
            threshold=data.get("threshold", 4),
            comment=data.get("comment", ""),
        )


@dataclass
class QualityEvaluation:
    """Quality evaluation for a single taskcard across all dimensions."""

    taskcard_id: str
    scores: list[QualityScore] = field(default_factory=list)
    accepted: bool = False
    rerouted: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskcard_id": self.taskcard_id,
            "scores": [s.to_dict() for s in self.scores],
            "accepted": self.accepted,
            "rerouted": self.rerouted,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualityEvaluation:
        scores = [QualityScore.from_dict(s) for s in data.get("scores", [])]
        return cls(
            taskcard_id=data["taskcard_id"],
            scores=scores,
            accepted=data.get("accepted", False),
            rerouted=data.get("rerouted", False),
        )


@dataclass
class Taskcard:
    """A sprint governance taskcard."""

    id: str
    title: str
    state: TaskcardState = TaskcardState.PROPOSED
    source_issue_id: str = ""
    lane: str = "default"
    quality_scores: list[QualityScore] = field(default_factory=list)
    attempts: int = 0
    max_attempts: int = 3
    acceptance_criteria: str = ""
    evidence_output: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskcard_id": self.id,
            "title": self.title,
            "state": str(self.state),
            "source_issue_id": self.source_issue_id,
            "lane": self.lane,
            "quality_scores": [s.to_dict() for s in self.quality_scores],
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "acceptance_criteria": self.acceptance_criteria,
            "evidence_output": self.evidence_output,
            "history": self.history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Taskcard:
        scores = [
            QualityScore.from_dict(s) for s in data.get("quality_scores", [])
        ]
        return cls(
            id=data.get("taskcard_id", data.get("id", "")),
            title=data.get("title", ""),
            state=TaskcardState(data.get("state", "PROPOSED")),
            source_issue_id=data.get("source_issue_id", ""),
            lane=data.get("lane", "default"),
            quality_scores=scores,
            attempts=data.get("attempts", 0),
            max_attempts=data.get("max_attempts", 3),
            acceptance_criteria=data.get("acceptance_criteria", ""),
            evidence_output=data.get("evidence_output", ""),
            history=data.get("history", []),
        )


@dataclass
class LoopDecision:
    """A single loop controller decision."""

    current_stage: LoopStage
    next_stage: LoopStage
    reason: str = ""
    iteration: int = 0
    summary_classification: SummaryClassification = SummaryClassification.MISSING

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_stage": str(self.current_stage),
            "next_stage": str(self.next_stage),
            "reason": self.reason,
            "iteration": self.iteration,
            "summary_classification": str(self.summary_classification),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoopDecision:
        return cls(
            current_stage=LoopStage(data["current_stage"]),
            next_stage=LoopStage(data["next_stage"]),
            reason=data.get("reason", ""),
            iteration=data.get("iteration", 0),
            summary_classification=SummaryClassification(
                data.get("summary_classification", "MISSING"),
            ),
        )


@dataclass
class ExecutionSummary:
    """Parsed Stage 3 execution summary."""

    timestamp: str = ""
    verdict: str = ""
    taskcards_attempted: int = 0
    taskcards_completed: int = 0
    taskcards_blocked: int = 0
    taskcards_rerouted: int = 0
    issues: list[Issue] = field(default_factory=list)
    quality_evaluations: list[QualityEvaluation] = field(default_factory=list)
    evidence_path: str = ""
    reroute_log: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "verdict": self.verdict,
            "taskcards_attempted": self.taskcards_attempted,
            "taskcards_completed": self.taskcards_completed,
            "taskcards_blocked": self.taskcards_blocked,
            "taskcards_rerouted": self.taskcards_rerouted,
            "issues": [i.to_dict() for i in self.issues],
            "quality_evaluations": [e.to_dict() for e in self.quality_evaluations],
            "evidence_path": self.evidence_path,
            "reroute_log": self.reroute_log,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionSummary:
        issues = [Issue.from_dict(i) for i in data.get("issues", [])]
        evals = [
            QualityEvaluation.from_dict(e)
            for e in data.get("quality_evaluations", [])
        ]
        return cls(
            timestamp=data.get("timestamp", ""),
            verdict=data.get("verdict", ""),
            taskcards_attempted=data.get("taskcards_attempted", 0),
            taskcards_completed=data.get("taskcards_completed", 0),
            taskcards_blocked=data.get("taskcards_blocked", 0),
            taskcards_rerouted=data.get("taskcards_rerouted", 0),
            issues=issues,
            quality_evaluations=evals,
            evidence_path=data.get("evidence_path", ""),
            reroute_log=data.get("reroute_log", []),
            raw=data,
        )


@dataclass
class LoopState:
    """Persistent state for the post-sprint loop."""

    iteration: int = 0
    max_iterations: int = 3
    stage: LoopStage = LoopStage.AUDIT
    decisions: list[LoopDecision] = field(default_factory=list)
    taskcards: list[Taskcard] = field(default_factory=list)
    sprint_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "max_iterations": self.max_iterations,
            "stage": str(self.stage),
            "decisions": [d.to_dict() for d in self.decisions],
            "taskcards": [t.to_dict() for t in self.taskcards],
            "sprint_name": self.sprint_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LoopState:
        decisions = [LoopDecision.from_dict(d) for d in data.get("decisions", [])]
        taskcards = [Taskcard.from_dict(t) for t in data.get("taskcards", [])]
        return cls(
            iteration=data.get("iteration", 0),
            max_iterations=data.get("max_iterations", 3),
            stage=LoopStage(data.get("stage", "AUDIT")),
            decisions=decisions,
            taskcards=taskcards,
            sprint_name=data.get("sprint_name", ""),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> LoopState:
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except (json.JSONDecodeError, OSError):
            return cls()
