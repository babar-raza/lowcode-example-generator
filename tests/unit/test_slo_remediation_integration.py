"""End-to-end integration tests for SLO remediation path — TC-S4-H4.

These tests use the real SLOCheckResult class from slo_monitor (not mocks)
to verify the full path: real SLOCheckResult → compute_remediations() →
RemediationAction → apply_remediations() → loop_config modification.
"""

from __future__ import annotations

from plugin_examples.reliability.slo_monitor import SLOCheckResult
from plugin_examples.reliability.slo_remediator import (
    RemediationAction,
    apply_remediations,
    compute_remediations,
)


def _make_critical_violation() -> SLOCheckResult:
    """Build a real SLOCheckResult representing a critical SLO violation."""
    return SLOCheckResult(
        slo_id="slo_build_success",
        metric="build_pass_rate",
        target=0.9,
        actual=0.4,
        passed=False,
        severity="critical",
        window_runs=10,
        detail="VIOLATED: 0.4000 vs target 0.9",
    )


def _make_warning_error_violation() -> SLOCheckResult:
    """Build a real SLOCheckResult for a warning-severity handler error rate violation."""
    return SLOCheckResult(
        slo_id="slo_handler_reliability",
        metric="handler_error_rate",
        target=0.05,
        actual=0.25,
        passed=False,
        severity="warning",
        window_runs=5,
        detail="VIOLATED: 0.2500 vs target 0.05",
    )


def _make_warning_run_violation() -> SLOCheckResult:
    """Build a real SLOCheckResult for a warning-severity run pass rate violation."""
    return SLOCheckResult(
        slo_id="slo_run_success",
        metric="run_pass_rate",
        target=0.8,
        actual=0.6,
        passed=False,
        severity="warning",
        window_runs=10,
        detail="VIOLATED: 0.6000 vs target 0.8",
    )


def _make_info_violation() -> SLOCheckResult:
    """Build a real SLOCheckResult for an info-severity cycle duration violation."""
    return SLOCheckResult(
        slo_id="slo_cycle_duration",
        metric="avg_cycle_duration_ms",
        target=5000.0,
        actual=12000.0,
        passed=False,
        severity="info",
        window_runs=5,
        detail="VIOLATED: 12000.0000 vs target 5000.0",
    )


def _make_passing() -> SLOCheckResult:
    """Build a real SLOCheckResult that is passing (should not generate remediation)."""
    return SLOCheckResult(
        slo_id="slo_build_success",
        metric="build_pass_rate",
        target=0.9,
        actual=0.95,
        passed=True,
        severity="critical",
        window_runs=10,
        detail="MET: 0.9500 vs target 0.9",
    )


class TestRealSLOCheckResultToRemediation:
    """Verify compute_remediations handles real SLOCheckResult objects correctly."""

    def test_critical_violation_produces_deprioritize_action(self):
        result = _make_critical_violation()
        remediations = compute_remediations([result])
        assert len(remediations) == 1
        assert remediations[0].action == "deprioritize_failing"
        assert remediations[0].slo_id == "slo_build_success"
        assert isinstance(remediations[0], RemediationAction)

    def test_warning_error_violation_produces_reduce_concurrency(self):
        result = _make_warning_error_violation()
        remediations = compute_remediations([result])
        assert len(remediations) == 1
        assert remediations[0].action == "reduce_concurrency"
        assert remediations[0].slo_id == "slo_handler_reliability"

    def test_warning_run_violation_produces_extend_window(self):
        result = _make_warning_run_violation()
        remediations = compute_remediations([result])
        assert len(remediations) == 1
        assert remediations[0].action == "extend_window"

    def test_info_violation_produces_alert_only(self):
        result = _make_info_violation()
        remediations = compute_remediations([result])
        assert len(remediations) == 1
        assert remediations[0].action == "alert"

    def test_passing_slo_produces_no_remediation(self):
        result = _make_passing()
        remediations = compute_remediations([result])
        assert remediations == []

    def test_mixed_results_only_remediate_failures(self):
        results = [_make_passing(), _make_critical_violation(), _make_info_violation()]
        remediations = compute_remediations(results)
        # 2 failures (critical + info), 1 passing → 2 remediations
        assert len(remediations) == 2
        actions = {r.action for r in remediations}
        assert "deprioritize_failing" in actions
        assert "alert" in actions


class TestApplyRemediationsWithRealResults:
    """Verify apply_remediations modifies loop_config correctly using real SLOCheckResult chain."""

    def test_critical_violation_lowers_deprioritization_threshold(self):
        result = _make_critical_violation()
        remediations = compute_remediations([result])
        config = {"deprioritization_threshold": 3, "max_cycles": 5}
        updated = apply_remediations(remediations, config)
        # deprioritize_failing lowers the threshold by 1
        assert updated["deprioritization_threshold"] < 3

    def test_warning_error_violation_reduces_max_cycles(self):
        result = _make_warning_error_violation()
        remediations = compute_remediations([result])
        config = {"deprioritization_threshold": 3, "max_cycles": 10}
        updated = apply_remediations(remediations, config)
        assert updated["max_cycles"] <= 3  # reduce_concurrency sets suggested_max_cycles=3

    def test_info_violation_does_not_modify_config(self):
        result = _make_info_violation()
        remediations = compute_remediations([result])
        config = {"deprioritization_threshold": 3, "max_cycles": 5}
        original_config = dict(config)
        updated = apply_remediations(remediations, config)
        # alert action adds no config changes
        assert updated.get("deprioritization_threshold") == original_config["deprioritization_threshold"]
        assert updated.get("max_cycles") == original_config["max_cycles"]

    def test_remediations_are_json_serializable(self):
        import json
        result = _make_critical_violation()
        remediations = compute_remediations([result])
        for r in remediations:
            # to_dict must produce a JSON-serializable dict
            as_dict = r.to_dict()
            json.dumps(as_dict)  # must not raise

    def test_apply_remediations_records_to_audit_trail(self):
        from plugin_examples.compliance.audit_trail import AuditTrail
        result = _make_critical_violation()
        remediations = compute_remediations([result])
        audit = AuditTrail()
        apply_remediations(remediations, {}, audit=audit)
        entries = [e for e in audit._entries if e.decision == "REMEDIATE"]
        assert len(entries) >= 1
        assert entries[0].policy_rule == "slo_build_success"
