"""Planner-driven execution loop — runs planner, executes safe actions, replans.

Usage:
    from plugin_examples.planner_loop import run_execution_loop
    result = run_execution_loop(repo_root, evidence_dir, max_cycles=5, dry_run_remote=True)
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from plugin_examples.compliance.audit_trail import AuditEntry, AuditTrail
from plugin_examples.compliance.reporter import compute_compliance_trend, generate_compliance_report
from plugin_examples.observability import get_logger
from plugin_examples.policy.loader import load_gate_policy, load_slos
from plugin_examples.portfolio_action_planner import (
    ActionBoard,
    compute_action_board,
    render_markdown,
)
from plugin_examples.reliability.sli_emitter import HandlerTimer, compute_slis_from_loop_metrics
from plugin_examples.reliability.slo_monitor import check_slos, slo_summary
from plugin_examples.reliability.slo_remediator import apply_remediations, compute_remediations

logger = get_logger(__name__)


def board_fingerprint(board: ActionBoard) -> str:
    """Compute a stable fingerprint of the board's action state.

    Ignores volatile fields (generated_at, duration) so repeated boards
    with identical action structure produce the same fingerprint.
    """
    stable = {
        "head": board.generated_from_head,
        "dirty_summary": board.git_dirty_summary,
        "actions": sorted(
            [(a.id, a.type, a.current_state, a.safe_to_execute_now, a.gate_present) for a in board.actions]
        ),
    }
    raw = json.dumps(stable, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Cycle ledger
# ---------------------------------------------------------------------------


@dataclass
class CycleResult:
    cycle: int
    generated_from_head: str = ""
    board_fingerprint: str = ""
    action_count: int = 0
    safe_count: int = 0
    blocked_count: int = 0
    executed: list[str] = field(default_factory=list)
    changed_actions: list[str] = field(default_factory=list)
    noop_actions: list[str] = field(default_factory=list)
    deferred: list[dict[str, str]] = field(default_factory=list)
    commit_sha: str | None = None
    verdict: str = ""
    duration_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle": self.cycle,
            "generated_from_head": self.generated_from_head,
            "board_fingerprint": self.board_fingerprint,
            "action_count": self.action_count,
            "safe_count": self.safe_count,
            "blocked_count": self.blocked_count,
            "executed": self.executed,
            "changed_actions": self.changed_actions,
            "noop_actions": self.noop_actions,
            "deferred": self.deferred,
            "commit_sha": self.commit_sha,
            "verdict": self.verdict,
            "duration_ms": self.duration_ms,
        }


@dataclass
class LoopMetrics:
    """Observable metrics for the agent execution loop."""

    total_cycles: int = 0
    total_duration_ms: int = 0
    actions_executed: int = 0
    actions_deferred: int = 0
    handler_errors: int = 0
    deprioritized_count: int = 0
    fingerprint_changes: int = 0
    idempotent_stops: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cycles": self.total_cycles,
            "total_duration_ms": self.total_duration_ms,
            "actions_executed": self.actions_executed,
            "actions_deferred": self.actions_deferred,
            "handler_errors": self.handler_errors,
            "deprioritized_count": self.deprioritized_count,
            "fingerprint_changes": self.fingerprint_changes,
            "idempotent_stops": self.idempotent_stops,
        }


@dataclass
class LoopResult:
    cycles: list[CycleResult] = field(default_factory=list)
    final_board: ActionBoard | None = None
    total_executed: int = 0
    total_deferred: int = 0
    stop_reason: str = ""
    metrics: LoopMetrics = field(default_factory=LoopMetrics)

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "total_cycles": len(self.cycles),
            "total_executed": self.total_executed,
            "total_deferred": self.total_deferred,
            "stop_reason": self.stop_reason,
            "metrics": self.metrics.to_dict(),
            "cycles": [c.to_dict() for c in self.cycles],
        }
        if self.final_board and self.final_board.dirty_categories:
            d["final_dirty_state"] = self.final_board.dirty_categories
        return d


# ---------------------------------------------------------------------------
# Action handlers
# ---------------------------------------------------------------------------

# Handlers are functions that take (repo_root, evidence_dir, action, dry_run_remote)
# and return a dict with execution results.

_APPROVAL_GATED_TYPES = {
    "MERGE_READY_PR",
    "PDF_PR_CONFLICT_RECOVERY",
    "LIVE_PUBLISH_READY_PACKAGE",
}


def _handle_conservation_check(repo_root: Path, evidence_dir: Path, **_kw: Any) -> dict:
    """Execute portfolio conservation check. Always read-only, never changes state."""
    from plugin_examples.portfolio_action_planner import ACTIVE_FAMILIES, _count_contracts, _load_denominators

    denoms = _load_denominators(repo_root)
    contracts = _count_contracts(repo_root)
    results = {}
    all_pass = True
    for f in ACTIVE_FAMILIES:
        d = denoms.get(f, {})
        pilot = d.get("allowed_pilot_count") or d.get("runnable_scenarios", 0)
        c = contracts.get(f, 0)
        ok = c == pilot
        results[f] = {"pilot": pilot, "contracts": c, "pass": ok}
        if not ok:
            all_pass = False
    return {"conservation_all_pass": all_pass, "families": results, "changed": False}


def _handle_version_drift_check(repo_root: Path, evidence_dir: Path, **_kw: Any) -> dict:
    """Execute version drift check. Always read-only, never changes state."""
    from plugin_examples.portfolio_action_planner import ACTIVE_FAMILIES, _load_denominators

    denoms = _load_denominators(repo_root)
    versions = {f: denoms.get(f, {}).get("source_version", "?") for f in ACTIVE_FAMILIES}
    return {"versions": versions, "status": "checked", "changed": False}


def _handle_blocker_recheck(repo_root: Path, evidence_dir: Path, action_id: str = "", **_kw: Any) -> dict:
    """Execute blocker recheck (NuGet availability). Read-only unless blocker is resolved."""
    results: dict[str, Any] = {"action_id": action_id, "changed": False}
    if action_id == "FORMIMPORTER_RETEST":
        try:
            r = subprocess.run(
                ["curl", "-s", "https://api.nuget.org/v3-flatcontainer/aspose.pdf/index.json"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            data = json.loads(r.stdout)
            latest = data.get("versions", [])[-1] if data.get("versions") else "unknown"
            results["latest_version"] = latest
            results["still_blocked"] = True  # Would need > 26.5.0
        except Exception:
            results["check_failed"] = True
    elif action_id == "OCR_DEPENDENCY_RECHECK":
        try:
            r = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    "https://api.nuget.org/v3-flatcontainer/aspose.ai.llm/index.json",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            results["http_status"] = r.stdout.strip()
            results["still_blocked"] = r.stdout.strip() != "200"
            if not results["still_blocked"]:
                results["changed"] = True
        except Exception:
            results["check_failed"] = True
    elif action_id == "PSD_DEPENDENCY_RECHECK":
        try:
            r = subprocess.run(
                [
                    "curl",
                    "-s",
                    "-o",
                    "/dev/null",
                    "-w",
                    "%{http_code}",
                    "https://api.nuget.org/v3-flatcontainer/aspose.javaattributes/index.json",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            results["http_status"] = r.stdout.strip()
            results["still_blocked"] = r.stdout.strip() != "200"
            if not results["still_blocked"]:
                results["changed"] = True
        except Exception:
            results["check_failed"] = True
    elif action_id == "PERMANENTLY_BLOCKED_WATCH":
        results["status"] = "confirmed_unchanged"
    return results


_ACTION_HANDLERS = {
    "PORTFOLIO_CONSERVATION_CHECK": _handle_conservation_check,
    "VERSION_DRIFT_CHECK": _handle_version_drift_check,
    "FORMIMPORTER_RETEST": _handle_blocker_recheck,
    "OCR_DEPENDENCY_RECHECK": _handle_blocker_recheck,
    "PSD_DEPENDENCY_RECHECK": _handle_blocker_recheck,
    "PERMANENTLY_BLOCKED_WATCH": _handle_blocker_recheck,
}


# ---------------------------------------------------------------------------
# Execution loop
# ---------------------------------------------------------------------------


def run_execution_loop(
    repo_root: Path,
    evidence_dir: Path,
    max_cycles: int = 5,
    dry_run_remote: bool = True,
    history_path: Path | None = None,
) -> LoopResult:
    """Run the planner-driven execution loop.

    1. Run planner and compute board fingerprint
    2. Execute all safe, non-approval-gated actions with handlers
    3. Track which handlers report changed=True vs changed=False
    4. Save cycle evidence
    5. Stop when: no safe actions, board fingerprint unchanged and no handlers
       changed state, or max_cycles reached

    history_path: Optional path to cross-run history JSON. When provided,
    families with >= 3 consecutive failures are deprioritized (deferred).
    """
    import time

    result = LoopResult()
    loop_start = time.monotonic()
    evidence_dir.mkdir(parents=True, exist_ok=True)
    prev_fingerprint: str | None = None

    # Load policy-as-code definitions (falls back to defaults if YAML missing)
    gate_policy = load_gate_policy(repo_root)
    slo_defs = load_slos(repo_root)

    # Initialize audit trail for action-to-policy-rule traceability
    audit = AuditTrail()

    # Load cross-run history for adaptive deprioritization (lazy import — optional feature)
    history = None
    if history_path is not None:
        from plugin_examples.state.run_history import RunHistory

        history = RunHistory.load(history_path)

    # A6 — Multi-agent coordination: registry, context, dispatcher
    from plugin_examples.agents.builtin import BlockerRecheckAgent, ConservationCheckAgent, VersionDriftAgent
    from plugin_examples.agents.context import SharedContext
    from plugin_examples.agents.dispatcher import AgentDispatcher
    from plugin_examples.agents.registry import AgentRegistry

    shared_context = SharedContext(
        repo_root=repo_root,
        evidence_dir=evidence_dir,
        dry_run_remote=dry_run_remote,
        gate_policy=gate_policy,
        slo_defs=slo_defs,
        history=history,
        audit=audit,
    )
    registry = AgentRegistry()
    registry.register(ConservationCheckAgent())
    registry.register(VersionDriftAgent())
    registry.register(BlockerRecheckAgent())
    dispatcher = AgentDispatcher(registry, shared_context)

    # Save agent catalog as evidence artifact
    dispatcher.save_catalog(evidence_dir)

    for cycle_num in range(1, max_cycles + 1):
        t0 = time.monotonic()
        board = compute_action_board(repo_root)
        fp = board_fingerprint(board)

        cycle = CycleResult(
            cycle=cycle_num,
            generated_from_head=board.generated_from_head,
            board_fingerprint=fp,
            action_count=len(board.actions),
            safe_count=len(board.safe_actions()),
            blocked_count=len(board.blocked_actions()),
        )

        # Save cycle action board
        cycle_json_path = evidence_dir / f"planner-cycle-{cycle_num:02d}.json"
        cycle_json_path.write_text(board.to_json(), encoding="utf-8")
        cycle_md_path = evidence_dir / f"planner-cycle-{cycle_num:02d}.md"
        cycle_md_path.write_text(render_markdown(board), encoding="utf-8")

        # Pre-execution idempotency stop: if fingerprint matches previous cycle
        # and previous cycle had no changes, skip handler execution entirely
        if prev_fingerprint is not None and fp == prev_fingerprint:
            prev_cycle = result.cycles[-1] if result.cycles else None
            if prev_cycle and not prev_cycle.changed_actions:
                cycle.verdict = "IDEMPOTENT_NO_CHANGE"
                cycle.duration_ms = int((time.monotonic() - t0) * 1000)
                result.metrics.idempotent_stops += 1
                result.cycles.append(cycle)
                result.stop_reason = "stopped_no_change"
                break

        # Find executable actions (safe + has handler + not approval-gated)
        executed_this_cycle: list[str] = []
        changed_this_cycle: list[str] = []
        noop_this_cycle: list[str] = []
        deferred_this_cycle: list[dict[str, str]] = []

        for action in board.safe_actions():
            if action.type in gate_policy.approval_gated_types and (dry_run_remote or not action.gate_present):
                    deferred_this_cycle.append(
                        {
                            "id": action.id,
                            "reason": "approval-gated (dry-run or gate absent)",
                            "taskcard_id": action.taskcard_id or "",
                        }
                    )
                    audit.record(AuditEntry(
                        action_id=action.id, decision="DEFER",
                        policy_rule="approval_gated_type",
                        detail=f"type={action.type}",
                    ))
                    continue

            # Adaptive deprioritization: skip families with repeated failures
            if history is not None and action.family and history.should_deprioritize(action.family):
                result.metrics.deprioritized_count += 1
                deferred_this_cycle.append(
                    {
                        "id": action.id,
                        "reason": "deprioritized_consecutive_failures",
                        "family": action.family,
                        "taskcard_id": action.taskcard_id or "",
                    }
                )
                audit.record(AuditEntry(
                    action_id=action.id, decision="DEFER",
                    policy_rule="deprioritization_threshold",
                    detail=f"family={action.family}",
                ))
                continue

            # A6 agent dispatch — try registry first, fallback to legacy handlers
            agent_result = dispatcher.dispatch(action.id, action.type, cycle_num=cycle_num)
            if agent_result is not None:
                executed_this_cycle.append(action.id)
                if agent_result.changed:
                    changed_this_cycle.append(action.id)
                else:
                    noop_this_cycle.append(action.id)
            else:
                # Legacy fallback for any handlers not yet migrated to agents
                handler = _ACTION_HANDLERS.get(action.id)
                if handler:
                    try:
                        with HandlerTimer(action.id) as timer:
                            handler_result = handler(
                                repo_root,
                                evidence_dir,
                                action_id=action.id,
                            )
                        executed_this_cycle.append(action.id)
                        if handler_result.get("changed", False):
                            changed_this_cycle.append(action.id)
                        else:
                            noop_this_cycle.append(action.id)
                        handler_result["sli_duration_ms"] = timer.duration_ms
                        handler_path = evidence_dir / f"handler-{action.id.lower()}-cycle{cycle_num:02d}.json"
                        handler_path.write_text(
                            json.dumps(handler_result, indent=2),
                            encoding="utf-8",
                        )
                        audit.record(AuditEntry(
                            action_id=action.id, decision="EXECUTE",
                            policy_rule="legacy_handler_dispatch",
                            goal_relevance=[action.type],
                            evidence_ref=str(handler_path),
                        ))
                    except Exception as e:
                        result.metrics.handler_errors += 1
                        deferred_this_cycle.append(
                            {
                                "id": action.id,
                                "reason": f"handler error: {e}",
                            }
                        )
                        audit.record(AuditEntry(
                            action_id=action.id, decision="BLOCK",
                            policy_rule="handler_error",
                            detail=str(e),
                        ))
                else:
                    deferred_this_cycle.append(
                        {
                            "id": action.id,
                            "reason": "no handler implemented",
                            "taskcard_id": action.taskcard_id or "",
                        }
                    )
                    audit.record(AuditEntry(
                        action_id=action.id, decision="BLOCK",
                        policy_rule="no_registered_handler",
                        detail=f"type={action.type}",
                    ))

        cycle.executed = executed_this_cycle
        cycle.changed_actions = changed_this_cycle
        cycle.noop_actions = noop_this_cycle
        cycle.deferred = deferred_this_cycle
        cycle.duration_ms = int((time.monotonic() - t0) * 1000)

        result.total_executed += len(executed_this_cycle)
        result.total_deferred += len(deferred_this_cycle)

        # --- Stop conditions ---

        # 1. No safe executable actions
        if not executed_this_cycle:
            cycle.verdict = "NO_SAFE_EXECUTABLE_ACTIONS"
            result.cycles.append(cycle)
            result.stop_reason = "exhausted_safe_actions"
            break

        cycle.verdict = f"EXECUTED_{len(executed_this_cycle)}_ACTIONS"
        result.cycles.append(cycle)
        _save_checkpoint(evidence_dir, cycle_num, result)
        if prev_fingerprint is not None and fp != prev_fingerprint:
            result.metrics.fingerprint_changes += 1
        prev_fingerprint = fp

        if cycle_num >= max_cycles:
            result.stop_reason = "max_cycles reached"
            break
    else:
        result.stop_reason = "loop completed normally"

    # Persist cross-run history with summary record for this loop run
    if history is not None:
        from plugin_examples.state.run_history import RunRecord

        history.record_run(
            RunRecord(
                family="__loop__",
                wave=str(len(result.cycles)),
                verdict="SPRINT_COMPLETE" if result.total_executed > 0 else "NO_SAFE_EXECUTABLE_ACTIONS",
                scenarios_attempted=result.total_executed + result.total_deferred,
                scenarios_succeeded=result.total_executed,
                scenarios_blocked=result.total_deferred,
            )
        )
        history.save()

    # Final board
    result.final_board = compute_action_board(repo_root)
    final_path = evidence_dir / "planner-loop-final-board.json"
    final_path.write_text(result.final_board.to_json(), encoding="utf-8")

    # Finalize loop metrics
    result.metrics.total_cycles = len(result.cycles)
    result.metrics.total_duration_ms = int((time.monotonic() - loop_start) * 1000)
    result.metrics.actions_executed = result.total_executed
    result.metrics.actions_deferred = result.total_deferred

    # Emit structured metrics log
    logger.info("loop_metrics", extra={"loop_metrics": result.metrics.to_dict()})

    # Emit SLI events derived from loop metrics
    compute_slis_from_loop_metrics(result.metrics)

    # Evaluate SLO compliance and persist results
    slo_results = None
    if slo_defs:
        slo_results = check_slos(slo_defs, history, current_metrics=result.metrics)
        slo_path = evidence_dir / "slo-check-results.json"
        slo_path.write_text(
            json.dumps(slo_summary(slo_results), indent=2),
            encoding="utf-8",
        )
        logger.info("slo_evaluation", extra={"slo_summary": slo_summary(slo_results)})

        # Auto-remediation: respond to SLO violations with concrete actions
        if slo_results and not all(r.passed for r in slo_results):
            remediations = compute_remediations(slo_results, gate_policy)
            if remediations:
                loop_config: dict[str, Any] = {"max_cycles": max_cycles}
                apply_remediations(remediations, loop_config, audit=audit)
                remediation_path = evidence_dir / "slo-remediations.json"
                remediation_path.write_text(
                    json.dumps([r.to_dict() for r in remediations], indent=2),
                    encoding="utf-8",
                )
                logger.info("slo_remediation_applied", extra={"count": len(remediations)})

    # Compute compliance trend and generate report
    if history is not None:
        trend = compute_compliance_trend(history, slo_results=slo_results)
        generate_compliance_report(trend, evidence_dir)
        logger.info("compliance_trend", extra={"trend": trend.to_dict()})

    # Persist audit trail
    audit.save(evidence_dir / "audit-trail.json")

    # Persist metrics to evidence directory
    metrics_path = evidence_dir / "planner-loop-metrics.json"
    metrics_path.write_text(
        json.dumps(result.metrics.to_dict(), indent=2),
        encoding="utf-8",
    )

    return result


# ---------------------------------------------------------------------------
# Checkpoint persistence for resume-from-failure
# ---------------------------------------------------------------------------


def _save_checkpoint(evidence_dir: Path, cycle_num: int, result: LoopResult) -> None:
    """Save loop state checkpoint for resume-from-failure (atomic write)."""
    checkpoint = {
        "cycle": cycle_num,
        "total_executed": result.total_executed,
        "total_deferred": result.total_deferred,
        "metrics": result.metrics.to_dict(),
        "cycles": [c.to_dict() for c in result.cycles],
    }
    path = evidence_dir / "loop-checkpoint.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")
    tmp.replace(path)


def _load_checkpoint(evidence_dir: Path) -> dict[str, Any] | None:
    """Load checkpoint if it exists."""
    path = evidence_dir / "loop-checkpoint.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


# ---------------------------------------------------------------------------
# Blocked actions report (evidence hygiene: no vague labels)
# ---------------------------------------------------------------------------

_RETRY_CONDITIONS: dict[str, str] = {
    "PORTFOLIO_CONSERVATION_CHECK": "always safe — read-only check",
    "VERSION_DRIFT_CHECK": "always safe — read-only check",
    "FORMIMPORTER_RETEST": "Aspose.PDF NuGet > 26.5.0 published",
    "OCR_DEPENDENCY_RECHECK": "Aspose.AI.LLM NuGet package returns HTTP 200",
    "PSD_DEPENDENCY_RECHECK": "Aspose.JavaAttributes NuGet package returns HTTP 200",
    "PERMANENTLY_BLOCKED_WATCH": "NEVER — permanently blocked by design",
    "MERGE_READY_PR": "PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR set",
    "PDF_PR_CONFLICT_RECOVERY": "manual conflict resolution",
    "LIVE_PUBLISH_READY_PACKAGE": "PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR set",
}


def generate_blocked_actions_report(board: ActionBoard) -> list[dict[str, Any]]:
    """Generate structured blocked-actions report with no vague labels.

    Every blocked or deferred action gets:
    - action_id, action_type, family, safe, blocker,
      approval_env, taskcard_id, retry_condition.
    """
    report: list[dict[str, Any]] = []
    for action in board.actions:
        if action.safe_to_execute_now:
            continue
        entry: dict[str, Any] = {
            "action_id": action.id,
            "action_type": action.type,
            "family": action.family or "cross-family",
            "safe": action.safe_to_execute_now,
            "blocker": action.blocker or "approval gate absent",
            "approval_env": action.approval_required or None,
            "taskcard_id": action.taskcard_id or f"TC-{action.id.replace('_', '-')}",
            "retry_condition": _RETRY_CONDITIONS.get(
                action.id,
                action.blocker or "unknown — requires taskcard creation",
            ),
        }
        report.append(entry)
    return report
