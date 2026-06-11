"""Post-merge remote truth verifier — TC-REMOTE-001.

Read-only verification of publication state against GitHub API.
Never mutates remote repositories.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com"


@dataclass
class RemoteTruthResult:
    """Result of a single remote truth verification."""
    owner: str
    repo: str
    pr_number: int
    pr_exists: bool = False
    pr_merged: bool = False
    pr_state: str = "unknown"
    branch_exists: bool | None = None
    file_exists: bool | None = None
    file_path_checked: str | None = None
    error: str | None = None


def _headers(token: str | None) -> dict:
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def verify_pr_state(
    owner: str, repo: str, pr_number: int, token: str | None = None
) -> RemoteTruthResult:
    """Verify PR existence and merge state (read-only)."""
    result = RemoteTruthResult(owner=owner, repo=repo, pr_number=pr_number)
    try:
        url = f"{_GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
        resp = requests.get(url, headers=_headers(token), timeout=30)
        if resp.status_code == 404:
            result.error = "PR not found (404)"
            return result
        resp.raise_for_status()
        data = resp.json()
        result.pr_exists = True
        result.pr_state = data.get("state", "unknown")
        result.pr_merged = data.get("merged_at") is not None
    except requests.RequestException as exc:
        result.error = str(exc)
    return result


def verify_branch_exists(
    owner: str, repo: str, branch: str, token: str | None = None
) -> bool:
    """Check if a branch exists on the remote (read-only)."""
    try:
        url = f"{_GITHUB_API}/repos/{owner}/{repo}/branches/{branch}"
        resp = requests.get(url, headers=_headers(token), timeout=30)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def verify_file_on_branch(
    owner: str, repo: str, branch: str, path: str, token: str | None = None
) -> bool:
    """Check if a file exists on a specific branch (read-only)."""
    try:
        url = f"{_GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
        resp = requests.get(url, headers=_headers(token), params={"ref": branch}, timeout=30)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def run_remote_truth_check(
    publication_records: list[dict],
    token: str | None = None,
) -> list[RemoteTruthResult]:
    """Run remote truth verification for a list of publication records.

    Each record must have: owner, repo, pr_number.
    Optional: branch, expected_file_path.
    """
    results = []
    for rec in publication_records:
        owner = rec["owner"]
        repo = rec["repo"]
        pr_number = rec["pr_number"]

        result = verify_pr_state(owner, repo, pr_number, token)

        branch = rec.get("branch")
        if branch and result.pr_merged:
            result.branch_exists = verify_branch_exists(owner, repo, branch, token)

        file_path = rec.get("expected_file_path")
        if file_path and result.pr_merged:
            default_branch = rec.get("default_branch", "main")
            result.file_exists = verify_file_on_branch(owner, repo, default_branch, file_path, token)
            result.file_path_checked = file_path

        results.append(result)
    return results


def write_remote_truth_report(results: list[RemoteTruthResult], output_path: Path) -> None:
    """Write remote truth results to a JSON file."""
    data = {
        "verification_type": "remote_truth",
        "total_checked": len(results),
        "total_merged": sum(1 for r in results if r.pr_merged),
        "total_errors": sum(1 for r in results if r.error),
        "results": [asdict(r) for r in results],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
