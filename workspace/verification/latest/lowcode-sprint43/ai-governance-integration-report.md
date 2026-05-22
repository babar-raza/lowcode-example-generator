# AI Governance Integration Report — Sprint 43

## Governance Test Suites (5)

All 5 suites import from **real source modules** and test **meaningful behavior**. None are decorative.

| Suite | Source Module | Purpose |
|-------|--------------|---------|
| test_provider_policy | llm_router.provider_policy | LLM provider/model enforcement |
| test_llm_router_preflight | llm_router | Router preflight checks |
| test_healing_intelligence_loader | healing_intelligence.loader | Failure pattern classification |
| test_metrics_collector | metrics.models | Pipeline execution tracking |
| test_safety_governance | codebase-wide | AGENTS.md rule enforcement |

## Connections to Execution

- **provider_policy** gates which LLM providers are used in code generation
- **healing_intelligence** feeds failure patterns into retry/repair decisions
- **metrics** tracks pipeline execution via MetricsSession
- **safety_governance** enforces security rules across codebase

## New This Sprint

`portfolio_action_planner.py` provides durable action ranking from repo state. 26 tests + CLI command.

## Gaps

1. No direct planner → metrics collector connection yet
2. No automated sprint-to-sprint evidence chain

## LLM Governance

- Approved endpoint: `https://llm.professionalize.com/v1/`
- No secrets in logs: confirmed
- Token accounting: via MetricsSession when enabled
