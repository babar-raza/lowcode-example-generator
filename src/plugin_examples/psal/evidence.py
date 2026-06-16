"""Evidence packaging — per-family and aggregate evidence for PSAL runs."""

from __future__ import annotations

import datetime
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FamilyExecutionRecord:
    """Record for a single family's PSAL execution."""

    family: str
    terminal_state: str  # ACCEPTED, ACCEPTED_WITH_LIMITATIONS, BLOCKED_EXTERNAL, ESCALATED, ERROR_TERMINAL
    iterations: int = 0
    verdict: str = ""
    sufficiency_status: str = ""
    ready_scenarios: int = 0
    blocked_scenarios: int = 0
    total_registry_entries: int = 0
    error: str | None = None
    duration_ms: int = 0
    decisions: list[dict] = field(default_factory=list)
    # Diagnostic fields (TC-PSAL-19) — populated for ESCALATED families
    diagnostic_category: str = ""
    suggested_action: str = ""
    registry_summary: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AllFamiliesReport:
    """Aggregate report for all families in a PSAL run."""

    records: dict[str, FamilyExecutionRecord] = field(default_factory=dict)
    started_at: str = ""
    completed_at: str = ""

    @property
    def total_families(self) -> int:
        return len(self.records)

    @property
    def accepted_count(self) -> int:
        return sum(
            1 for r in self.records.values()
            if r.terminal_state in ("ACCEPTED", "ACCEPTED_WITH_LIMITATIONS")
        )

    @property
    def blocked_count(self) -> int:
        return sum(
            1 for r in self.records.values()
            if r.terminal_state == "BLOCKED_EXTERNAL"
        )

    @property
    def escalated_count(self) -> int:
        return sum(
            1 for r in self.records.values()
            if r.terminal_state == "ESCALATED"
        )

    @property
    def error_count(self) -> int:
        return sum(
            1 for r in self.records.values()
            if r.terminal_state == "ERROR_TERMINAL"
        )


def write_family_evidence(
    record: FamilyExecutionRecord,
    evidence_dir: Path,
) -> None:
    """Write per-family evidence files."""
    family_dir = evidence_dir / record.family
    family_dir.mkdir(parents=True, exist_ok=True)

    # Execution record
    (family_dir / "execution-record.json").write_text(
        json.dumps(record.to_dict(), indent=2), encoding="utf-8"
    )

    # Terminal classification
    classification = {
        "family": record.family,
        "terminal_state": record.terminal_state,
        "verdict": record.verdict,
        "sufficiency_status": record.sufficiency_status,
        "iterations": record.iterations,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
    }
    (family_dir / "terminal-classification.json").write_text(
        json.dumps(classification, indent=2), encoding="utf-8"
    )


def write_aggregate_evidence(
    report: AllFamiliesReport,
    target_families: list[str],
    evidence_dir: Path,
) -> None:
    """Write aggregate evidence files for the full PSAL run."""
    evidence_dir.mkdir(parents=True, exist_ok=True)

    # All-families summary
    summary = {
        "started_at": report.started_at,
        "completed_at": report.completed_at,
        "total_families": report.total_families,
        "accepted": report.accepted_count,
        "blocked": report.blocked_count,
        "escalated": report.escalated_count,
        "errors": report.error_count,
        "families": {
            fam: rec.to_dict() for fam, rec in report.records.items()
        },
    }
    (evidence_dir / "all-families-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    # Family matrix (compact)
    matrix = {
        fam: {
            "terminal_state": rec.terminal_state,
            "iterations": rec.iterations,
            "verdict": rec.verdict,
        }
        for fam, rec in report.records.items()
    }
    (evidence_dir / "family-matrix.json").write_text(
        json.dumps(matrix, indent=2), encoding="utf-8"
    )

    # Completeness assertion
    processed = sorted(report.records.keys())
    missing = sorted(set(target_families) - set(processed))
    assertion = {
        "target_families": sorted(target_families),
        "processed_families": processed,
        "missing_families": missing,
        "target_count": len(target_families),
        "processed_count": len(processed),
        "passed": len(missing) == 0,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
    }
    (evidence_dir / "completeness-assertion.json").write_text(
        json.dumps(assertion, indent=2), encoding="utf-8"
    )
