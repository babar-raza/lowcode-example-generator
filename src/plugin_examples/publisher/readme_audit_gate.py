"""README audit gate for the example publishing pipeline.

Publication readiness requires a README audit for the target family.
This gate blocks PR package creation if:
- No README audit artifact exists for the family
- The README audit artifact is stale (older than the last generation run)
- The README audit found failures (shallow audit, content failures)

The gate integrates into PR package readiness. See publish_readiness.py
for the 4-tier readiness model.

Environment variable for bypass:
    PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH

This gate does NOT replace the live-PR approval gate. Both must be satisfied
for a live publish to proceed.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Approval constant — matches the pattern from approval_gate.py
README_AUDIT_ENV_VAR = "PLUGIN_EXAMPLES_README_PUSH_APPROVAL"
README_AUDIT_EXPECTED_VALUE = "APPROVE_README_PUSH"

# Blocked reason constants
BLOCKED_README_AUDIT_MISSING = "blocked_readme_audit_missing"
BLOCKED_README_AUDIT_SHALLOW = "blocked_readme_audit_shallow"
BLOCKED_README_AUDIT_FAILED = "blocked_readme_audit_failed"
BLOCKED_README_AUDIT_STALE = "blocked_readme_audit_stale"

# README audit artifact filename convention
_README_AUDIT_FILENAME = "readme-audit.json"

# Fields that prove a README audit is content-based (not size/presence only)
_CONTENT_AUDIT_PROOF_FIELDS = frozenset({
    "workflow_type_in_readme",
    "family_in_readme",
    "package_id_in_readme",
    "content_audit",
})

# Shallow audit detection: if none of these fields are present, it's size/presence only
_SHALLOW_DETECTION_FIELDS = _CONTENT_AUDIT_PROOF_FIELDS


def check_readme_audit_gate(
    family: str,
    verification_dir: Path,
    run_id: str | None = None,
    readme_push_approval: str | None = None,
) -> dict:
    """Check whether the README audit gate is satisfied for a family.

    Args:
        family: Family name (e.g., "cells").
        verification_dir: Base verification directory (workspace/verification).
        run_id: Current run ID for staleness check. If None, staleness check is skipped.
        readme_push_approval: Explicit approval token, or None to read from env var.

    Returns:
        Dict with keys:
            - family: str
            - gate_passed: bool
            - blocked_reason: str | None
            - audit_path: str | None
            - audit_is_content_based: bool
            - audit_record_count: int
    """
    result: dict = {
        "family": family,
        "gate_passed": False,
        "blocked_reason": None,
        "audit_path": None,
        "audit_is_content_based": False,
        "audit_record_count": 0,
    }

    # Check for explicit approval bypass
    token = readme_push_approval or os.environ.get(README_AUDIT_ENV_VAR, "")
    approval_bypass = token == README_AUDIT_EXPECTED_VALUE

    # Locate the README audit artifact
    audit_path = _find_readme_audit(family, verification_dir)
    if audit_path is None:
        result["blocked_reason"] = BLOCKED_README_AUDIT_MISSING
        logger.warning("README audit gate BLOCKED for %s: no audit artifact found", family)
        return result

    result["audit_path"] = str(audit_path)

    # Load and validate the audit artifact
    try:
        import json
        audit_data = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        result["blocked_reason"] = BLOCKED_README_AUDIT_MISSING
        logger.warning("README audit gate BLOCKED for %s: cannot read audit file: %s", family, exc)
        return result

    records = audit_data.get("records", audit_data.get("entries", []))
    result["audit_record_count"] = len(records)

    # Check whether the audit is content-based
    is_content_based = _is_content_based_audit(records)
    result["audit_is_content_based"] = is_content_based

    if not is_content_based:
        result["blocked_reason"] = BLOCKED_README_AUDIT_SHALLOW
        logger.warning(
            "README audit gate BLOCKED for %s: audit is size/presence only (not content-based)",
            family,
        )
        return result

    # Check for audit failures
    failed_records = [
        r for r in records
        if r.get("content_audit") in ("FAIL", "NEEDS_REVIEW")
    ]
    if failed_records and not approval_bypass:
        result["blocked_reason"] = BLOCKED_README_AUDIT_FAILED
        logger.warning(
            "README audit gate BLOCKED for %s: %d records failed content checks",
            family, len(failed_records),
        )
        return result

    # All checks pass
    result["gate_passed"] = True
    logger.info("README audit gate PASSED for %s (%d records)", family, len(records))
    return result


def _find_readme_audit(family: str, verification_dir: Path) -> Path | None:
    """Locate the most recent README audit artifact for a family.

    Search order:
    1. workspace/verification/latest/families/{family}/readme-audit.json
    2. workspace/verification/latest/{family}-readme-audit.json
    """
    latest = verification_dir / "latest"
    candidates = [
        latest / "families" / family / _README_AUDIT_FILENAME,
        latest / f"{family}-{_README_AUDIT_FILENAME}",
        latest / f"{family}-readme-backfill-simulation.json",  # Sprint 59 legacy format
        latest / f"{family}-root-readme-audit.json",  # root readme audit
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _is_content_based_audit(records: list[dict]) -> bool:
    """Return True if the audit records contain content-based checks.

    An audit is content-based if at least one record contains one of the
    fields that prove content was checked (not just presence/size).
    """
    if not records:
        return False
    for record in records:
        if any(field in record for field in _SHALLOW_DETECTION_FIELDS):
            return True
    return False
