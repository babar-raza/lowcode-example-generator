Sprint 87 — Root README Strategy Update
=========================================
Date: 2026-05-25
Author: Lane 2

## Current Open PRs (Root README Backfill)
| PR | Family | Status | Created |
|----|--------|--------|---------|
| #5 | cells | Open | Sprint 72 era |
| #7 | words | Open | Sprint 72 era |
| #2 | diagram | Open | Sprint 72 era |

## Strategy
Root README PRs were explicitly EXCLUDED from Sprint 83+ PR batching strategy.
The FAMILY_BATCH_PR approach (1 PR per family, 6 total) handles README I/O only.
Root README PRs (#2, #5, #7) remain separate and will be merged independently.

## Sprint 87 Actions
1. No new root README PRs created (approval blocked)
2. Existing PRs (#2, #5, #7) remain open — no stale close
3. Families without root README PRs (pdf, email, slides): root README will be
   included in the family batch PR when README I/O is published

## Conflict Risk Assessment
- PRs #2, #5, #7 modify only the root README.md in each family's examples directory
- README I/O PRs will modify per-example README.md files (different paths)
- **No conflict expected** — root README and per-example READMEs are separate files
- Exception: if family batch PR also updates root README, rebase required

## Next Steps (Post-Approval)
1. Merge root README PRs first (#2, #5, #7)
2. Then create family batch PRs for README I/O
3. Or: include root README update in family batch PR and close #2/#5/#7
