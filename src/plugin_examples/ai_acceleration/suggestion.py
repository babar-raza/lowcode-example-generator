"""AiSuggestion model — AI-suggested type/method mapping for non-LowCode families.

All AI outputs enter as status=AI_DRAFT (non-authoritative).
PROBE_CONFIRMED requires a probe_evidence field.
No hardcoded model IDs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

# Path to the JSON Schema for AI suggestions
_SCHEMA_PATH = Path(__file__).resolve().parents[4] / "pipeline" / "schemas" / "ai-suggestion-schema.json"

_VALID_STATUSES = {
    "AI_DRAFT",
    "REFLECTION_CONFIRMED",
    "PROBE_CONFIRMED",
    "REJECTED_BY_VALIDATOR",
}

_PROBE_EVIDENCE_REQUIRED_STATUSES = {"PROBE_CONFIRMED"}


@dataclass
class AiSuggestion:
    """An AI-suggested plugin type/method mapping.

    Always enters the pipeline as AI_DRAFT.
    model may be a model identifier or the sentinel "MANUAL_MAPPING".
    """

    type_name: str
    method_name: str
    status: str = "AI_DRAFT"
    confidence: float = 0.0
    model: str = "MANUAL_MAPPING"
    probe_evidence: str | None = None
    rejection_reason: str | None = None
    rationale: str = ""
    extra: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in _VALID_STATUSES:
            raise ValueError(f"Invalid status '{self.status}'. Must be one of: {sorted(_VALID_STATUSES)}")
        if self.status in _PROBE_EVIDENCE_REQUIRED_STATUSES and not self.probe_evidence:
            raise ValueError(f"status='{self.status}' requires a non-empty probe_evidence field")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(f"confidence must be in [0.0, 1.0], got {self.confidence}")

    @classmethod
    def from_dict(cls, data: dict) -> AiSuggestion:
        """Construct an AiSuggestion from a raw dict (e.g. parsed from LLM response).

        Raises ValueError on schema violations.
        """
        return cls(
            type_name=data["type_name"],
            method_name=data["method_name"],
            status=data.get("status", "AI_DRAFT"),
            confidence=float(data.get("confidence", 0.0)),
            model=data.get("model", "MANUAL_MAPPING"),
            probe_evidence=data.get("probe_evidence"),
            rejection_reason=data.get("rejection_reason"),
            rationale=data.get("rationale", ""),
            extra={
                k: v
                for k, v in data.items()
                if k
                not in {
                    "type_name",
                    "method_name",
                    "status",
                    "confidence",
                    "model",
                    "probe_evidence",
                    "rejection_reason",
                    "rationale",
                }
            },
        )
