"""Publish permission probe — read-only GitHub API access check.

Performs a safe, read-only probe to confirm push permissions are still
available for family publish targets. No branches, files, commits,
or PRs are created. Only GET requests are issued.

Safety contract:
    - Only GET requests via check_repo_access (urllib, read-only).
    - GITHUB_TOKEN is never printed, logged, or stored.
    - No content is pushed in any mode.
    - dry_run flag does not change safety — probe is always read-only.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def probe_publish_permissions(
    families: list[tuple[str, Any, str]],
    verification_dir: Path,
    *,
    dry_run: bool = True,
    promote_latest: bool = False,
) -> dict:
    """Probe GitHub push permissions for family publish targets (read-only).

    Args:
        families: List of (family_name, family_config, config_path) tuples.
        verification_dir: Base verification directory.
        dry_run: When True (default), no writes occur except the probe report.
            The probe itself is always read-only regardless of this flag.
        promote_latest: Write report to latest/ subdirectory.

    Returns:
        Probe result dict.
    """
    from plugin_examples.publisher.repo_access_resolver import (
        check_repo_access,
        _get_headers,
        ACCESS_OK,
    )

    headers = _get_headers()
    token_present = headers is not None

    probe_records = []

    for family, config, config_path in families:
        if config is None:
            probe_records.append({
                "family": family,
                "config_path": config_path,
                "probe_status": "skipped",
                "skip_reason": "family_config is None",
                "can_read": False,
                "can_push": None,
                "repo_access_ready": False,
                "pr_permission_ready": False,
                "safe_to_publish": False,
            })
            continue

        status = getattr(config, "status", "unknown")
        if status not in {"active"}:
            probe_records.append({
                "family": family,
                "config_path": config_path,
                "probe_status": "skipped",
                "skip_reason": f"family_status={status} is not active",
                "can_read": False,
                "can_push": None,
                "repo_access_ready": False,
                "pr_permission_ready": False,
                "safe_to_publish": False,
            })
            continue

        github_cfg = getattr(config, "github", None)
        pub_repo = getattr(github_cfg, "published_plugin_examples_repo", None) if github_cfg else None

        if pub_repo is None:
            probe_records.append({
                "family": family,
                "config_path": config_path,
                "probe_status": "skipped",
                "skip_reason": "no published_plugin_examples_repo in config",
                "can_read": False,
                "can_push": None,
                "repo_access_ready": False,
                "pr_permission_ready": False,
                "safe_to_publish": False,
            })
            continue

        owner = getattr(pub_repo, "owner", "") or ""
        repo = getattr(pub_repo, "repo", "") or ""
        branch = getattr(pub_repo, "branch", "main") or "main"

        access = check_repo_access(owner, repo, branch, headers=headers)

        probe_records.append({
            "family": family,
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "config_path": config_path,
            "probe_status": "completed",
            "error_classification": access["error_classification"],
            "can_read": access["can_read"],
            "can_push": access["can_push"],
            "http_status": access["http_status"],
            "visibility": access["visibility"],
            "default_branch": access["default_branch"],
            "branch_exists": access["branch_exists"],
            "repo_access_ready": access["repo_access_ready"],
            "pr_permission_ready": access["pr_permission_ready"],
            "safe_to_publish": False,  # always False — probe never authorizes live publish
            "interpretation": access["interpretation"],
        })

    ready = [r for r in probe_records if r.get("pr_permission_ready")]
    not_ready = [r for r in probe_records if not r.get("pr_permission_ready")]

    result = {
        "probe_type": "publish_permission_probe",
        "probe_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "sprint": "Live PR Approval Gate and Safe Branch Probe Sprint",
        "token_present": token_present,
        "dry_run": dry_run,
        "probe_is_read_only": True,
        "no_content_pushed": True,
        "families": probe_records,
        "summary": {
            "total_probed": len(probe_records),
            "permission_ready": len(ready),
            "not_ready": len(not_ready),
            "permission_ready_families": [r["family"] for r in ready],
            "not_ready_families": [r["family"] for r in not_ready],
            "live_publish_authorized": False,
            "note": (
                "Permission probe confirms push access is available. "
                "This does NOT authorize live publishing. "
                "Live publish still requires: approval_token=APPROVE_LIVE_PR, "
                "explicit human sign-off, and followup-live-pr-approval-gate closed."
            ),
        },
    }

    output_dir = verification_dir / "latest" if promote_latest else verification_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "publish-permission-probe.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info("Publish permission probe written: %s", output_path)

    return result
