# Agent-Operated Live PR Runbook

This runbook guides human operators through the process of authorizing and executing a live PR publication using the lowcode-example-generator pipeline.

## Prerequisites

- Generated examples have passed all validation gates (build + run + reviewer)
- Gate verdict is `PR_READY` or `FULL_E2E_PASSED`
- You have a `GITHUB_TOKEN` with sufficient permissions (see Token Requirements below)
- You have reviewed the generated examples and are ready to approve publication

## Token Requirements

The pipeline reads **`GITHUB_TOKEN`** exclusively.

Use a **classic PAT** with **`repo` scope** to ensure full repository access (Contents read/write, Pull Requests, Issues).

Alternatively, a fine-grained PAT with:
- **Contents: Write** on the target examples repository
- **Pull Requests: Write** on the target examples repository
- **Metadata: Read** (required by fine-grained PATs)

**Note on token scope (HTTP 403 errors):** Fine-grained PATs that lack Contents:Write on the target repository will receive HTTP 403 when the pipeline attempts to push the branch. If you see 403 errors during PR creation, switch to a classic PAT with `repo` scope.

## Step 1: Review Generated Examples

Before authorizing publication, review the examples in:

```
workspace/pr-dry-run/{family}-{run-id}/
```

Confirm:
- Each `.cs` file uses the LowCode API as the primary demonstrated API
- Non-LowCode types are only used for fixture creation or supporting setup
- Build and runtime output is correct
- Gate result file shows `publishable: true`

## Step 2: Set the Approval Token

The live PR creation gate requires:
```
PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR
```

This must be provided **interactively by a human operator** — it must NOT be stored as a CI secret.

## Step 3: Execute the Live PR Command

```bash
PYTHONPATH=src \
  GITHUB_TOKEN="<your-classic-PAT-with-repo-scope>" \
  PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL="APPROVE_LIVE_PR" \
  GPT_OSS_ENDPOINT="<endpoint>" \
  GPT_OSS_API_KEY="<key>" \
  .venv/Scripts/python.exe -m plugin_examples run \
    --family <family> \
    --tier 5 \
    --promote-latest
```

Or use the `publish-pr` subcommand if you have an existing dry-run package:

```bash
PYTHONPATH=src \
  GITHUB_TOKEN="<your-token>" \
  PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL="APPROVE_LIVE_PR" \
  .venv/Scripts/python.exe -m plugin_examples publish-pr \
    --family <family> \
    --approval-token APPROVE_LIVE_PR \
    --promote-latest
```

## Step 4: Verify PR Creation

After the command completes:
1. Check `workspace/verification/latest/{family}-live-pr-result.json` for `pr_url`
2. Open the PR URL and verify the PR description is correct
3. Confirm the PR branch contains the expected examples

## Step 5: Record Evidence

The pipeline automatically records:
- `{family}-live-pr-result.json` — PR URL, number, branch
- `release-status.json` (when `--promote-latest` is set)

## Merge Authorization

PR merging is a **separate gate** requiring `APPROVE_MERGE_PR`. The live publish token (`APPROVE_LIVE_PR`) is explicitly rejected for merge — using it will return `blocked_merge_reused_live_publish_token`.

See [post-merge-verification-runbook.md](post-merge-verification-runbook.md) for merge and post-merge verification steps.
