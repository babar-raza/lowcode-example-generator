# Branch Deletion Policy

## Plugin Example Repos (BarCode, SVG, CAD)
- PR source branches (`lowcode/wave19/*`) must be deleted after PR merge
- Deletion script: `gh api repos/{repo}/git/refs/heads/{branch} --method DELETE`
- Requires human approval (branch deletion is destructive and irreversible)
- Approval packet: `approval-packets/merge-and-branch-cleanup-approval.md`

## LowCode Example Repos (cells, diagram, email, pdf, slides, words)
- All 6 source branches confirmed DELETED post-merge (2026-06-02)
- Policy compliant

## Rules
1. Only delete branches that are confirmed merged (merged_at not null)
2. Only delete branches in expected repos (not forks)
3. Only delete non-protected branches
4. Log every deletion
