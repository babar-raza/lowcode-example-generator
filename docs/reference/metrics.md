# Metrics Reference

Audience: Operator, Contributor
Source of truth: `src/plugin_examples/metrics/`, `pipeline/configs/metrics.yml`

Metrics are optional. Most commands support shared metrics flags documented in [CLI Reference](cli.md).

## Config

Config file: `pipeline/configs/metrics.yml`

Key areas:

- Enablement: `metrics.enabled`, `metrics.dry_run`, `metrics.strict_mode`
- Identity: `agent_owner`, `agent_name`, `website`, `website_section`, `platform`
- Mappings: `family_to_product`, `command_to_job_type`, `command_to_item_name`, `verdict_to_status`
- Allowed values: `allowed_statuses`, `allowed_job_types`
- Env var names under `env`
- Ledger path: `post_ledger_path`

## Environment

Metrics env vars include:

- `AGENT_METRICS_ENABLED`
- `AGENT_METRICS_DRY_RUN`
- `AGENT_METRICS_STRICT`
- `AGENT_METRICS_ENDPOINT`
- `AGENT_METRICS_TOKEN`
- `AGENT_METRICS_PRODUCTION_ENABLED`

## Evidence

Metrics evidence writers can create:

- `llm-calls.jsonl`
- `run-summary.json`
- `metrics-payload.json`
- validation result JSON
- post result JSON

POST duplicate detection uses `workspace/verification/agent-metrics-post-ledger.jsonl`.
