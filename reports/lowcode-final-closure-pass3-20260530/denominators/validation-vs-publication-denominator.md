# Validation vs Publication Denominator — LANE 8

**Sprint**: lowcode-final-closure-pass3-20260530

## The 42 vs 41 Truth Model

The pipeline produces **42 validated examples** across 6 families, but only **41 PR candidates**.
This is a deliberate, documented split.

| Denominator | Count | Source |
|-------------|-------|--------|
| Validated (build + run pass) | **42** | Lane 4 raw logs (42/42 PASS) |
| PR candidates (publication eligible) | **41** | workspace/verification/latest/pr-candidate-manifest.json |
| Excluded | **1** | words-comparer (EXAMPLE_BLOCKED_CODE_CONTRACT_FAILED) |

## Per-Family Breakdown

| Family | Validated | PR Candidates | Excluded | Notes |
|--------|-----------|--------------|----------|-------|
| cells | 9 | 9 | 0 | All pass |
| words | 8 | 7 | 1 | words-comparer excluded |
| pdf | 19 | 19 | 0 | All pass |
| diagram | 2 | 2 | 0 | All pass (post DEF-004/005 fix) |
| slides | 3 | 3 | 0 | All pass (post DEF-009 fix) |
| email | 1 | 1 | 0 | Passes |
| **TOTAL** | **42** | **41** | **1** | |

## The Excluded Example: words-comparer

| Field | Value |
|-------|-------|
| Scenario ID | words-comparer |
| Validated? | **YES** — build PASS, run PASS (8/8 words) |
| PR candidate? | **NO** — EXAMPLE_BLOCKED_CODE_CONTRACT_FAILED |
| Blocked reason | Code contract validation failed (blocking mode) |
| Contract | same_format_converter_guard advisory contract |
| What it does | Converts .docx → .docx (same format in, same format out) |
| Why excluded | The contract detects same-format-in-same-format-out as an advisory violation — the example would compare rather than convert formats, which is not the intended pattern for the LowCode SDK |

Source: `workspace/verification/latest/families/words/pr-candidate-manifest.json`

## Evidence of 42 Validated

The validation_results.json for each family confirms 42/42 PASS:
- cells: 9/9 (workspace/verification/latest/families/cells/validation-results.json)
- words: 8/8 (includes words-comparer — it builds and runs, just blocked from PR)
- pdf: 19/19
- diagram: 2/2
- slides: 3/3
- email: 1/1

Lane 4 raw logs confirm this independently: `e2e-raw/e2e-aggregate.json` shows 42/42 PASS.

## Evidence of 41 PR Candidates

`workspace/verification/latest/pr-candidate-manifest.json`:
```
"included_manifest_candidate_count": 41
"excluded_examples": [] (words-comparer counted in words family manifest, not aggregate)
```

`workspace/verification/latest/families/words/pr-candidate-manifest.json`:
```
"excluded_examples": [{"scenario_id": "words-comparer", ...}]
"exclusion_reasons": {"EXAMPLE_BLOCKED_CODE_CONTRACT_FAILED": ["words-comparer"]}
```

## Conclusion

- **42 validated** = 42 examples that pass dotnet restore + build + run
- **41 PR candidates** = 42 minus 1 excluded (words-comparer, contract-blocked)
- This is NOT a defect — it reflects correct contract enforcement
- words-comparer CAN be published if the advisory contract is waived, but the
  current sprint does not waive it
- The sprint claims 42/42 validation and 41 PR candidates — both are correct
