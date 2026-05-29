# Lane 6: Local Publication Package Dry-Run

**Sprint**: lowcode-durable-full-closure-20260529
**Date**: 2026-05-29
**Status**: COMPLETE

## PR Candidate Count

Total PR candidates across all families: **41**

| Family | Run ID | PR Candidates | Excluded | Publisher Status |
|--------|--------|---------------|----------|-----------------|
| cells | pilot-cells-20260529-221017 | 9 | 0 | dry_run |
| diagram | pilot-diagram-20260529-221021 | 2 | 0 | blocked (stale verification/latest) |
| words | pilot-words-20260529-221024 | 7 | 1 | dry_run |
| pdf | pilot-pdf-20260529-222233 | 19 | 0 | dry_run |
| email | pilot-email-20260529-220716 | 1 | 0 | dry_run |
| slides | pilot-slides-20260529-221814 | 3 | 0 | dry_run |
| **TOTAL** | | **41** | **1** | |

Note: The "41 + 1 = 42" truth matches the sprint truth record (words has 1 excluded example).

## Diagram Publisher Blocked Analysis

The diagram publisher reports "No passing examples to publish" because `workspace/verification/latest/families/diagram/publishing-report.json` contains a stale state from a prior run that had `BLOCKED_GENERATION`. The publisher checks this verification state before publishing.

**Root cause**: `workspace/verification/latest` is not automatically updated when a new pilot run completes. The stale state has `publishable: false` and `blocking: ['gate_generation']`.

**Impact**: The 2 diagram examples ARE valid:
- pr-candidate-manifest shows both as `current_run` / `EXAMPLE_READY_FOR_PR_DRY_RUN`
- aggregate-gate-results shows `total_pr_candidates: 2, total_excluded: 0`
- Both build and runtime pass (2/2)

**Resolution**: This is a pre-existing architectural limitation. The diagram examples will be included in the global pr-candidate-manifest (41 included) and the blocked publisher status is a false negative from stale verification state.

## Words Family: 7/8 PR Candidates

Words generates 8 examples but only 7 are PR candidates. The excluded example is a pre-existing exclusion from Sprint 91 (confirmed in sprint truth records: "Words family: 8 generated, 7 PR candidates (1 excluded)"). This is expected and does not represent a regression.

## PR Dry-Run Branches

All non-blocked families show dry_run branches prepared:
- cells: `plugin-examples/cells/...`
- words: `plugin-examples/words/...`
- pdf: `plugin-examples/pdf/...`
- email: `plugin-examples/email/...`
- slides: `plugin-examples/slides/...`

No live pushes have been performed. All operations are dry-run only.

## Publication Gate Status

All families blocked from live publication by:
- `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` approval gate = NOT SET
- This is the expected state. No live publication authorized in this sprint.
