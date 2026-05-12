# Publishing and GitHub

Audience: Operator, Contributor
Source of truth: `src/plugin_examples/publisher/`, `src/plugin_examples/__main__.py`

## Publishing Model

Publishing is PR-based. The pipeline does not directly push to `main`.

Family publish targets come from `github.published_plugin_examples_repo` in family configs.

## Token Setup

The pipeline reads `GITHUB_TOKEN`. The operator stores the PAT in `GH_TOKEN` (Windows system env) and maps it before each command:

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
```

`GH_TOKEN` must be a **classic PAT** (`ghp_*`) with `repo` scope. Fine-grained PATs with a personal account as resource owner cannot write to org-owned repos — they return HTTP 403 on the Git Data API even when the user is an org admin.

## Dry-Run Publishing

`publish-pr --dry-run` simulates PR creation and writes evidence without remote mutation.

## Live PR Creation

`publish-pr --publish` requires:

- `GITHUB_TOKEN` (mapped from `GH_TOKEN`)
- `--approval-token APPROVE_LIVE_PR` or `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`
- Publishable gate verdict
- Existing package path
- Repo access readiness
- Push permission readiness
- Branch name different from target branch

## Merge

`merge-pr --merge` requires:

- `GITHUB_TOKEN` (mapped from `GH_TOKEN`)
- `--approval-token APPROVE_MERGE_PR` or `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`
- A separate approval from live PR creation

`APPROVE_LIVE_PR` is rejected for merge.

## Related Commands

- `validate-publish-targets`
- `resolve-repo-access`
- `probe-publish-permissions`
- `publish-pr`
- `merge-pr`
- `release-status`

See [CLI Reference](cli.md), [Live Publishing](../operations/live-publishing.md), and [Environment Variables](environment-variables.md).
