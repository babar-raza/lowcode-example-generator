"""Publish validated examples via GitHub PR."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PublishingError(Exception):
    """Raised when publishing fails."""


@dataclass
class PublishResult:
    """Result of publishing operation."""
    dry_run: bool = True
    branch_name: str | None = None
    pr_url: str | None = None
    pr_number: int | None = None
    files_included: list[str] = field(default_factory=list)
    evidence_verified: bool = False
    status: str = "pending"  # pending, published, dry_run, blocked, PR_SIMULATION_PASSED
    blocked_reason: str | None = None


def _is_central_repo(owner: str, repo: str, family: str) -> bool:
    """Return True if the repo appears to be a central shared repo, not family-specific.

    A repo is considered family-specific when either the owner or the repo name
    contains the family name as a substring (case-insensitive). If neither does,
    it is likely a central combined repository.

    Examples:
        family=words, owner=aspose-words → False (family-specific)
        family=cells, owner=aspose, repo=aspose-plugins-examples-dotnet → True (central)
    """
    family_lower = family.lower()
    return family_lower not in owner.lower() and family_lower not in repo.lower()


def publish_examples(
    *,
    family: str,
    run_id: str,
    examples: list[dict],
    verification_dir: Path,
    dry_run: bool = True,
    github_token: str | None = None,
    gate_verdict: Any = None,
    family_config: Any = None,
    approval_token: str | None = None,
    repo_access_ready: bool = False,
    pr_permission_ready: bool = False,
    package_path: Path | None = None,
    package_version: str = "unknown",
) -> PublishResult:
    """Publish validated examples.

    Never pushes directly to main. Creates a branch and PR via GitHub REST API.

    Args:
        family: Family name.
        run_id: Current run ID.
        examples: List of validated example metadata.
        verification_dir: Path to verification directory.
        dry_run: If True, skip actual GitHub operations.
        github_token: GitHub token (required for live publishing).
            NEVER logged, serialized, or stored.
        gate_verdict: In-memory GateVerdict from the current run. When provided,
            the publisher uses it directly instead of reading gate-results.json
            from disk. This avoids the ordering bug where gate-results.json is
            written after the stage loop but the publisher runs inside the loop.
        family_config: FamilyConfig dataclass. When provided, live publishing is
            blocked if published_plugin_examples_repo is a central shared repo
            and central_repo_allowed is not True.
        approval_token: Live publish approval token. Must equal
            approval_gate.APPROVAL_EXPECTED_VALUE ("APPROVE_LIVE_PR"), or be
            present via PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL env var. Required
            for all live publishes — never automated without this explicit value.
        repo_access_ready: Whether the target repo passed a recent GitHub API
            access probe (HTTP 200, can_read=True). Must be True for live publish.
        pr_permission_ready: Whether the token has push permission to the target
            repo (can_push=True). Must be True for live publish.
        package_path: Path to the assembled PR dry-run package directory.
            Required for live publishing. When None, live publish returns
            blocked_real_publisher_not_implemented.
        package_version: NuGet package version string for the PR body.

    Returns:
        PublishResult.
    """
    from plugin_examples.publisher.approval_gate import (
        check_approval,
        BLOCKED_PUBLISH_TO_MAIN,
        BLOCKED_REPO_ACCESS_NOT_READY,
        BLOCKED_PR_PERMISSION_NOT_READY,
    )

    result = PublishResult(dry_run=dry_run)

    # Verify all required evidence exists
    evidence_check = _verify_evidence(verification_dir, family, gate_verdict=gate_verdict)
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

    # Generate branch name: plugin-examples/{family}/{timestamp}
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    result.branch_name = f"plugin-examples/{family}/{ts}"

    if dry_run:
        result.status = "dry_run"
        logger.info("Dry-run publish: %d examples for %s", len(passed), family)
        return result

    # --- Live publish guards (all must pass) ---

    # APPROVAL GATE: require explicit human approval token
    approved, approval_blocked = check_approval(approval_token)
    if not approved:
        result.status = "blocked"
        result.blocked_reason = approval_blocked
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    # BRANCH CHECK: never push/PR from a branch named main
    if result.branch_name == "main":
        result.status = "blocked"
        result.blocked_reason = BLOCKED_PUBLISH_TO_MAIN
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    # REPO ACCESS CHECK: must have confirmed read access to target repo
    if not repo_access_ready:
        result.status = "blocked"
        result.blocked_reason = BLOCKED_REPO_ACCESS_NOT_READY
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    # PR PERMISSION CHECK: must have confirmed push permission
    if not pr_permission_ready:
        result.status = "blocked"
        result.blocked_reason = BLOCKED_PR_PERMISSION_NOT_READY
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    # Block live publish when family_config is absent — cannot verify target
    if family_config is None:
        result.status = "blocked"
        result.blocked_reason = (
            "blocked_missing_family_config: family_config must be provided for live publishing"
        )
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    # Block live publish if target is a central repo and central_repo_allowed is not True
    github_cfg = getattr(family_config, "github", None)
    if github_cfg is not None:
        pub_repo = github_cfg.published_plugin_examples_repo
        if _is_central_repo(pub_repo.owner, pub_repo.repo, family) and not github_cfg.central_repo_allowed:
            result.status = "blocked"
            result.blocked_reason = (
                f"blocked_central_repo_target_not_allowed: "
                f"published_plugin_examples_repo ({pub_repo.owner}/{pub_repo.repo}) "
                f"is not family-specific for '{family}'. "
                f"Set central_repo_allowed: true in family config to override."
            )
            logger.warning("Publishing blocked: %s", result.blocked_reason)
            return result

    if not github_token:
        result.status = "dry_run"
        result.blocked_reason = "No GITHUB_TOKEN available"
        return result

    # PACKAGE PATH CHECK: must have assembled package for real publishing
    if package_path is None:
        result.status = "blocked"
        result.blocked_reason = (
            "blocked_real_publisher_not_implemented: "
            "package_path is required for live publishing. "
            "Use 'python -m plugin_examples publish-pr --family "
            f"{family} --publish --approval-token APPROVE_LIVE_PR' command."
        )
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    # --- Real GitHub PR creation ---
    from plugin_examples.publisher.github_pr_publisher import (
        create_github_pr,
        PublishingError as GitHubError,
    )
    from plugin_examples.publisher.pr_builder import build_pr

    # Load excluded scenarios from blocked-scenarios.json for PR body
    excluded_scenario_lines = _load_excluded_scenario_summaries(verification_dir, family)

    pr_content = build_pr(
        family=family,
        run_id=run_id,
        examples_count=len(passed),
        package_version=package_version,
        examples_list=result.files_included,
        excluded_scenarios=excluded_scenario_lines or None,
    )
    result.branch_name = pr_content.branch  # plugin-examples/{family}/{run_id}

    # Extract target repo from family_config
    pub_repo = github_cfg.published_plugin_examples_repo if github_cfg else None
    if pub_repo is None:
        result.status = "blocked"
        result.blocked_reason = "blocked_missing_publish_target: no published_plugin_examples_repo in config"
        logger.warning("Publishing blocked: %s", result.blocked_reason)
        return result

    try:
        # IMPORTANT: github_token is passed here but NEVER logged or returned
        pr_result = create_github_pr(
            owner=pub_repo.owner,
            repo=pub_repo.repo,
            base_branch=getattr(pub_repo, "branch", "main"),
            branch_name=result.branch_name,
            pr_title=pr_content.title,
            pr_body=pr_content.body,
            package_path=package_path,
            labels=pr_content.labels,
            github_token=github_token,
        )
        result.status = "published"
        result.pr_url = pr_result["pr_url"]
        result.pr_number = pr_result["pr_number"]
        logger.info("PR created: #%d %s", result.pr_number, result.pr_url)
    except GitHubError as exc:
        result.status = "blocked"
        result.blocked_reason = f"github_publish_failed: {exc}"
        logger.error("GitHub PR creation failed: %s", exc)

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
        "pr_number": result.pr_number,
        "files_included": result.files_included,
        "evidence_verified": result.evidence_verified,
        "status": result.status,
        "blocked_reason": result.blocked_reason,
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info("Publishing report written: %s", path)
    return path


def _load_excluded_scenario_summaries(
    verification_dir: Path,
    family: str,
) -> list[str]:
    """Load excluded scenario summaries from blocked-scenarios.json.

    Returns a list of human-readable exclusion lines for the PR body, e.g.
    "pdf-splitter — blocked_pilot_not_in_scope: Type 'Splitter' not in allowlist".
    """
    from plugin_examples.evidence_layout import resolve_family_evidence_path

    blocked_path = resolve_family_evidence_path(
        verification_dir, family, "blocked-scenarios.json",
    )
    if blocked_path is None or not blocked_path.exists():
        return []
    try:
        with open(blocked_path) as f:
            data = json.load(f)
        lines: list[str] = []
        for entry in data.get("blocked_scenarios", []):
            sid = entry.get("scenario_id", "unknown")
            status = entry.get("status", "blocked")
            reason = entry.get("blocked_reason", "")
            lines.append(f"{sid} — {status}: {reason}")
        return lines
    except (OSError, json.JSONDecodeError, KeyError):
        return []


def _verify_evidence(
    verification_dir: Path,
    family: str,
    gate_verdict: Any = None,
) -> dict:
    """Verify all required evidence files exist for publishing.

    Required disk files are those written by stages before the publisher runs
    (stages 1-16). gate-results.json is written after the stage loop, so it is
    NOT checked on disk when gate_verdict is provided in-memory. scenario-catalog
    is a planning manifest (not in latest/), so it is not required here.

    Prefers family-scoped evidence at verification/latest/families/{family}/ over
    the legacy top-level verification/latest/ to prevent cross-family contamination.
    """
    from plugin_examples.evidence_layout import resolve_family_evidence_path

    latest = verification_dir / "latest"
    # Only check files that are definitely written before the publisher stage.
    # {family}-source-of-truth-proof.json is already family-prefixed — check top-level.
    # validation-results.json is family-scoped — prefer families/{family}/ path.
    missing = []
    proof_path = latest / f"{family}-source-of-truth-proof.json"
    if not proof_path.exists():
        missing.append(f"{family}-source-of-truth-proof.json")

    validation_path = resolve_family_evidence_path(verification_dir, family, "validation-results.json")
    if not validation_path.exists():
        missing.append("validation-results.json")

    # Gate verdict: prefer in-memory gate_verdict (avoids ordering bug).
    # Fall back to reading gate-results.json from disk only when gate_verdict
    # is not provided (e.g., standalone calls in tests or external tools).
    verdict_ok = False
    if gate_verdict is not None:
        verdict_ok = (
            getattr(gate_verdict, "all_required_passed", False)
            or getattr(gate_verdict, "publishable", False)
        )
        if not verdict_ok:
            missing.append(
                f"gate verdict not publishable: {getattr(gate_verdict, 'verdict', 'UNKNOWN')}"
            )
    else:
        gate_path = resolve_family_evidence_path(verification_dir, family, "gate-results.json")
        if gate_path.exists():
            try:
                with open(gate_path) as f:
                    gate_data = json.load(f)
                verdict_ok = gate_data.get("publishable", False) or gate_data.get(
                    "all_required_passed", False
                )
                if not verdict_ok:
                    missing.append(
                        f"gate verdict not publishable: {gate_data.get('verdict', 'UNKNOWN')}"
                    )
            except (json.JSONDecodeError, OSError):
                missing.append("gate-results.json unreadable")
        else:
            missing.append("gate-results.json")

    return {
        "all_present": len(missing) == 0 and verdict_ok,
        "missing": missing,
    }
