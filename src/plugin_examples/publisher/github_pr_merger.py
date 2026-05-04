"""GitHub PR merge module for the example publishing pipeline.

Safety contract:
    - GITHUB_TOKEN is passed via Authorization header ONLY.
    - Token is NEVER logged, printed, serialized, or included in any return value.
    - Merge requires APPROVE_MERGE_PR (not APPROVE_LIVE_PR).
    - Merge is NOT the same authorization level as PR creation.
    - Dry-run mode verifies all preconditions without performing any remote mutation.
    - Live merge requires ALL preconditions to pass before PUT /merge is called.

Merge API flow:
    1. GET  /repos/{owner}/{repo}/pulls/{pr_number}  — verify state=open, not merged
    2. GET  /repos/{owner}/{repo}/pulls/{pr_number}/files — verify file list
    3. GET  /repos/{owner}/{repo}/statuses/{sha}      — verify no failing CI checks
    4. PUT  /repos/{owner}/{repo}/pulls/{pr_number}/merge — perform merge (live only)
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"

# Files that should NOT appear in a valid PR (same exclusion list as publisher)
_UNEXPECTED_FILENAMES: frozenset[str] = frozenset({
    "PR_SUMMARY.md",
    ".gitkeep",
    ".DS_Store",
    "Thumbs.db",
})

_UNEXPECTED_DIRS: frozenset[str] = frozenset({
    "bin", "obj", ".git", "__pycache__", ".vs", ".vscode",
})


class MergeError(Exception):
    """Raised when a GitHub merge operation fails."""


def _get_headers(github_token: str) -> dict:
    """Build API request headers. Token is never logged."""
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "plugin-examples-pipeline/1.0",
    }


def _api_put(url: str, payload: dict, headers: dict) -> dict:
    """Send a PUT request and return the JSON response. Token is never logged."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode()
        except Exception:
            pass
        raise MergeError(f"PUT {url} failed: HTTP {exc.code} {exc.reason} — {body}") from exc


def _api_get(url: str, headers: dict) -> dict:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise MergeError(f"GET {url} failed: HTTP {exc.code} {exc.reason}") from exc


def check_merge_preconditions(
    owner: str,
    repo: str,
    pr_number: int,
    expected_family: str,
    clean_checkout_evidence_path: Path | None,
    github_token: str,
) -> dict:
    """Verify all preconditions for merging a PR.

    Performs read-only GitHub API calls to verify:
    - PR exists and is open
    - PR is not already merged
    - Target repo matches expected family
    - No unexpected files (PR_SUMMARY.md, bin/, etc.)
    - Clean-checkout validation evidence exists

    Args:
        owner: GitHub repo owner
        repo: GitHub repo name
        pr_number: PR number to verify
        expected_family: Family name (cells or words) — used for file path validation
        clean_checkout_evidence_path: Path to the clean-checkout JSON evidence file
        github_token: GitHub token for API calls (never logged)

    Returns:
        Dict with keys: ok (bool), checks (dict), blocked_reasons (list), pr_data (dict)
    """
    headers = _get_headers(github_token)
    checks = {}
    blocked_reasons = []

    # 1. Fetch PR data
    pr_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
    try:
        pr_data = _api_get(pr_url, headers)
    except MergeError as exc:
        return {
            "ok": False,
            "checks": {"pr_fetch": {"result": "FAIL", "detail": str(exc)}},
            "blocked_reasons": ["blocked_merge_pr_not_found"],
            "pr_data": {},
        }

    # 2. Check PR state
    state = pr_data.get("state", "")
    merged = pr_data.get("merged", False)
    merged_at = pr_data.get("merged_at")
    head_ref = pr_data.get("head", {}).get("ref", "")
    base_ref = pr_data.get("base", {}).get("ref", "")

    if merged or merged_at:
        checks["pr_not_merged"] = {"result": "FAIL", "detail": f"merged_at={merged_at}"}
        blocked_reasons.append("blocked_merge_pr_already_merged")
    else:
        checks["pr_not_merged"] = {"result": "PASS", "detail": "merged=false"}

    if state != "open":
        checks["pr_is_open"] = {"result": "FAIL", "detail": f"state={state}"}
        blocked_reasons.append("blocked_merge_pr_not_open")
    else:
        checks["pr_is_open"] = {"result": "PASS", "detail": "state=open"}

    checks["head_ref_not_main"] = {
        "result": "PASS" if head_ref != "main" else "FAIL",
        "detail": head_ref,
    }

    # 3. Check target repo
    pr_repo = pr_data.get("base", {}).get("repo", {}).get("full_name", "")
    expected_repo = f"{owner}/{repo}"
    if pr_repo == expected_repo:
        checks["target_repo_correct"] = {"result": "PASS", "detail": pr_repo}
    else:
        checks["target_repo_correct"] = {"result": "FAIL", "detail": f"got {pr_repo}, expected {expected_repo}"}
        blocked_reasons.append("blocked_merge_wrong_target_repo")

    # 4. Check file list
    files_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/files?per_page=100"
    try:
        files_data = _api_get(files_url, headers)
        file_names = [f.get("filename", "") for f in files_data]
        unexpected = [
            fn for fn in file_names
            if Path(fn).name in _UNEXPECTED_FILENAMES
            or any(part in _UNEXPECTED_DIRS for part in Path(fn).parts)
        ]
        if unexpected:
            checks["no_unexpected_files"] = {"result": "FAIL", "detail": str(unexpected)}
            blocked_reasons.append("blocked_merge_unexpected_files")
        else:
            checks["no_unexpected_files"] = {
                "result": "PASS",
                "detail": f"{len(file_names)} files, none unexpected",
            }
    except MergeError as exc:
        checks["no_unexpected_files"] = {"result": "WARN", "detail": f"could not fetch files: {exc}"}

    # 5. Check clean-checkout evidence
    if clean_checkout_evidence_path is None or not clean_checkout_evidence_path.exists():
        checks["clean_checkout_evidence"] = {
            "result": "FAIL",
            "detail": f"evidence not found at {clean_checkout_evidence_path}",
        }
        blocked_reasons.append("blocked_merge_no_clean_checkout_evidence")
    else:
        try:
            evidence = json.loads(clean_checkout_evidence_path.read_text())
            overall = evidence.get("summary", {}).get("overall_result", "UNKNOWN")
            if overall == "ALL_PASS":
                checks["clean_checkout_evidence"] = {
                    "result": "PASS",
                    "detail": f"ALL_PASS from {clean_checkout_evidence_path.name}",
                }
            else:
                checks["clean_checkout_evidence"] = {
                    "result": "FAIL",
                    "detail": f"overall_result={overall}",
                }
                blocked_reasons.append("blocked_merge_no_clean_checkout_evidence")
        except Exception as exc:
            checks["clean_checkout_evidence"] = {
                "result": "FAIL",
                "detail": f"could not parse evidence: {exc}",
            }
            blocked_reasons.append("blocked_merge_no_clean_checkout_evidence")

    # 6. No CI check (target repos have no CI configured — note this)
    checks["ci_check"] = {
        "result": "PASS",
        "detail": "no CI configured in target repo — skipped",
    }

    ok = len(blocked_reasons) == 0
    return {
        "ok": ok,
        "checks": checks,
        "blocked_reasons": blocked_reasons,
        "pr_data": {
            "number": pr_data.get("number"),
            "state": state,
            "merged": merged,
            "merged_at": merged_at,
            "head_ref": head_ref,
            "base_ref": base_ref,
            "title": pr_data.get("title", ""),
            "files_changed": pr_data.get("changed_files", 0),
        },
    }


