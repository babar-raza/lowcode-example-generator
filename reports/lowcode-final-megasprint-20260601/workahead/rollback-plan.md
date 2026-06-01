# Rollback Plan

If any PR causes issues after merge:
1. Revert the merge commit: `git revert <merge-sha>`
2. Push revert to main
3. Close any related PRs
4. Document in incident log
