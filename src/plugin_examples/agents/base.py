"""Agent base class and capability metadata for multi-agent coordination."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plugin_examples.agents.context import SharedContext


@dataclass(frozen=True)
class AgentCapability:
    """Declares what an agent can handle and its operational characteristics."""

    action_types: frozenset[str]
    specialization: str
    read_only: bool = True
    priority: int = 100


@dataclass
class AgentResult:
    """Outcome of an agent execution."""

    changed: bool = False
    data: dict[str, Any] = field(default_factory=dict)
    sli_duration_ms: int = 0


class Agent(ABC):
    """Base class for specialized pipeline agents."""

    @property
    @abstractmethod
    def agent_id(self) -> str: ...

    @property
    @abstractmethod
    def capability(self) -> AgentCapability: ...

    @abstractmethod
    def execute(self, context: SharedContext, action_id: str) -> AgentResult: ...

    def can_handle(self, action_id: str, action_type: str) -> bool:
        """Check if this agent can handle the given action."""
        return action_type in self.capability.action_types
