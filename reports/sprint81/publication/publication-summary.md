# Sprint 81 -- Publication Summary

## Approval Gate

| Gate | Status |
|------|--------|
| PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL | NOT_SET |
| PLUGIN_EXAMPLES_MERGE_PR_APPROVAL | NOT_SET |

**Verdict: LOWCODE_LIVE_PUBLICATION_BLOCKED_BY_APPROVAL**

## Remote State (as of 2026-05-24)

| Family | Examples | Code Published | README I/O | Version |
|--------|----------|---------------|-----------|---------|
| cells | 9 | YES | 0/9 NO_IO | 26.5.0 |
| words | 8 | YES | 0/8 NO_IO | 26.5.0 |
| pdf | 19 | YES | 1/19 partial (pdf-signature output-only) | latest |
| diagram | 2 | YES | 0/2 NO_IO | latest |
| email | 1 | YES | 0/1 NO_IO | latest |
| slides | 3 | YES | 0/3 NO_IO | latest |
| **Total** | **42** | **42/42** | **0/42 full I/O** | all ok |

## Local Handoff State

| Family | Examples | README I/O Ready |
|--------|----------|-----------------|
| cells | 9 | 9/9 (## Input and Output) |
| words | 8 | 8/8 |
| pdf | 19 | 19/19 |
| diagram | 2 | 2/2 |
| email | 1 | 1/1 |
| slides | 3 | 3/3 |
| **Total** | **42** | **42/42** |

## Words Version Drift

**RESOLVED** — Remote=26.5.0 = Handoff=26.5.0. No version bump needed.

## PR Status

| Family | PR URL | Status |
|--------|--------|--------|
| cells | (not created) | APPROVAL_BLOCKED |
| words | (not created) | APPROVAL_BLOCKED |
| pdf | (not created) | APPROVAL_BLOCKED |
| diagram | (not created) | APPROVAL_BLOCKED |
| email | (not created) | APPROVAL_BLOCKED |
| slides | (not created) | APPROVAL_BLOCKED |

## Publication Status Distribution

| Status | Count |
|--------|-------|
| CODE_PUBLISHED_README_IO_PENDING_APPROVAL | 41 |
| CODE_PUBLISHED_README_PARTIAL_IO_PENDING_BACKFILL | 1 (pdf-signature) |

## Existing Open PRs (Root README Backfill)

| Family | PR# | Status |
|--------|-----|--------|
| cells | #5 | OPEN (root README only) |
| words | #7 | OPEN (root README only) |
| diagram | #2 | OPEN (root README only) |

## Remaining Blocker

Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` to proceed with Sprint 82 README I/O publication.
