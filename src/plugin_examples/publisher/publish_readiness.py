"""Publish readiness validator for family configs.

Evaluates whether each family is ready for live PR creation by checking:
- family_config is present
- family status is active (not discovery_only, experimental, disabled)
- published_plugin_examples_repo is set and family-specific
- central_repo_allowed is not needed (or is explicitly true)

4-tier readiness model:
- config_ready: target configured and family-specific (no live API needed)
- repo_access_ready: repo is accessible via GitHub API (HTTP 200)
- pr_permission_ready: token has push permission for the repo
- live_publish_ready: all above + explicit human approval (never automated)

Write evidence: workspace/verification/latest/family-publish-readiness.json
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

from plugin_examples.publisher.publisher import _is_central_repo

logger = logging.getLogger(__name__)

# Blocked reason constants — canonical set used by publisher and readiness validator.
BLOCKED_MISSING_FAMILY_CONFIG = "blocked_missing_family_config"
BLOCKED_MISSING_FAMILY_PUBLISH_TARGET = "blocked_missing_family_publish_target"
BLOCKED_CENTRAL_REPO_TARGET_NOT_ALLOWED = "blocked_central_repo_target_not_allowed"
BLOCKED_UNCERTAIN_PUBLISH_TARGET = "blocked_uncertain_publish_target"
BLOCKED_FAMILY_NOT_ACTIVE = "blocked_family_not_active"
BLOCKED_SOURCE_OF_TRUTH_NOT_READY = "blocked_source_of_truth_not_ready"

# The known central placeholder repo used before family-specific targets are configured.
# If a config points here it signals the target has not been set, not that it was
# intentionally chosen.
_CENTRAL_PLACEHOLDER = ("aspose", "aspose-plugins-examples-dotnet")

# Statuses that may generate and publish
_ACTIVE_STATUSES = {"active"}


def check_family_publish_readiness(
    family: str,
    family_config: Any,
    *,
    config_path: str | None = None,
) -> dict:
    """Return a publish-readiness record for a single family.

    Args:
        family: Family name (e.g., "cells").
        family_config: FamilyConfig dataclass or None.
        config_path: Source YAML path for audit purposes.

    Returns:
        Dict with fields: family, publish_target_owner, publish_target_repo,
        publish_target_branch, target_type, is_family_specific,
        central_repo_allowed, publish_ready, blocked_reason, config_path.
    """
    record: dict = {
        "family": family,
        "publish_target_owner": None,
        "publish_target_repo": None,
        "publish_target_branch": None,
        "target_type": "unknown",
        "is_family_specific": False,
        "central_repo_allowed": False,
        "publish_ready": False,
        "blocked_reason": None,
        "config_path": config_path or "",
        # 4-tier readiness model
        "config_ready": False,
        "repo_access_ready": False,
        "pr_permission_ready": False,
        "live_publish_ready": False,
    }

    if family_config is None:
        record["blocked_reason"] = BLOCKED_MISSING_FAMILY_CONFIG
        return record

    status = getattr(family_config, "status", "unknown")
    if status not in _ACTIVE_STATUSES:
        record["blocked_reason"] = BLOCKED_FAMILY_NOT_ACTIVE
        record["target_type"] = f"not_active:{status}"
        return record

    github_cfg = getattr(family_config, "github", None)
    if github_cfg is None:
        record["blocked_reason"] = BLOCKED_MISSING_FAMILY_PUBLISH_TARGET
        return record

    pub_repo = getattr(github_cfg, "published_plugin_examples_repo", None)
    if pub_repo is None:
        record["blocked_reason"] = BLOCKED_MISSING_FAMILY_PUBLISH_TARGET
        return record

    owner = getattr(pub_repo, "owner", "") or ""
    repo = getattr(pub_repo, "repo", "") or ""
    branch = getattr(pub_repo, "branch", "") or ""

    if not owner or not repo:
        record["blocked_reason"] = BLOCKED_MISSING_FAMILY_PUBLISH_TARGET
        return record

    record["publish_target_owner"] = owner
    record["publish_target_repo"] = repo
    record["publish_target_branch"] = branch
    record["central_repo_allowed"] = getattr(github_cfg, "central_repo_allowed", False)

    is_central = _is_central_repo(owner, repo, family)
    record["is_family_specific"] = not is_central

    if is_central:
        record["target_type"] = "central_shared"
        # Distinguish: known placeholder (target never set) vs other central repo
        if (owner, repo) == _CENTRAL_PLACEHOLDER:
            # Placeholder means no family-specific target has been configured yet
            record["blocked_reason"] = BLOCKED_MISSING_FAMILY_PUBLISH_TARGET
        elif not record["central_repo_allowed"]:
            record["blocked_reason"] = BLOCKED_CENTRAL_REPO_TARGET_NOT_ALLOWED
        else:
            # Central repo explicitly approved — allowed
            record["target_type"] = "central_allowed"
            record["is_family_specific"] = False  # still central but allowed
            record["publish_ready"] = True
    else:
        record["target_type"] = "family_specific"
        record["is_family_specific"] = True
        record["publish_ready"] = True
        record["config_ready"] = True
        # repo_access_ready and pr_permission_ready require live API probe
        # (see resolve_repo_access in repo_access_resolver.py)

    return record


def check_publish_readiness(
    families: list[tuple[str, Any, str]],
) -> dict:
    """Check publish readiness for multiple families.

    Args:
        families: List of (family_name, family_config, config_path) tuples.

    Returns:
        Summary dict with per-family records and aggregate counts.
    """
    records = []
    for family, config, config_path in families:
        record = check_family_publish_readiness(family, config, config_path=config_path)
        records.append(record)

    publish_ready = [r for r in records if r["publish_ready"]]
    blocked = [r for r in records if not r["publish_ready"]]

    return {
        "audit_date": str(date.today()),
        "total_families": len(records),
        "publish_ready_count": len(publish_ready),
        "blocked_count": len(blocked),
        "publish_ready_families": [r["family"] for r in publish_ready],
        "blocked_families": [r["family"] for r in blocked],
        "families": records,
    }


def merge_repo_access_results(result: dict, verification_dir: Path) -> None:
    """Merge repo_access_ready and pr_permission_ready from resolver evidence into result.

    Reads workspace/verification/latest/family-repo-access-resolution.json when present
    and updates the per-family records in-place. Also sets blocked_reason to
    blocked_live_pr_approval_required for families that are publish_ready and
    have repo_access_ready=True but live_publish_ready=False.

    Args:
        result: Result dict from check_publish_readiness (modified in-place).
        verification_dir: Base verification directory.
    """
    from plugin_examples.publisher.approval_gate import BLOCKED_LIVE_PR_APPROVAL_REQUIRED

    resolver_path = verification_dir / "latest" / "family-repo-access-resolution.json"
    if not resolver_path.exists():
        return

    try:
        with open(resolver_path) as f:
            resolver_data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    resolver_by_family = {r["family"]: r for r in resolver_data.get("families", [])}

    for rec in result.get("families", []):
        family = rec["family"]
        if family not in resolver_by_family:
            continue
        resolver_rec = resolver_by_family[family]
        rec["repo_access_ready"] = resolver_rec.get("repo_access_ready", False)
        rec["pr_permission_ready"] = resolver_rec.get("pr_permission_ready", False)
        # If publish_ready (config OK), repo accessible, but no approval → set blocked_reason
        if rec.get("publish_ready") and rec["repo_access_ready"] and not rec.get("live_publish_ready"):
            rec["blocked_reason"] = BLOCKED_LIVE_PR_APPROVAL_REQUIRED


def write_publish_readiness_report(
    result: dict,
    verification_dir: Path,
) -> Path:
    """Write family-publish-readiness.json to workspace/verification/latest/.

    Also merges repo_access_ready / pr_permission_ready from
    family-repo-access-resolution.json when present.
    """
    merge_repo_access_results(result, verification_dir)
    latest = verification_dir / "latest"
    latest.mkdir(parents=True, exist_ok=True)
    path = latest / "family-publish-readiness.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info("Publish readiness report written: %s", path)
    return path
