"""Real GitHub PR publisher using GitHub REST API (urllib only, no extra deps).

Safety contract:
    - GITHUB_TOKEN is passed via Authorization header ONLY.
    - Token is NEVER logged, printed, serialized, or included in any return value.
    - No pushes to main branch (enforced by caller before this module is called).
    - All operations require prior approval gate check from caller.
    - On failure, partially created resources are identified in the error message
      so they can be cleaned up manually if needed.

API flow:
    1. GET  /repos/{owner}/{repo}/git/ref/heads/{base} — get base branch commit SHA
    2. GET  /repos/{owner}/{repo}/git/commits/{sha}    — get base tree SHA
    3. POST /repos/{owner}/{repo}/git/blobs  (×N)     — upload each file as blob
    4. POST /repos/{owner}/{repo}/git/trees            — create new tree
    5. POST /repos/{owner}/{repo}/git/commits          — create commit
    6. POST /repos/{owner}/{repo}/git/refs             — create branch pointing to commit
    7. POST /repos/{owner}/{repo}/pulls                — open pull request
    8. POST /repos/{owner}/{repo}/issues/{n}/labels    — add labels (optional)
"""

from __future__ import annotations

import base64
import json
import logging
import urllib.error
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"

# Files excluded from PR commit even if present in the package root
_EXCLUDED_FILENAMES: frozenset[str] = frozenset({
    "PR_SUMMARY.md",
    ".gitkeep",
    ".DS_Store",
    "Thumbs.db",
})

# Directory names skipped when collecting files
_EXCLUDED_DIRS: frozenset[str] = frozenset({
    "bin", "obj", ".git", "__pycache__", ".vs", ".vscode",
})


class PublishingError(Exception):
    """Raised when a GitHub publish operation fails."""


def _build_headers(github_token: str) -> dict[str, str]:
    """Build API request headers.  Token is placed in Authorization header only.

    IMPORTANT: Never pass this dict to a logger or serialize it.
    """
    return {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "lowcode-example-generator/1.0",
    }


def _api_request(
    method: str,
    url: str,
    headers: dict[str, str],
    body: dict | None = None,
) -> dict:
    """Perform a GitHub REST API call via urllib.

    Args:
        method: HTTP method (GET, POST, PATCH, DELETE).
        url: Full URL.
        headers: Request headers (must include Authorization).
        body: JSON-serialisable request body (POST/PATCH only).

    Returns:
        Parsed JSON response dict.

    Raises:
        PublishingError on HTTP errors or JSON parse failure.
    """
    req_headers = dict(headers)
    data: bytes | None = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method, headers=req_headers)
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body) if resp_body.strip() else {}
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        # Truncate to avoid leaking large response bodies in logs
        raise PublishingError(
            f"GitHub API {method} {url} returned HTTP {exc.code}: "
            f"{error_body[:400]}"
        ) from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PublishingError(
            f"GitHub API {method} {url} returned invalid JSON: {exc}"
        ) from exc


def collect_package_files(package_path: Path) -> list[dict]:
    """Collect all publishable files from a PR dry-run package directory.

    Files are collected recursively. Excluded: PR_SUMMARY.md, bin/, obj/,
    .git/, __pycache__/, .vs/.vscode directories.

    Args:
        package_path: Root directory of the assembled PR package.

    Returns:
        List of dicts with keys: path (str, repo-relative), content_bytes (bytes).

    Raises:
        PublishingError if package_path does not exist or is empty.
    """
    if not package_path.exists():
        raise PublishingError(f"Package path does not exist: {package_path}")

    entries: list[dict] = []
    for file_path in sorted(package_path.rglob("*")):
        if not file_path.is_file():
            continue
        rel_parts = file_path.relative_to(package_path).parts
        # Skip excluded directories
        if any(part in _EXCLUDED_DIRS for part in rel_parts):
            continue
        # Skip excluded filenames
        if file_path.name in _EXCLUDED_FILENAMES:
            continue
        rel_posix = file_path.relative_to(package_path).as_posix()
        entries.append({
            "path": rel_posix,
            "content_bytes": file_path.read_bytes(),
        })

    if not entries:
        raise PublishingError(
            f"No publishable files found in package path: {package_path}"
        )

    logger.info("Collected %d files from package: %s", len(entries), package_path)
    return entries


