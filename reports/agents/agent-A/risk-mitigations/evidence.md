# Agent A Risk Mitigation Evidence

## Date: 2026-06-10

## Files Modified

| File | Action | Risk |
|------|--------|------|
| `src/plugin_examples/gates/example_gates.py` | Added `_GATE_ISOLATION_FORBIDDEN` constant | R10-01 |
| `src/plugin_examples/llm_router/sanitizer.py` | Created new file | R07-01, R07-02, R08 |
| `src/plugin_examples/runner.py` | Wired sanitizer into build+runtime repair prompts | R07-03 |

## Verification Checklist

- [x] `example_gates.py` has no imports from llm_router, healing_intelligence, or generator
- [x] `_GATE_ISOLATION_FORBIDDEN` frozenset declared with all three forbidden prefixes
- [x] `sanitizer.py` exports `sanitize_llm_input`, `check_generated_code_safety`, `scrub_secrets`
- [x] `sanitize_llm_input` strips ANSI, control chars, injection lines, and truncates to 800
- [x] `check_generated_code_safety` detects 10 dangerous C# patterns
- [x] `scrub_secrets` redacts API keys, tokens, and Windows paths
- [x] `runner.py` build repair: compiler stdout/stderr sanitized before prompt
- [x] `runner.py` build repair: complete prompt scrubbed for secrets before LLM call
- [x] `runner.py` runtime repair: runtime stdout/stderr sanitized before prompt
- [x] `runner.py` runtime repair: complete prompt scrubbed for secrets before LLM call
- [x] No changes to prompt structure or repair logic
- [x] Existing `_prompt_hash` computation moved after sanitization (hashes the cleaned prompt)

## Grep Evidence

Build repair sanitization (runner.py):
```
1234: from plugin_examples.llm_router.sanitizer import sanitize_llm_input, scrub_secrets
1235: _clean_build_stdout = sanitize_llm_input(build_stdout)
1236: _clean_build_stderr = sanitize_llm_input(build_stderr)
1248: repair_prompt = scrub_secrets(repair_prompt)
```

Runtime repair sanitization (runner.py):
```
1385: _clean_run_stdout = sanitize_llm_input(run_stdout)
1386: _clean_run_stderr = sanitize_llm_input(run_stderr)
1401: repair_prompt = scrub_secrets(repair_prompt)
```

Gate isolation guard (example_gates.py):
```
16: _GATE_ISOLATION_FORBIDDEN = frozenset({
17:     "plugin_examples.llm_router",
18:     "plugin_examples.healing_intelligence",
19:     "plugin_examples.generator",
20: })
```
