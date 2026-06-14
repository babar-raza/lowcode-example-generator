"""Tests for SLO auto-remediation — TC-S4-10."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from plugin_examples.reliability.slo_remediator import (
    RemediationAction,
    apply_remediations,
    compute_remediations,
)

# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


@dataclass
class FakeSLOResult:
    slo_id: str = ""
    metric: str = ""
    target: float = 0.0
    actual: float = 0.0
    passed: bool = True
    severity: str = "warning"


@dataclass
class FakeGatePolicy:
    deprioritization_threshold: int = 3


class FakeAuditTrail:
    def __init__(self):
        self.entries = []

    def record(self, entry):
        self.entries.append(entry)


# ---------------------------------------------------------------------------
# compute_remediations tests
# ---------------------------------------------------------------------------


class TestComputeRemediations:

    def test_no_remediations_when_all_pass(self):
        results = [
            FakeSLOResult(slo_id="slo1", passed=True),
            FakeSLOResult(slo_id="slo2", passed=True),
        ]
        assert compute_remediations(results) == []

    def test_critical_violation_produces_deprioritize(self):
        results = [
            FakeSLOResult(
                slo_id="slo_build_success",
                metric="build_pass_rate",
                target=0.95,
                actual=0.70,
                passed=False,
                severity="critical",
            ),
        ]
        remediations = compute_remediations(results)
        assert len(remediations) == 1
        assert remediations[0].action == "deprioritize_failing"
        assert remediations[0].slo_id == "slo_build_success"
        assert "critical" in remediations[0].reason.lower() or "Critical" in remediations[0].reason

    def test_warning_error_violation_reduces_concurrency(self):
        results = [
            FakeSLOResult(
                slo_id="slo_handler_reliability",
                metric="handler_error_rate",
                target=0.05,
                actual=0.15,
                passed=False,
                severity="warning",
            ),
        ]
        remediations = compute_remediations(results)
        assert len(remediations) == 1
        assert remediations[0].action == "reduce_concurrency"
        assert remediations[0].parameters["suggested_max_cycles"] == 3

    def test_warning_non_error_violation_extends_window(self):
        results = [
            FakeSLOResult(
                slo_id="slo_run_success",
                metric="run_pass_rate",
                target=0.80,
                actual=0.60,
                passed=False,
                severity="warning",
            ),
        ]
        remediations = compute_remediations(results)
        assert len(remediations) == 1
        assert remediations[0].action == "extend_window"
        assert remediations[0].parameters["extend_by_runs"] == 5

    def test_info_violation_advisory_only(self):
        results = [
            FakeSLOResult(
                slo_id="slo_cycle_duration",
                metric="avg_cycle_duration_ms",
                target=30000,
                actual=45000,
                passed=False,
                severity="info",
            ),
        ]
        remediations = compute_remediations(results)
        assert len(remediations) == 1
        assert remediations[0].action == "alert"

    def test_multiple_violations_produce_multiple_actions(self):
        results = [
            FakeSLOResult(slo_id="s1", metric="build_pass_rate", passed=False, severity="critical", actual=0.5, target=0.95),
            FakeSLOResult(slo_id="s2", metric="handler_error_rate", passed=False, severity="warning", actual=0.2, target=0.05),
            FakeSLOResult(slo_id="s3", passed=True),
        ]
        remediations = compute_remediations(results)
        assert len(remediations) == 2
        actions = {r.action for r in remediations}
        assert "deprioritize_failing" in actions
        assert "reduce_concurrency" in actions

    def test_gate_policy_threshold_used(self):
        results = [
            FakeSLOResult(slo_id="s1", metric="build_pass_rate", passed=False, severity="critical", actual=0.5, target=0.95),
        ]
        policy = FakeGatePolicy(deprioritization_threshold=5)
        remediations = compute_remediations(results, gate_policy=policy)
        assert remediations[0].parameters["failure_threshold"] == 5


# ---------------------------------------------------------------------------
# apply_remediations tests
# ---------------------------------------------------------------------------


class TestApplyRemediations:

    def test_deprioritize_lowers_threshold(self):
        config = {"deprioritization_threshold": 3, "max_cycles": 5}
        remediations = [
            RemediationAction(slo_id="s1", action="deprioritize_failing",
                              parameters={"failure_threshold": 3}),
        ]
        result = apply_remediations(remediations, config)
        assert result["deprioritization_threshold"] == 2

    def test_reduce_concurrency_caps_max_cycles(self):
        config = {"max_cycles": 5}
        remediations = [
            RemediationAction(slo_id="s1", action="reduce_concurrency",
                              parameters={"suggested_max_cycles": 3}),
        ]
        result = apply_remediations(remediations, config)
        assert result["max_cycles"] == 3

    def test_extend_window_increases_override(self):
        config = {"slo_window_override": 10}
        remediations = [
            RemediationAction(slo_id="s1", action="extend_window",
                              parameters={"extend_by_runs": 5}),
        ]
        result = apply_remediations(remediations, config)
        assert result["slo_window_override"] == 15

    def test_alert_no_config_change(self):
        config = {"max_cycles": 5}
        remediations = [
            RemediationAction(slo_id="s1", action="alert", parameters={}),
        ]
        result = apply_remediations(remediations, config)
        assert result == {"max_cycles": 5}

    def test_apply_records_audit_entries(self):
        config = {"max_cycles": 5}
        audit = FakeAuditTrail()
        remediations = [
            RemediationAction(slo_id="s1", action="reduce_concurrency",
                              parameters={"suggested_max_cycles": 3},
                              reason="test"),
            RemediationAction(slo_id="s2", action="alert", parameters={},
                              reason="advisory"),
        ]
        apply_remediations(remediations, config, audit=audit)
        assert len(audit.entries) == 2

    def test_remediations_are_serializable(self):
        rem = RemediationAction(
            slo_id="slo1",
            action="deprioritize_failing",
            parameters={"failure_threshold": 3, "metric": "build_pass_rate"},
            reason="test",
        )
        d = rem.to_dict()
        # Must be JSON-serializable
        serialized = __import__("json").dumps(d)
        assert "slo1" in serialized

    def test_deprioritize_threshold_floor_is_1(self):
        config = {"deprioritization_threshold": 1}
        remediations = [
            RemediationAction(slo_id="s1", action="deprioritize_failing",
                              parameters={"failure_threshold": 1}),
        ]
        result = apply_remediations(remediations, config)
        assert result["deprioritization_threshold"] >= 1
