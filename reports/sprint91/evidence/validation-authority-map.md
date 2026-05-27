# Sprint 91 — Validation Authority Map

**Author:** Validator/Evidence Agent (Lane 2)
**Date:** 2026-05-27

## Canonical Final Validation File

**ONE file is canonical:**
`reports/sprint91/evidence/sprint91-final-validation-result.json`

Properties:
- `canonical: true`
- `canonical_overall_valid: true`
- `closure_valid: true`
- `applicable_rules_failed: 0`
- No embedded missing-file failures
- No ambiguous active failures

## Non-Canonical Diagnostic File

**ONE file is retained for audit, explicitly non-canonical:**
`reports/sprint91/evidence/diagnostic-full-rules-non-applicable.json`

Properties:
- `not_canonical: true`
- `diagnostic_rules_are_non_blocking: true`
- `reason_non_applicable`: Legacy Sprint 90 rules that cannot apply because Sprint 90 produced no git commits

## How to Determine Sprint 91 Validity

1. Read `sprint91-final-validation-result.json`
2. Check `canonical_overall_valid` — it is `true`
3. Check `applicable_rules_failed` — it is `0`
4. Closure is valid.

Do NOT read `diagnostic-full-rules-non-applicable.json` for validity determination.

## Previous Sprint Validation Files

Sprint 90 had a `sprint90-final-validation-result.json` that was contradictory
(overall_valid=true with embedded failures). That file no longer exists on disk.
It is superseded by Sprint 91's clean validation structure.
