# Sprint 66 — Publication State Model

Generated: 2026-05-22
Sprint: sprint66-remote-truth-repair-self-contained-artifacts-readme-io-publication-proof

## Motivation

Sprint 65 mixed two incompatible states: "42/42 already published" and "APPROVAL_BLOCKED".
This model separates historical publication, current remote content accuracy, dry-run readiness,
and live approval state into distinct per-example fields.

## State Fields (per example)

| Field | Type | Meaning |
|-------|------|---------|
| `remote_example_present` | bool | Example path exists in remote repo |
| `remote_programcs_sha` | string | SHA of Program.cs in remote repo |
| `remote_readme_has_io_docs` | bool | Remote README has "## Input and Output" section |
| `remote_root_readme_current` | bool/null | Root README lists this example with correct version |
| `dry_run_package_ready` | bool | Local dry-run package exists with corrected README |
| `live_pr_needed` | bool | Remote state differs from dry-run package (needs update PR) |
| `live_pr_open` | bool | A PR is currently open for this example |
| `live_pr_merged` | bool | A PR has been merged that introduced this example |
| `post_merge_verified` | bool | Remote content was verified after merge |
| `branch_deleted` | bool/null | PR branch was deleted after merge |
| `approval_blocked` | bool | PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL not present |

## Status Values

| Status | Meaning |
|--------|---------|
| `REMOTE_PUBLISHED_CURRENT` | Remote example present, README has I/O, Program.cs matches authority |
| `REMOTE_PUBLISHED_STALE_README` | Remote example present, README is old-format, no corrected package available |
| `REMOTE_PUBLISHED_STALE_IO` | Remote example present, README is old-format, corrected package available (needs PR) |
| `REMOTE_MISSING` | No example directory in remote repo |
| `DRY_RUN_READY_NOT_PUBLISHED` | Package ready but no remote publish yet |
| `APPROVAL_BLOCKED` | Live PR not created because approval env var absent |
| `BLOCKED` | Publication blocked by technical issue |

## Current State (2026-05-22)

| Status | Count |
|--------|-------|
| REMOTE_PUBLISHED_STALE_IO | 42 |
| REMOTE_PUBLISHED_CURRENT | 0 |
| REMOTE_MISSING | 0 |

**All 42 examples are in state `REMOTE_PUBLISHED_STALE_IO`:**
- Remote path exists ✓
- Remote README is OLD_FORMAT (no I/O section) ✗
- Corrected local package with I/O README available ✓
- Live PR needed: YES
- Approval token present: NO → `APPROVAL_BLOCKED`

## Separation of States

| Sprint 65 Mixed Claim | Correct Separation |
|-----------------------|-------------------|
| "42/42 already published" | TRUE for `remote_example_present=True` (all 42 paths exist) |
| "approval blocked" | TRUE for `approval_blocked=True` (README I/O updates not pushed) |
| Combined implies README I/O published | FALSE: `remote_readme_has_io_docs=False` for all 42 |

## Required Approval Token for README I/O Updates

```
PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
```

Without this token, Sprint 66 produces a self-contained dry-run handoff package
containing all 42 updated READMEs, ready for live publication in a future sprint.
