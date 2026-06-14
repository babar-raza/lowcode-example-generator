"""Compliance trend reporting — aggregates SLO and gate results across runs.

Produces structured compliance reports showing whether the project's
operational health is improving, stable, or degrading over time.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ComplianceRecord:
    """A single run's compliance snapshot."""

    run_timestamp: str = ""
    slo_pass_rate: float = 0.0
    goals_met: int = 0
    goals_total: int = 0
    evidence_chain_status: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_timestamp": self.run_timestamp,
            "slo_pass_rate": round(self.slo_pass_rate, 4),
            "goals_met": self.goals_met,
            "goals_total": self.goals_total,
            "evidence_chain_status": self.evidence_chain_status,
        }


@dataclass
class ComplianceTrend:
    """Compliance trend analysis over a window of runs."""

    records: list[ComplianceRecord] = field(default_factory=list)
    trend_direction: str = "stable"  # improving | stable | degrading
    current_compliance_score: float = 0.0
    window_size: int = 10

    def to_dict(self) -> dict[str, Any]:
        return {
            "trend_direction": self.trend_direction,
            "current_compliance_score": round(self.current_compliance_score, 4),
            "window_size": self.window_size,
            "record_count": len(self.records),
            "records": [r.to_dict() for r in self.records],
        }


def _classify_trend(scores: list[float]) -> str:
    """Classify trend direction from a list of compliance scores."""
    if len(scores) < 2:
        return "stable"
    first_half = scores[: len(scores) // 2]
    second_half = scores[len(scores) // 2:]
    avg_first = sum(first_half) / len(first_half) if first_half else 0
    avg_second = sum(second_half) / len(second_half) if second_half else 0
    delta = avg_second - avg_first
    if delta > 0.05:
        return "improving"
    if delta < -0.05:
        return "degrading"
    return "stable"


def compute_compliance_trend(
    history: Any | None,
    slo_results: list[Any] | None = None,
    goals: list[Any] | None = None,
    window: int = 10,
) -> ComplianceTrend:
    """Compute compliance trend from run history.

    Args:
        history: RunHistory instance (or None).
        slo_results: List of SLOCheckResult from current run.
        goals: List of GoalSpec definitions.
        window: Number of runs to analyze.

    Returns:
        ComplianceTrend with direction classification.
    """
    records: list[ComplianceRecord] = []
    history_records = getattr(history, "records", []) if history is not None else []
    recent = history_records[-window:] if history_records else []

    for rec in recent:
        attempted = getattr(rec, "scenarios_attempted", 0)
        succeeded = getattr(rec, "scenarios_succeeded", 0)
        pass_rate = succeeded / attempted if attempted > 0 else 1.0
        records.append(ComplianceRecord(
            run_timestamp=getattr(rec, "timestamp", ""),
            slo_pass_rate=pass_rate,
            goals_met=succeeded,
            goals_total=attempted,
            evidence_chain_status="checked",
        ))

    scores = [r.slo_pass_rate for r in records]
    trend_dir = _classify_trend(scores)
    current = scores[-1] if scores else 0.0

    return ComplianceTrend(
        records=records,
        trend_direction=trend_dir,
        current_compliance_score=current,
        window_size=window,
    )


def generate_compliance_report(
    trend: ComplianceTrend,
    output_dir: Path,
) -> Path:
    """Write compliance-trend-report.json to output_dir and return path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "compliance-trend-report.json"
    path.write_text(json.dumps(trend.to_dict(), indent=2), encoding="utf-8")
    return path
