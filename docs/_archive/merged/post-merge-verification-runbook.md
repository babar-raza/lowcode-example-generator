# Post-Merge Verification Runbook

**Purpose:** After a PR is merged, the agent verifies that the merge completed correctly,
the default branch contains expected files, examples still build and run, and a release
evidence file is written.

**Status:** PLANNED — no PR has been merged yet. This runbook documents the required steps
for a future merge sprint.

---

## When to Run

Run after a human explicitly approves a merge (provides `APPROVE_MERGE_PR`) and the merge
command completes successfully.

Do NOT run this runbook until:
1. Human provides explicit `APPROVE_MERGE_PR` approval
2. `merge-pr --merge --approval-token APPROVE_MERGE_PR` exits 0
3. GitHub API confirms `merged=true` for the PR

---

## Runbook Steps

### Step 1: Confirm Merge State via GitHub API

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number} --jq '{state:.state, merged:.merged, merged_at:.merged_at, merge_commit_sha:.merge_commit_sha}'
```

Verify:
- `state = "closed"`
- `merged = true`
- `merged_at` is a non-null timestamp
- `merge_commit_sha` is a non-null SHA

Record `merge_commit_sha` in evidence.

### Step 2: Verify Default Branch Contains Expected Files

```bash
gh api repos/{owner}/{repo}/git/trees/main?recursive=1 --jq '[.tree[] | .path]'
```

Verify:
- All examples present in `examples/{family}/lowcode/`
- `Directory.Build.props`, `Directory.Packages.props`, `global.json` present
- No unexpected files (PR_SUMMARY.md, bin/, obj/)
- File paths match what was in the PR

### Step 3: Clean Clone from Default Branch

```bash
TMPDIR=$(mktemp -d)
git clone --depth=1 https://github.com/{owner}/{repo}.git "$TMPDIR/{family}-post-merge"
```

Run build and run for each example from default branch:

```bash
for example in {example_dirs}; do
  cd "$TMPDIR/{family}-post-merge/examples/{family}/lowcode/$example"
  dotnet restore --verbosity quiet
  dotnet build --verbosity quiet --no-restore
  dotnet run
done
```

Verify: all examples pass (same results as pre-merge clean-checkout validation)

### Step 4: Record Merge Evidence

Write `workspace/verification/latest/{family}-post-merge-verification.json`:

```json
{
  "verification_type": "{family}_post_merge_verification",
  "verification_date": "{date}",
  "pr_number": 1,
  "merge_commit_sha": "{sha}",
  "state": "closed",
  "merged": true,
  "merged_at": "{timestamp}",
  "default_branch_file_check": "PASS",
  "clean_clone_result": "ALL_PASS",
  "examples_count": {n},
  "examples_passed": {n},
  "overall_result": "POST_MERGE_VERIFIED"
}
```

### Step 5: No Branch Cleanup Without Explicit Approval

The PR branch (`plugin-examples/{family}/{timestamp}`) is NOT deleted unless explicitly
approved. GitHub may auto-delete PR branches after merge depending on repo settings.

If the human wants the branch preserved:
- Document in evidence
- Do not run `git push origin --delete plugin-examples/{family}/{timestamp}`

If the human wants the branch deleted:
- Confirm explicitly (separate approval action)
- Run deletion only with written authorization

### Step 6: Notify Human

Report:
- Merge commit SHA
- Default branch file count
- Clean-clone build/run result for each example
- Link to merged PR

---

## Required Evidence Files

| File | Written when |
|---|---|
| `{family}-post-merge-verification.json` | After merge confirmed + clone validated |
| `{family}-post-merge-verification.md` | Human-readable summary |

---

## Safety Rules

1. **Do not merge without `APPROVE_MERGE_PR`** — separate from `APPROVE_LIVE_PR`
2. **Record merge commit SHA** — needed for rollback tracing
3. **Do not delete PR branch** unless explicitly authorized
4. **Do not push to main directly** — only via PR merge flow
5. **Do not run post-merge verification on un-merged PRs** — check `merged=true` first
6. **Rollback option**: if post-merge clean-clone fails, document the failure in evidence
   and notify human; do NOT auto-revert without human approval

---

## Rollback Procedure

If post-merge clean-clone fails for any example:

1. Document failure in `{family}-post-merge-verification.json` with `overall_result: POST_MERGE_FAILED`
2. Write human-readable report at `docs/publishing/{family}-post-merge-failure.md`
3. Create new taskcard: `followup-{family}-post-merge-rollback`
4. Do NOT automatically revert — present options to human:
   - Option A: Revert merge commit (requires `APPROVE_MERGE_PR` reuse + human confirmation)
   - Option B: Create fix PR targeting main
   - Option C: Accept failure, log, create generation re-run taskcard

---

## Future Automation

When CI is added to target repos, Step 3 (clean clone) can be replaced by:
- Waiting for CI check suite to complete on `main`
- Reading `GET /repos/{owner}/{repo}/commits/{sha}/check-suites`
- Verifying all check suites are `completed` with `conclusion=success`
