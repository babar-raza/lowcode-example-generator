# Validator Gap Analysis

**Run ID:** sysqual-20260528-001
**Date:** 2026-05-28

## Gaps Found During Qualification Run

### GAP-001: runner.py dependency resolution missing include_all_tfm_groups
- **Product affected:** pdf
- **Failure type:** DllReflector FileNotFoundException
- **Gap:** runner.py did not match discovery_sweep.py include_all_tfm_groups behavior
- **Fix applied:** Added config option and wired through model/loader/runner
- **Validator coverage:** New invariant added (see invariant-coverage-matrix.json)

### GAP-002: words denominator hash stale-cache false positive
- **Product affected:** words
- **Failure type:** Catalog hash mismatch
- **Gap:** First pilot run used stale cached catalog. Clean run produced correct hash.
- **Fix applied:** Reverted denominator hash to original value; source updated
- **Validator coverage:** Existing hash validation catches this; no new rule needed

## Existing Validator

- Validator has 145 rules (`grep -c "def _rule_" evidence_validator.py` = 145)
- All existing rules remain valid

## New Rules

No new rules required — GAP-001 is a machinery fix; GAP-002 is a false-positive diagnosed by rerunning clean.
