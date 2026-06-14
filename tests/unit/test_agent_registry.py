"""Tests for AgentRegistry — registration, lookup, and catalog serialization."""

from __future__ import annotations

import pytest

from plugin_examples.agents.base import Agent, AgentCapability, AgentResult
from plugin_examples.agents.context import SharedContext
from plugin_examples.agents.registry import AgentRegistry


class _StubAgent(Agent):
    def __init__(self, aid: str, action_types: frozenset[str], spec: str = "test", priority: int = 100):
        self._aid = aid
        self._cap = AgentCapability(action_types=action_types, specialization=spec, priority=priority)

    @property
    def agent_id(self) -> str:
        return self._aid

    @property
    def capability(self) -> AgentCapability:
        return self._cap

    def execute(self, context: SharedContext, action_id: str) -> AgentResult:
        return AgentResult(data={"agent": self._aid, "action": action_id})


class TestAgentRegistry:
    def test_register_and_get(self):
        reg = AgentRegistry()
        agent = _StubAgent("a1", frozenset({"TYPE_A"}))
        reg.register(agent)
        assert reg.get("a1") is agent

    def test_get_missing_returns_none(self):
        reg = AgentRegistry()
        assert reg.get("nonexistent") is None

    def test_find_for_action_by_type(self):
        reg = AgentRegistry()
        a = _StubAgent("a1", frozenset({"TYPE_A"}))
        b = _StubAgent("b1", frozenset({"TYPE_B"}))
        reg.register(a)
        reg.register(b)
        assert reg.find_for_action("any_id", "TYPE_A") is a
        assert reg.find_for_action("any_id", "TYPE_B") is b

    def test_find_for_action_no_match(self):
        reg = AgentRegistry()
        reg.register(_StubAgent("a1", frozenset({"TYPE_A"})))
        assert reg.find_for_action("x", "TYPE_Z") is None

    def test_find_for_action_priority(self):
        reg = AgentRegistry()
        low = _StubAgent("low", frozenset({"TYPE_A"}), priority=10)
        high = _StubAgent("high", frozenset({"TYPE_A"}), priority=50)
        reg.register(high)
        reg.register(low)
        assert reg.find_for_action("x", "TYPE_A") is low

    def test_all_agents(self):
        reg = AgentRegistry()
        a = _StubAgent("a1", frozenset({"T"}))
        b = _StubAgent("b1", frozenset({"T"}))
        reg.register(a)
        reg.register(b)
        assert set(reg.all_agents()) == {a, b}

    def test_catalog_serializable(self):
        reg = AgentRegistry()
        reg.register(_StubAgent("a1", frozenset({"TYPE_A", "TYPE_B"}), spec="conservation", priority=10))
        catalog = reg.catalog()
        assert len(catalog) == 1
        entry = catalog[0]
        assert entry["agent_id"] == "a1"
        assert entry["specialization"] == "conservation"
        assert entry["action_types"] == ["TYPE_A", "TYPE_B"]
        assert entry["read_only"] is True
        assert entry["priority"] == 10

    def test_catalog_empty_registry(self):
        reg = AgentRegistry()
        assert reg.catalog() == []

    def test_register_overwrites_same_id(self):
        reg = AgentRegistry()
        a1 = _StubAgent("same", frozenset({"T1"}))
        a2 = _StubAgent("same", frozenset({"T2"}))
        reg.register(a1)
        reg.register(a2)
        assert reg.get("same") is a2
        assert len(reg.all_agents()) == 1
