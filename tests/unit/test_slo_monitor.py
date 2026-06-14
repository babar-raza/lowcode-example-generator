"""Tests for plugin_examples.reliability.slo_monitor."""

from __future__ import annotations

from dataclasses import dataclass, field

from plugin_examples.reliability.slo_monitor import (
    SLOCheckResult,
    check_slos,
    slo_summary,
)

# ---------------------------------------------------------------------------
# Fake data models (avoid importing real ones to keep tests isolated)
# ---------------------------------------------------------------------------


@dataclass
class FakeSLO:
    id: str = ""
    metric: str = ""
    target: float = 0.0
    window_runs: int = 10
    severity: str = "warning"


@dataclass
class FakeRecord:
    family: str = "__loop__"
    verdict: str = "SPRINT_COMPLETE"
    scenarios_attempted: int = 10
    scenarios_succeeded: int = 9
    scenarios_blocked: int = 1
    error_types: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class FakeHistory:
    records: list[FakeRecord] = field(default_factory=list)


@dataclass
class FakeMetrics:
    actions_executed: int = 10
    handler_errors: int = 1
    total_duration_ms: int = 5000
    total_cycles: int = 3


# ---------------------------------------------------------------------------
# SLOCheckResult
# ---------------------------------------------------------------------------


class TestSLOCheckResult:
    def test_to_dict(self) -> None:
        r = SLOCheckResult(
            slo_id="s1", metric="m", target=0.95, actual=0.97,
            passed=True, severity="critical", window_runs=10,
        )
        d = r.to_dict()
        assert d["slo_id"] == "s1"
        assert d["passed"] is True
        assert d["actual"] == 0.97


# ---------------------------------------------------------------------------
# check_slos
# ---------------------------------------------------------------------------


class TestCheckSLOs:
    def test_build_pass_rate_met(self) -> None:
        slos = [FakeSLO(id="s1", metric="build_pass_rate", target=0.80)]
        history = FakeHistory(records=[
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=9),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=8),
        ])
        results = check_slos(slos, history)
        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].actual == 17 / 20  # 0.85

    def test_build_pass_rate_violated(self) -> None:
        slos = [FakeSLO(id="s1", metric="build_pass_rate", target=0.95)]
        history = FakeHistory(records=[
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=5),
        ])
        results = check_slos(slos, history)
        assert results[0].passed is False

    def test_run_pass_rate(self) -> None:
        slos = [FakeSLO(id="s1", metric="run_pass_rate", target=0.50)]
        history = FakeHistory(records=[
            FakeRecord(verdict="SPRINT_COMPLETE"),
            FakeRecord(verdict="FAILED"),
            FakeRecord(verdict="SPRINT_COMPLETE"),
        ])
        results = check_slos(slos, history)
        assert results[0].passed is True
        assert abs(results[0].actual - 2 / 3) < 0.01

    def test_handler_error_rate_from_metrics(self) -> None:
        slos = [FakeSLO(id="s1", metric="handler_error_rate", target=0.10)]
        metrics = FakeMetrics(actions_executed=10, handler_errors=1)
        results = check_slos(slos, None, current_metrics=metrics)
        assert results[0].passed is True
        assert abs(results[0].actual - 1 / 11) < 0.01

    def test_handler_error_rate_violated(self) -> None:
        slos = [FakeSLO(id="s1", metric="handler_error_rate", target=0.05)]
        metrics = FakeMetrics(actions_executed=5, handler_errors=5)
        results = check_slos(slos, None, current_metrics=metrics)
        assert results[0].passed is False

    def test_avg_cycle_duration(self) -> None:
        slos = [FakeSLO(id="s1", metric="avg_cycle_duration_ms", target=30000)]
        metrics = FakeMetrics(total_duration_ms=9000, total_cycles=3)
        results = check_slos(slos, None, current_metrics=metrics)
        assert results[0].passed is True
        assert results[0].actual == 3000.0

    def test_insufficient_data(self) -> None:
        slos = [FakeSLO(id="s1", metric="build_pass_rate", target=0.95)]
        results = check_slos(slos, None)
        assert results[0].passed is True
        assert "insufficient" in results[0].detail

    def test_no_history_no_metrics(self) -> None:
        slos = [FakeSLO(id="s1", metric="handler_error_rate", target=0.05)]
        results = check_slos(slos, None, current_metrics=None)
        assert results[0].passed is True

    def test_window_limits_records(self) -> None:
        slos = [FakeSLO(id="s1", metric="build_pass_rate", target=0.95, window_runs=2)]
        history = FakeHistory(records=[
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=1),  # old, out of window
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=10),
            FakeRecord(scenarios_attempted=10, scenarios_succeeded=10),
        ])
        results = check_slos(slos, history)
        assert results[0].passed is True  # only last 2 records: 100%

    def test_multiple_slos(self) -> None:
        slos = [
            FakeSLO(id="s1", metric="build_pass_rate", target=0.50),
            FakeSLO(id="s2", metric="handler_error_rate", target=0.10),
        ]
        history = FakeHistory(records=[FakeRecord(scenarios_attempted=10, scenarios_succeeded=9)])
        metrics = FakeMetrics(actions_executed=10, handler_errors=0)
        results = check_slos(slos, history, current_metrics=metrics)
        assert len(results) == 2
        assert all(r.passed for r in results)


# ---------------------------------------------------------------------------
# slo_summary
# ---------------------------------------------------------------------------


class TestSLOSummary:
    def test_all_passed(self) -> None:
        results = [
            SLOCheckResult("s1", "m", 0.9, 0.95, True, "critical", 10),
            SLOCheckResult("s2", "m", 0.8, 0.85, True, "warning", 10),
        ]
        s = slo_summary(results)
        assert s["total"] == 2
        assert s["passed"] == 2
        assert s["failed"] == 0
        assert s["all_passed"] is True

    def test_with_failures(self) -> None:
        results = [
            SLOCheckResult("s1", "m", 0.9, 0.5, False, "critical", 10),
            SLOCheckResult("s2", "m", 0.8, 0.85, True, "warning", 10),
        ]
        s = slo_summary(results)
        assert s["failed"] == 1
        assert s["critical_failures"] == 1
        assert s["all_passed"] is False

    def test_empty(self) -> None:
        s = slo_summary([])
        assert s["total"] == 0
        assert s["all_passed"] is True
