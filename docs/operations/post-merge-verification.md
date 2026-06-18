# Post-Merge Verification

Audience: Operator

Purpose: verify that merged examples are healthy after publication.

Canonical references: [CLI](../reference/cli.md), [Publishing and GitHub](../reference/publishing-and-github.md), [File and Evidence Contracts](../reference/file-contracts.md)

## Preconditions

- `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` must be set to `APPROVE_MERGE_PR` before any merge action.
- PR was merged with `APPROVE_MERGE_PR`.
- Merge result evidence exists for the family.
- Target repo and branch are known from the family config.

## Confirm Merge Gate

```bash
# Gate must be explicitly set before any merge action
PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR
```

## Record merge_commit_sha

After a PR is merged, obtain and record the `merge_commit_sha`:

```python
merge_result = gh_pr_merge(pr_number=<N>, merge_method="merge")
merge_commit_sha = merge_result["merge_commit_sha"]
```

Verify the merge commit exists in the target repo:

```bash
gh api repos/{owner}/{repo}/commits/{merge_commit_sha}
```

The `merge_commit_sha` must be recorded in sprint evidence as part of publication proof.

## Verify Published Build Regression

```powershell
python scripts/validate_published_examples_build.py
```

Default report:

```text
workspace/verification/latest/monthly-build-regression-report.json
```

## Verify Local PR Packages

For local dry-run packages:

```powershell
python -m plugin_examples post-publication-verify --family <family>
```

Use `--output PATH` to write the report to a custom location.

## Refresh Release Status

```powershell
python -m plugin_examples release-status --families cells words pdf --promote-latest
```

Use `--validate-bundle BUNDLE_DIR` when validating a sprint/evidence bundle as part of release status.

## Rollback Procedure

If a merge produces an incorrect result or evidence contradictions are found:

1. **Do not delete the branch immediately** — preserve it for audit.
2. Record the `merge_commit_sha` and the reason for rollback.
3. Open a revert PR in the target repo:
   ```bash
   gh api repos/{owner}/{repo}/git/refs -X POST \
     -f ref="refs/heads/revert-{merge_commit_sha[:8]}" \
     -f sha="{merge_commit_sha}"
   ```
4. Apply revert commit via GitHub API.
5. Document in `reports/<sprint-id>/publication/rollback-proof.md`.

## Stop Conditions

Stop and record evidence if:

- Build regression fails.
- Post-publication verification reports incomplete or failed package verification.
- Release status cannot read required evidence.
- The merged PR contains unexpected files.

## Approval Gate Reference

| Gate | Value Required | Purpose |
|---|---|---|
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | `APPROVE_LIVE_PR` | Allows live PR creation |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | `APPROVE_MERGE_PR` | Allows PR merge |

Both gates must be independently verified before proceeding.

## Safety Rules

- Never merge without `APPROVE_MERGE_PR` gate.
- Always record `merge_commit_sha` in evidence.
- Always document rollback conditions before merging.
- No force-push to merged branches.

## Evidence

Common evidence includes:

- `{family}-merge-result.json`
- `{family}-post-merge-clean-checkout-validation.json`
- `monthly-build-regression-report.json`
- `release-status.json`
- Post-publication verification report
- `publication/merge-verification-proof.json`:

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

See [File and Evidence Contracts](../reference/file-contracts.md).
