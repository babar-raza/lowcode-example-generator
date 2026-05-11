# Environment Variables

Audience: Operator, Contributor
Source of truth: `src/plugin_examples/__main__.py`, `src/plugin_examples/llm_router/router.py`, `src/plugin_examples/metrics/config.py`, `src/plugin_examples/publisher/`, `src/plugin_examples/verifier_bridge/`

## GitHub

| Variable | Purpose |
|---|---|
| `GITHUB_TOKEN` | Live PR creation, live merge, repo access probes, permission probes, published example build regression. |

## Approval Gates

| Variable | Required value | Purpose |
|---|---|---|
| `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` | `APPROVE_LIVE_PR` | Fallback approval token for live PR creation. |
| `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL` | `APPROVE_MERGE_PR` | Fallback approval token for live merge. |

Merge rejects the live publish approval token. Publishing and merging require separate approvals.

## LLM Providers

| Variable | Purpose |
|---|---|
| `LLM_PROFESSIONALIZE_API_KEY` | API key for configured `llm_professionalize` provider. |
| `LLM_PROFESSIONALIZE_BASE_URL` | Base URL env name declared in `pipeline/configs/llm-routing.yml`. |
| `LLM_API_KEY` | Generic LLM API key fallback. |
| `OPENAI_API_KEY` | OpenAI-compatible fallback key. |
| `OPENAI_MODEL` | OpenAI-compatible model override. |
| `GPT_OSS_API_KEY` | GPT-OSS/OpenAI-compatible route key. |
| `GPT_OSS_ENDPOINT` | GPT-OSS/OpenAI-compatible endpoint. |
| `GPT_OSS_MODEL` | GPT-OSS/OpenAI-compatible model. |
| `OLLAMA_HOST` | Ollama endpoint; defaults to local Ollama when not set. |

## Reviewer

| Variable | Purpose |
|---|---|
| `EXAMPLE_REVIEWER_PATH` | Path to external `example-reviewer` checkout used by reviewer preflight and execution. |

## Metrics

| Variable | Purpose |
|---|---|
| `AGENT_METRICS_ENABLED` | Enables metrics collection when set to `true`. |
| `AGENT_METRICS_DRY_RUN` | Controls dry-run behavior; `false` disables dry-run. |
| `AGENT_METRICS_STRICT` | Fails command on metrics errors when set to `true`. |
| `AGENT_METRICS_ENDPOINT` | Metrics POST endpoint. |
| `AGENT_METRICS_TOKEN` | Metrics POST token. |
| `AGENT_METRICS_PRODUCTION_ENABLED` | Enables production metrics behavior when set to `true`. |

## Local Development

| Variable | Purpose |
|---|---|
| `PYTHONPATH=src` | Useful for direct test runs and local module execution. |

See:

- [CLI Reference](cli.md)
- [Configuration Reference](config.md)
- [Metrics Reference](metrics.md)
