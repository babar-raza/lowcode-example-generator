"""SharedContext — state object propagated between agents within a cycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from plugin_examples.compliance.audit_trail import AuditTrail
    from plugin_examples.policy.loader import GatePolicy, SLODefinition
    from plugin_examples.state.run_history import RunHistory

from plugin_examples.agents.protocol import AgentMessage, MessageBus, MessageType


@dataclass
class SharedContext:
    """Execution context shared across all agents in a cycle."""

    repo_root: Path
    evidence_dir: Path
    dry_run_remote: bool = True
    gate_policy: GatePolicy | None = None
    slo_defs: list[SLODefinition] = field(default_factory=list)
    history: RunHistory | None = None
    audit: AuditTrail | None = None
    message_bus: MessageBus = field(default_factory=MessageBus)

    _store: dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def post_message(
        self,
        sender: str,
        msg_type: MessageType,
        payload: dict[str, Any] | None = None,
        recipient: str | None = None,
    ) -> None:
        """Post a message to the inter-agent message bus."""
        self.message_bus.post(AgentMessage(
            sender=sender,
            msg_type=msg_type,
            payload=payload or {},
            recipient=recipient,
        ))

    def get_messages(
        self,
        *,
        recipient: str | None = None,
        msg_type: MessageType | None = None,
    ) -> list[AgentMessage]:
        """Retrieve messages from the bus, optionally filtered."""
        return self.message_bus.get_messages(recipient=recipient, msg_type=msg_type)

    def snapshot(self) -> dict[str, Any]:
        """Return a frozen copy of the shared store for audit."""
        return dict(self._store)
