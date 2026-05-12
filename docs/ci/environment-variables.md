# CI Environment Variables

This document describes all environment variables required by the lowcode-example-generator pipeline.

## Required CI Secrets

These variables must be stored as CI secrets (e.g., GitHub Actions secrets) and are safe to inject automatically.

| Variable | Purpose |
|----------|---------|
| `GH_TOKEN` | **Operator storage.** Classic PAT (`ghp_*`) with `repo` scope. Stored as a Windows system environment variable or CI secret. Never read directly by the pipeline — must be mapped to `GITHUB_TOKEN` before running commands. |
| `GITHUB_TOKEN` | **Read by the pipeline.** Always populated from `GH_TOKEN` at command time. Used for live PR creation, merge, repo access probes, permission probes, and build regression. |
| `GPT_OSS_ENDPOINT` | LLM provider endpoint URL (e.g., `https://llm.professionalize.com/v1/`) |
| `GPT_OSS_API_KEY` | LLM provider API key |
| `GPT_OSS_MODEL` | LLM model name (default: `recommended`) |
| `EXAMPLE_REVIEWER_PATH` | Absolute path to the `example-reviewer` repository on the runner |

**Token type requirement:** `GH_TOKEN` must be a **classic PAT** (`ghp_*`) with `repo` scope. Fine-grained PATs with a personal account as resource owner cannot write to org-owned repositories — they return HTTP 403 on the Git Data API even when the user is an org admin.

## Approval Tokens (Human Operator — NOT CI Secrets)

The following tokens require human operator input and must NOT be stored as CI secrets.
They must be provided interactively by an authorized human operator at the point of use.

| Variable | Value | Purpose |
|----------|-------|---------|
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | `APPROVE_LIVE_PR` | Approves creation of a live GitHub PR to the target examples repo |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | `APPROVE_MERGE_PR` | Approves merging a PR that was previously created; separate gate from publish |

**Why these must NOT be stored as CI secrets:**

- They represent explicit human authorization for irreversible actions (publishing and merging public PRs).
- Storing them as CI secrets would allow automated runs to publish or merge without human review.
- Each use must be a conscious, deliberate act by a human operator who has reviewed the generated examples.
- `APPROVE_LIVE_PR` and `APPROVE_MERGE_PR` are different tokens — using the wrong one is explicitly rejected.

## Optional Variables

| Variable | Purpose |
|----------|---------|
| `PYTHONPATH` | Set to `src` when running the pipeline locally |

## Example: Running a Live Pipeline Step (PowerShell)

```powershell
# Map GH_TOKEN to GITHUB_TOKEN for the current session
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
$env:PYTHONPATH = "src"
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = "APPROVE_LIVE_PR"

# Publish a live PR (human operator must provide APPROVE_LIVE_PR interactively)
.venv\Scripts\python.exe -m plugin_examples publish-pr `
    --family cells `
    --publish `
    --approval-token APPROVE_LIVE_PR `
    --promote-latest
```
