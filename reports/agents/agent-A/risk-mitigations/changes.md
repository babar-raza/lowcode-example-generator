# Agent A Risk Mitigation Changes

## Date: 2026-06-10

## R10-01: Gate Isolation Guard

**File**: `src/plugin_examples/gates/example_gates.py`

**Change**: Added `_GATE_ISOLATION_FORBIDDEN` frozenset constant after the logger declaration (line 12-20). This declares the set of module prefixes that must never be imported in gate code:
- `plugin_examples.llm_router`
- `plugin_examples.healing_intelligence`
- `plugin_examples.generator`

This is a declarative guard. Enforcement is performed by CI tests (R10-02) that inspect the gate module's imports against this list.

## R07-01 / R07-02: Prompt Sanitizer

**File created**: `src/plugin_examples/llm_router/sanitizer.py`

Three functions implemented:

1. **`sanitize_llm_input(text: str) -> str`** (RISK-07)
   - Strips ANSI escape codes via regex
   - Strips control characters except newline/tab
   - Removes lines matching prompt-injection patterns (System:, User:, Assistant:, IGNORE, Forget)
   - Truncates to 800 characters max
   - Returns cleaned text

2. **`check_generated_code_safety(code: str) -> list[str]`** (RISK-07)
   - Checks for 10 dangerous C# patterns: HttpClient, WebClient, WebRequest, Process.Start, Assembly.Load, Activator.CreateInstance, Type.GetType, AppDomain, eval, dynamic
   - Returns list of violation descriptions (empty = safe)

3. **`scrub_secrets(text: str) -> str`** (RISK-08)
   - Redacts: sk-* API keys, ghp_/gho_ GitHub tokens, Bearer tokens, absolute Windows user paths, long base64/hex strings
   - Replaces with descriptive [REDACTED-*] placeholders

## R07-03: Runner Sanitization Wiring

**File**: `src/plugin_examples/runner.py`

### Build repair prompt (line ~1234)
- Added deferred import of `sanitize_llm_input` and `scrub_secrets`
- `build_stdout` and `build_stderr` are now passed through `sanitize_llm_input()` before prompt interpolation
- Complete `repair_prompt` is passed through `scrub_secrets()` before LLM call

### Runtime repair prompt (line ~1385)
- `run_stdout` and `run_stderr` are now passed through `sanitize_llm_input()` before prompt interpolation
- Complete `repair_prompt` is passed through `scrub_secrets()` before LLM call

No changes to prompt structure, repair logic, or system prompts.
