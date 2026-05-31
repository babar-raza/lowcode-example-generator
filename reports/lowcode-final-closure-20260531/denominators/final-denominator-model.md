# Final Denominator Model — lowcode-final-closure-20260531
Generated: 2026-05-31T13:33:10

## Denominator Definitions

| Denominator | Count | Definition |
|---|---|---|
| generated | 42 | Examples from canonical pass4+words-repair generation runs |
| build_valid | 42 | Examples that built successfully (all 42) |
| run_valid | 42 | Examples that ran with exit_code=0 (all 42) |
| semantic_valid | 42 | Examples with valid output or result-object proof (all 42) |
| package_included | 42 | Examples included in package (all 42) |
| publication_candidates | 42 | Examples eligible for live PR (all 42) |
| live_pr_candidates | 42 | Examples in live PR queue (all 42, gated by approval) |

## Per-Family Counts (CORRECTED)

| Family | Count | Source Run |
|---|---|---|
| cells | 9 | pass4-gen-cells-20260530 |
| diagram | 2 | pass4-gen-diagram-20260530 |
| email | 1 | pass4-gen-email-20260530 |
| pdf | 19 | pass4-gen-pdf-20260530 |
| slides | 3 | pass4-gen-slides-20260530 |
| words | 8 | pilot-words-repair-20260530 |
| **TOTAL** | **42** | |

## Key Corrections from Previous Sprint
1. email has 1 canonical example (not 7 as previously claimed)
2. diagram has 2 canonical examples (not 7 as previously claimed)
3. slides has 3 canonical examples (not 5 as previously claimed)
4. pdf has 19 canonical examples (not 9)
5. words has 8 canonical examples (not 7 — mail-merger is included and working)
6. PR candidates = 42 (not 41 — mail-merger is self-contained, no fixture required)

## words-mail-merger Decision
words-mail-merger is INCLUDED as a PR candidate.
The example creates a template.docx programmatically using DocumentBuilder + MERGEFIELD.
No external fixture file required. Confirmed: builds, runs, outputs "Mail merge succeeded: output.docx".

## pdf-timestamp Decision
pdf-timestamp is NOT in the canonical 42.
It is a legacy example in workspace/pr-dry-run/pdf-controlled-pilot-pr11 from a prior sprint.
source_run=null, EXTERNAL_TSA_DEPENDENCY.
It is not counted in any denominator for this sprint.
If TSA becomes available, it can be added as example #43.
