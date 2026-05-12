# Agent-Operated Live PR Runbook

This runbook guides human operators through the process of authorizing and executing a live PR publication using the lowcode-example-generator pipeline.

## Prerequisites

- Generated examples have passed all validation gates (build + run + reviewer)
- Gate verdict is `PR_READY` or `FULL_E2E_PASSED`
- `GH_TOKEN` is set as a Windows system environment variable (see Token Requirements below)
- You have reviewed the generated examples and are ready to approve publication

## Token Requirements

The pipeline reads **`GITHUB_TOKEN`** exclusively at runtime.

The operator stores the actual PAT in **`GH_TOKEN`** (Windows system environment variable) and maps it to `GITHUB_TOKEN` at the point of use. `GH_TOKEN` is never read directly by the pipeline — it is the operator's storage convention.

### Required: Classic PAT stored as `GH_TOKEN`

Use a **classic PAT** with **`repo` scope**. This grants full repository access (Contents read/write, Pull Requests, Issues) for all repositories the user can access, including org-owned repos. It avoids all fine-grained PAT org-policy restrictions.

Create at: `github.com/settings/tokens/new` → check **`repo`** → Generate. Token starts with `ghp_`.

Save to Windows system environment once (persists across sessions):

```powershell
[Environment]::SetEnvironmentVariable("GH_TOKEN", "ghp_YOUR_TOKEN", "User")
```

Verify (prints character count, not the value):

```powershell
[Environment]::GetEnvironmentVariable("GH_TOKEN", "User") | Measure-Object -Character | Select-Object -ExpandProperty Characters
```

### Mapping `GH_TOKEN` → `GITHUB_TOKEN` before each command

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "Machine")
if (-not $env:GITHUB_TOKEN) {
    $env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
}
```

### Fine-grained PAT limitations (do not use for org repos)

Fine-grained PATs fail at the Git Data API level for org-owned repos unless:

1. The **resource owner is the organization** (e.g., `aspose-diagram-net`), not the personal account.
2. The organization has enabled fine-grained PATs in org settings.
3. **Contents: Read and write** and **Pull requests: Read and write** are explicitly granted.

Setting resource owner to your personal account and targeting an org repo produces HTTP 403 on `/git/blobs` even when the user is an org admin. The `probe-publish-permissions` command may still report `can_push=True` because it checks repo metadata — not the Git Data API scope.

**Use a classic PAT with `repo` scope to avoid all of these restrictions.**

## Step 1: Review Generated Examples

Before authorizing publication, review the examples in:

```
workspace/pr-dry-run/{family}-controlled-pilot/
```

Confirm:
- Each `.cs` file uses the LowCode API as the primary demonstrated API
- Non-LowCode types are only used for fixture creation or supporting setup
- Build and runtime output is correct
- Gate result file shows `publishable: true`

## Step 2: Map Token and Set Approval

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"
$env:PYTHONPATH = "src"
```

`PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` must be provided **interactively by a human operator** — it must NOT be stored as a CI secret.

## Step 3: Execute the Live PR Command

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"
$env:PYTHONPATH = "src"

.venv\Scripts\python.exe -m plugin_examples publish-pr `
    --family <family> `
    --publish `
    --approval-token APPROVE_LIVE_PR `
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

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PLUGIN_EXAMPLES_MERGE_PR_APPROVAL = "APPROVE_MERGE_PR"
$env:PYTHONPATH = "src"

.venv\Scripts\python.exe -m plugin_examples merge-pr `
    --family <family> `
    --pr-number <number> `
    --merge `
    --approval-token APPROVE_MERGE_PR `
    --promote-latest
```

See [post-merge-verification-runbook.md](post-merge-verification-runbook.md) for merge and post-merge verification steps.
