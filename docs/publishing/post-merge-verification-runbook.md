# Post-Merge Verification Runbook

## Purpose

This runbook describes the steps required to verify a successful PR merge for LowCode example publication.

## Prerequisites

- `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` gate must be set to `APPROVE_MERGE_PR`
- `GH_TOKEN` or equivalent token must be available
- The `merge_commit_sha` must be obtained from the merged PR

## Steps

### 1. Confirm Merge Gate

```bash
# Gate must be explicitly set before any merge action
PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
```

### 2. Obtain merge_commit_sha

After a PR is merged, obtain the `merge_commit_sha` from the GitHub merge response:

```python
merge_result = gh_pr_merge(pr_number=<N>, merge_method="merge")
merge_commit_sha = merge_result["merge_commit_sha"]
```

The `merge_commit_sha` must be recorded in the sprint evidence as part of publication proof.

### 3. Verify Post-Merge State

```bash
# Verify the merge commit exists in the target repo
gh api repos/{owner}/{repo}/commits/{merge_commit_sha}
```

### 4. Rollback Procedure

If a merge produces an incorrect result or evidence contradictions are found, follow this rollback procedure:

1. **Do not delete the branch immediately** — preserve it for audit
2. Record the `merge_commit_sha` and the reason for rollback
3. Open a revert PR in the target repo:
   ```bash
   gh api repos/{owner}/{repo}/git/refs -X POST \
     -f ref="refs/heads/revert-{merge_commit_sha[:8]}" \
     -f sha="{merge_commit_sha}"
   ```
4. Apply revert commit via GitHub API
5. Document in `reports/<sprint-id>/publication/rollback-proof.md`

### 5. Post-Merge Evidence

Record in `publication/merge-verification-proof.json`:

```json
{
  "pr_number": "<N>",
  "merge_commit_sha": "<sha>",
  "merged_at": "<ISO8601>",
  "merged_by": "<actor>",
  "target_repo": "<owner>/<repo>",
  "rollback_needed": false,
  "verification_status": "PASS"
}
```

## Approval Gate Reference

| Gate | Value Required | Purpose |
|---|---|---|
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | `APPROVE_LIVE_PR` | Allows live PR creation |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | `APPROVE_MERGE_PR` | Allows PR merge |

Both gates must be independently verified before proceeding.

## Safety Rules

- Never merge without `APPROVE_MERGE_PR` gate
- Always record `merge_commit_sha` in evidence
- Always document rollback conditions before merging
- No force-push to merged branches
