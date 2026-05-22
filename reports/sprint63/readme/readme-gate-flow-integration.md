# README Gate Flow Integration — Sprint 63

## Status: WIRED AND ACTIVE

The README audit gate is wired into the `publish-pr --publish` flow.

## Integration Points

1. **`publish-pr --publish`** calls `check_readme_audit_gate()` before any PR creation
2. Gate passes only when `PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH`
3. Failed audit blocks push: `APPROVE_README_PUSH` does NOT bypass failed audit (Sprint 62 hardening)
4. Only `APPROVE_README_AUDIT_OVERRIDE` can bypass with explicit override (records `audit_override_used=True`)

## Gate Source

`src/plugin_examples/publisher/readme_audit_gate.py` — `check_readme_audit_gate()`

## Sprint 62 Hardening

Gate was hardened in Sprint 62 (SD61-06 closed):
- `APPROVE_README_PUSH` no longer bypasses failed audit
- New `APPROVE_README_AUDIT_OVERRIDE` emergency token required for bypass
- 19 gate tests: 19 PASS (see `tests/unit/test_readme_audit_gate.py`)

## Test Coverage

- `tests/unit/test_readme_audit_gate.py` — 19 tests
- `tests/unit/test_publish_pr_readme_gate.py` — 19 tests
- `tests/unit/test_pipeline_evidence_gate.py` — 5 tests

## Verified Active

Gate is import-verified: `publish-pr` CLI calls `check_readme_audit_gate()` before any
remote mutation. No unauthorized push possible without explicit approval token.
