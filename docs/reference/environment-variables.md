# Environment Variables

Audience: Operator, Contributor

Source of truth: `src/plugin_examples/__main__.py`, `src/plugin_examples/llm_router/router.py`, `src/plugin_examples/metrics/config.py`, `src/plugin_examples/publisher/`, `src/plugin_examples/verifier_bridge/`

Last verified: 2026-06-17

## GitHub Tokens

| Variable | Purpose |
|---|---|
| `GH_TOKEN` | Operator storage convention for a classic GitHub PAT with `repo` scope. The pipeline generally does not read this directly; map it to `GITHUB_TOKEN` before live commands. One target-repo health path has a fallback read of `GH_TOKEN`, which is a known code/doc governance gap. |
| `GITHUB_TOKEN` | Token read by the pipeline for live PR creation, live merge, repo access probes, permission probes, fixture/example repo access, and published example checks. |

PowerShell mapping:

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "Machine")
if (-not $env:GITHUB_TOKEN) {
    $env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable("GH_TOKEN", "User")
}
```

Use a classic PAT beginning with `ghp_` and `repo` scope for org-owned target repos. Fine-grained PATs owned by a personal account can fail on the Git Data API for org-owned repos.

## Approval Gates

| Variable | Required value | Purpose |
|---|---|---|
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | `APPROVE_LIVE_PR` | Fallback approval token for live PR creation and README PR publication. |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | `APPROVE_MERGE_PR` | Fallback approval token for live merge. |
| `PLUGIN_EXAMPLES_README_AUDIT_APPROVAL` | operator-defined | Override token for README audit gate. |
| `APPROVE_LIVE_MERGE` | `1` | Agent auto-merge authority gate. Set to `1` to allow `gh pr merge --squash` when all AMG gates pass. |
| `APPROVE_DELETE_BRANCH` | `1` | Post-merge branch deletion gate. Set to `1` to enable branch deletion after verified merge. |

`APPROVE_LIVE_PR` is rejected for merge. Publishing and merging require separate approvals.

Approval token values are human operator inputs. They must NOT be stored as CI secrets or reused across publishing and merge gates.

## LLM

Two provider families are approved (enforced in `src/plugin_examples/llm_router/provider_policy.py`):

| Variable | Provider | Required / Optional | Purpose |
|---|---|---|---|
| `GPT_OSS_ENDPOINT` | `llm_professionalize` | Required for production | Base URL. Default: `https://llm.professionalize.com/v1/`. If missing or empty, generation aborts. |
| `GPT_OSS_MODEL` | `llm_professionalize` | Required for production | Model name served by `llm.professionalize.com`. |
| `GPT_OSS_API_KEY` | `llm_professionalize` | Required for production | API key. |
| `OLLAMA_HOST` | `ollama` | Optional (local dev only) | Base URL for local ollama provider. Default: `http://localhost:11434`. |

Forbidden provider variables (blocked by policy — `openai`, `azure_openai` are unapproved provider families):

| Variable | Status |
|---|---|
| `LLM_API_KEY` | Unapproved. Not a valid substitute. |
| `OPENAI_API_KEY` | Unapproved. Not a valid substitute. |
| `OPENAI_MODEL` | Unapproved. Not a valid substitute. |

See [AGENTS.md](../../AGENTS.md) for provider governance rules.

## Reviewer

| Variable | Purpose |
|---|---|
| `EXAMPLE_REVIEWER_PATH` | Path to external `example-reviewer` checkout used by reviewer preflight and execution. |

## Metrics

| Variable | Purpose |
|---|---|
| `AGENT_METRICS_ENABLED` | Enables metrics collection when set to `true`. |
| `AGENT_METRICS_DRY_RUN` | Controls metrics dry-run behavior. |
| `AGENT_METRICS_STRICT` | Fails the command on metrics errors when set to `true`. |
| `AGENT_METRICS_ENDPOINT` | Metrics POST endpoint. |
| `AGENT_METRICS_TOKEN` | Metrics POST token. |
| `AGENT_METRICS_PRODUCTION_ENABLED` | Enables production metrics behavior when set to `true`. |

## Logging

| Variable | Purpose |
|---|---|
| `LOG_LEVEL` | Log level override (e.g., `DEBUG`, `INFO`, `WARNING`). Default: `INFO`. Read by `src/plugin_examples/observability.py`. |
| `PLUGIN_EXAMPLES_LOG_FORMAT` | Set to `json` to enable JSON-structured log output. |

## Catalog Discovery

| Variable | Purpose |
|---|---|
| `CATALOG_CRAWL_DELAY_MS` | Override crawl delay in milliseconds for `catalog-discover`. Default: set by `_DEFAULT_DELAY_MS` in crawler.py. |

## Runtime Behavior

| Variable | Purpose |
|---|---|
| `ACCEPT_VERSION_DRIFT` | Set to `1` to suppress version drift errors in the runner (for local development). |

## Local Development

| Variable | Purpose |
|---|---|
| `PYTHONPATH=src` | Useful for direct test runs and local module execution. |

## Related Pages

- [CLI Reference](cli.md)
- [Configuration Reference](config.md)
- [Publishing and GitHub](publishing-and-github.md)
- [Metrics](metrics.md)
