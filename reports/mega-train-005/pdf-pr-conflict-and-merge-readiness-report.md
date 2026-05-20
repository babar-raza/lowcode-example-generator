# Lane B: PDF PR Conflict and Merge Readiness Report

**Sprint:** LOWCODE-MEGA-TRAIN-005
**Date:** 2026-05-20

## Current State

- **Published PDF examples:** 5 (merged PRs #2, #4, #11, #17-#21)
- **PR-ready examples:** 14
- **Total PDF denominator:** 19 runnable (of 101 total types)
- **Conservation:** PASS (5 published + 14 PR-ready = 19 = runnable)

## PR Status Assessment

### Published (5 examples via merged PRs)
Already merged and live in aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples.

### PR-Ready (14 examples)
These 14 examples are in PR_DRY_RUN_READY state locally. PRs for these were either:
- Never created (need APPROVE_LIVE_PR)
- Created but likely CONFLICTING due to base branch changes from merged PRs

### Superseded PRs (#5-#10)
PRs #5-#10 were created for earlier waves and are now superseded by the merged PRs. They should be closed but require write access.

## Blockers

| Blocker | Type | Required Gate |
|---------|------|---------------|
| Live publish approval | Gate absent | PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR |
| Merge approval | Gate absent | PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR |

## Recovery Plan (When Approval Granted)

### Step 1: Close superseded PRs
```bash
for pr in 5 6 7 8 9 10; do
  gh pr close $pr --repo aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples --comment "Superseded by merged PRs"
done
```

### Step 2: Recreate PRs for 14 remaining examples
```bash
export GITHUB_TOKEN="$GH_TOKEN"
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family pdf --publish \
  --approval-token APPROVE_LIVE_PR \
  --package-path workspace/pr-dry-run/pdf-controlled-pilot
```

### Step 3: Merge after human review
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family pdf --pr-number <N> --merge \
  --approval-token APPROVE_MERGE_PR
```

### Rollback Plan
- PRs can be closed without merging
- No code is pushed until approval gates are present
- Package artifacts preserved locally for recreation

## Dry-Run Verification
- Local package exists: workspace/pr-dry-run/pdf-controlled-pilot
- All 14 examples build+run verified in prior sprints
- README audit passes for all examples

## Verdict
**PDF_PR_APPROVAL_BLOCKED** — 14 examples ready, blocked only by absent approval gates.
No local work needed. Recovery plan documented above.
