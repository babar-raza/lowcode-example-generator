# Live Publishing

Audience: Operator

Purpose: create GitHub pull requests for verified generated examples without pushing directly to `main`.

Canonical references: [CLI](../reference/cli.md), [Environment Variables](../reference/environment-variables.md), [Publishing and GitHub](../reference/publishing-and-github.md), [File and Evidence Contracts](../reference/file-contracts.md)

## Preconditions

- The family has a publishable gate verdict.
- A dry-run package exists under `workspace/pr-dry-run/`.
- Repo access and publish permission probes are ready.
- `GH_TOKEN` exists as a Windows user or machine environment variable and stores a classic PAT with `repo` scope.
- A human operator is ready to provide `APPROVE_LIVE_PR`.

## Map Token

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "Machine")
if (-not $env:GITHUB_TOKEN) {
    $env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
}
$env:PYTHONPATH = "src"
```

## Probe First

```powershell
python -m plugin_examples validate-publish-targets --families <family> --promote-latest
python -m plugin_examples resolve-repo-access --families <family> --promote-latest
python -m plugin_examples probe-publish-permissions --families <family> --promote-latest
```

## Simulate PR Creation

```powershell
python -m plugin_examples publish-pr --family <family> --dry-run --promote-latest
```

Stop if the simulation reports blocked reasons.

## Create Live PR

```powershell
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"

python -m plugin_examples publish-pr `
    --family <family> `
    --publish `
    --approval-token APPROVE_LIVE_PR `
    --promote-latest
```

## Verify Evidence

Check the relevant publishing evidence under `workspace/verification/latest/` and `workspace/verification/latest/families/{family}/`.

Expected evidence includes PR result data and updated release status where applicable. See [File and Evidence Contracts](../reference/file-contracts.md).

## Merge Is Separate

Merge requires `APPROVE_MERGE_PR`, not `APPROVE_LIVE_PR`. Use [Post-Merge Verification](post-merge-verification.md) after merge.
