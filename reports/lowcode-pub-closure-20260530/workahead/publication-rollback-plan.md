# Publication Rollback Plan — lowcode-pub-closure-20260530

If a PR causes issues after merge:
1. Create revert PR: `gh pr create --title "revert: ..." --body "Reverts #N"`
2. Or directly revert commit: `git revert <sha>`
3. No force-push to main branches
4. Communicate via PR comments
