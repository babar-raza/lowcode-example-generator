# PDF PR Conflict Analysis — Sprint 45 Lane C

## PR Status (live GitHub API)

| PR | Branch | Mergeable |
|----|--------|-----------|
| #5 | plugin-examples/pdf/20260518-150226 | CONFLICTING |
| #6 | plugin-examples/pdf/20260518-150254 | CONFLICTING |
| #7 | plugin-examples/pdf/20260518-150331 | CONFLICTING |
| #8 | plugin-examples/pdf/20260518-150408 | CONFLICTING |
| #9 | plugin-examples/pdf/20260518-150429 | CONFLICTING |
| #10 | plugin-examples/pdf/20260518-150454 | CONFLICTING |

## Conflict Root Cause
All 6 PRs conflict on README.md. PRs #8-#10 also conflict on build config files.

## Existing Dry-Run Packages
Local packages exist at `workspace/pr-dry-run/pdf-controlled-pilot-pr{5..9}/`.

## Recovery Strategy
Preferred: Close existing PRs, recreate from fresh branches against current target main.
Requires: `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`

## Gate Status
- APPROVE_LIVE_PR: ABSENT — recovery blocked
- APPROVE_MERGE_PR: ABSENT — merge blocked

## Verdict
PDF_PR_CONFLICT_RECOVERY_BLOCKED — packages exist locally, remote action requires approval.
