# Post-Merge Verification Runbook

This runbook documents the steps to verify that a merged PR is healthy and the published examples are correct.

## Prerequisites

- PR has been merged using `APPROVE_MERGE_PR` token
- `merge_commit_sha` is recorded in the merge result evidence file
- Post-merge verification plan exists at `workspace/verification/latest/post-merge-verification-plan.json`

## Steps

### 1. Confirm Merge Result

Check that `merge_commit_sha` was recorded:

```bash
cat workspace/verification/latest/cells-merge-result.json
# or
cat workspace/verification/latest/words-merge-result.json
```

Verify:
- `merge_commit_sha` is present and non-null
- `merge_date` is present
- `merged_by` identifies the correct token holder

### 2. Checkout the Target Repo

```bash
git clone https://github.com/{owner}/{repo}.git /tmp/post-merge-verify
cd /tmp/post-merge-verify
git checkout main
git pull
```

Confirm the merge commit is at HEAD:
```bash
git log --oneline -5
```

### 3. Build and Run All Published Examples

For each example in the merged PR:

```bash
dotnet restore
dotnet build --no-restore
dotnet run --no-build
```

Expected: all examples build and run without errors.

### 4. Record Post-Merge Validation Evidence

Run the pipeline's post-merge validation command:

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples merge-pr \
  --family {cells|words} \
  --pr-number N \
  --verify-post-merge \
  --promote-latest
```

This writes:
- `workspace/verification/latest/{family}-post-merge-clean-checkout-validation.json`
- `summary.overall_result` must be `POST_MERGE_VERIFIED`

### 5. Update Release Status

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples release-status \
  --families cells words pdf \
  --promote-latest
```

Verify `workspace/verification/latest/release-status.json` shows `all_merged: true` for merged families.

## Approval Token Reference

| Token | Variable | Purpose |
|-------|----------|---------|
| `APPROVE_MERGE_PR` | `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | Required to execute the merge |

**Note:** `APPROVE_LIVE_PR` is explicitly rejected for merge operations — it will fail with `blocked_merge_reused_live_publish_token`.

## Rollback Procedure

If post-merge verification fails (examples fail to build or run on the target repo):

1. Revert the merge commit on the target repo:
   ```bash
   git revert <merge_commit_sha> --no-edit
   git push origin main
   ```
2. Document the rollback in `workspace/verification/latest/{family}-rollback-record.json`
3. Open a follow-up taskcard with the root cause and rerun strategy

**Rollback is irreversible on public repos** — coordinate with repo maintainers before reverting.

## Evidence Files

After successful post-merge verification, the following files must exist:

| File | Required Field |
|------|---------------|
| `{family}-merge-result.json` | `merge_commit_sha` |
| `{family}-post-merge-clean-checkout-validation.json` | `summary.overall_result == POST_MERGE_VERIFIED` |
| `release-status.json` | `all_merged` |