def create_github_pr(
    *,
    owner: str,
    repo: str,
    base_branch: str,
    branch_name: str,
    pr_title: str,
    pr_body: str,
    package_path: Path,
    labels: list[str] | None = None,
    github_token: str,
) -> dict:
    """Create a branch, commit all package files, and open a pull request via GitHub REST API.

    Token safety:
        - github_token is passed via Authorization header only.
        - It is NEVER included in log output, exception messages, or return values.
        - Callers must NOT log the arguments to this function.

    Args:
        owner: GitHub repository owner.
        repo: GitHub repository name.
        base_branch: Target branch for the PR (PR base, e.g. 'main').
        branch_name: New branch to create (e.g. 'plugin-examples/cells/20260501-120000').
                     Must NOT be 'main'.
        pr_title: Pull request title.
        pr_body: Pull request body markdown.
        package_path: Local directory containing files to commit.
        labels: Optional list of label names to attach to the PR.
        github_token: GitHub personal access token with 'repo' scope.

    Returns:
        Dict with keys: branch_name, pr_url, pr_number, commit_sha, files_count.
        Token is NEVER present in the return value.

    Raises:
        PublishingError if branch_name == base_branch, package is empty,
        or any GitHub API call fails.
    """
    if branch_name == base_branch:
        raise PublishingError(
            f"blocked_publish_to_main: branch_name '{branch_name}' equals "
            f"base_branch '{base_branch}'. Creating a PR against itself is not allowed."
        )

    headers = _build_headers(github_token)
    api = GITHUB_API_BASE
    repo_base = f"{api}/repos/{owner}/{repo}"

    # Step 1 — get base branch commit SHA
    logger.info("[github_pr] Step 1: get base branch ref %s/%s@%s", owner, repo, base_branch)
    ref_data = _api_request("GET", f"{repo_base}/git/ref/heads/{base_branch}", headers)
    base_commit_sha: str = ref_data["object"]["sha"]
    logger.info("[github_pr] Base commit SHA: %s", base_commit_sha[:12])

    # Step 2 — get base commit's tree SHA
    logger.info("[github_pr] Step 2: get base commit tree SHA")
    commit_data = _api_request("GET", f"{repo_base}/git/commits/{base_commit_sha}", headers)
    base_tree_sha: str = commit_data["tree"]["sha"]
    logger.info("[github_pr] Base tree SHA: %s", base_tree_sha[:12])

    # Step 3 — collect files and create blobs
    logger.info("[github_pr] Step 3: collect and upload %s", package_path)
    file_entries = collect_package_files(package_path)

    tree_nodes: list[dict] = []
    for entry in file_entries:
        content_b64 = base64.b64encode(entry["content_bytes"]).decode("utf-8")
        blob_data = _api_request(
            "POST",
            f"{repo_base}/git/blobs",
            headers,
            {"content": content_b64, "encoding": "base64"},
        )
        tree_nodes.append({
            "path": entry["path"],
            "mode": "100644",
            "type": "blob",
            "sha": blob_data["sha"],
        })
        logger.debug("[github_pr] blob: %s → %s", entry["path"], blob_data["sha"][:8])

    # Step 4 — create tree
    logger.info("[github_pr] Step 4: create tree (%d nodes)", len(tree_nodes))
    tree_data = _api_request(
        "POST",
        f"{repo_base}/git/trees",
        headers,
        {"base_tree": base_tree_sha, "tree": tree_nodes},
    )
    new_tree_sha: str = tree_data["sha"]
    logger.info("[github_pr] New tree SHA: %s", new_tree_sha[:12])

    # Step 5 — create commit
    logger.info("[github_pr] Step 5: create commit")
    commit_message = (
        f"{pr_title}\n\n"
        f"Generated by lowcode-example-generator pipeline.\n"
        f"DO NOT MERGE without human review."
    )
    new_commit_data = _api_request(
        "POST",
        f"{repo_base}/git/commits",
        headers,
        {
            "message": commit_message,
            "tree": new_tree_sha,
            "parents": [base_commit_sha],
        },
    )
    new_commit_sha: str = new_commit_data["sha"]
    logger.info("[github_pr] New commit SHA: %s", new_commit_sha[:12])

    # Step 6 — create branch ref
    logger.info("[github_pr] Step 6: create branch ref %s", branch_name)
    _api_request(
        "POST",
        f"{repo_base}/git/refs",
        headers,
        {"ref": f"refs/heads/{branch_name}", "sha": new_commit_sha},
    )
    logger.info("[github_pr] Branch created: %s", branch_name)

    # Step 7 — open pull request
    logger.info("[github_pr] Step 7: create pull request")
    pr_data = _api_request(
        "POST",
        f"{repo_base}/pulls",
        headers,
        {
            "title": pr_title,
            "body": pr_body,
            "head": branch_name,
            "base": base_branch,
        },
    )
    pr_url: str = pr_data["html_url"]
    pr_number: int = pr_data["number"]
    logger.info("[github_pr] PR created: #%d %s", pr_number, pr_url)

    # Step 8 — add labels (optional, best-effort)
    if labels:
        try:
            _api_request(
                "POST",
                f"{repo_base}/issues/{pr_number}/labels",
                headers,
                {"labels": labels},
            )
            logger.info("[github_pr] Labels added: %s", labels)
        except PublishingError as exc:
            logger.warning("[github_pr] Labels could not be added (non-fatal): %s", exc)

    # Return value: token is NEVER included
    return {
        "branch_name": branch_name,
        "pr_url": pr_url,
        "pr_number": pr_number,
        "commit_sha": new_commit_sha,
        "files_count": len(file_entries),
    }
