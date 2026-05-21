# README Gate Flow Integration — Sprint 61 Phase 5

## Defect Closed

**SD60-03:** `readme_audit_gate.py` was created in Sprint 60 but never imported or
called by any pipeline command. A gate that is never called is not a gate.

---

## Implementation

### Source Change: `src/plugin_examples/__main__.py`

Added README audit gate check inside the `publish-pr` live mode block, after all
existing guards (token, approval, package, repo-access) and before `create_github_pr`:

```python
# README audit gate — must have a content-based, passing audit before live publish
from plugin_examples.publisher.readme_audit_gate import (
    check_readme_audit_gate as _check_readme_gate,
    README_AUDIT_ENV_VAR as _README_ENV,
    README_AUDIT_EXPECTED_VALUE as _README_EXPECTED,
)
_readme_push_approval = os.environ.get(_README_ENV, getattr(args, "approval_token", None))
_gate_result = _check_readme_gate(
    family=family,
    verification_dir=verification_dir,
    run_id=run_id,
    readme_push_approval=_readme_push_approval,
)
if not _gate_result.get("gate_passed"):
    print(f"ERROR: README audit gate blocked live publish: {_gate_result.get('blocked_reason')}")
    print(f"  Set {_README_ENV}={_README_EXPECTED} to override if audit is valid")
    return 1
```

### Insertion Point

Lines 1071-1087 in `src/plugin_examples/__main__.py` — inside `if live_mode:` block,
after `target_owner is None` guard and before `github_pr_publisher` import.

---

## Gate Behavior

| Condition | Gate Result | CLI Exit |
|-----------|------------|---------|
| No README audit artifact for family | `BLOCKED_README_AUDIT_MISSING` | 1 |
| Audit exists but size/presence only (shallow) | `BLOCKED_README_AUDIT_SHALLOW` | 1 |
| Audit has FAIL/NEEDS_REVIEW records | `BLOCKED_README_AUDIT_FAILED` | 1 |
| Content-based audit, all records PASS | `gate_passed=True` | 0 (continues) |
| `APPROVE_README_PUSH` set (bypass) | `gate_passed=True` | 0 (continues) |

The gate reads approval from:
1. `readme_push_approval` argument (from `--approval-token` CLI flag)
2. `PLUGIN_EXAMPLES_README_PUSH_APPROVAL` environment variable

---

## Tests

File: `tests/unit/test_publish_pr_readme_gate.py` — 14 tests

| Test Class | Tests |
|------------|-------|
| `TestReadmeAuditGateUnit` | 7 (direct gate function tests) |
| `TestPublishPrReadmeGateWiring` | 4 (wiring behavior tests) |
| `TestReadmeGateWiredInMainPy` | 3 (source scan tests) |

**14 passed, 0 failed**

---

## Source Scan Verification

`test_readme_audit_gate_imported_in_main` scans `src/plugin_examples/__main__.py`
for `readme_audit_gate` substring.

`test_check_readme_audit_gate_called_in_main` confirms `check_readme_audit_gate`
is called (not just imported).

`test_gate_passed_check_in_main` confirms `gate_passed` result is checked (not
silently ignored).

---

## CLI Usage

```bash
# Live publish — README audit gate will run automatically:
GITHUB_TOKEN="$GH_TOKEN" PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
    --family cells --publish --approval-token APPROVE_LIVE_PR

# If gate blocks: ERROR: README audit gate blocked live publish: blocked_readme_audit_missing
# Override if audit is valid:
GITHUB_TOKEN="$GH_TOKEN" PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH \
    PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples publish-pr \
    --family cells --publish --approval-token APPROVE_LIVE_PR
```

---

## Audit Evidence Files

| File | Description |
|------|-------------|
| `readme-gate-flow-test-results.txt` | 14 passed, 0 failed in 0.54s |
| `readme-gate-flow-source-proof.patch` | git diff of __main__.py + full test file (408 lines) |
| `readme-gate-flow-integration.md` | This document |
