"""Agent negotiation protocol — inter-agent message passing for A6 coordination.

Provides a lightweight message-passing protocol that allows agents to
communicate claims, yields, information, and requests during dispatch
cycles. This elevates the agent framework from "independent agents" to
"cooperating agents" — the key differentiator for A6 (Coordinated).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class MessageType(StrEnum):
    """Standard message types for inter-agent communication."""

    CLAIM = "CLAIM"
    YIELD = "YIELD"
    INFORM = "INFORM"
    REQUEST_INFO = "REQUEST_INFO"


@dataclass(frozen=True)
class AgentMessage:
    """A single message exchanged between agents."""

    sender: str
    msg_type: MessageType
    payload: dict[str, Any] = field(default_factory=dict)
    recipient: str | None = None
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now(UTC).isoformat())


class MessageBus:
    """In-memory message bus for agent-to-agent communication within a cycle."""

    def __init__(self) -> None:
        self._messages: list[AgentMessage] = []

    def post(self, message: AgentMessage) -> None:
        """Post a message to the bus."""
        self._messages.append(message)

    def get_messages(
        self,
        *,
        recipient: str | None = None,
        msg_type: MessageType | None = None,
    ) -> list[AgentMessage]:
        """Retrieve messages, optionally filtered by recipient and/or type."""
        result = self._messages
        if recipient is not None:
            result = [m for m in result if m.recipient is None or m.recipient == recipient]
        if msg_type is not None:
            result = [m for m in result if m.msg_type == msg_type]
        return list(result)

    def clear(self) -> None:
        """Clear all messages (e.g., between cycles)."""
        self._messages.clear()

    @property
    def count(self) -> int:
        return len(self._messages)

    def to_list(self) -> list[dict[str, Any]]:
        """Serialize all messages for evidence/audit."""
        return [
            {
                "sender": m.sender,
                "msg_type": m.msg_type.value,
                "recipient": m.recipient,
                "payload": m.payload,
                "timestamp": m.timestamp,
            }
            for m in self._messages
        ]
