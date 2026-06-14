"""Audit trail — links each action execution to the policy rule that permitted/blocked it.

Every action decision is recorded with:
- which policy rule matched
- which goals the action serves
- what evidence was produced
- the decision outcome (EXECUTE / DEFER / BLOCK)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class AuditEntry:
    """A single audit trail entry for an action decision."""

    timestamp: str = ""
    action_id: str = ""
    decision: str = ""  # EXECUTE | DEFER | BLOCK
    policy_rule: str = ""  # e.g., "gates.yml:approval_gated_types"
    goal_relevance: list[str] = field(default_factory=list)
    evidence_ref: str = ""  # path to handler result JSON
    detail: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "action_id": self.action_id,
            "decision": self.decision,
            "policy_rule": self.policy_rule,
            "goal_relevance": self.goal_relevance,
            "evidence_ref": self.evidence_ref,
            "detail": self.detail,
        }


class AuditTrail:
    """Accumulates audit entries during a pipeline run."""

    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def record(self, entry: AuditEntry) -> None:
        """Append an audit entry."""
        self._entries.append(entry)

    @property
    def entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def to_json(self) -> str:
        """Serialize the full audit trail as JSON."""
        return json.dumps(
            {"audit_trail": [e.to_dict() for e in self._entries]},
            indent=2,
        )

    def save(self, path: Path) -> None:
        """Persist audit trail to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> AuditTrail:
        """Load an audit trail from a JSON file."""
        trail = cls()
        if not path.exists():
            return trail
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry_data in data.get("audit_trail", []):
                trail.record(AuditEntry(
                    timestamp=entry_data.get("timestamp", ""),
                    action_id=entry_data.get("action_id", ""),
                    decision=entry_data.get("decision", ""),
                    policy_rule=entry_data.get("policy_rule", ""),
                    goal_relevance=entry_data.get("goal_relevance", []),
                    evidence_ref=entry_data.get("evidence_ref", ""),
                    detail=entry_data.get("detail", ""),
                ))
        except (json.JSONDecodeError, OSError):
            pass
        return trail
