# Final Validation Gate — Sprint 62

**Sprint:** 62
**Date:** 2026-05-21
**Source:** `src/plugin_examples/evidence_validator.py`
**Tests:** `tests/unit/test_evidence_validator.py` (69 tests, all passing)
**Defect Closed:** SD61-05 (Sprint 61 missing its own bundle validation JSON)

---

## Problem (Sprint 61 SD61-05)

Sprint 61 closed without `evidence/sprint61-bundle-validation-result.json`.
The EvidenceValidator was wired into `release-status --validate-bundle` (Phase 3 Sprint 61),
but the resulting JSON was never captured in the bundle. A sprint that runs EV but doesn't
store the result cannot prove it passed.

Additionally, the EV was optional — it was called only when `--validate-bundle` flag was passed.
Sprint 62 requires it to be mandatory for final closure.

---

## Fix (Sprint 62 Phase 7)

### New EV Rule: `bundle_validation_result_present_and_valid`

Added to `EvidenceValidator.validate()` as rule #21:

```python
def _rule_bundle_validation_result_present_and_valid(self) -> RuleResult:
    """Sprint bundle validation result must exist and show overall_valid=true.

    Missing/stale validation = BLOCKED.
    """
```

**Rule behavior:**
- Looks for `evidence/*-bundle-validation-result.json` (any sprint)
- If not found: FAILURE — "No evidence/*-bundle-validation-result.json found"
- If found but overall_valid=false: FAILURE — shows failed rule count
- If found and overall_valid=true: PASS

**Severity:** FAILURE (blocks closure)

**Implication:** To close a sprint, you MUST:
1. Run `release-status --validate-bundle` or equivalent
2. Store the result as `evidence/sprint{N}-bundle-validation-result.json`
3. Ensure overall_valid=true before claiming closure

---

## Tests

69 tests, 69 passing (0 failed):

### New Tests (`TestBundleValidationResultPresentAndValid`):
- `test_fails_when_no_bundle_validation_result` — Missing JSON = FAIL
- `test_fails_when_bundle_validation_result_shows_failures` — overall_valid=false = FAIL
- `test_passes_when_bundle_validation_result_is_valid` — overall_valid=true = PASS
- `test_uses_most_recent_file_when_multiple_exist` — uses alphabetically last file
- `test_overall_valid_false_when_bundle_validation_missing` — overall_valid False when missing

### Existing tests updated:
- `_make_bundle`: now creates `evidence/sprint60-bundle-validation-result.json`
- `test_to_dict_structure`: updated to expect 21 rules (was 20)
- `test_passes_with_complete_valid_bundle`: updated to expect total_rules=21

Test file: `tests/unit/test_evidence_validator.py`
Results: `reports/sprint62/evidence/final-validation-test-results.txt`
Patch: `reports/sprint62/evidence/final-validation-source-proof.patch` (245 lines)

---

## Closure

SD61-05 closed. Final bundle closure now requires `evidence/sprint{N}-bundle-validation-result.json`
to be present and overall_valid=true. Cannot close sprint without running EV on bundle.
