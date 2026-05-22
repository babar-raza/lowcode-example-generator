# EvidenceValidator Pipeline Integration — Sprint 63

## Status: WIRED AND ACTIVE

EvidenceValidator is wired into the `release-status --validate-bundle` CLI flow.

## Integration Points

1. **`release-status --validate-bundle`** calls `EvidenceValidator(bundle_dir).validate()`
2. Returns `ValidationReport` with `overall_valid`, `passed`, `failed` counts
3. Sprint closure requires `overall_valid=true` stored as `evidence/sprint{N}-bundle-validation-result.json`
4. EV rule #21 checks that this file exists and is valid (EV execution is mandatory for closure)

## Sprint 62 New Capability: Two-Phase Validation

- `validate_for_storage()` — Phase A: runs 20 rules (excludes self-referential rule 21)
- `validate()` — Phase B: runs all 21 rules after storing Phase A result
- Eliminates bootstrap contradiction (Sprint 63 Phase 2 fix)

## Sprint 63 New Rule: Contradiction Detection

- Rule 21 now detects: `overall_valid=true` + embedded rule with `passed=false`
- Sprint 62 defect detected and reported as `overall_valid=false` on revalidation

## Source

`src/plugin_examples/evidence_validator.py` — `EvidenceValidator` class
- 21 rules, `SELF_REFERENCE_RULE_ID = "bundle_validation_result_present_and_valid"`
- `validate_for_storage()` added (Sprint 63)
- `validate(exclude_rule_ids)` parameter added (Sprint 63)

## Test Coverage

- `tests/unit/test_evidence_validator.py` — 76 tests, 76 PASS
- `tests/unit/test_pipeline_evidence_gate.py` — 5 tests
