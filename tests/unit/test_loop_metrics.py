"""Tests for LoopMetrics observable metrics in planner_loop."""

from __future__ import annotations

from plugin_examples.planner_loop import LoopMetrics, LoopResult


class TestLoopMetrics:
    def test_default_values_all_zero(self) -> None:
        m = LoopMetrics()
        assert m.total_cycles == 0
        assert m.total_duration_ms == 0
        assert m.actions_executed == 0
        assert m.actions_deferred == 0
        assert m.handler_errors == 0
        assert m.deprioritized_count == 0
        assert m.fingerprint_changes == 0
        assert m.idempotent_stops == 0

    def test_to_dict_has_expected_keys(self) -> None:
        m = LoopMetrics()
        d = m.to_dict()
        expected_keys = {
            "total_cycles",
            "total_duration_ms",
            "actions_executed",
            "actions_deferred",
            "handler_errors",
            "deprioritized_count",
            "fingerprint_changes",
            "idempotent_stops",
        }
        assert set(d.keys()) == expected_keys

    def test_to_dict_reflects_mutations(self) -> None:
        m = LoopMetrics()
        m.handler_errors = 3
        m.total_cycles = 5
        d = m.to_dict()
        assert d["handler_errors"] == 3
        assert d["total_cycles"] == 5


class TestLoopResultMetrics:
    def test_loop_result_includes_metrics_in_dict(self) -> None:
        lr = LoopResult()
        d = lr.to_dict()
        assert "metrics" in d
        assert isinstance(d["metrics"], dict)
        assert d["metrics"]["total_cycles"] == 0

    def test_loop_result_metrics_is_loop_metrics_instance(self) -> None:
        lr = LoopResult()
        assert isinstance(lr.metrics, LoopMetrics)
