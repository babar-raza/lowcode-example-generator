# Agent B Risk Mitigations — Evidence

## Verification

### RISK-06 Circuit Breaker

1. **Breaker threshold**: 5 consecutive failures trip the breaker (configurable via `_CIRCUIT_BREAKER_THRESHOLD`).
2. **Breaker effect**: Once tripped, all subsequent `generate()` calls raise `LLMProviderError` without making any network request.
3. **Reset on success**: Any successful `generate()` call resets the failure counter to 0.
4. **Re-raise preserved**: The original exception from `_call_provider` is always re-raised after recording the failure — callers see the same error they would have seen before.
5. **Retry logic untouched**: The per-call retry logic in `_call_ollama` and `_call_openai_compatible` (max 2 retries with backoff) remains unchanged. The circuit breaker operates at the `LLMRouter.generate()` level, counting calls that exhaust all retries.
6. **Provider policy untouched**: `_APPROVED_PROVIDER_FAMILIES`, preflight, and provider selection are unchanged.
7. **Metrics collection untouched**: All `metrics_collector.record_call()` invocations remain in place.

### RISK-03 Temperature Pinning

1. **OpenAI-compatible**: Temperature changed from `0.2` to `0.0` on line ~429 in `_call_openai_compatible`.
2. **Ollama**: Temperature `0.0` added via `"options": {"temperature": 0.0}` in the request body on line ~355 in `_call_ollama`.
3. **Effect**: Both providers now produce deterministic (greedy) output, eliminating sampling variance across pipeline runs.

## Files Changed

| File | Lines Changed | Risk ID |
|------|--------------|---------|
| `src/plugin_examples/llm_router/router.py` | +30 (circuit breaker), +2 (temperature) | R06-01, R03-01 |

## What Was NOT Changed

- Retry backoff logic (`_LLM_RETRY_BACKOFF_SECONDS`, `_LLM_MAX_RETRIES`)
- Provider approval policy (`_APPROVED_PROVIDER_FAMILIES`)
- Preflight check logic (`run_preflight`, `_check_provider`)
- Metrics collection (`record_call` invocations)
- Provider routing (`_call_provider` dispatch)
