Sprint 88 — Validation Count Reconciliation
==============================================
Date: 2026-05-25

## The 134 vs 133 Mismatch Explained

| Method | Total Rules | Explanation |
|--------|------------|-------------|
| validate() (Phase B) | 134 | All rules including rule 21 (self-referential) |
| validate_for_storage() (Phase A) | 133 | Excludes rule 21 (self-referential bootstrap) |

## Root Cause
Rule 21 (`bundle_validation_result_present_and_valid`) is self-referential: it checks
whether the bundle-validation-result file itself exists and is valid. When writing the
bundle-validation-result (Phase A), rule 21 must be excluded to avoid circular dependency.

This is an ARCHITECTURAL INVARIANT, not a defect:
- validate_for_storage() = total_rules - 1 (always excludes rule 21)
- validate() = total_rules (includes rule 21)

## Sprint 88 Action
- bundle-validation-result.json documents total_rules as Phase A count (N-1)
- final-validation-result.json documents total_rules as Phase B count (N)
- Both files include a note explaining the rule-21 exclusion
- EV Rule 128 (validation_result_not_placeholder) updated to accept N-1 for bundle results
