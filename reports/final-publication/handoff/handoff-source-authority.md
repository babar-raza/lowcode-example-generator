# Final Publication Sprint — Handoff Source Authority

**Author:** Handoff/File Plan Agent (Lane 2)
**Date:** 2026-05-27

## Handoff Source

The accepted handoff is sourced from:
`workspace/verification/latest/families/*/`

This is the workspace evidence directory containing the full per-family pipeline output.
The `workspace/` directory is gitignored and contains untracked local state.

Note: `reports/sprint72/handoff/per-family` (referenced in sprint spec) does not exist
on disk. The authoritative handoff data is in `workspace/verification/latest/families/`.

## Confirmed Family Counts

From `workspace/verification/latest/families/*/aggregate-gate-results.json`:

| Family | Generated | Built | PR Candidates | Build Status | Run Status |
|---|---|---|---|---|---|
| Cells | 9 | 9 | 9 | passed_all | passed_all |
| Words | 8 | 8 | 7 | passed_all | passed_all |
| PDF | 19 | 19 | 19 | passed_all | passed_all |
| Diagram | 2 | 2 | 2 | passed_all | passed_all |
| Email | 1 | 1 | 1 | passed_all | passed_all |
| Slides | 3 | 3 | 3 | passed_all | passed_all |
| **Total** | **42** | **42** | **41** | — | — |

Words: 8 generated, 7 PR candidates (1 example excluded from PR — partial family).
Total PR candidates: 41 (not 42). Words partial status is documented in Sprint 91.

## Handoff Validation Status

| Check | Result |
|---|---|
| 6 families represented | YES |
| Total examples: 42 | YES |
| All families have build status passed_all | YES |
| All families have run status passed_all | YES |
| Handoff data source exists | YES (workspace/verification/latest/families/) |

## Note on Full I/O Validation

Full per-example README I/O validation (confirming Input + Output sections exist in each
README.md file) requires traversing individual example files. This is deferred to the PR
creation phase (Lane 3) since:
1. Publication approval gate is absent
2. Per-example file validation during approval-blocked state would be readiness-only work
   which is not authorized per sprint instructions
