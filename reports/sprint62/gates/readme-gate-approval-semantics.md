# README Gate Approval Semantics — Sprint 62

**Sprint:** 62
**Date:** 2026-05-21
**Source:** `src/plugin_examples/publisher/readme_audit_gate.py`
**Tests:** `tests/unit/test_publish_pr_readme_gate.py` (19 tests, all passing)
**Defect Closed:** SD61-06 (APPROVE_README_PUSH could bypass failed audit)

---

## Problem (Sprint 61 SD61-06)

In Sprint 61, `check_readme_audit_gate()` at line 126 had:

```python
if failed_records and not approval_bypass:
```

where `approval_bypass = token == "APPROVE_README_PUSH"`. This allowed any caller with
`APPROVE_README_PUSH` to bypass a failed README audit by passing the normal push token.
This meant a failed audit was NOT actually blocking — it could be silently bypassed with
the same token used for all README pushes.

---

## Fix (Sprint 62 Phase 6)

### New Token: Emergency Override

Added to `readme_audit_gate.py`:

```python
README_AUDIT_OVERRIDE_ENV_VAR = "PLUGIN_EXAMPLES_README_AUDIT_APPROVAL"
README_AUDIT_OVERRIDE_VALUE = "APPROVE_README_AUDIT_OVERRIDE"
```

### Hardened Semantics

The failed-records check was changed from:
```python
if failed_records and not approval_bypass:  # OLD: APPROVE_README_PUSH could bypass
```

To:
```python
if failed_records:
    if not audit_override:  # NEW: only APPROVE_README_AUDIT_OVERRIDE can bypass
        result["blocked_reason"] = BLOCKED_README_AUDIT_FAILED
        return result
    # Emergency override: record evidence and allow through
    result["audit_override_used"] = True
```

### Behavior Table

| Scenario | APPROVE_README_PUSH | APPROVE_README_AUDIT_OVERRIDE | Result |
|----------|---------------------|-------------------------------|--------|
| All audit records PASS | Present | Absent | PASS |
| Audit FAIL records exist | Present | Absent | BLOCKED |
| Audit FAIL records exist | Absent | Absent | BLOCKED |
| Audit FAIL records exist | Present | Present | PASS (override, evidence recorded) |
| Audit FAIL records exist | Absent | Present | PASS (override, evidence recorded) |
| Audit missing | Present | Present | BLOCKED (missing cannot be overridden) |
| Audit shallow | Present | Present | BLOCKED (shallow cannot be overridden) |

**Key rule:** `APPROVE_README_PUSH` is the push authorization token. It does NOT override
audit failures. Only `APPROVE_README_AUDIT_OVERRIDE` can override a failed audit, and it
records evidence (`audit_override_used=True`).

---

## Tests

19 tests, 19 passing (0 failed):

- `test_normal_approval_does_not_bypass_failed_audit` — APPROVE_README_PUSH + failed audit = BLOCKED
- `test_env_var_approval_does_not_bypass_failed_audit` — Same via env var
- `test_emergency_override_bypasses_failed_audit` — APPROVE_README_AUDIT_OVERRIDE bypasses
- `test_emergency_override_records_evidence` — audit_override_used=True set
- `test_normal_approval_plus_failed_audit_is_blocked` — explicit integration test
- `test_emergency_override_token_defined_in_gate` — constants correct
- Plus 13 other tests covering missing/shallow/pass/wiring

Test file: `tests/unit/test_publish_pr_readme_gate.py`
Results: `reports/sprint62/gates/readme-gate-test-results.txt`
Patch: `reports/sprint62/gates/readme-gate-source-proof.patch` (335 lines)

---

## Closure

SD61-06 closed. Failed README audit now requires `APPROVE_README_AUDIT_OVERRIDE` to bypass.
Normal `APPROVE_README_PUSH` cannot bypass. Emergency override records `audit_override_used=True`.
