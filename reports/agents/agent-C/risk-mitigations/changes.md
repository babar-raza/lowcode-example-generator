# Risk Mitigation Changes — Agent C

## File Modified
- `src/plugin_examples/runner.py`

## R01-01: Output Hash Logging
- Added `import hashlib` at line 5 (stdlib imports block).
- Build repair loop (line ~1257): `_code_hash = hashlib.sha256(fixed_code.encode("utf-8")).hexdigest()` computed after `_extract_code(response)`.
- Runtime repair loop (line ~1407): same `_code_hash` computation.
- `"output_hash": _code_hash` added to all 6 repair_log entries (build: success, semantic_fail, diff_cap; runtime: success, semantic_fail, diff_cap).

## R01-02: Repair Diff Cap
- Build repair loop (lines 1258-1277): after `_code_hash` computation and before semantic validation, a `SequenceMatcher` similarity check rejects repairs with <0.40 similarity (>60% rewrite). Logs `rejection_reason: repair_diff_cap_exceeded` with `similarity` value.
- Runtime repair loop (lines 1410-1427): identical diff cap logic using `rt_attempt` and `rc.classification`.

## R03-02: Prompt Fingerprint Logging
- Build repair loop (line 1249): `_prompt_hash = hashlib.sha256(repair_prompt.encode("utf-8")).hexdigest()` computed after `repair_prompt` is finalized (post `scrub_secrets`).
- Runtime repair loop (line 1398): same `_prompt_hash` computation after `repair_prompt` is built.
- `"prompt_hash": _prompt_hash` added to all 6 repair_log entries.

## Summary of repair_log Entry Changes
Each repair_log dict now includes two new keys:
- `output_hash` — SHA-256 hex digest of the LLM-generated fixed code
- `prompt_hash` — SHA-256 hex digest of the repair prompt sent to the LLM

New diff-cap entries additionally include:
- `rejection_reason` — `"repair_diff_cap_exceeded"`
- `similarity` — float rounded to 3 decimal places
