"""Tests for AgentDispatcher — routing, audit recording, SLI timing, evidence."""

from __future__ import annotations

import json
from pathlib import Path

from plugin_examples.agents.base import Agent, AgentCapability, AgentResult
from plugin_examples.agents.context import SharedContext
from plugin_examples.agents.dispatcher import AgentDispatcher
from plugin_examples.agents.registry import AgentRegistry
from plugin_examples.compliance.audit_trail import AuditTrail


class _EchoAgent(Agent):
    def __init__(self, aid: str, action_types: frozenset[str], changed: bool = False):
        self._aid = aid
        self._cap = AgentCapability(action_types=action_types, specialization="echo")
        self._changed = changed

    @property
    def agent_id(self) -> str:
        return self._aid

    @property
    def capability(self) -> AgentCapability:
        return self._cap

    def execute(self, context: SharedContext, action_id: str) -> AgentResult:
        context.set(f"executed_{action_id}", True)
        return AgentResult(changed=self._changed, data={"echoed": action_id})


class TestAgentDispatcher:
    def _make(self, tmp_path: Path, agents: list[Agent] | None = None) -> tuple[AgentDispatcher, SharedContext]:
        ev = tmp_path / "evidence"
        ev.mkdir()
        audit = AuditTrail()
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=ev, audit=audit)
        reg = AgentRegistry()
        for a in (agents or []):
            reg.register(a)
        return AgentDispatcher(reg, ctx), ctx

    def test_dispatch_routes_to_agent(self, tmp_path: Path):
        agent = _EchoAgent("e1", frozenset({"TYPE_A"}))
        disp, ctx = self._make(tmp_path, [agent])
        result = disp.dispatch("action1", "TYPE_A")
        assert result is not None
        assert result.data["echoed"] == "action1"

    def test_dispatch_no_match_returns_none(self, tmp_path: Path):
        disp, _ = self._make(tmp_path)
        assert disp.dispatch("x", "UNKNOWN_TYPE") is None

    def test_dispatch_records_audit(self, tmp_path: Path):
        agent = _EchoAgent("e1", frozenset({"TYPE_A"}))
        disp, ctx = self._make(tmp_path, [agent])
        disp.dispatch("action1", "TYPE_A")
        entries = ctx.audit.entries
        assert len(entries) == 1
        assert entries[0].action_id == "action1"
        assert entries[0].decision == "EXECUTE"
        assert "agent_dispatch:e1" in entries[0].policy_rule

    def test_dispatch_sets_sli_duration(self, tmp_path: Path):
        agent = _EchoAgent("e1", frozenset({"TYPE_A"}))
        disp, _ = self._make(tmp_path, [agent])
        result = disp.dispatch("action1", "TYPE_A")
        assert result.sli_duration_ms >= 0

    def test_dispatch_writes_evidence(self, tmp_path: Path):
        agent = _EchoAgent("e1", frozenset({"TYPE_A"}))
        disp, ctx = self._make(tmp_path, [agent])
        disp.dispatch("action1", "TYPE_A", cycle_num=1)
        handler_path = ctx.evidence_dir / "handler-action1-cycle01.json"
        assert handler_path.exists()
        data = json.loads(handler_path.read_text())
        assert data["echoed"] == "action1"
        assert "sli_duration_ms" in data

    def test_dispatch_propagates_context(self, tmp_path: Path):
        agent = _EchoAgent("e1", frozenset({"TYPE_A"}))
        disp, ctx = self._make(tmp_path, [agent])
        disp.dispatch("action1", "TYPE_A")
        assert ctx.get("executed_action1") is True

    def test_dispatch_changed_flag(self, tmp_path: Path):
        agent = _EchoAgent("e1", frozenset({"TYPE_A"}), changed=True)
        disp, _ = self._make(tmp_path, [agent])
        result = disp.dispatch("a1", "TYPE_A")
        assert result.changed is True

    def test_save_catalog(self, tmp_path: Path):
        agent = _EchoAgent("e1", frozenset({"TYPE_A"}))
        disp, ctx = self._make(tmp_path, [agent])
        path = disp.save_catalog(ctx.evidence_dir)
        assert path.exists()
        catalog = json.loads(path.read_text())
        assert len(catalog) == 1
        assert catalog[0]["agent_id"] == "e1"

    def test_dispatch_without_audit(self, tmp_path: Path):
        ev = tmp_path / "evidence"
        ev.mkdir()
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=ev, audit=None)
        reg = AgentRegistry()
        reg.register(_EchoAgent("e1", frozenset({"TYPE_A"})))
        disp = AgentDispatcher(reg, ctx)
        result = disp.dispatch("a1", "TYPE_A")
        assert result is not None
