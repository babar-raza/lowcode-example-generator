"""SLO auto-remediation — maps SLO violations to concrete strategy adjustments.

When SLO check results contain violations, this module computes remediation
actions that the planner loop can apply to adjust its strategy for the next
cycle or run.  Remediations are runtime-only; they never modify persisted
YAML configs or policy files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RemediationAction:
    """A single remediation action in response to an SLO violation."""

    slo_id: str
    action: str  # deprioritize_failing | reduce_concurrency | extend_window | alert
    parameters: dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "slo_id": self.slo_id,
            "action": self.action,
            "parameters": self.parameters,
            "reason": self.reason,
        }


def compute_remediations(
    slo_results: list[Any],
    gate_policy: Any | None = None,
) -> list[RemediationAction]:
    """Map SLO violations to remediation actions.

    Rules:
    1. critical SLO violated (build_pass_rate) → deprioritize_failing
    2. warning SLO violated (handler_error_rate) → reduce_concurrency
    3. warning SLO violated (run_pass_rate) → extend_window
    4. info SLO violated (cycle_duration) → alert (advisory only)
    """
    remediations: list[RemediationAction] = []

    for result in slo_results:
        passed = getattr(result, "passed", True)
        if passed:
            continue

        slo_id = getattr(result, "slo_id", "")
        metric = getattr(result, "metric", "")
        severity = getattr(result, "severity", "info")
        actual = getattr(result, "actual", 0.0)
        target = getattr(result, "target", 0.0)

        if severity == "critical":
            # Critical SLO violation → deprioritize families with worst failure rate
            threshold = 3
            if gate_policy is not None:
                threshold = getattr(gate_policy, "deprioritization_threshold", 3)
            remediations.append(RemediationAction(
                slo_id=slo_id,
                action="deprioritize_failing",
                parameters={
                    "failure_threshold": threshold,
                    "metric": metric,
                    "actual": actual,
                    "target": target,
                },
                reason=f"Critical SLO '{slo_id}' violated: {actual:.4f} vs target {target}",
            ))

        elif severity == "warning" and "error" in metric:
            # Handler error rate too high → reduce concurrency
            remediations.append(RemediationAction(
                slo_id=slo_id,
                action="reduce_concurrency",
                parameters={
                    "metric": metric,
                    "actual": actual,
                    "target": target,
                    "suggested_max_cycles": 3,
                },
                reason=f"Warning SLO '{slo_id}' violated: error rate {actual:.4f} > {target}",
            ))

        elif severity == "warning":
            # Other warning (e.g. run_pass_rate) → extend evaluation window
            remediations.append(RemediationAction(
                slo_id=slo_id,
                action="extend_window",
                parameters={
                    "metric": metric,
                    "actual": actual,
                    "target": target,
                    "extend_by_runs": 5,
                },
                reason=f"Warning SLO '{slo_id}' violated: {actual:.4f} vs target {target}; extending window",
            ))

        else:
            # Info severity → advisory alert, no config change
            remediations.append(RemediationAction(
                slo_id=slo_id,
                action="alert",
                parameters={
                    "metric": metric,
                    "actual": actual,
                    "target": target,
                },
                reason=f"Info SLO '{slo_id}' violated: {actual:.4f} vs target {target} (advisory)",
            ))

    return remediations


def apply_remediations(
    remediations: list[RemediationAction],
    loop_config: dict[str, Any],
    audit: Any | None = None,
) -> dict[str, Any]:
    """Apply remediation actions to loop configuration.

    Modifies and returns the loop_config dict.  Records each
    remediation in the audit trail if provided.

    Args:
        remediations: List of RemediationAction to apply.
        loop_config: Mutable dict of loop configuration
                     (e.g. max_cycles, deprioritization_threshold).
        audit: Optional AuditTrail instance for recording remediation decisions.

    Returns:
        The modified loop_config dict.
    """
    for rem in remediations:
        if rem.action == "deprioritize_failing":
            threshold = rem.parameters.get("failure_threshold", 3)
            loop_config["deprioritization_threshold"] = max(1, threshold - 1)

        elif rem.action == "reduce_concurrency":
            suggested = rem.parameters.get("suggested_max_cycles", 3)
            current = loop_config.get("max_cycles", 5)
            loop_config["max_cycles"] = min(current, suggested)

        elif rem.action == "extend_window":
            extend_by = rem.parameters.get("extend_by_runs", 5)
            current = loop_config.get("slo_window_override", 10)
            loop_config["slo_window_override"] = current + extend_by

        # "alert" action — no config change, just recorded

        if audit is not None:
            try:
                from plugin_examples.compliance.audit_trail import AuditEntry
                audit.record(AuditEntry(
                    action_id=f"slo_remediation_{rem.slo_id}",
                    decision="REMEDIATE",
                    policy_rule=rem.slo_id,
                    detail=rem.reason,
                ))
            except ImportError:
                pass

    return loop_config
