# Branch Auto-Delete Policy — Sprint 57

**Sprint 57 Lane G**
**Date:** 2026-05-21

## Policy

After a PR is successfully merged to a destination repo's main branch:
1. The PR source branch SHALL be deleted from the destination repo.
2. Deletion MUST occur only after merge verification (merge_sha confirmed, PR state=closed with merged_at).
3. Deletion MUST NOT occur for:
   - Open PRs
   - Failed PRs (state=closed, merged_at=null)
   - PRs where merge verification has not been performed

## Implementation Status

**Current state:** Branches from merged PRs (cells PR#1, PR#6; words PR#1, PR#5; pdf PR#1, PR#2, PR#4, PR#11, PR#17-#21; diagram PR; email PR; slides PR) may still exist in destination repos.

**Sprint 57 action:** The destination repo audit confirmed all examples are present on main. Branch deletion for already-merged PRs is a cleanup action that requires manual verification of which branches exist.

**Future implementation:** The `github_pr_publisher.py` module should be updated to:
1. After verifying merge_sha is present in the destination repo, call the GitHub API to delete the source branch.
2. Only trigger if `allow_branch_auto_delete=True` in family config (default False for safety).
3. Log the deletion as part of the publication record.

## Branch Deletion API

```python
# GitHub API call to delete a branch
import requests
headers = {'Authorization': f'token {GITHUB_TOKEN}'}
url = f'https://api.github.com/repos/{org}/{repo}/git/refs/heads/{branch}'
response = requests.delete(url, headers=headers)
assert response.status_code == 204, f'Branch deletion failed: {response.status_code}'
```

## Safety Rules

- NEVER delete main branch
- NEVER delete branches with open PRs
- NEVER delete branches without first confirming the PR was merged (not just closed)
- ALWAYS log the deletion with timestamp and SHA
- Only delete branches created by this pipeline (prefixed with `lowcode-pilot-` or `lowcode-wave-`)