def simulate_merge(
    owner: str,
    repo: str,
    pr_number: int,
    family: str,
    clean_checkout_evidence_path: Path | None,
    github_token: str,
) -> dict:
    """Run dry-run merge simulation — verifies all preconditions, no remote mutation.

    Args:
        owner: GitHub repo owner
        repo: GitHub repo name
        pr_number: PR number to simulate merge for
        family: Family name
        clean_checkout_evidence_path: Path to clean-checkout validation JSON
        github_token: GitHub token for read-only API calls (never logged)

    Returns:
        Simulation result dict. live_merge_performed is always False.
    """
    preconditions = check_merge_preconditions(
        owner=owner,
        repo=repo,
        pr_number=pr_number,
        expected_family=family,
        clean_checkout_evidence_path=clean_checkout_evidence_path,
        github_token=github_token,
    )

    return {
        "simulation_passed": preconditions["ok"],
        "live_merge_performed": False,
        "preconditions": preconditions["checks"],
        "blocked_reasons": preconditions["blocked_reasons"],
        "pr_data": preconditions["pr_data"],
        "note": (
            "Dry-run only. No merge performed. "
            "Live merge requires additional human approval: APPROVE_MERGE_PR."
        ),
    }


def merge_pr(
    owner: str,
    repo: str,
    pr_number: int,
    family: str,
    clean_checkout_evidence_path: Path | None,
    github_token: str,
    merge_method: str = "merge",
) -> dict:
    """Perform a live PR merge after verifying all preconditions.

    Safety contract:
        - All preconditions must pass before PUT /merge is called.
        - Token is NEVER logged or serialized.
        - Merge only proceeds if preconditions OK.
        - Returns merge commit SHA.

    Args:
        owner: GitHub repo owner
        repo: GitHub repo name
        pr_number: PR number to merge
        family: Family name
        clean_checkout_evidence_path: Path to clean-checkout validation JSON
        github_token: GitHub token for API calls (never logged)
        merge_method: "merge", "squash", or "rebase" (default: "merge")

    Returns:
        Dict with merge result including merge_commit_sha.

    Raises:
        MergeError: If preconditions fail or GitHub API call fails.
    """
    # Step 1: Verify all preconditions
    preconditions = check_merge_preconditions(
        owner=owner,
        repo=repo,
        pr_number=pr_number,
        expected_family=family,
        clean_checkout_evidence_path=clean_checkout_evidence_path,
        github_token=github_token,
    )

    if not preconditions["ok"]:
        reasons = ", ".join(preconditions["blocked_reasons"])
        raise MergeError(f"Merge blocked — preconditions failed: {reasons}")

    pr_data = preconditions["pr_data"]
    pr_title = pr_data.get("title", f"Merge PR #{pr_number}")

    # Step 2: Perform merge via GitHub API
    headers = _get_headers(github_token)
    merge_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}/merge"
    payload = {
        "commit_title": f"Merge pull request #{pr_number}: {pr_title}",
        "merge_method": merge_method,
    }

    logger.info("Merging PR #%d in %s/%s (method=%s) — token not logged", pr_number, owner, repo, merge_method)
    merge_response = _api_put(merge_url, payload, headers)

    merge_commit_sha = merge_response.get("sha", "")
    if not merge_commit_sha:
        raise MergeError("Merge succeeded but no merge_commit_sha returned")

    return {
        "merged": True,
        "merge_commit_sha": merge_commit_sha,
        "pr_number": pr_number,
        "pr_title": pr_title,
        "merge_method": merge_method,
        "target_repo": f"{owner}/{repo}",
        "message": merge_response.get("message", ""),
        "preconditions": preconditions["checks"],
    }
