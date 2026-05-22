# Phase 1 — EV+ECC Final Gate Alignment

## Sprint 63 Defect S63-D1: EV/ECC Silent Disagreement

Sprint 63 closed with `EvidenceValidator overall_valid=true` (21/21 rules pass) but
`EvidenceContractComputer closure_valid=false` (11 blocking failures). These two
systems checked different things and their results were never cross-validated.

## Root Cause Analysis

### Root Cause 1: ECC Timing (Primary)

The `evidence-contract-computed.json` was computed at `2026-05-22T07:18:19Z`.
The final commits that created 7 required files were made at `07:19–07:21Z`.

Result: ECC reported 7 MISSING files that actually existed at review time.

**Fix:** ECC must always be run AFTER all bundle files are committed. The new EV
rule 22 (`ecc_contract_computed_and_valid`) detects stale ECC runs by checking
`closure_valid=true`. If ECC was run early, it will have MISSING entries →
`closure_valid=false` → EV rule 22 FAILS → forces a re-run.

### Root Cause 2: pytest "0 failed" Pattern Bug

The `_TEST_ZERO_FAILED_PATTERN` regex required literal `"0 failed"` but pytest
omits this string entirely when there are no failures. `2976 passed, 3 skipped
in 96.19s` has no `"0 failed"` substring → ECC reported SEMANTIC_FAILED for
valid test logs.

**Fix:** Accept either:
- Literal `"0 failed"` or `"0 fail"` (classic CI format)
- `"N passed"` with no `"N failed"` count (pytest format — no failures means no
  "failed" line at all)

### Root Cause 3: "6 families" Dict-Key Bug

The `_check_semantic` code for `"6 families"` used `data.get("families", [])`,
which returns `[]` because `package-artifact-index.json` uses family names as
top-level dict keys (`{"cells": {...}, "diagram": {...}, ...}`), not a `"families"`
list. Result: ECC reported SEMANTIC_FAILED for a valid artifact index.

**Fix:** Detect the layout: if `"families"` key is absent, count top-level string
keys that match known family names (`cells`, `diagram`, `email`, `pdf`, `slides`,
`words`). Legacy format with explicit `"families"` key still supported.

## Changes Made

### `src/plugin_examples/evidence_contract_computer.py`

1. **Pytest "0 failed" fix**: Replaced `_TEST_ZERO_FAILED_PATTERN` with two
   patterns: `_TEST_ZERO_FAILED_LITERAL_PATTERN` (legacy) and `_TEST_PASSED_PATTERN`
   + `_TEST_FAILED_COUNT_PATTERN` (pytest format). Semantic check accepts either.

2. **"6 families" dict-key fix**: `_check_semantic` now first checks `"families"`
   key (legacy); if absent, counts top-level `_KNOWN_FAMILY_NAMES` keys.

3. **Contract format support**: `compute()` now reads `sprint_id` or `contract_id`,
   and `required_evidence_categories` or `categories`.

### `src/plugin_examples/evidence_validator.py`

4. **New rule 22: `ecc_contract_computed_and_valid`**: Checks that
   `evidence/evidence-contract-computed.json` exists and shows `closure_valid=true`.
   If ECC was run before final commits (stale) → `closure_valid=false` → rule 22
   FAILS → sprint cannot close → ECC must be re-run after commit.

5. **Total rules**: 21 → 22. `validate_for_storage()` still excludes rule 21
   (self-reference) but includes rule 22. `validate()` runs all 22.

## Combined Gate Behavior

| Scenario | EV outcome | ECC outcome | Combined result |
|----------|------------|-------------|-----------------|
| Both pass | overall_valid=true | closure_valid=true | PASS |
| EV pass, ECC fail | overall_valid=false | closure_valid=false | FAIL (rule 22) |
| EV fail (any rule) | overall_valid=false | closure_valid=true | FAIL |
| EV fail, ECC fail | overall_valid=false | closure_valid=false | FAIL |

## Verification

- Sprint 63 bundle under repaired gate: `overall_valid=false`, failed=1
  (rule 22: `ecc_contract_computed_and_valid` — stale ECC result)
- Sprint 64 bundle: ECC run AFTER all commits → `closure_valid=true` → rule 22 passes
- Tests: 106/106 pass (see `final-gate-test-results.txt`)

## Acceptance

EV and ECC can no longer disagree silently. Combined gate fails if either fails.
Sprint 63 bundle correctly fails under repaired gate (S63-D1 confirmed as defect).
