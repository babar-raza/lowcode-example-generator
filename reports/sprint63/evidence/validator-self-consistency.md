# Validator Self-Consistency — Sprint 63 Phase 2

## Root Cause

Sprint 62 `sprint62-bundle-validation-result.json` was manually bootstrapped:
- Top-level: `overall_valid=true`, `failed=0`, `passed=21`
- Embedded rules: one rule (`bundle_validation_result_present_and_valid`) had `passed=false`

This is a self-contradiction: `overall_valid=true` cannot be valid when an embedded rule
reports `passed=false`.

**How it happened:** The bootstrap ran EV before the result file existed (20/21 rules pass),
then manually patched the JSON to claim 21/21. Rule 21 was present in the embedded rules list
from a prior 20-rule run, still showing `passed=false`.

## Fix: Two-Phase Validation

Added `validate_for_storage()` and `exclude_rule_ids` parameter to `EvidenceValidator.validate()`.

### Phase A — Run 20 rules (exclude self-referential rule 21)
```python
result = ev.validate_for_storage()  # excludes SELF_REFERENCE_RULE_ID
# Store result — overall_valid reflects 20 actual rules, no bootstrap contradiction
```

### Phase B — Run all 21 rules (result file now present)
```python
result = ev.validate()  # all 21 rules, rule 21 now passes because result file exists
```

### Contradiction Detection
Added check: if `overall_valid=true` but any embedded rule has `passed=false`, rule 21 FAILS.
This prevents future manual bootstrapping from hiding failures.

## Evidence

- `sprint62-revalidation-result.json` — Sprint 62 bundle re-run with new validator: `overall_valid=false`, `failed=1` (rule 21 detects contradiction)
- `validator-test-results.txt` — 76 tests, 76 pass, 0 fail

## Files Changed

- `src/plugin_examples/evidence_validator.py`
  - `validate(exclude_rule_ids)` parameter added
  - `validate_for_storage()` added
  - `SELF_REFERENCE_RULE_ID = "bundle_validation_result_present_and_valid"` added
  - `_rule_bundle_validation_result_present_and_valid()` — internal contradiction detection added
- `tests/unit/test_evidence_validator.py`
  - `TestTwoPhaseValidation` (7 tests) added
