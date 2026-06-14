"""Multi-agent coordination framework for pipeline execution (A6 — Coordinated)."""

from plugin_examples.agents.base import Agent, AgentCapability, AgentResult
from plugin_examples.agents.context import SharedContext
from plugin_examples.agents.dispatcher import AgentDispatcher
from plugin_examples.agents.registry import AgentRegistry

__all__ = [
    "Agent",
    "AgentCapability",
    "AgentDispatcher",
    "AgentRegistry",
    "AgentResult",
    "SharedContext",
]
