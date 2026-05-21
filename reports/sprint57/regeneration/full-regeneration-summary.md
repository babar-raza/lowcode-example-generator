# Sprint 57 Full Regeneration Summary

**Run Date:** 2026-05-21
**Mode:** `--promote-latest` (from-scratch regeneration)
**Denominator:** 42 runnable types across 6 families

## Results

| Family | Scenarios | Generated | Built | Run Passed | Gate Verdict |
|--------|-----------|-----------|-------|-----------|-------------|
| cells | 9 | 9 | 9 | 9 | PR_DRY_RUN_READY |
| words | 8 | 8 | 8 | 8 | PARTIAL_PR_DRY_RUN_READY |
| pdf | 19 | 18 | 18 | 18 | PR_DRY_RUN_READY |
| diagram | 2 | 2 | 2 | 2 | PR_DRY_RUN_READY |
| email | 1 | 1 | 1 | 1 | PR_DRY_RUN_READY |
| slides | 3 | 3 | 3 | 3 | PR_DRY_RUN_READY |
| **TOTAL** | **42** | **41** | **41** | **41** | **41/42 PASS** |

## Overall Verdict

`SPRINT57_REGENERATION_41_OF_42_PASS`

- 41/42 examples: generated, built, runtime passed
- 5 examples required build-repair (auto-repaired, still passed)
- 1 example blocked at generation: `pdf-pdf-aconverter`

## Notes

- **Build repairs**: `pdf-table-generator`, `pdf-text-extractor`, `pdf-tiff`, `pdf-toc-generator`, `pdf-xls-converter`, `slides-convert`, `slides-merger` — all repaired successfully on first attempt
- **words PARTIAL**: 4 Wave 1 published (PR_DRY_RUN_READY); 4 Wave 2 at BACKLOGGED/BLOCKED status. PARTIAL gate is expected behavior.
- **pdf-pdf-aconverter**: Generation failed due to `TextFragment` missing `using Aspose.Pdf.Text;` directive. Post-repair validation blocked. Backlogged at `high` priority. Known LLM constraint issue.

## Evidence

- Lifecycle records: `workspace/verification/latest/families/{family}/example-lifecycle-records.json`
- Gate results: `workspace/verification/latest/families/{family}/gate-results.json`
- Full ledger: `reports/sprint57/regeneration/full-regeneration-ledger.json`
