# Live Publishing

Audience: Operator

Live publishing creates GitHub pull requests. It does not push directly to `main`.

## Preconditions

- Family run has a publishable gate verdict.
- Dry-run package exists under `workspace/pr-dry-run/`.
- Repo access and publish permission probes are ready.
- `GH_TOKEN` is set as a Windows system environment variable (classic PAT, `repo` scope).
- Human supplies `APPROVE_LIVE_PR`.

## Token Setup (once per session)

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PYTHONPATH = "src"
```

## Probe First

```powershell
.venv\Scripts\python.exe -m plugin_examples validate-publish-targets --families <family> --promote-latest
.venv\Scripts\python.exe -m plugin_examples resolve-repo-access --families <family> --promote-latest
.venv\Scripts\python.exe -m plugin_examples probe-publish-permissions --families <family> --promote-latest
```

## Simulate PR

```powershell
.venv\Scripts\python.exe -m plugin_examples publish-pr --family <family> --dry-run --promote-latest
```

## Create Live PR

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

## Merge

Merge requires a separate approval token:

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

See [Publishing and GitHub](../reference/publishing-and-github.md) and [Agent-Operated Live PR Runbook](../publishing/agent-operated-live-pr-runbook.md).
