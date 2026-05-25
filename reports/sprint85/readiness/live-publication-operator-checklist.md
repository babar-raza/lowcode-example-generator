Sprint 85 — Live Publication Operator Checklist
=================================================
Date: 2026-05-24
Author: Lane F

## To Create PRs
1. Set environment variable:
   PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
2. Ensure GH_TOKEN is set with repo scope (classic PAT, not fine-grained)
3. Run sprint with approval gate set
4. Expected: 6 PRs created (1 per family)

## To Merge PRs
1. Verify all 6 PRs are created and CI-green
2. Set environment variable:
   PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
3. Run sprint with merge gate set
4. Expected: 6 PRs merged, post-merge verified, branches deleted

## To Rollback
- If PR has wrong content: close PR, delete branch, re-run from handoff
- If merge introduces regression: revert merge commit on destination main
- If branch deletion was premature: branch can be recreated from merge commit

## Expected PR Content (per family)
Each PR contains only README.md files with Input/Output documentation.
No code changes, no build file changes, no root README changes.
Total files across all PRs: 42

## Approval Variables
| Variable | Value | Effect |
|----------|-------|--------|
| PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL | APPROVE_LIVE_PR | Enables PR creation |
| PLUGIN_EXAMPLES_MERGE_PR_APPROVAL | APPROVE_MERGE_PR | Enables PR merge |
| Neither set (default) | NOT_SET | Approval-blocked, plans only |
