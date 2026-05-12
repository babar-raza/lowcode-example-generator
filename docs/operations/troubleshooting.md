# Troubleshooting

Audience: Operator, Contributor

## Source-of-Truth Failure

Check:

- Family config under `pipeline/configs/families/`
- NuGet package availability
- Reflection output under the run catalog directory
- `{family}-source-of-truth-proof.json`

## Build or Runtime Failure

Check:

- `validation-results.json`
- `runtime-failure-classifications.json`
- `repair-attempts.json`
- Generated project under `workspace/runs/{run_id}/generated/`

## Reviewer Unavailable

Check:

- `EXAMPLE_REVIEWER_PATH`
- `reviewer-preflight.json`
- `reviewer-results.json`

## Publishing Blocked

Check:

- `gate-results.json`
- `publish-readiness` evidence
- repo access and permission probe evidence
- approval token value
- `GITHUB_TOKEN` (must be set from `GH_TOKEN` before running the command)

### HTTP 403 on PR creation (Git Data API)

Symptom: `GitHub API POST .../git/blobs returned HTTP 403`

Cause: `GITHUB_TOKEN` is a fine-grained PAT with a personal account as resource owner. Fine-grained PATs cannot write to org-owned repositories unless the resource owner is the organization itself.

Fix: Use a classic PAT (`ghp_*`) with `repo` scope, stored in `GH_TOKEN`:

```powershell
# Verify GH_TOKEN is set
[Environment]::GetEnvironmentVariable("GH_TOKEN", "User") | Measure-Object -Character | Select-Object -ExpandProperty Characters

# Map to GITHUB_TOKEN before running the pipeline
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
```

Note: `probe-publish-permissions` may report `can_push=True` even when the token cannot write via the Git Data API. That probe checks repo metadata permissions, not Git Data API scope. The Git Blobs write test is the authoritative check.

### `probe-publish-permissions` reports `can_push=True` but PR creation still fails

This is expected when using a fine-grained PAT with the wrong resource owner. The metadata probe and the Git Data API use different permission checks. Switch to a classic PAT.

### Approval token rejected

- `APPROVE_LIVE_PR` is rejected for merge — use `APPROVE_MERGE_PR`
- Both tokens must be provided interactively; they must not be stored as CI secrets

References:

- [File Contracts](../reference/file-contracts.md)
- [Gates and Verdicts](../reference/gates-and-verdicts.md)
- [Validation and Reviewer](../reference/validation-and-reviewer.md)
- [Environment Variables](../reference/environment-variables.md)
