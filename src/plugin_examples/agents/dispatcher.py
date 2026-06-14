"""AgentDispatcher — routes actions to appropriate agents via registry."""

from __future__ import annotations

import json
from pathlib import Path

from plugin_examples.agents.base import AgentResult
from plugin_examples.agents.context import SharedContext
from plugin_examples.agents.registry import AgentRegistry
from plugin_examples.compliance.audit_trail import AuditEntry
from plugin_examples.reliability.sli_emitter import HandlerTimer


class AgentDispatcher:
    """Routes actions to registered agents and records audit + SLI data."""

    def __init__(self, registry: AgentRegistry, context: SharedContext) -> None:
        self._registry = registry
        self._context = context

    def dispatch(self, action_id: str, action_type: str, cycle_num: int = 0) -> AgentResult | None:
        """Find and invoke the appropriate agent. Returns None if no agent matches."""
        agent = self._registry.find_for_action(action_id, action_type)
        if agent is None:
            return None

        with HandlerTimer(action_id) as timer:
            result = agent.execute(self._context, action_id)

        result.sli_duration_ms = timer.duration_ms

        if self._context.audit is not None:
            self._context.audit.record(
                AuditEntry(
                    action_id=action_id,
                    decision="EXECUTE",
                    policy_rule=f"agent_dispatch:{agent.agent_id}",
                    detail=f"specialization={agent.capability.specialization}",
                )
            )

        # Persist handler result as evidence
        if self._context.evidence_dir and cycle_num > 0:
            handler_path = self._context.evidence_dir / f"handler-{action_id.lower()}-cycle{cycle_num:02d}.json"
            evidence_data = {**result.data, "sli_duration_ms": result.sli_duration_ms}
            handler_path.write_text(json.dumps(evidence_data, indent=2), encoding="utf-8")

        return result

    def save_catalog(self, output_dir: Path) -> Path:
        """Write agent catalog to evidence directory."""
        catalog_path = output_dir / "agent-catalog.json"
        catalog_path.write_text(
            json.dumps(self._registry.catalog(), indent=2),
            encoding="utf-8",
        )
        return catalog_path
