# Pipeline Integration Proof — Sprint 62

**Sprint:** 62
**EvidenceValidator source:** `src/plugin_examples/evidence_validator.py`
**Wired in:** `src/plugin_examples/__main__.py` (release-status --validate-bundle)

## EvidenceValidator is wired into the pipeline

The `EvidenceValidator` is imported and called in `__main__.py` via the
`release-status --validate-bundle` subcommand:

```python
# In __main__.py, release-status path:
from plugin_examples.evidence_validator import EvidenceValidator

if validate_bundle:
    validator = EvidenceValidator(bundle_dir=Path(validate_bundle))
    result = validator.validate()
    ...
```

This was confirmed by scanning source imports:
`grep -r "EvidenceValidator" src/plugin_examples/__main__.py` → FOUND

## Sprint 62 EV Rule 21

Rule `bundle_validation_result_present_and_valid` was added in Sprint 62.
This rule blocks sprint closure if `evidence/*-bundle-validation-result.json`
is absent or has `overall_valid=false`.

EV execution is now **mandatory** for final sprint closure.
Cannot pass EV without first running EV and storing its result.

## Integration Test
`tests/unit/test_pipeline_evidence_gate.py::TestReleaseStatusValidateBundleFlag`:
- `test_returns_0_on_valid_bundle` — EV wired and returns 0 on valid bundle
- `test_returns_1_on_invalid_bundle` — returns 1 on invalid bundle
- `test_validate_bundle_not_called_without_flag` — not called without --validate-bundle flag

All 3 tests: PASS
