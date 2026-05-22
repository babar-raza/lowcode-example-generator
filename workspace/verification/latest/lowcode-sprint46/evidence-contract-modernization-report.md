# Evidence Contract Modernization — Sprint 46

## New Contract: PlannerSprintEvidenceContract (planner-v1)

Validates planner/execution-loop sprint bundles with 17 required categories:

| Category | Required Files |
|----------|---------------|
| final_state_summary | final-state-summary.json/md |
| final_next_actions | final-next-actions.json/md |
| final_git_status | final-git-status.txt |
| final_git_log | final-git-log.txt |
| final_git_diff_stat | final-git-diff-stat.txt |
| final_changed_files | final-changed-files.txt |
| test_full_log | test-full-log.txt |
| test_targeted_log | test-targeted-log.txt |
| planner_cycle_ledger | planner-cycle-01.json |
| planner_final_board | final-planner-board.json |
| planner_loop_ledger | planner-loop-ledger.json |
| dirty_state_proof | final-dirty-state.json |
| taskcard_state | taskcard-state.json/md |
| local_metrics | local-metrics.json |
| bundle_manifest | bundle-manifest.json |
| no_secret_proof | no-secret-proof.txt |
| execution_ledger | execution-ledger.md |

## Content Checks
- final-state-summary.json: `head` field must exist
- final-next-actions.json: `generated_from_head` must exist
- bundle-manifest.json: all files must have `sha256`

## Tests: 14 added, all PASS
## Existing generation/publication contracts (V1-V8): UNCHANGED
