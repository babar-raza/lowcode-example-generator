# Branch Auto-Delete Implementation Proof — Sprint 58 Lane G

**Date:** 2026-05-21
**Defect Repaired:** Sprint 57 D09 — branch auto-delete was policy text only, no implementation or tests

---

## Implementation

**File:** `src/plugin_examples/publisher/github_pr_merger.py`

Added:
1. `_api_delete(url, headers)` — HTTP DELETE helper
2. `delete_branch_after_merge(owner, repo, branch_ref, github_token, allow_branch_auto_delete=False, dry_run=True)` — branch auto-delete with safety contract
3. Integration into `merge_pr()` — calls `delete_branch_after_merge` with `allow_branch_auto_delete=False, dry_run=True` (no-op by default)

### Safety Contract

| Condition | Behavior |
|-----------|----------|
| `branch_ref` not starting with `lowcode-pilot-` or `lowcode-wave-` | SKIP — never touch non-lowcode branches |
| `allow_branch_auto_delete=False` (default) | SKIP — explicit opt-in required |
| `dry_run=True` (default) | Returns `dry_run_would_delete` — no API call |
| `allow_branch_auto_delete=True` AND `dry_run=False` | Calls DELETE `/repos/{owner}/{repo}/git/refs/heads/{branch_ref}` |

---

## Tests

**File:** `tests/unit/test_merge_governance.py`
**Class:** `TestBranchAutoDelete` (7 tests)

| Test | Result |
|------|--------|
| `test_dry_run_by_default` | PASS |
| `test_skips_non_lowcode_branch` | PASS |
| `test_skips_feature_branch_without_prefix` | PASS |
| `test_skips_when_flag_disabled` | PASS |
| `test_lowcode_wave_prefix_recognized` | PASS |
| `test_dry_run_does_not_call_api` | PASS |
| `test_no_api_call_when_flag_disabled` | PASS |

---

## Usage (opt-in)

To enable real branch deletion after merge:
```python
delete_branch_after_merge(
    owner="aspose-cells-net",
    repo="Aspose.Cells.LowCode-for-.NET-Examples",
    branch_ref="lowcode-pilot-cells-sprint58",
    github_token=token,
    allow_branch_auto_delete=True,  # must explicitly set
    dry_run=False,                  # must explicitly set
)
```

The approval gate for this is `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`.
