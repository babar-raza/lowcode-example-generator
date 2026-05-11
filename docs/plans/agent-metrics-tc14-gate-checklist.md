# TC14 Sprint 2 Approval Checklist

**Sprint:** TC14 Source Gate and Production-Shaped Dry Run
**Checklist version:** 1.0
**Date:** 2026-05-07
**Status:** 14/18 agent-verified PASS, 4 PENDING_HUMAN

This checklist must be fully signed before executing Sprint 2 (one-row production POST).

## Checklist Items

| # | Item | Status | Verified By |
|---|------|--------|-------------|
| C01 | Full test suite passes (0 failures) | PASS | Agent — 1017 passed |
| C02 | 14 new TC14-03 tests pass | PASS | Agent — all 14 pass |
| C03 | Dry-run gates DR-1 through DR-14 all pass | PASS | Agent — all 14 pass |
| C04 | payload.website == "aspose.net" confirmed | PASS | Agent — DR-3 PASS |
| C05 | payload.agent_name == "lowcode-example-generator" (no "test-" prefix) | PASS | Agent — DR-4 PASS |
| C06 | payload.job_type == "examples_generation" | PASS | Agent — DR-5 PASS |
| C07 | payload.run_id does NOT start with "test-" | PASS | Agent — DR-6 PASS |
| C08 | post_result.posted == false (dry-run confirms no POST) | PASS | Agent — DR-1 PASS |
| C09 | AGENT_METRICS_TOKEN is available (not empty, not test value) | **PENDING_HUMAN** | Human must set token |
| C10 | API endpoint confirmed from metrics.yml | PASS | Agent — verified in config |
| C11 | AGENT_METRICS_PRODUCTION_ENABLED=true will be set intentionally for Sprint 2 | **PENDING_HUMAN** | Human must confirm |
| C12 | AGENT_METRICS_DRY_RUN=false will be set intentionally for Sprint 2 | **PENDING_HUMAN** | Human must confirm |
| C13 | Maximum production rows: 1 | PASS | Agent — max_rows enforced |
| C14 | Rollback procedure reviewed | PASS | Agent — unset env vars, re-run, expect dry_run |
| C15 | Sheet verification method reviewed (human-only, no Sheets API available) | PASS | Agent — documented |
| C16 | git status clean (no unrelated changes) | PASS | Agent — only TC14 changes |
| C17 | Pre-POST ledger has 0 production entries | PASS | Agent — ledger verified (1 test entry only) |
| C18 | Human approval recorded in agent-metrics-tc14-gate-checklist.json | **PENDING_HUMAN** | Human must sign |

## Sprint 2 Production Command (Execute ONLY after all 18 items are PASS)

```bash
PYTHONPATH=src \
  AGENT_METRICS_TOKEN="<token>" \
  AGENT_METRICS_DRY_RUN=false \
  AGENT_METRICS_PRODUCTION_ENABLED=true \
  EXAMPLE_REVIEWER_PATH="C:/Users/prora/OneDrive/Documents/GitHub/example-reviewer" \
  .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --tier 5 \
  --metrics --metrics-post \
  --promote-latest
```

**DO NOT include `--metrics-force-repost` in this command.**

## Post-Production Acceptance Gates

| Gate | Check | Expected |
|------|-------|----------|
| P-1 | post_result.posted | true |
| P-2 | post_result.http_status | 200 |
| P-3 | post_result.payload_hash | non-empty |
| P-4 | Ledger non-dry-run entries delta | +1 (exactly) |
| P-5 | Ledger entry dry_run field | false |
| P-6 | Ledger entry http_status | 200 |
| P-7 | payload.agent_name | "lowcode-example-generator" |
| P-8 | payload.website | "aspose.net" |
| P-9 | payload.job_type | "examples_generation" |
| P-10 | No secret in evidence | AGENT_METRICS_TOKEN value absent |
| P-11 | Human sheet confirmation | Row found by run_id in Google Sheet UI |

## Rollback Command (Final step of Sprint 2)

```bash
PYTHONPATH=src AGENT_METRICS_ENABLED=true \
  EXAMPLE_REVIEWER_PATH="C:/Users/prora/OneDrive/Documents/GitHub/example-reviewer" \
  .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --tier 5 --metrics --promote-latest
```

Expected: `post_result.reason="dry_run"`, `posted=false`. Confirms instant disable.

## Evidence

`workspace/verification/latest/agent-metrics-tc14-gate-checklist.json`
