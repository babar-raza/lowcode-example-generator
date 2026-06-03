# Operator Quickstart

Audience: Operator

## Prerequisites

- Python 3.12 or newer.
- .NET SDK 8.0 for reflector and generated project validation.
- Dependencies installed with `pip install -e ".[dev]"` for test workflows or `pip install -e .` for basic operation.
- `GH_TOKEN` set as a Windows system environment variable (classic PAT, `repo` scope) for live GitHub operations.

## Token Setup

Store your GitHub classic PAT once:

```powershell
[Environment]::SetEnvironmentVariable("GH_TOKEN", "ghp_YOUR_TOKEN", "User")
```

```bash
# bash / Linux / macOS — add to ~/.bashrc or ~/.zshrc
export GH_TOKEN="ghp_YOUR_TOKEN"
```

Before any live command, map it to what the pipeline reads:

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
```

```bash
# bash / Linux / macOS
export GITHUB_TOKEN="$GH_TOKEN"
```

## LLM Endpoint Access

The pipeline uses `https://llm.professionalize.com/v1/` as its exclusive LLM endpoint. This is enforced by an approved-providers whitelist in the LLM router — the pipeline will reject any other endpoint at preflight and abort before generation.

### Required Environment Variables

| Variable | Value |
|---|---|
| `GPT_OSS_ENDPOINT` | `https://llm.professionalize.com/v1/` (must be exactly this URL) |
| `GPT_OSS_MODEL` | Model name served by the endpoint (provided by your team) |
| `GPT_OSS_API_KEY` | API key for the endpoint |

Set them before running any generation command:

```powershell
$env:GPT_OSS_ENDPOINT = "https://llm.professionalize.com/v1/"
$env:GPT_OSS_MODEL    = "<model-name>"
$env:GPT_OSS_API_KEY  = "<api-key>"
```

```bash
# bash / Linux / macOS
export GPT_OSS_ENDPOINT="https://llm.professionalize.com/v1/"
export GPT_OSS_MODEL="<model-name>"
export GPT_OSS_API_KEY="<api-key>"
```

### Verify Connectivity

```powershell
Invoke-WebRequest -Uri "https://llm.professionalize.com/v1/models" -Headers @{"Authorization"="Bearer $env:GPT_OSS_API_KEY"} | Select-Object StatusCode
```

```bash
# bash / Linux / macOS
curl -s -o /dev/null -w "%{http_code}" https://llm.professionalize.com/v1/models -H "Authorization: Bearer $GPT_OSS_API_KEY"
```

A 200 response confirms the endpoint is reachable and the API key is valid. The pipeline also runs its own preflight check (`llm-preflight.json`) before generation, which validates endpoint reachability, model availability, JSON response format, and response latency.

### What Works Without the LLM

The LLM endpoint is only used during the `generation` stage. All other pipeline stages are fully deterministic and work without it:

- `--dry-run` — runs NuGet fetch through scenario planning, skips generation.
- `--template-mode` — uses template-based generation instead of LLM calls.
- `status`, `discover-lowcode`, `validate-portfolio-truth` — no LLM needed.
- Unit tests (`pytest`) — no LLM needed.

### API Key Provisioning

Contact your team lead or infrastructure administrator for API key provisioning. The endpoint is an internal service — credentials are not self-service.

### Legacy Providers (Not Approved)

The router code retains fallback branches for `OPENAI_API_KEY`, `LLM_API_KEY`, and `OLLAMA_HOST`. These are not approved for production use and are blocked by the approved-providers policy. Do not set these variables as substitutes for the `GPT_OSS_*` variables.

## GitHub Organization Access

The pipeline publishes examples to family-specific repositories in Aspose GitHub organizations. You need org membership with write access to create and merge PRs.

### Target Repositories

| Family | Repository |
|---|---|
| Cells | `aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples` |
| Diagram | `aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples` |
| Email | `aspose-email-net/Aspose.Email.LowCode-for-.NET-Examples` |
| PDF | `aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples` |
| Slides | `aspose-slides-net/Aspose.Slides.LowCode-for-.NET-Examples` |
| Words | `aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples` |

### Token Requirements

You need a **classic PAT** (`ghp_*`) with `repo` scope. Fine-grained PATs with a personal account as resource owner cannot write to org-owned repositories via the Git Data API — the pipeline will get HTTP 403 on PR creation even if `probe-publish-permissions` reports `can_push=True`.

Store the token and map it before live commands:

```powershell
# Store once (Windows system env)
[Environment]::SetEnvironmentVariable("GH_TOKEN", "ghp_YOUR_TOKEN", "User")

# Map before each live command
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
```

```bash
# bash / Linux / macOS — add to ~/.bashrc or ~/.zshrc
export GH_TOKEN="ghp_YOUR_TOKEN"

# Map before each live command
export GITHUB_TOKEN="$GH_TOKEN"
```

### Verify Access

Check org membership and repo permissions using the GitHub CLI:

```bash
# Verify org membership (replace <org> with e.g. aspose-cells-net)
gh api orgs/<org>/members --jq '.[].login' | grep "$(gh api user --jq '.login')"

# Verify repo write access
gh api repos/<org>/Aspose.Cells.LowCode-for-.NET-Examples --jq '.permissions'
```

You should see `"push": true` in the permissions output.

### What Works Without Org Access

Everything except live PR creation and merge works without GitHub org access:

- Dry-run pipelines, tests, local generation, template-mode runs.
- Source-of-truth discovery, validation, evidence building.
- The `--dry-run` flag on publish commands prepares the PR package without pushing.

## Check the CLI

```powershell
python -m plugin_examples status
```

```bash
# bash / Linux / macOS
python3 -m plugin_examples status
```

## Run a Dry-Run Pipeline

```powershell
python -m plugin_examples run --family cells --dry-run --template-mode --promote-latest
```

```bash
# bash / Linux / macOS
python3 -m plugin_examples run --family cells --dry-run --template-mode --promote-latest
```

Inspect:

- `workspace/runs/{run_id}/pilot-report.json`
- `workspace/runs/{run_id}/evidence/latest/`
- `workspace/verification/latest/families/cells/` when promoted

## Next Steps

- Full command details: [CLI Reference](../reference/cli.md)
- Evidence files: [File Contracts](../reference/file-contracts.md)
- Monthly operation: [Monthly Maintenance](../operations/monthly-maintenance.md)
- Publishing: [Live Publishing](../operations/live-publishing.md)
- Environment variables: [Environment Variables](../reference/environment-variables.md)
