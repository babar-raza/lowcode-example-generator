# Agent Metrics Runbook

## Overview

The pipeline can optionally collect and POST per-run metrics (LLM token usage, API call counts, item counts, verdicts) to an Agent Metrics Google Sheet via a Google Apps Script endpoint.

Metrics are **disabled by default** and **dry-run by default** when enabled. No external mutation occurs unless explicitly opted in.

## Target Website

This pipeline generates examples for **aspose.net** (the .NET Aspose domain). The `website` field in metrics payloads defaults to `"aspose.net"` and is always read from config — never hardcoded in source.

## Config File

**Location**: `pipeline/configs/metrics.yml`

Key fields:
- `enabled` / `dry_run` / `strict_mode` — runtime behavior
- `agent_name` — stable application identity: `lowcode-example-generator` (not command-specific)
- `agent_name_test_prefix` — prefix for test rows: `test-`
- `website` — target website (config-owned)
- `family_to_product` — maps family short name to product display name
- `command_to_job_type` — maps CLI command to metrics job type
- `verdict_to_status` — maps all 18 pipeline verdicts to status
- `api_endpoint` — Google Apps Script URL (non-secret)
- `post_ledger_path` — persistent JSONL ledger for duplicate prevention

## Environment Variables

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `AGENT_METRICS_TOKEN` | Auth token for the API endpoint | Only when `--metrics-post` |
| `AGENT_METRICS_ENABLED` | `"true"` to enable (alternative to `--metrics`) | No |
| `AGENT_METRICS_DRY_RUN` | `"false"` to allow POST | No |
| `AGENT_METRICS_STRICT` | `"true"` to fail pipeline on metrics errors | No |

## CLI Flags (on `run` command)

| Flag | Default | Purpose |
|------|---------|---------|
| `--metrics` | absent | Enable metrics collection (dry-run) |
| `--metrics-post` | absent | Enable real POST to API |
| `--metrics-job-type TYPE` | auto | Override job_type (e.g., `test`) |
| `--metrics-strict` | absent | Fail pipeline on metrics errors |
| `--metrics-force-repost` | absent | Bypass duplicate ledger check |
| `--metrics-config PATH` | `pipeline/configs/metrics.yml` | Override config path |

## Dry-Run Procedure

Collect metrics locally without POSTing:

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --tier 5 --metrics --promote-latest
```

This writes 5 evidence files to the run directory:
- `agent-metrics-llm-calls.jsonl`
- `agent-metrics-run-summary.json`
- `agent-metrics-payload.json`
- `agent-metrics-validation.json`
- `agent-metrics-post-result.json` (with `posted: false, reason: dry_run`)

## Test POST Procedure

Send a test row (`job_type=test`) to verify API connectivity:

```bash
PYTHONPATH=src AGENT_METRICS_TOKEN="<token>" \
  .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --tier 5 --metrics --metrics-post \
  --metrics-job-type test --promote-latest
```

Verify the row appears in the [Google Sheet](https://docs.google.com/spreadsheets/d/1zhesamAtW00gBa43JZMqb2AKJ-GuM_hSjoDKz_MoDm4/edit?gid=0#gid=0).

**Limit**: Maximum 2 test rows per sprint.

## Production Enablement

Production POST requires:
1. Test POST verified successfully
2. Remove `--metrics-job-type test` flag
3. Set `AGENT_METRICS_DRY_RUN=false` or use `--metrics-post`
4. Explicit human approval (separate from test POST approval)

**Not enabled in this sprint.** `test_only_sprint=True` blocks all non-test job types.

## No-Secrets Policy

The following are NEVER written to evidence files, logs, or exceptions:
- `AGENT_METRICS_TOKEN` value
- Any authentication headers
- LLM prompt/completion content
- Request/response bodies

The token is read from the environment variable at POST time and immediately used in the HTTP header — it is never stored or returned in result dicts.

## Duplicate Ledger

**Location**: `workspace/verification/agent-metrics-post-ledger.jsonl`

Each successful POST appends a JSONL entry with `run_id`, `job_type`, `payload_hash`, and `posted_at`. Before POSTing, the poster checks if the same `run_id + job_type` already exists (non-dry-run).

### Recovery

If the ledger becomes corrupted or you need to re-POST:
- Use `--metrics-force-repost` to bypass the duplicate check
- Or delete the ledger file to reset (all entries lost)

The ledger auto-rotates at 500 entries (configurable via `ledger_max_entries`).

## Evidence Files

| File | Format | Written When |
|------|--------|-------------|
| `agent-metrics-llm-calls.jsonl` | JSONL | After each LLM call (per-call record) |
| `agent-metrics-run-summary.json` | JSON | Pipeline end |
| `agent-metrics-payload.json` | JSON | After payload build |
| `agent-metrics-validation.json` | JSON | After validation |
| `agent-metrics-post-result.json` | JSON | After POST attempt |

All evidence is written to `workspace/runs/{run_id}/evidence/` (run-scoped).

## Troubleshooting

| Issue | Resolution |
|-------|-----------|
| "missing env var AGENT_METRICS_TOKEN" | Set the token in your environment |
| "production job_type blocked in test-only sprint" | Use `--metrics-job-type test` or wait for production enablement |
| "duplicate_already_posted" | Use `--metrics-force-repost` if intentional |
| "network_error" | Check network connectivity and endpoint URL |
| Validation fails | Check `agent-metrics-validation.json` for specific errors |
| No evidence files | Ensure `--metrics` flag is passed |
