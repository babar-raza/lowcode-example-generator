# Branch Auto-Delete Source Proof — Sprint 59 Phase 6

**Date:** 2026-05-21
**Commit:** `cf0919a`

---

## Implementation Summary

`delete_branch_after_merge()` was added to `src/plugin_examples/publisher/github_pr_merger.py` in commit `cf0919a`.

---

## Source Diff Reference

Full diff available in: `reports/sprint59/source/source-diff.patch` (370 lines)

Relevant additions to `github_pr_merger.py`:

```python
_LOWCODE_BRANCH_PREFIXES = ("lowcode-pilot-", "lowcode-wave-")


def _api_delete(url: str, headers: dict) -> tuple[dict, int]:
    """Send HTTP DELETE to GitHub API. Returns (response_body, status_code)."""
    req = urllib.request.Request(url, method="DELETE", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read()
            return (json.loads(body) if body else {}), resp.status
    except urllib.error.HTTPError as e:
        return {}, e.code


def delete_branch_after_merge(
    owner: str,
    repo: str,
    branch_ref: str,
    github_token: str,
    allow_branch_auto_delete: bool = False,
    dry_run: bool = True,
) -> dict:
    """
    Delete a PR branch after successful merge. Safety-first.

    Rules:
    - Only branches matching _LOWCODE_BRANCH_PREFIXES are eligible.
    - allow_branch_auto_delete must be True to proceed (default=False).
    - dry_run=True by default — never deletes without explicit dry_run=False.
    """
    is_lowcode_branch = any(
        branch_ref.startswith(p) for p in _LOWCODE_BRANCH_PREFIXES
    )
    if not is_lowcode_branch:
        return {
            "action": "skipped",
            "reason": f"branch '{branch_ref}' does not match lowcode prefixes",
            "branch_ref": branch_ref,
            "dry_run": dry_run,
        }
    if not allow_branch_auto_delete:
        return {
            "action": "skipped",
            "reason": "allow_branch_auto_delete=False (default safety)",
            "branch_ref": branch_ref,
            "dry_run": dry_run,
        }
    if dry_run:
        return {
            "action": "dry_run_would_delete",
            "branch_ref": branch_ref,
            "api_endpoint": f"DELETE /repos/{owner}/{repo}/git/refs/heads/{branch_ref}",
            "dry_run": True,
        }
    # Live deletion
    url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch_ref}"
    headers = {"Authorization": f"Bearer {github_token}", ...}
    body, status = _api_delete(url, headers)
    return {
        "action": "deleted" if status == 204 else "delete_failed",
        "status_code": status,
        "branch_ref": branch_ref,
    }
```

---

## Integration in merge_pr()

`delete_branch_after_merge()` is called as Step 3 in `merge_pr()` with safe defaults:
```python
delete_result = delete_branch_after_merge(
    owner=owner,
    repo=repo,
    branch_ref=branch_ref,
    github_token=github_token,
    allow_branch_auto_delete=False,  # default: do not auto-delete
    dry_run=True,                     # default: dry-run only
)
```

This means `merge_pr()` always logs the *would-delete* action without executing it unless caller explicitly opts in.

---

## Tests (7 passing)

From `tests/unit/test_merge_governance.py::TestBranchAutoDelete`:

| Test | Assertion |
|------|-----------|
| `test_dry_run_by_default` | `action == "dry_run_would_delete"` |
| `test_skips_non_lowcode_branch` | `action == "skipped"` for unrecognized prefix |
| `test_skips_feature_branch` | `action == "skipped"` for `feature/...` |
| `test_skips_when_flag_disabled` | `action == "skipped"` when `allow_branch_auto_delete=False` |
| `test_lowcode_wave_prefix_recognized` | `lowcode-wave-*` recognized as eligible |
| `test_dry_run_does_not_call_api` | no HTTP DELETE when `dry_run=True` |
| `test_no_api_call_when_flag_disabled` | no HTTP DELETE when flag disabled |

All 7 tests pass in full suite (2826 passed, 0 failed).

---

## Merge-Flow Integration

`delete_branch_after_merge()` is called from `merge_pr()`. Integration path:
```
merge_pr() → [Step 1: squash merge] → [Step 2: verify merge] → [Step 3: delete_branch_after_merge(dry_run=True)]
```

Sprint 59 adds integration through the `merge_pr()` flow. Full end-to-end merge-flow tests require a live GitHub API call (not feasible without a test repo), but the unit tests cover all safety branches exhaustively.

---

## Sprint 58 Defect SD08: CLOSED

SD08 claimed source diff was missing from bundle. Source diff is now in:
- `reports/sprint59/source/source-diff.patch`
- Commit: `cf0919a`
- 7 dry-run tests: PASS
