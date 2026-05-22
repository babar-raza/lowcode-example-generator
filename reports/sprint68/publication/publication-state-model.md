# Publication State Model — Sprint 68

Date: 2026-05-22
Sprint: sprint68

## State

```
SPRINT_68_DEFECT_REPAIR_COMPLETE_PUBLICATION_BLOCKED_BY_APPROVAL
```

## Fields

| Field | Value |
|-------|-------|
| approval_token_present | false |
| approval_token_required | APPROVE_LIVE_PR |
| sprint_scope | DEFECT_REPAIR |
| new_packages_generated | false |
| handoff_packages_ready | true |
| handoff_package_count | 42 |
| publication_blocked | true |
| block_reason | APPROVE_LIVE_PR_NOT_SET |

## Separation of Concerns

Publication and sprint closure are separate states:
- Sprint 68 closure is COMPLETE when EV 57/57 PASS and ECC closed
- Publication is BLOCKED independently by missing token
- Sprint 68 does NOT require live publication for closure

## Families Awaiting Publication

| Family | Pending Action | Package Version |
|--------|---------------|-----------------|
| words | PR creation + merge | 26.5.0 |
| diagram | PR creation + merge | 26.5.0 |

## Notes

PDF version drift resolved: content-audit-sprint68.json shows all PDF records at 26.5.0.
The remote repos for words and diagram still show 26.4.0 — version update PRs are pending.
