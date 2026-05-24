Sprint 84 — Branch Delete Plan
================================
Date: 2026-05-24
Author: Lane E

## Branches to Delete After Merge

| Family  | Branch                              | Delete After Merge? |
|---------|-------------------------------------|---------------------|
| email   | lowcode-examples-email-sprint84     | YES                 |
| slides  | lowcode-examples-slides-sprint84    | YES                 |
| diagram | lowcode-examples-diagram-sprint84   | YES                 |
| cells   | lowcode-examples-cells-sprint84     | YES                 |
| words   | lowcode-examples-words-sprint84     | YES                 |
| pdf     | lowcode-examples-pdf-sprint84       | YES                 |

## Procedure
Branches are deleted automatically by `merge-pr` command when `--delete-branch` flag is passed,
or manually via gh CLI:
```
gh api -X DELETE /repos/{org}/{repo}/git/refs/heads/{branch}
```

## Open Root-README PR Branches (DO NOT DELETE)
These are NOT sprint84 branches and must NOT be deleted:
- cells: plugin-examples/cells/readme/20260519-143139 (PR #5 open)
- words: plugin-examples/words/readme/20260519-143151 (PR #7 open)
- diagram: plugin-examples/diagram/readme/20260519-143201 (PR #2 open)

## Status
APPROVAL_BLOCKED — plan ready for execution when gates are lifted.
