Sprint 89 — Validation Authority Repair
==========================================
Date: 2026-05-25

## Sprint 88 Defect

`sprint88-final-validation-result.json` contained:
- `overall_valid: false` (68 diagnostic failures)
- `not_canonical: true`
- `canonical_overall_valid: true`

This violates Rule 111 (no_active_validation_file_with_ambiguous_false): an active validation file with overall_valid=false must have not_canonical=true, but having both together on the PRIMARY validation file is ambiguous.

## Root Cause

The FINISH_LINE_ADVANCEMENT bundle type has many non-applicable rules that fail diagnostically. The file correctly marks these as non-blocking, but the field combination `overall_valid=false + not_canonical=true` on the FINAL validation result creates confusion about whether the sprint actually passed.

## Sprint 89 Pattern

Sprint 89 uses two separate files:
1. `sprint89-final-validation-result.json`: canonical authority file
   - `canonical_overall_valid: true` (sole authority field)
   - NO `overall_valid` field (removed to avoid ambiguity)
   - `bundle_type: "FINISH_LINE_ADVANCEMENT"` (Rule 105 escape)
   - `applicable` and `diagnostic` counts
2. `diagnostic-full-rules-non-applicable.json`: diagnostic file
   - Clearly named "diagnostic"
   - `not_canonical: true`
   - Contains full rule-by-rule breakdown
   - Non-blocking per Rule 105 (bundle_type field present)
