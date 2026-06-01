# Rollback Plan

1. Close PR without merging if issues found during review.
2. If merged: revert commit via `git revert` on the target repo.
3. Delete the feature branch: `git push origin --delete <branch>`.
4. No data loss risk: examples are additive, no existing files modified.
