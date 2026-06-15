"""Contract tests for agent dispatch framework invariants — TC-RH09.

These tests verify structural invariants of the agent framework that
must hold regardless of which agents are registered. They serve as
boundary enforcement for the A6 Coordinated agent architecture.
"""

from __future__ import annotations

from pathlib import Path

from plugin_examples.agents.base import Agent, AgentCapability, AgentResult
from plugin_examples.agents.context import SharedContext
from plugin_examples.agents.dispatcher import AgentDispatcher
from plugin_examples.agents.protocol import MessageType
from plugin_examples.agents.registry import AgentRegistry
from plugin_examples.compliance.audit_trail import AuditTrail


class _StubAgent(Agent):
    def __init__(self, aid: str, action_types: frozenset[str], priority: int = 100):
        self._aid = aid
        self._cap = AgentCapability(
            action_types=action_types,
            specialization="stub",
            priority=priority,
        )

    @property
    def agent_id(self) -> str:
        return self._aid

    @property
    def capability(self) -> AgentCapability:
        return self._cap

    def execute(self, context: SharedContext, action_id: str) -> AgentResult:
        return AgentResult(changed=False, data={"changed": False, "agent": self._aid})


class TestRegistryInvariants:
    def test_unique_agent_ids(self):
        reg = AgentRegistry()
        a1 = _StubAgent("agent-1", frozenset({"TYPE_A"}))
        a2 = _StubAgent("agent-2", frozenset({"TYPE_B"}))
        reg.register(a1)
        reg.register(a2)
        ids = [a.agent_id for a in reg.all_agents()]
        assert len(ids) == len(set(ids)), "Agent IDs must be unique"

    def test_overwrite_same_id(self):
        reg = AgentRegistry()
        a1 = _StubAgent("agent-1", frozenset({"TYPE_A"}))
        a2 = _StubAgent("agent-1", frozenset({"TYPE_B"}))
        reg.register(a1)
        reg.register(a2)
        assert len(reg.all_agents()) == 1
        assert reg.get("agent-1").capability.action_types == frozenset({"TYPE_B"})

    def test_all_agents_have_non_empty_action_types(self):
        reg = AgentRegistry()
        a1 = _StubAgent("a1", frozenset({"TYPE_A"}))
        a2 = _StubAgent("a2", frozenset({"TYPE_B", "TYPE_C"}))
        reg.register(a1)
        reg.register(a2)
        for agent in reg.all_agents():
            assert len(agent.capability.action_types) > 0, f"Agent {agent.agent_id} has empty action_types"

    def test_find_for_action_returns_lowest_priority(self):
        reg = AgentRegistry()
        high = _StubAgent("high", frozenset({"TYPE_A"}), priority=10)
        low = _StubAgent("low", frozenset({"TYPE_A"}), priority=1)
        reg.register(high)
        reg.register(low)
        best = reg.find_for_action("action1", "TYPE_A")
        assert best.agent_id == "low"

    def test_find_for_action_returns_none_for_unknown(self):
        reg = AgentRegistry()
        reg.register(_StubAgent("a1", frozenset({"TYPE_A"})))
        assert reg.find_for_action("x", "UNKNOWN") is None

    def test_catalog_matches_registry_state(self):
        reg = AgentRegistry()
        reg.register(_StubAgent("a1", frozenset({"TYPE_A"})))
        reg.register(_StubAgent("a2", frozenset({"TYPE_B", "TYPE_C"})))
        catalog = reg.catalog()
        assert len(catalog) == 2
        ids = {c["agent_id"] for c in catalog}
        assert ids == {"a1", "a2"}
        for entry in catalog:
            assert "action_types" in entry
            assert "priority" in entry
            assert "read_only" in entry


class TestDispatchInvariants:
    def _make_dispatcher(self, tmp_path: Path) -> tuple[AgentDispatcher, SharedContext]:
        ev = tmp_path / "evidence"
        ev.mkdir()
        audit = AuditTrail()
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=ev, audit=audit)
        reg = AgentRegistry()
        reg.register(_StubAgent("a1", frozenset({"TYPE_A"})))
        reg.register(_StubAgent("a2", frozenset({"TYPE_B"}), priority=50))
        return AgentDispatcher(reg, ctx), ctx

    def test_dispatch_records_audit_entry(self, tmp_path: Path):
        disp, ctx = self._make_dispatcher(tmp_path)
        disp.dispatch("action1", "TYPE_A")
        assert len(ctx.audit.entries) == 1
        entry = ctx.audit.entries[0]
        assert entry.decision == "EXECUTE"
        assert "agent_dispatch:" in entry.policy_rule

    def test_result_data_contains_changed_key(self, tmp_path: Path):
        disp, _ = self._make_dispatcher(tmp_path)
        result = disp.dispatch("action1", "TYPE_A")
        assert "changed" in result.data, "AgentResult.data must contain 'changed' key"

    def test_no_match_returns_none_no_audit(self, tmp_path: Path):
        disp, ctx = self._make_dispatcher(tmp_path)
        result = disp.dispatch("x", "UNKNOWN_TYPE")
        assert result is None
        assert len(ctx.audit.entries) == 0

    def test_save_catalog_roundtrip(self, tmp_path: Path):
        import json
        disp, ctx = self._make_dispatcher(tmp_path)
        path = disp.save_catalog(ctx.evidence_dir)
        catalog = json.loads(path.read_text())
        assert len(catalog) == 2
        for entry in catalog:
            assert entry["agent_id"] in {"a1", "a2"}

    def test_flush_messages_returns_and_clears(self, tmp_path: Path):
        disp, ctx = self._make_dispatcher(tmp_path)
        ctx.post_message("a1", MessageType.INFORM, {"key": "val"})
        ctx.post_message("a2", MessageType.CLAIM, {"action": "test"})
        flushed = disp.flush_messages()
        assert len(flushed) == 2
        assert flushed[0]["sender"] == "a1"
        assert ctx.message_bus.count == 0, "Bus must be empty after flush"
