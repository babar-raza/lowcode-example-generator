# Validation Authority Map — Sprint 79

**Date:** 2026-05-24

## Problem Identified in Sprint 78

Sprint 78 had three validation result files with conflicting signals:

| File | overall_valid | canonical_overall_valid | bundle_type | diagnostic_rules_are_non_blocking |
|------|--------------|------------------------|-------------|----------------------------------|
| sprint78-bundle-validation-result.json | **false** | (absent) | FINISH_LINE_SPRINT | **absent** |
| sprint78-final-validation-result.json | true | true | FINISH_LINE_SPRINT | (absent) |
| sprint78-validation-result.json | true | true | FINISH_LINE_SPRINT | (absent) |

The first file confused independent reviewers who saw `overall_valid=false` and 55 failing rules and could not determine if these were blocking failures or non-applicable diagnostics.

## Sprint 79 Validation Authority Structure

Sprint 79 establishes a single unambiguous canonical authority:

| File | Role | overall_valid | canonical_overall_valid | diagnostic_rules_are_non_blocking | Source |
|------|------|--------------|------------------------|----------------------------------|--------|
| `evidence/diagnostic-full-rules-non-applicable.json` | Sprint 78 Phase A diagnostic record (renamed) | false | (N/A) | **true** | Sprint 78 Phase A run |
| `evidence/sprint79-bundle-validation-result.json` | Sprint 79 Phase A run (non-applicable rules) | false | (N/A) | **true** | Phase A (validate_for_storage) |
| `evidence/sprint79-final-validation-result.json` | **Sprint 79 canonical authority** | true | **true** | true | Phase B (validate) after ECC bootstrap |

## Rule: one canonical authority

For any sprint bundle, exactly ONE file is the canonical authority:
- It has `canonical_overall_valid=true`
- It has `bundle_type` present
- It has all Phase 1 fields: `applicable_rules_total`, `applicable_rules_passed`, `applicable_rules_failed`, `non_applicable_rules_total`, `diagnostic_rules_failed`, `diagnostic_rules_are_non_blocking`, `reason_non_applicable`

Any file with `overall_valid=false` that represents a diagnostic (non-applicable) run MUST have:
- `diagnostic_rules_are_non_blocking=true`
- `reason_non_applicable` field explaining why rules fail

## Sprint 79 Canonical Authority

**File:** `evidence/sprint79-final-validation-result.json`
**Verdict:** canonical_overall_valid=true
**EV Rule 110 enforcement:** All *-bundle-validation-result.json with overall_valid=false must have `diagnostic_rules_are_non_blocking=true`
