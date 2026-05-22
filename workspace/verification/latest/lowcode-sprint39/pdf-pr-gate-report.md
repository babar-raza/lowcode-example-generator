# Lane C — PDF PR Merge and Publication Gate Report

**Date:** 2026-05-19
**Status:** APPROVAL_GATES_SET_BUT_PRS_CLOSED

## Approval Gates

| Gate | Status |
|------|--------|
| GITHUB_TOKEN | AVAILABLE |
| APPROVE_MERGE_PR | SET |
| APPROVE_LIVE_PR | SET |

## PR Status

| PR | State | Merged | Closed At |
|----|-------|--------|-----------|
| #5 | CLOSED | NO | 2026-05-19T05:53:19Z |
| #6 | CLOSED | NO | 2026-05-19T05:53:22Z |
| #7 | CLOSED | NO | 2026-05-19T05:53:24Z |
| #8 | CLOSED | NO | 2026-05-19T05:53:27Z |
| #9 | CLOSED | NO | 2026-05-19T05:53:31Z |
| #10 | CLOSED | NO | 2026-05-19T05:53:34Z |

All 6 PRs were closed without merging (mergedAt: null). Closure was recent (today, ~05:53 UTC).

## Impact

- **14 examples remain unpublished** in the target repo
- **PDF published count stays at 5** (Merger, TextExtractor, PdfAConverter, Splitter, Optimizer)
- PR packages and contracts are still valid locally
- Target repo is HEALTHY but only has 5 examples

## Actions NOT Taken

- Did not attempt to reopen or recreate PRs (requires operator decision)
- Did not merge (PRs are closed, cannot merge closed PRs)
- Did not create new live PRs (need operator guidance on strategy)

## Recommendation

Operator should decide whether to:
1. Recreate PRs from existing dry-run packages
2. Consolidate all 14 examples into fewer PRs
3. Use batch publication pipeline

The approval gates are set, so publication is authorized once new PRs are created.

## Target Repo Health

All 6 family repos: HEALTHY (verified via GH CLI)
