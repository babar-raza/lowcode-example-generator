"""Tests for plugin_examples.compliance.reporter."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from plugin_examples.compliance.reporter import (
    ComplianceRecord,
    ComplianceTrend,
    compute_compliance_trend,
    generate_compliance_report,
)


@dataclass
class FakeRecord:
    timestamp: str = "2026-06-13T00:00:00Z"
    scenarios_attempted: int = 10
    scenarios_succeeded: int = 9
    scenarios_blocked: int = 1
    verdict: str = "SPRINT_COMPLETE"


@dataclass
class FakeHistory:
    records: list[FakeRecord] = field(default_factory=list)


class TestComplianceRecord:
    def test_to_dict(self) -> None:
        r = ComplianceRecord(
            run_timestamp="2026-01-01",
            slo_pass_rate=0.95,
            goals_met=3,
            goals_total=4,
        )
        d = r.to_dict()
        assert d["slo_pass_rate"] == 0.95
        assert d["goals_met"] == 3


class TestComplianceTrend:
    def test_to_dict(self) -> None:
        t = ComplianceTrend(
            trend_direction="improving",
            current_compliance_score=0.92,
            window_size=10,
        )
        d = t.to_dict()
        assert d["trend_direction"] == "improving"
        assert d["record_count"] == 0


class TestComputeComplianceTrend:
    def test_stable_trend(self) -> None:
        history = FakeHistory(records=[
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=9),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=9),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=9),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=9),
        ])
        trend = compute_compliance_trend(history)
        assert trend.trend_direction == "stable"
        assert len(trend.records) == 4

    def test_improving_trend(self) -> None:
        history = FakeHistory(records=[
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=5),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=5),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=10),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=10),
        ])
        trend = compute_compliance_trend(history)
        assert trend.trend_direction == "improving"

    def test_degrading_trend(self) -> None:
        history = FakeHistory(records=[
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=10),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=10),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=3),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=3),
        ])
        trend = compute_compliance_trend(history)
        assert trend.trend_direction == "degrading"

    def test_empty_history(self) -> None:
        trend = compute_compliance_trend(None)
        assert trend.trend_direction == "stable"
        assert trend.current_compliance_score == 0.0
        assert len(trend.records) == 0

    def test_single_record(self) -> None:
        history = FakeHistory(records=[
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=8),
        ])
        trend = compute_compliance_trend(history)
        assert trend.trend_direction == "stable"
        assert trend.current_compliance_score == 0.8

    def test_window_limits(self) -> None:
        records = [FakeRecord(scenarios_attempted=10, scenarios_succeeded=9) for _ in range(20)]
        history = FakeHistory(records=records)
        trend = compute_compliance_trend(history, window=5)
        assert len(trend.records) == 5


class TestGenerateComplianceReport:
    def test_writes_report(self, tmp_path: Path) -> None:
        trend = ComplianceTrend(
            trend_direction="stable",
            current_compliance_score=0.9,
        )
        path = generate_compliance_report(trend, tmp_path)
        assert path.exists()
        assert "stable" in path.read_text(encoding="utf-8")

    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        output = tmp_path / "nested" / "dir"
        trend = ComplianceTrend()
        path = generate_compliance_report(trend, output)
        assert path.exists()
