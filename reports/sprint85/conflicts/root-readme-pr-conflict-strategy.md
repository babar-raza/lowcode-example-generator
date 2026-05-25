Sprint 85 — Root README PR Conflict Strategy
==============================================
Date: 2026-05-24
Author: Lane C (Conflict Strategy Agent)

## Strategy: EXCLUDE_ROOT_README_FROM_ALL_SPRINT85_PRS

Sprint 85 example README I/O PRs do NOT touch root README files for any family.
This eliminates all possible conflicts with existing root README-only PRs.

## Per-Family Resolution

| Family | Open Root README PR | Sprint 85 PR touches root README? | Conflict? | Resolution |
|--------|--------------------|------------------------------------|-----------|------------|
| cells | #5 (OPEN) | NO | NO | EXCLUDE — root README handled by existing PR #5 |
| words | #7 (OPEN) | NO | NO | EXCLUDE — root README handled by existing PR #7 |
| diagram | #2 (OPEN) | NO | NO | EXCLUDE — root README handled by existing PR #2 |
| pdf | none | NO | NO | NOT_CHANGED — no root README changes needed |
| email | none | NO | NO | NOT_CHANGED — no root README changes needed |
| slides | none | NO | NO | NOT_CHANGED — no root README changes needed |

## Rationale
1. Root README updates (badge links, table-of-contents) are independent of example README I/O.
2. Existing PRs #5, #7, #2 address root README content for cells, words, diagram.
3. Sprint 85 PRs only add Input/Output documentation to individual example README.md files.
4. Keeping scopes separate prevents merge conflicts and simplifies review.

## Future Handling
When root README PRs (#5, #7, #2) are merged or closed, future sprints may include
root README updates in family PRs. This is a deferred decision, not a Sprint 85 concern.
