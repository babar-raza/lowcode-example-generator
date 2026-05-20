# Lane H: Provider Telemetry and Agent Metrics Hardening Report

**Sprint:** LOWCODE-MEGA-TRAIN-005
**Date:** 2026-05-20

## Canonical Provider Policy

### Approved Providers
- `llm_professionalize` — primary LLM provider via GPT_OSS_ENDPOINT
- `ollama` — local model provider

### Rejected Providers
- `azure_openai` — explicitly forbidden
- `gpt_oss` — explicitly forbidden (transport alias, not provider identity)
- `openai` — explicitly forbidden

### Policy Verification (from provider-telemetry-normalization-tests.json)
All 8 test cases PASS:
1. approved_llm_professionalize: PASS
2. approved_ollama: PASS
3. unapproved_azure_openai: correctly produces violations, PASS
4. unapproved_gpt_oss: correctly produces violations, PASS
5. unapproved_openai: correctly produces violations, PASS
6. model_gpt4o_under_approved_provider: model label is not provider authority, PASS
7. forbidden_model_gpt4o_mini: correctly forbidden, PASS
8. classify_approved_hit: correct classification, PASS

### Model vs Provider Distinction
- `gpt-4o` is a **model label** under `llm_professionalize` provider — NOT a provider identity
- `gpt-4o-mini` is **forbidden as a configured pipeline model** (quality threshold)
- Provider identity comes from endpoint configuration, not model name

## Agent Metrics

### Token Usage
- Computed from actual API response `usage` fields
- NOT hardcoded or estimated
- Fields: `prompt_tokens`, `completion_tokens`, `total_tokens`

### API Calls Count
- Computed by counting actual API invocations
- NOT hardcoded
- Incremented per LLM call in generation and review stages

### Sample Normalized Payload
```json
{
  "canonical_provider": "llm_professionalize",
  "transport_alias": "gpt-oss-endpoint",
  "endpoint_family": "llm_professionalize",
  "model_label": "gpt-4o",
  "policy_status": "APPROVED",
  "provider_violations": []
}
```

## Local/Test/Prod Posting Rules
- **Local/test:** Metrics computed and stored locally, never posted to production
- **Production:** Requires explicit metrics posting gate (not present)
- **No production metrics posting occurred in this sprint**

## Existing Test Coverage
From tests/unit/:
- test_ai_provider_policy.py — provider approval/rejection
- test_ai_router.py — routing and endpoint configuration
- test_ai_healing_intelligence.py — HI constraint generation
- test_ai_metrics.py — metrics computation
- test_ai_safety.py — safety boundaries

No gaps identified — existing tests cover all verification points.

## Verdict
Provider telemetry policy verified. Metrics computed (not hardcoded). No production posting. No new tests needed.
