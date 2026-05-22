# PDF PR Conflict Analysis — Sprint 44 Lane B

## PR Status (live from GitHub API)

| PR | Branch | Mergeable | State |
|----|--------|-----------|-------|
| #5 | plugin-examples/pdf/20260518-150226 | CONFLICTING | open |
| #6 | plugin-examples/pdf/20260518-150254 | CONFLICTING | open |
| #7 | plugin-examples/pdf/20260518-150331 | CONFLICTING | open |
| #8 | plugin-examples/pdf/20260518-150408 | CONFLICTING | open |
| #9 | plugin-examples/pdf/20260518-150429 | CONFLICTING | open |
| #10 | plugin-examples/pdf/20260518-150454 | CONFLICTING | open |

## Conflict Root Cause
All 6 PRs conflict on README.md (and build configs for #8-#10). The target repo's main branch has diverged since the PRs were created.

## Recovery Strategy
1. Close existing PRs
2. Recreate from fresh branches against current main
3. Requires `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`

## Gate Status
- `APPROVE_LIVE_PR`: ABSENT — recovery blocked
- `APPROVE_MERGE_PR`: ABSENT — merge blocked

## Impact
14 PDF examples stuck at PR_DRY_RUN_READY until conflicts resolved and PRs merged.

## Verdict
PDF_PR_CONFLICT_ANALYSIS_COMPLETE — all 6 PRs confirmed CONFLICTING, recovery blocked by absent gate.
