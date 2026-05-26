# Environment Variables

Audience: Operator, Contributor

Source of truth: `src/plugin_examples/__main__.py`, `src/plugin_examples/llm_router/router.py`, `src/plugin_examples/metrics/config.py`, `src/plugin_examples/publisher/`, `src/plugin_examples/verifier_bridge/`

Last verified from audit: 2026-05-25

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

`APPROVE_LIVE_PR` is rejected for merge. Publishing and merging require separate approvals.

Approval token values are human operator inputs. They must NOT be stored as CI secrets or reused across publishing and merge gates.

## LLM

Repository governance requires all LLM inference to use:

```text
https://llm.professionalize.com/v1/
```

Required governance variables:

| Variable | Required behavior |
|---|---|
| `GPT_OSS_ENDPOINT` | Must be `https://llm.professionalize.com/v1/`. If missing or different, generation is governed as blocked. |
| `GPT_OSS_MODEL` | Model name served by `llm.professionalize.com`. |
| `GPT_OSS_API_KEY` | API key for `llm.professionalize.com`. |

Known code gap from the audit: the current router still contains non-authoritative fallbacks and branches for generic/OpenAI/Ollama-style providers. Documentation must not recommend those fallbacks for live generation.

Code-visible variables that remain in implementation and should be treated as legacy or internal until code is aligned:

| Variable | Current code visibility |
|---|---|
| `LLM_API_KEY` | Fallback read in router code. Not an approved governance substitute. |
| `OPENAI_API_KEY` | Fallback read in router code. Not an approved governance substitute. |
| `OPENAI_MODEL` | Fallback read in router code. Not an approved governance substitute. |
| `OLLAMA_HOST` | Used for evidence/base URL metadata; local Ollama is not an approved live-generation fallback under repo governance. |

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

## Local Development

| Variable | Purpose |
|---|---|
| `PYTHONPATH=src` | Useful for direct test runs and local module execution. |

## Related Pages

- [CLI Reference](cli.md)
- [Configuration Reference](config.md)
- [Publishing and GitHub](publishing-and-github.md)
- [Metrics](metrics.md)
