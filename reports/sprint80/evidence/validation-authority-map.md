# Validation Authority Map — Sprint 80

**Date:** 2026-05-24

## Single Canonical Validation Authority

| File | Role | Canon |
|------|------|-------|
| `evidence/sprint80-final-validation-result.json` | CANONICAL — Phase B full validation result | YES |
| `evidence/diagnostic-full-rules-non-applicable.json` | DIAGNOSTIC — Phase A non-applicable rules (not_canonical=true) | NO |

## Rule

- `sprint80-final-validation-result.json` is the ONLY authoritative validation result.
- It must have `canonical_overall_valid=true` and must NOT have `overall_valid=false`.
- `diagnostic-full-rules-non-applicable.json` carries `not_canonical=true` to signal it is not the authority.

## Sprint 79 Defect S79-B1 (Now Closed)

Sprint 79's `sprint79-final-validation-result.json` had `"overall_valid": false` alongside
`"canonical_overall_valid": true`. This created ambiguity for future agents.

Sprint 80 closes this defect:
- EV Rule 111 (`no_active_validation_file_with_ambiguous_false`) now fails any bundle where
  `evidence/*-validation-result.json` has `overall_valid=false` without `not_canonical=true`.
- Sprint 80's canonical file omits `overall_valid` entirely (only `canonical_overall_valid=true`).

## Sprint 80 Applicable Rules Count

- EV total rules: 111 (Sprint 80 added Rule 111)
- REPAIR_SPRINT applicable rules: ~56 (55 from Sprint 79 + Rule 111 which now passes)
- Non-applicable diagnostic rules: ~55 (same generation/handoff/remote-proof rules)
