"""Tests for plugin_examples.reliability.sli_emitter."""

from __future__ import annotations

from dataclasses import dataclass

from plugin_examples.reliability.sli_emitter import (
    HandlerTimer,
    SLIEvent,
    compute_slis_from_loop_metrics,
    emit_handler_sli,
    emit_sli,
)


class TestSLIEvent:
    def test_auto_timestamp(self) -> None:
        event = SLIEvent(metric_name="test", value=1.0)
        assert event.timestamp  # auto-populated

    def test_to_dict(self) -> None:
        event = SLIEvent(metric_name="m", value=42.0, labels={"a": "b"})
        d = event.to_dict()
        assert d["metric_name"] == "m"
        assert d["value"] == 42.0
        assert d["labels"] == {"a": "b"}

    def test_explicit_timestamp(self) -> None:
        event = SLIEvent(metric_name="m", value=1.0, timestamp="2026-01-01T00:00:00Z")
        assert event.timestamp == "2026-01-01T00:00:00Z"


class TestEmitSli:
    def test_returns_event(self) -> None:
        event = emit_sli("test_metric", 99.5, env="prod")
        assert event.metric_name == "test_metric"
        assert event.value == 99.5
        assert event.labels == {"env": "prod"}

    def test_no_labels(self) -> None:
        event = emit_sli("bare", 0.0)
        assert event.labels == {}


class TestEmitHandlerSli:
    def test_success(self) -> None:
        event = emit_handler_sli("CONSERVATION_CHECK", 150, True)
        assert event.labels["handler_id"] == "CONSERVATION_CHECK"
        assert event.labels["success"] == "true"
        assert event.value == 150

    def test_failure(self) -> None:
        event = emit_handler_sli("BLOCKER_RECHECK", 300, False)
        assert event.labels["success"] == "false"


class TestComputeSLIsFromLoopMetrics:
    def test_basic_metrics(self) -> None:
        @dataclass
        class FakeMetrics:
            actions_executed: int = 10
            handler_errors: int = 2
            total_duration_ms: int = 5000
            total_cycles: int = 3

        events = compute_slis_from_loop_metrics(FakeMetrics())
        metrics_by_name = {e.metric_name: e for e in events}
        assert "handler_error_rate" in metrics_by_name
        assert "avg_cycle_duration_ms" in metrics_by_name
        assert "actions_per_cycle" in metrics_by_name
        # error_rate = 2 / (10+2) = 0.1667
        assert abs(metrics_by_name["handler_error_rate"].value - 2 / 12) < 0.01

    def test_zero_cycles(self) -> None:
        @dataclass
        class FakeMetrics:
            actions_executed: int = 0
            handler_errors: int = 0
            total_duration_ms: int = 0
            total_cycles: int = 0

        events = compute_slis_from_loop_metrics(FakeMetrics())
        metrics_by_name = {e.metric_name: e for e in events}
        assert metrics_by_name["avg_cycle_duration_ms"].value == 0.0
        assert metrics_by_name["actions_per_cycle"].value == 0.0


class TestHandlerTimer:
    def test_success_timing(self) -> None:
        with HandlerTimer("test_handler") as timer:
            pass
        assert timer.success is True
        assert timer.duration_ms >= 0
        assert timer.sli_event is not None
        assert timer.sli_event.labels["success"] == "true"

    def test_failure_timing(self) -> None:
        try:
            with HandlerTimer("fail_handler") as timer:
                raise ValueError("boom")
        except ValueError:
            pass
        assert timer.success is False
        assert timer.sli_event is not None
        assert timer.sli_event.labels["success"] == "false"
