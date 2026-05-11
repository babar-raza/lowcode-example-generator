# TC14 Production-Shaped Dry Run

**Sprint:** TC14 Source Gate and Production-Shaped Dry Run
**Date:** 2026-05-07
**Run ID:** pilot-cells-20260507-140836
**Verdict:** TC14_DRY_RUN_ALL_14_GATES_PASS

## Purpose

This dry-run proves that with the production gate source change in place:
1. `test_only_sprint=False` is correctly passed when `AGENT_METRICS_PRODUCTION_ENABLED=true`
2. The `dry_run=True` gate blocks the POST (no `--metrics-post` flag)
3. The payload is production-shaped (no "test-" prefixes, correct website, correct job_type)
4. No token is required and no POST occurs

## Command

```bash
PYTHONPATH=src \
  AGENT_METRICS_ENABLED=true \
  AGENT_METRICS_PRODUCTION_ENABLED=true \
  EXAMPLE_REVIEWER_PATH="C:/Users/prora/OneDrive/Documents/GitHub/example-reviewer" \
  .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --tier 5 \
  --metrics \
  --promote-latest
```

Note: `--metrics-post` is NOT included — `dry_run=True` is the blocking gate.

## Dry-Run Gate Results

| Gate | Check | Result |
|------|-------|--------|
| DR-1 | post_result.posted | false — PASS |
| DR-2 | post_result.reason | "dry_run" — PASS |
| DR-3 | payload.website | "aspose.net" — PASS |
| DR-4 | payload.agent_name | "lowcode-example-generator" (no "test-" prefix) — PASS |
| DR-5 | payload.job_type | "examples_generation" — PASS |
| DR-6 | payload.run_id | "pilot-cells-20260507-140836" (no "test-" prefix) — PASS |
| DR-7 | payload.product | "Aspose.Cells" — PASS |
| DR-8 | payload.item_name | "Examples" (no "test-" prefix) — PASS |
| DR-9 | payload.token_usage | integer >= 0 — PASS |
| DR-10 | payload.api_calls_count | integer >= 0 — PASS |
| DR-11 | payload.platform | ".NET" — PASS |
| DR-12 | validation.valid | true (17/17 fields) — PASS |
| DR-13 | AGENT_METRICS_TOKEN in evidence | NOT PRESENT — PASS |
| DR-14 | Evidence files written | 5 files in evidence dir — PASS |

**All 14 gates: PASS**

## Bug Found and Fixed

During the first dry-run attempt, `validation.valid=false` was observed:
```
WARNING: Metrics payload validation failed: ["field 'run_duration_ms' must be a non-negative integer, got 247507.789..."]
```

Root cause: pipeline timing returns float milliseconds; validator strictly requires int.

Fix applied in `src/plugin_examples/metrics/payload_builder.py`:
```python
# BEFORE:
"run_duration_ms": run_duration_ms,
# AFTER:
"run_duration_ms": int(run_duration_ms),
```

After fix: DR-12 passes (validation.valid=true, all 17 fields valid).

## Ledger Verification

Pre-run: 1 entry (TC-13 test row: run_id=test-metrics-integration-1, job_type=test)
Post-run: 1 entry (unchanged — no POST occurred as expected)

## Evidence

`workspace/verification/latest/agent-metrics-tc14-production-shaped-dry-run.json`
