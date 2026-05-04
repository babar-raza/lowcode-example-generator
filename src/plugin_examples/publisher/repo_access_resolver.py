"""GitHub repository access resolver for family publish targets.

Performs safe, read-only GitHub API probes to determine whether the configured
published_plugin_examples_repo for each family is accessible with the current
GITHUB_TOKEN. Results are written to workspace/verification/latest/.

Safety contract:
- Uses only GITHUB_TOKEN env var. Never prints, logs, or serializes the token.
- Only GET requests. No mutations (no repo creation, no PR, no push).
- 404 is classified as repo_not_found_or_no_access (same response for missing
  and private-without-access in GitHub's API).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Canonical error classification values
ACCESS_OK = "repo_access_ok"
REPO_NOT_FOUND = "repo_not_found_or_no_access"
ORG_NOT_FOUND = "org_not_found_or_no_access"
BRANCH_NOT_FOUND = "branch_not_found"
TOKEN_MISSING = "token_missing"
TOKEN_INSUFFICIENT_SCOPE = "token_insufficient_scope"
TOKEN_NOT_AUTHORIZED = "token_not_authorized_for_repo"
API_RATE_LIMITED = "api_rate_limited"
UNKNOWN_ERROR = "unknown_github_error"


def _get_headers() -> dict[str, str] | None:
    """Return Authorization headers using GITHUB_TOKEN. Returns None if token absent."""
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return None
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}


def _github_get(url: str, headers: dict[str, str]) -> tuple[int, dict | list | None]:
    """Execute a GET request to the GitHub API. Returns (status_code, body_or_none)."""
    try:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return resp.status, body
    except Exception as exc:  # noqa: BLE001
        import urllib.error as ue

        if isinstance(exc, ue.HTTPError):
            return exc.code, None
        logger.debug("GitHub GET %s failed: %s", url, exc)
        return 0, None


def _classify_status(status_code: int, url: str) -> str:
    """Map HTTP status to canonical error classification string."""
    if status_code == 200:
        return ACCESS_OK
    if status_code == 404:
        return REPO_NOT_FOUND
    if status_code == 401:
        return TOKEN_NOT_AUTHORIZED
    if status_code == 403:
        return TOKEN_INSUFFICIENT_SCOPE
    if status_code in (429, 503):
        return API_RATE_LIMITED
    return UNKNOWN_ERROR


def check_repo_access(
    owner: str,
    repo: str,
    branch: str,
    *,
    headers: dict[str, str] | None,
) -> dict:
    """Check GitHub API access for a single repo.

    Returns a result dict with fields:
        owner, repo, branch, error_classification, can_read, can_push,
        default_branch, visibility, branch_exists, permissions_object,
        http_status, interpretation, repo_access_ready, pr_permission_ready
    """
    result: dict[str, Any] = {
        "owner": owner,
        "repo": repo,
        "branch": branch,
        "error_classification": TOKEN_MISSING,
        "can_read": False,
        "can_push": None,
        "default_branch": None,
        "visibility": None,
        "branch_exists": None,
        "permissions_object": None,
        "http_status": None,
        "interpretation": "",
        # 4-tier readiness fields
        "repo_access_ready": False,
        "pr_permission_ready": False,
    }

    if headers is None:
        result["error_classification"] = TOKEN_MISSING
        result["interpretation"] = (
            "GITHUB_TOKEN not set. Cannot probe repo access. "
            "Set GITHUB_TOKEN to a fine-grained PAT with read access to the target repos."
        )
        return result

    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    status, body = _github_get(repo_url, headers)
    result["http_status"] = status

    if status == 200 and isinstance(body, dict):
        result["error_classification"] = ACCESS_OK
        result["can_read"] = True
        result["default_branch"] = body.get("default_branch")
        result["visibility"] = body.get("visibility")
        perms = body.get("permissions") or {}
        result["permissions_object"] = perms
        result["can_push"] = perms.get("push", False)
        result["repo_access_ready"] = True
        result["pr_permission_ready"] = bool(result["can_push"])
        result["interpretation"] = (
            f"Repo accessible. visibility={result['visibility']}, "
            f"default_branch={result['default_branch']}, "
            f"can_push={result['can_push']}"
        )
        # Check target branch
        branch_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{branch}"
        b_status, _ = _github_get(branch_url, headers)
        result["branch_exists"] = b_status == 200
        if not result["branch_exists"]:
            result["interpretation"] += f" | Branch '{branch}' not found (HTTP {b_status})."
    elif status == 404:
        result["error_classification"] = REPO_NOT_FOUND
        result["interpretation"] = (
            f"HTTP 404 for {owner}/{repo}. "
            "Repo does not exist or fine-grained PAT lacks read access to it. "
            "GitHub returns 404 for both missing repos and private repos without access."
        )
    elif status == 401:
        result["error_classification"] = TOKEN_NOT_AUTHORIZED
        result["interpretation"] = "Token authentication failed (HTTP 401)."
    elif status == 403:
        result["error_classification"] = TOKEN_INSUFFICIENT_SCOPE
        result["interpretation"] = "Token forbidden (HTTP 403). Scope may be insufficient."
    elif status in (429, 503):
        result["error_classification"] = API_RATE_LIMITED
        result["interpretation"] = f"GitHub API rate limited or unavailable (HTTP {status})."
    else:
        result["error_classification"] = UNKNOWN_ERROR
        result["interpretation"] = f"Unexpected HTTP {status} from GitHub API."

    return result


def probe_org_repo_creation(
    org: str,
    *,
    headers: dict[str, str] | None,
) -> dict:
    """Probe whether the token can create repos in the org (read-only API check).

    Checks GET /orgs/{org} and GET /user/memberships/orgs/{org}.
    Does NOT create any repos.
    """
    result: dict[str, Any] = {
        "org": org,
        "org_exists": None,
        "member_role": None,
        "can_create_repos": None,
        "http_status_org": None,
        "http_status_membership": None,
        "interpretation": "",
    }

    if headers is None:
        result["interpretation"] = "GITHUB_TOKEN not set. Cannot probe org membership."
        return result

    org_url = f"https://api.github.com/orgs/{org}"
    status, body = _github_get(org_url, headers)
    result["http_status_org"] = status

    if status == 200 and isinstance(body, dict):
        result["org_exists"] = True
    elif status == 404:
        result["org_exists"] = False
        result["interpretation"] = f"Org '{org}' not found (HTTP 404)."
        return result

    # Check membership role — if admin/member with create repos permission
    membership_url = f"https://api.github.com/user/memberships/orgs/{org}"
    m_status, m_body = _github_get(membership_url, headers)
    result["http_status_membership"] = m_status

    if m_status == 200 and isinstance(m_body, dict):
        result["member_role"] = m_body.get("role")
        result["can_create_repos"] = result["member_role"] == "admin"
        result["interpretation"] = (
            f"Org '{org}' exists. Member role={result['member_role']}. "
            f"can_create_repos={result['can_create_repos']} "
            f"(requires admin role in org)."
        )
    elif m_status in (403, 404):
        result["can_create_repos"] = False
        result["interpretation"] = (
            f"Org '{org}' exists but membership check returned HTTP {m_status}. "
            "Token may not be org member or fine-grained PAT scope prevents membership read. "
            "Cannot determine repo creation capability."
        )
    else:
        result["can_create_repos"] = None
        result["interpretation"] = (
            f"Org '{org}' check inconclusive (HTTP {m_status})."
        )

    return result


def resolve_repo_access(
    families: list[tuple[str, Any, str]],
    verification_dir: Path,
    *,
    promote_latest: bool = False,
) -> dict:
    """Resolve GitHub repo access for all family publish targets.

    Args:
        families: List of (family_name, family_config, config_path) tuples.
        verification_dir: Base verification directory.
        promote_latest: Whether to write to latest/ subdirectory.

    Returns:
        Resolution result dict.
    """
    headers = _get_headers()
    token_present = headers is not None

    resolution_records = []
    org_probes: dict[str, dict] = {}

    for family, config, config_path in families:
        if config is None:
            resolution_records.append({
                "family": family,
                "config_path": config_path,
                "error_classification": TOKEN_MISSING if not token_present else UNKNOWN_ERROR,
                "can_read": False,
                "can_push": None,
                "branch_exists": None,
                "org_probe": None,
                "interpretation": "family_config is None — cannot determine publish target",
            })
            continue

        status = getattr(config, "status", "unknown")
        if status not in {"active"}:
            resolution_records.append({
                "family": family,
                "config_path": config_path,
                "error_classification": "skipped_family_not_active",
                "can_read": False,
                "can_push": None,
                "branch_exists": None,
                "org_probe": None,
                "interpretation": f"Family status={status} — not active, skipping access check",
            })
            continue

        github_cfg = getattr(config, "github", None)
        pub_repo = getattr(github_cfg, "published_plugin_examples_repo", None) if github_cfg else None
        if pub_repo is None:
            resolution_records.append({
                "family": family,
                "config_path": config_path,
                "error_classification": UNKNOWN_ERROR,
                "can_read": False,
                "can_push": None,
                "branch_exists": None,
                "org_probe": None,
                "interpretation": "No published_plugin_examples_repo in family config",
            })
            continue

        owner = getattr(pub_repo, "owner", "") or ""
        repo = getattr(pub_repo, "repo", "") or ""
        branch = getattr(pub_repo, "branch", "main") or "main"

        access = check_repo_access(owner, repo, branch, headers=headers)

        # Probe org (cached)
        if owner not in org_probes:
            org_probes[owner] = probe_org_repo_creation(owner, headers=headers)
        org_probe = org_probes[owner]

        record = {
            "family": family,
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "config_path": config_path,
            "error_classification": access["error_classification"],
            "can_read": access["can_read"],
            "can_push": access["can_push"],
            "default_branch": access["default_branch"],
            "visibility": access["visibility"],
            "branch_exists": access["branch_exists"],
            "permissions_object": access["permissions_object"],
            "http_status": access["http_status"],
            "org_probe": org_probe,
            "interpretation": access["interpretation"],
            # 4-tier readiness
            "config_ready": True,  # we got here, so config has a target
            "repo_access_ready": access["can_read"],
            "pr_permission_ready": bool(access["can_push"]),
            "live_publish_ready": False,  # never automated without human approval
        }
        resolution_records.append(record)

    accessible = [r for r in resolution_records if r.get("can_read")]
    blocked = [r for r in resolution_records if not r.get("can_read")]

    result = {
        "resolution_type": "github_repo_access_resolution",
        "resolution_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "sprint": "Repo Access Resolution and Repeatable Target Provisioning Sprint",
        "token_present": token_present,
        "families": resolution_records,
        "summary": {
            "total_checked": len(resolution_records),
            "accessible": len(accessible),
            "blocked": len(blocked),
            "accessible_families": [r["family"] for r in accessible],
            "blocked_families": [r["family"] for r in blocked],
            "live_publish_allowed": False,
            "note": (
                "live_publish_ready=False for all families. "
                "Live publish requires: repo_access_ready=True, "
                "pr_permission_ready=True, and explicit human approval gate. "
                "dry_run=True is enforced in publisher regardless."
            ),
        },
    }

    output_dir = verification_dir / "latest" if promote_latest else verification_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "family-repo-access-resolution.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info("Repo access resolution written: %s", output_path)

    return result
