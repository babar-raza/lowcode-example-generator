# PR Lifecycle Contract

Date: 2026-06-08

## States
| State | Meaning |
|-------|---------|
| `CANONICAL_PACKAGE_PROVEN` | Example built and run; output validated locally |
| `PR_PACKET_GENERATED` | PR files prepared in sprint |
| `PR_CREATED` | PR opened on target repo (requires real PR URL) |
| `EXTERNAL_REVIEW_PENDING` | Awaiting maintainer review/merge |
| `MERGE_READY_APPROVAL_BLOCKED` | All checks pass; blocked on human approval |
| `MERGED` | GitHub confirms merged_at is not null |
| `BRANCH_CLEANED` | Source branch deleted after merge |
| `PUBLISHED` | Release pipeline triggered (external) |

## Invariants
- `PR_CREATED` requires real `pr_url`
- `MERGED` requires GitHub `merged_at` timestamp
- `BRANCH_CLEANED` requires branch lookup proving branch does not exist
- `PUBLISHED` requires external release confirmation
- No status may be inflated (e.g., claiming MERGED when only PR_CREATED)

## Post-Merge Branch Cleanup Policy
1. After PR merge is confirmed: source branch SHOULD be deleted
2. GitHub can auto-delete on merge (repo setting)
3. Manual deletion: `gh api repos/{repo}/git/refs/heads/{branch} --method DELETE`
4. Only delete branches that:
   - Are confirmed merged (not closed-unmerged)
   - Belong to the expected repo
   - Are not protected branches
5. Deletion requires human approval unless auto-delete is enabled in repo settings

## Approval Packets
Any merge or branch deletion requiring human action is documented in:
`approval-packets/merge-and-branch-cleanup-approval.md`
