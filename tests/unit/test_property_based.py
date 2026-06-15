"""Property-based tests using Hypothesis — TC-RH02.

Tests structural invariants of critical data models using
property-based testing to broaden the test pyramid beyond
example-based tests.
"""

from __future__ import annotations

import json

import pytest

try:
    from hypothesis import given, settings
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

from plugin_examples.compliance.audit_trail import AuditEntry, AuditTrail
from plugin_examples.policy.loader import GoalSpec, SLODefinition

pytestmark = pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")


# ---------------------------------------------------------------------------
# AuditEntry / AuditTrail roundtrip
# ---------------------------------------------------------------------------

@given(
    action_id=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("L", "N"))),
    decision=st.sampled_from(["EXECUTE", "DEFER", "BLOCK"]),
    policy_rule=st.text(min_size=0, max_size=100),
    detail=st.text(min_size=0, max_size=200),
)
@settings(max_examples=50)
def test_audit_trail_roundtrip(tmp_path_factory, action_id, decision, policy_rule, detail):
    """AuditTrail save+load roundtrip preserves all entry fields."""
    tmp_path = tmp_path_factory.mktemp("audit")
    trail = AuditTrail()
    entry = AuditEntry(
        action_id=action_id,
        decision=decision,
        policy_rule=policy_rule,
        detail=detail,
    )
    trail.record(entry)

    path = tmp_path / "audit-trail.json"
    trail.save(path)
    loaded = AuditTrail.load(path)

    assert len(loaded.entries) == 1
    loaded_entry = loaded.entries[0]
    assert loaded_entry.action_id == action_id
    assert loaded_entry.decision == decision
    assert loaded_entry.policy_rule == policy_rule
    assert loaded_entry.detail == detail


# ---------------------------------------------------------------------------
# AuditTrail JSON is always valid
# ---------------------------------------------------------------------------

@given(
    n_entries=st.integers(min_value=0, max_value=20),
)
@settings(max_examples=30)
def test_audit_trail_json_always_valid(n_entries):
    """AuditTrail.to_json() always produces valid JSON."""
    trail = AuditTrail()
    for i in range(n_entries):
        trail.record(AuditEntry(action_id=f"action_{i}", decision="EXECUTE"))
    data = json.loads(trail.to_json())
    assert "audit_trail" in data
    assert len(data["audit_trail"]) == n_entries


# ---------------------------------------------------------------------------
# GoalSpec roundtrip
# ---------------------------------------------------------------------------

@given(
    id_val=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L", "N"))),
    metric=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L", "N"))),
    threshold=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    weight=st.integers(min_value=1, max_value=100),
)
@settings(max_examples=50)
def test_goal_spec_to_dict_roundtrip(id_val, metric, threshold, weight):
    """GoalSpec.to_dict() preserves all fields."""
    spec = GoalSpec(id=id_val, metric=metric, threshold=threshold, weight=weight)
    d = spec.to_dict()
    assert d["id"] == id_val
    assert d["metric"] == metric
    assert d["threshold"] == threshold
    assert d["weight"] == weight


# ---------------------------------------------------------------------------
# SLODefinition roundtrip
# ---------------------------------------------------------------------------

@given(
    id_val=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("L", "N"))),
    metric=st.text(min_size=1, max_size=30, alphabet=st.characters(whitelist_categories=("L", "N"))),
    target=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
    window_runs=st.integers(min_value=1, max_value=1000),
    severity=st.sampled_from(["info", "warning", "critical"]),
)
@settings(max_examples=50)
def test_slo_definition_to_dict_roundtrip(id_val, metric, target, window_runs, severity):
    """SLODefinition.to_dict() preserves all fields."""
    slo = SLODefinition(id=id_val, metric=metric, target=target, window_runs=window_runs, severity=severity)
    d = slo.to_dict()
    assert d["id"] == id_val
    assert d["metric"] == metric
    assert d["target"] == target
    assert d["window_runs"] == window_runs
    assert d["severity"] == severity
