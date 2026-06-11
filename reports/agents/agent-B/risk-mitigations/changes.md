# Agent B Risk Mitigations — Changes

## File Modified

`src/plugin_examples/llm_router/router.py`

## RISK-06: Circuit Breaker (R06-01)

### Added to LLMRouter dataclass (lines 59-62)

Three new fields for circuit breaker state:
- `_consecutive_failures: int = 0`
- `_circuit_breaker_tripped: bool = False`
- `_CIRCUIT_BREAKER_THRESHOLD: int = 5`

### Added methods (lines 64-82)

- `_record_success()` — resets `_consecutive_failures` to 0.
- `_record_failure()` — increments counter; trips breaker at threshold with a warning log.
- `circuit_breaker_tripped` property — read-only access to breaker state.

### Modified `generate()` method (lines 141-155)

- Added early-exit check: if `_circuit_breaker_tripped` is True, raises `LLMProviderError` immediately.
- Wrapped `_call_provider()` in try/except: calls `_record_success()` on success, `_record_failure()` on any exception (then re-raises).
- Existing retry logic inside `_call_provider` / `_call_ollama` / `_call_openai_compatible` is unchanged.

## RISK-03: Temperature Pinning (R03-01)

### `_call_openai_compatible` (line ~429)

Changed `"temperature": 0.2` to `"temperature": 0.0` for deterministic output.

### `_call_ollama` (line ~355)

Added `"options": {"temperature": 0.0}` to the Ollama request JSON body. Previously no temperature was set (Ollama default is 0.8).
