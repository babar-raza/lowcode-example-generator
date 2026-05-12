"""Completeness gate — verifies the denominator conservation equation and writes ledger.

The conservation equation requires that for every family, every type in the
LowCode namespace is accounted for in either ready_scenarios or blocked_scenarios.
If a type is missing from both, we have a gap in coverage tracking.

Equation (simplified):
    ready_count + blocked_count >= denominator_expected_count

For PILOT_ALLOWED families: denominator_expected_count = allowed_pilot_count
For FULL_SOT families: denominator_expected_count = workflow_root_types
For DISCOVERY_ONLY families: gate is skipped (no generation expected)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CompletenessResult:
    """Result of the completeness gate check."""
    family: str
    status: str  # "pass", "warn", "fail", "skip"
    denominator_basis: str
    expected_count: int | None
    ready_count: int
    blocked_count: int
    accounted_count: int
    gap: int  # accounted_count - expected_count (negative means shortage)
    message: str
    violations: list[str] = field(default_factory=list)
    ledger_path: str | None = None

    @property
    def holds(self) -> bool:
        return self.status in ("pass", "skip")


class CompletenessViolationError(Exception):
    """Raised when the denominator equation fails in live mode."""


def check_completeness(
    family: str,
    denominator: dict,
    planning_result,  # PlanningResult from planner.py
    *,
    dry_run: bool = True,
) -> CompletenessResult:
    """Verify the denominator conservation equation for a family.

    Args:
        family: Family name (e.g. "pdf", "cells")
        denominator: Loaded denominator JSON dict from pipeline/configs/denominators/
        planning_result: PlanningResult from plan_scenarios()
        dry_run: If True, violations produce warnings instead of exceptions.

    Returns:
        CompletenessResult with equation status.

    Raises:
        CompletenessViolationError: If equation fails and dry_run is False.
    """
    basis = denominator.get("denominator_basis", "UNKNOWN")

    # DISCOVERY_ONLY families have no generation — gate is not applicable
    if basis == "DISCOVERY_ONLY":
        return CompletenessResult(
            family=family,
            status="skip",
            denominator_basis=basis,
            expected_count=None,
            ready_count=planning_result.ready_count,
            blocked_count=planning_result.blocked_count,
            accounted_count=planning_result.ready_count + planning_result.blocked_count,
            gap=0,
            message=f"Family '{family}' is DISCOVERY_ONLY — completeness gate skipped.",
        )

    # Determine expected count based on basis
    if basis == "PILOT_ALLOWED":
        expected = denominator.get("allowed_pilot_count")
        if expected is None:
            return CompletenessResult(
                family=family,
                status="warn",
                denominator_basis=basis,
                expected_count=None,
                ready_count=planning_result.ready_count,
                blocked_count=planning_result.blocked_count,
                accounted_count=planning_result.ready_count + planning_result.blocked_count,
                gap=0,
                message=f"Family '{family}': PILOT_ALLOWED but allowed_pilot_count is missing from denominator.",
                violations=["allowed_pilot_count missing from denominator"],
            )
    elif basis == "FULL_SOT":
        expected = denominator.get("workflow_root_types")
        if expected is None:
            return CompletenessResult(
                family=family,
                status="warn",
                denominator_basis=basis,
                expected_count=None,
                ready_count=planning_result.ready_count,
                blocked_count=planning_result.blocked_count,
                accounted_count=planning_result.ready_count + planning_result.blocked_count,
                gap=0,
                message=f"Family '{family}': FULL_SOT but workflow_root_types is missing from denominator.",
                violations=["workflow_root_types missing from denominator"],
            )
    else:
        return CompletenessResult(
            family=family,
            status="warn",
            denominator_basis=basis,
            expected_count=None,
            ready_count=planning_result.ready_count,
            blocked_count=planning_result.blocked_count,
            accounted_count=planning_result.ready_count + planning_result.blocked_count,
            gap=0,
            message=f"Family '{family}': unknown denominator_basis '{basis}' — cannot verify.",
            violations=[f"Unknown denominator_basis: {basis}"],
        )

    accounted = planning_result.ready_count + planning_result.blocked_count
    gap = accounted - expected
    violations = []

    if accounted < expected:
        violations.append(
            f"Equation shortfall: {accounted} accounted ({planning_result.ready_count} ready + "
            f"{planning_result.blocked_count} blocked) < {expected} expected. "
            f"Gap of {expected - accounted} types unaccounted for."
        )

    if violations:
        msg = (
            f"Family '{family}' completeness check FAILED ({basis}): "
            + "; ".join(violations)
        )
        status = "warn" if dry_run else "fail"
        if dry_run:
            logger.warning("%s", msg)
        else:
            logger.error("%s", msg)
            raise CompletenessViolationError(msg)
        return CompletenessResult(
            family=family,
            status=status,
            denominator_basis=basis,
            expected_count=expected,
            ready_count=planning_result.ready_count,
            blocked_count=planning_result.blocked_count,
            accounted_count=accounted,
            gap=gap,
            message=msg,
            violations=violations,
        )

    msg = (
        f"Family '{family}' completeness check PASS ({basis}): "
        f"{accounted} accounted == {expected} expected."
    )
    logger.info("%s", msg)
    return CompletenessResult(
        family=family,
        status="pass",
        denominator_basis=basis,
        expected_count=expected,
        ready_count=planning_result.ready_count,
        blocked_count=planning_result.blocked_count,
        accounted_count=accounted,
        gap=gap,
        message=msg,
    )


def write_completeness_gate_result(
    result: CompletenessResult,
    evidence_dir: Path,
) -> Path:
    """Write completeness gate result to evidence directory."""
    families_dir = evidence_dir / "latest" / "families" / result.family
    families_dir.mkdir(parents=True, exist_ok=True)
    path = families_dir / "completeness-gate-result.json"
    data = {
        "family": result.family,
        "status": result.status,
        "denominator_basis": result.denominator_basis,
        "expected_count": result.expected_count,
        "ready_count": result.ready_count,
        "blocked_count": result.blocked_count,
        "accounted_count": result.accounted_count,
        "gap": result.gap,
        "message": result.message,
        "violations": result.violations,
        "holds": result.holds,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    logger.info("Completeness gate result written: %s", path)
    return path


def write_denominator_ledger(
    family: str,
    denominator: dict,
    planning_result,  # PlanningResult
    type_roles: list,  # list[TypeRole] from classify_catalog
    evidence_dir: Path,
) -> Path:
    """Write per-family denominator ledger to evidence directory.

    The ledger lists every type in the LowCode namespace with:
    - type_name, full_name, namespace, role
    - lifecycle_state: ready | blocked_<reason> | unknown
    - pilot_scope: in_scope | out_of_scope | not_applicable

    Args:
        family: Family name.
        denominator: Loaded denominator dict.
        planning_result: PlanningResult from plan_scenarios().
        type_roles: List of TypeRole from classify_catalog().
        evidence_dir: workspace/verification directory.

    Returns:
        Path to written ledger file.
    """
    # Index planning result by target_type
    ready_types = {s.target_type for s in planning_result.ready_scenarios}
    blocked_map: dict[str, str] = {}
    for s in planning_result.blocked_scenarios:
        blocked_map[s.target_type] = s.status  # status IS the blocked reason

    allowed_pilot = set(denominator.get("allowed_pilot_types", []))
    basis = denominator.get("denominator_basis", "UNKNOWN")

    entries = []
    for role in type_roles:
        full_name = role.full_name
        type_name = full_name.split(".")[-1] if full_name else ""
        namespace = ".".join(full_name.split(".")[:-1]) if full_name else ""

        if full_name in ready_types:
            lifecycle_state = "ready"
        elif full_name in blocked_map:
            lifecycle_state = blocked_map[full_name]
        else:
            lifecycle_state = "unknown"

        if basis == "PILOT_ALLOWED" and allowed_pilot:
            pilot_scope = "in_scope" if type_name in allowed_pilot else "out_of_scope"
        else:
            pilot_scope = "not_applicable"

        entries.append({
            "type_name": type_name,
            "full_name": full_name,
            "namespace": namespace,
            "role": role.role,
            "lifecycle_state": lifecycle_state,
            "pilot_scope": pilot_scope,
        })

    families_dir = evidence_dir / "latest" / "families" / family
    families_dir.mkdir(parents=True, exist_ok=True)
    path = families_dir / "denominator-ledger.json"

    ledger = {
        "family": family,
        "denominator_basis": basis,
        "total_types": len(entries),
        "ready_count": sum(1 for e in entries if e["lifecycle_state"] == "ready"),
        "blocked_count": sum(1 for e in entries if e["lifecycle_state"] not in ("ready", "unknown")),
        "unknown_count": sum(1 for e in entries if e["lifecycle_state"] == "unknown"),
        "entries": entries,
    }
    path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    logger.info("Denominator ledger written: %s (%d entries)", path, len(entries))
    return path
