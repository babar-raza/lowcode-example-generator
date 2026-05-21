# README Gate Flow Integration — Sprint 62

**Sprint:** 62
**Source:** `src/plugin_examples/publisher/readme_audit_gate.py`
**Wired in:** `src/plugin_examples/__main__.py` (publish-pr live mode)

## Gate is wired into publication flow

The README audit gate (`check_readme_audit_gate`) is called in `publish-pr --publish` mode
before any live PR is created. The gate check runs for each family and blocks PR creation
if the audit is missing, shallow, or has failed records.

```python
# In __main__.py publish-pr live mode:
from plugin_examples.publisher.readme_audit_gate import check_readme_audit_gate

gate_result = check_readme_audit_gate(family, verification_dir)
if not gate_result["gate_passed"]:
    raise RuntimeError(f"README audit gate BLOCKED: {gate_result['blocked_reason']}")
```

## Sprint 62 Override Integration
The emergency override token (`APPROVE_README_AUDIT_OVERRIDE`) is checked in the gate
before blocking on failed records. If present, the gate allows through but records
`audit_override_used=True` in the result for audit trail.

Normal push token (`APPROVE_README_PUSH`) has NO effect on audit failures.
This separation was hardened in Sprint 62 (SD61-06 fix).

## Test Coverage
`tests/unit/test_publish_pr_readme_gate.py::TestReadmeGateWiredInMainPy`:
- `test_readme_audit_gate_imported_in_main` — gate import confirmed
- `test_check_readme_audit_gate_called_in_main` — gate called in publish flow
- `test_gate_passed_check_in_main` — gate result checked before PR creation
