# PDF Approval Runbook — Sprint 48

## Strategy: CLOSE_AND_RECREATE
All 6 PRs (#5-#10) conflict on README. Newer PRs (#17-#21) merged since creation.

## 6 Phases

### Phase 1: Prerequisite Check
Verify gh auth, target repo access, 6 local packages, tests pass.

### Phase 2: Close Conflicting PRs
Close #5-#10 with comment explaining recreation.

### Phase 3: Recreate PRs
Run `publish-pr` for each of 6 local packages. Requires `APPROVE_LIVE_PR`.

### Phase 4: Verify Conflict-Free
All 6 new PRs must show `mergeable=MERGEABLE`.

### Phase 5: Merge PRs
Merge via `merge-pr` command. Requires `APPROVE_MERGE_PR`.

### Phase 6: Post-Merge Validation
Verify 19 examples in target repo, conservation passes, tests pass.
