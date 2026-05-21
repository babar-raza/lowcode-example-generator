# Process: Branch Auto-Delete Governance

**Process ID:** LANE-J-06
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

Sprint 57 Defect D09: `branch-deletion-policy.md` contained policy text only — no implementation, no tests.

Sprint 58 Phase 7 implemented `delete_branch_after_merge()` in `github_pr_merger.py` with 7 dry-run tests.

---

## Implementation

**Module:** `src/plugin_examples/publisher/github_pr_merger.py`

**Key constants:**
```python
_LOWCODE_BRANCH_PREFIXES = ("lowcode-pilot-", "lowcode-wave-")
```

**Function signature:**
```python
def delete_branch_after_merge(
    owner: str,
    repo: str,
    branch_ref: str,
    github_token: str,
    allow_branch_auto_delete: bool = False,
    dry_run: bool = True,
) -> dict:
```

**Safety rules (all enforced in code):**
1. Only branches matching `lowcode-pilot-*` or `lowcode-wave-*` prefixes are eligible
2. `allow_branch_auto_delete=False` by default — must explicitly opt in
3. `dry_run=True` by default — never deletes without explicit `dry_run=False`
4. Non-lowcode branches → `action: "skipped"` always

---

## Integration in merge_pr()

`delete_branch_after_merge()` is called as Step 3 in `merge_pr()`:
```python
delete_result = delete_branch_after_merge(
    owner=owner, repo=repo, branch_ref=branch_ref,
    github_token=github_token,
    allow_branch_auto_delete=False,  # safe default
    dry_run=True,
)
```

To activate live deletion, caller must pass:
```python
allow_branch_auto_delete=True, dry_run=False
```

---

## Tests (7 cases)

| Test | Scenario |
|------|----------|
| `test_dry_run_by_default` | Default call → action=dry_run_would_delete |
| `test_skips_non_lowcode_branch` | Non-prefixed branch → action=skipped |
| `test_skips_feature_branch` | feature/* branch → action=skipped |
| `test_skips_when_flag_disabled` | allow_branch_auto_delete=False → action=skipped |
| `test_lowcode_wave_prefix_recognized` | lowcode-wave-* prefix → recognized |
| `test_dry_run_does_not_call_api` | dry_run=True → no HTTP DELETE call |
| `test_no_api_call_when_flag_disabled` | allow_branch_auto_delete=False → no HTTP DELETE |

All 7 tests PASS.

---

## Activation for Live Deletion

Future sprints can activate live branch deletion by:
1. Setting `allow_branch_auto_delete=True` in the `merge_pr()` call
2. Setting `dry_run=False`
3. Confirming the branch has a recognized lowcode prefix

Requires explicit opt-in — cannot happen by accident.
