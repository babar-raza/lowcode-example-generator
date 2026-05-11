# Telemetry

Audience: Operator

Telemetry is implemented as optional agent metrics.

## Dry Run Metrics

```powershell
python -m plugin_examples run --family cells --dry-run --metrics
```

## Post Metrics

```powershell
python -m plugin_examples run --family cells --dry-run --metrics --metrics-post
```

Required env vars for posting:

- `AGENT_METRICS_ENDPOINT`
- `AGENT_METRICS_TOKEN`

## Evidence

Metrics evidence and duplicate-post ledger locations are documented in [Metrics Reference](../reference/metrics.md).
