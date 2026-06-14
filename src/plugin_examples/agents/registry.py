"""AgentRegistry — catalog of available agents with runtime discovery."""

from __future__ import annotations

from typing import Any

from plugin_examples.agents.base import Agent


class AgentRegistry:
    """Catalog of registered agents with capability-based lookup."""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        self._agents[agent.agent_id] = agent

    def get(self, agent_id: str) -> Agent | None:
        return self._agents.get(agent_id)

    def find_for_action(self, action_id: str, action_type: str) -> Agent | None:
        """Find the best agent for a given action via capability matching."""
        candidates = [a for a in self._agents.values() if a.can_handle(action_id, action_type)]
        if not candidates:
            return None
        return min(candidates, key=lambda a: a.capability.priority)

    def all_agents(self) -> list[Agent]:
        return list(self._agents.values())

    def catalog(self) -> list[dict[str, Any]]:
        """Serializable catalog of registered agents (evidence artifact)."""
        return [
            {
                "agent_id": a.agent_id,
                "specialization": a.capability.specialization,
                "action_types": sorted(a.capability.action_types),
                "read_only": a.capability.read_only,
                "priority": a.capability.priority,
            }
            for a in self._agents.values()
        ]
