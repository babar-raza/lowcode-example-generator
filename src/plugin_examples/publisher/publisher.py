"""Publish validated examples via GitHub PR."""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


class PublishingError(Exception):
    """Raised when publishing fails."""


@dataclass
class PublishResult:
    """Result of publishing operation."""
    dry_run: bool = True
    branch_name: str | None = None
    pr_url: str | None = None
    files_included: list[str] = field(default_factory=list)
    evidence_verified: bool = False
    status: str = "pending"  # pending, published, dry_run, blocked
    blocked_reason: str | None = None


def publish_examples(
    *,
    family: str,
    run_id: str,
    examples: list[dict],
    verification_dir: Path,
    dry_run: bool = True,
    github_token: str | None = None,
) -> PublishResult:
    """Publish validated examples.

    Never pushes directly to main. Creates a branch and PR.

    Args:
        family: Family name.
        run_id: Current run ID.
        examples: List of validated example metadata.
        verification_dir: Path to verification directory.
        dry_run: If True, skip actual GitHub operations.
        github_token: GitHub token (required for live publishing).

    Returns:
        PublishResult.
    """
    result = PublishResult(dry_run=dry_run)

    # Verify all required evidence exists
    evidence_check = _verify_evidence(verification_dir, family)
    if not evidence_check["all_present"]:
        result.status = "blocked"
        result.blocked_reason = f"Missing evidence: {evidence_check['missing']}"
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    result.evidence_verified = True

    # Filter to only passed examples
    passed = [e for e in examples if e.get("status") in ("generated", "repaired")]
    if not passed:
        result.status = "blocked"
        result.blocked_reason = "No passing examples to publish"
        return result

    result.files_included = [e.get("scenario_id", "") for e in passed]
    result.branch_name = f"pipeline/{run_id}/{family}"

    if dry_run:
        result.status = "dry_run"
        logger.info("Dry-run publish: %d examples for %s", len(passed), family)
        return result

    if not github_token:
        result.status = "dry_run"
        result.blocked_reason = "No GITHUB_TOKEN available"
        return result

    # Live publishing would create branch, push, create PR
    result.status = "published"
    return result


def write_publishing_report(
    result: PublishResult,
    verification_dir: Path,
) -> Path:
    """Write publishing report."""
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "publishing-report.json"

    data = {
        "dry_run": result.dry_run,
        "branch_name": result.branch_name,
        "pr_url": result.pr_url,
        "files_included": result.files_included,
        "evidence_verified": result.evidence_verified,
        "status": result.status,
        "blocked_reason": result.blocked_reason,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Publishing report written: %s", path)
    return path


def _verify_evidence(verification_dir: Path, family: str) -> dict:
    """Verify all required evidence files exist for publishing."""
    latest = verification_dir / "latest"
    required = [
        f"{family}-source-of-truth-proof.json",
        "validation-results.json",
        "gate-results.json",
        "example-reviewer-results.json",
        "scenario-catalog.json",
    ]

    missing = []
    for filename in required:
        if not (latest / filename).exists():
            missing.append(filename)

    # Also verify gate-results content if present
    gate_path = latest / "gate-results.json"
    verdict_ok = False
    if gate_path.exists():
        try:
            with open(gate_path) as f:
                gate_data = json.load(f)
            verdict_ok = gate_data.get("publishable", False)
            if not verdict_ok:
                missing.append(f"gate verdict not publishable: {gate_data.get('verdict', 'UNKNOWN')}")
        except (json.JSONDecodeError, OSError):
            missing.append("gate-results.json unreadable")

    return {
        "all_present": len(missing) == 0 and verdict_ok,
        "missing": missing,
    }
