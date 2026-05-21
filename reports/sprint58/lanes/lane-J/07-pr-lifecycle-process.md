# Process: PR Lifecycle (Publish → Merge → Delete)

**Process ID:** LANE-J-07
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

Full PR lifecycle for publishing a new or updated example to a target GitHub repo.

---

## Step 1: Resolve Repo Access

Must run once per session before any publish operations:
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples resolve-repo-access \
  --families {family}
```

This validates GitHub token, org access, and repo write permissions.

---

## Step 2: Dry Run

Generate PR package and validate locally (no GitHub API calls):
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
  --family {family} --dry-run --promote-latest
```

Output: `workspace/pr-dry-run/{family}-controlled-pilot/`

---

## Step 3: Publish (Live PR)

Requires `APPROVE_LIVE_PR` token:
```python
os.environ['GITHUB_TOKEN'] = os.environ['GH_TOKEN']
sys.argv = ['plugin_examples', 'publish-pr', '--family', '{family}',
            '--publish', '--approval-token', 'APPROVE_LIVE_PR', '--promote-latest']
from plugin_examples.__main__ import main; main()
```

Creates a branch `lowcode-pilot-{family}-{timestamp}` and opens a PR.

---

## Step 4: Merge PR

Requires `APPROVE_MERGE_PR` token (separate from APPROVE_LIVE_PR):
```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family {family} --pr-number {N} --merge --approval-token APPROVE_MERGE_PR
```

Step 3 (branch delete) in merge_pr(): calls `delete_branch_after_merge()` with safe defaults (dry_run=True).

---

## Step 5: Branch Auto-Delete (Optional)

After merge, branch can be deleted:
```python
from plugin_examples.publisher.github_pr_merger import delete_branch_after_merge
result = delete_branch_after_merge(
    owner=owner, repo=repo,
    branch_ref=f"lowcode-pilot-{family}-{timestamp}",
    github_token=token,
    allow_branch_auto_delete=True,
    dry_run=False,
)
```

---

## Token Requirements

| Operation | Token |
|-----------|-------|
| GitHub API | `GITHUB_TOKEN` (set from `GH_TOKEN`) |
| Live PR publish | `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` |
| PR merge | `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR` |
| README push | `PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH` |

**Token type:** Classic PAT (ghp_*) with `repo` scope. Fine-grained PATs cannot push to org repos (HTTP 403 on `/git/blobs`).

---

## Verification After Merge

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status --promote-latest
```

Check: `PR_MERGED_AND_CONTENT_VERIFIED` for the merged PR.
