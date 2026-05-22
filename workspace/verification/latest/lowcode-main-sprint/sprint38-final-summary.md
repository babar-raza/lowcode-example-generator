# Sprint 38 — Final Summary

**Sprint:** 38 (Main Sprint — Multi-Lane Governed Execution)
**Date:** 2026-05-19
**Branch:** main
**HEAD at start:** a474b97
**Previous sprint:** 37 (SPRINT37_APPROVAL_BLOCKED_PORTFOLIO_ADVANCED_VERSION_DRIFT_PILOTED)

## Verdict

**SPRINT38_STATE_RECONCILIATION_COMPLETE_ALL_FAMILIES_CONSISTENT**

## What Was Fixed

### Denominator Reconciliation (4 fixes)

1. **Email denominator** (`pipeline/configs/denominators/email.json`):
   - Fixed stale discovery-only metadata
   - `allowed_pilot_types`: `[]` -> `["Converter"]`
   - `runnable_scenarios`: `0` -> `1`
   - `runnable_scenario_ids`: `[]` -> `["email-converter"]`
   - `coverage_pct_of_workflow_root`: `0.0` -> `100.0`
   - `excluded_count`: `3` -> `2`
   - `last_verified_at`: updated to 2026-05-19

2. **Slides denominator** (`pipeline/configs/denominators/slides.json`):
   - Fixed stale discovery-only metadata
   - `allowed_pilot_types`: `[]` -> `["Compress", "Convert", "Merger"]`
   - `runnable_scenarios`: `0` -> `3`
   - `runnable_scenario_ids`: `[]` -> `["slides-compress", "slides-convert", "slides-merger"]`
   - `coverage_pct_of_workflow_root`: `0.0` -> `100.0`
   - `excluded_count`: `5` -> `2`
   - `last_verified_at`: updated to 2026-05-19

3. **Words denominator** (`pipeline/configs/denominators/words.json`):
   - Added missing `"words-report-builder"` to `runnable_scenario_ids`
   - Now 8 entries matching `runnable_scenarios=8` and `allowed_pilot_count=8`

4. **PDF denominator** (`pipeline/configs/denominators/pdf.json`):
   - Corrected `coverage_pct_of_pilot_allowed`: `27.78%` (5/18) -> `26.32%` (5/19)
   - Updated `coverage_pct_detail` to use 19 denominator
   - Added `pr_packages_without_contracts_count=5` tracking (PR#8-PR#10 examples)
   - `last_verified_at`: updated to 2026-05-19

## What Was NOT Fixed

- **PDF PR merge**: 6 PRs (#5-#10) still require human merge (APPROVE_MERGE_PR not set)
- **PDF live publication**: APPROVE_LIVE_PR not set
- **Cells/Diagram denominator version update**: Drift piloted PASS but source_version not updated (requires controlled rerun)
- **PDF pipeline contracts**: 5 examples (security, form-flattener, form-editor, form-exporter, signature) lack pipeline/contracts/pdf/ entries
- **FormImporter**: Still blocked by Aspose.PDF 26.5.0 bug
- **OCR/PSD**: Still blocked by missing NuGet dependencies

## Publication Status

No new publications or PRs this sprint. This was a reconciliation sprint.

## Current State by Family

| Family | Published | Status | Coverage | Drift |
|--------|-----------|--------|----------|-------|
| cells | 9 | FAMILY_COMPLETE | 100% | 26.4.0->26.5.1 (MAJOR, pilot PASS) |
| words | 8 | PILOT_COMPLETE | 100% of pilot | CURRENT |
| pdf | 5 (+14 pending) | PARTIAL_CANARY | 26.32% of pilot (100% after PR merge) | CURRENT |
| diagram | 2 | PILOT_COMPLETE | 100% | 26.4.0->26.5.0 (MAJOR, pilot PASS) |
| email | 1 | PILOT_COMPLETE | 100% | CURRENT |
| slides | 3 | PILOT_COMPLETE | 100% | CURRENT |

## Tests

- **1876/1876 PASS** (0 failed)
- Source compile: PASS
- Evidence contract: V7 (69 categories) — Sprint 37 bundle validated

## Remaining Blockers

1. PDF PR merge (#5-#10): Requires APPROVE_MERGE_PR
2. PDF live publication: Requires APPROVE_LIVE_PR
3. FormImporter: Blocked by Aspose.PDF 26.5.0 bug (TC-PDF-FORMIMPORTER-RETEST)
4. Cells/Diagram: Version drift requires controlled denominator update
5. Words Processor: PERMANENTLY_BLOCKED (no public constructor)
6. OCR: Blocked (Aspose.AI.LLM missing from NuGet)
7. PSD: Blocked (Aspose.JavaAttributes missing from NuGet)

## Next Sprint Recommendations

1. **Create PDF pipeline contracts** for PR#8-PR#10 examples (security, form-flattener, form-editor, form-exporter, signature)
2. **Update Cells denominator** to 26.5.1 (pilot PASS, safe)
3. **Update Diagram denominator** to 26.5.0 (pilot PASS, safe)
4. **PDF PR merge** when operator provides APPROVE_MERGE_PR
5. **FormImporter retest** when Aspose.PDF > 26.5.0 available
6. **Monitor OCR/PSD** for dependency resolution

## Evidence Artifacts

All sprint artifacts in: `workspace/verification/latest/lowcode-main-sprint/`

- execution-ledger.md
- lane-ownership.md
- overlap-control.md
- evidence-intake-report.md
- evidence-intake-summary.json
- family-state-matrix.md
- family-state-matrix.json
- pdf-publication-readiness.md
- pdf-publication-readiness.json
- readme-cumulative-audit.md
- readme-cumulative-audit.json
- version-drift-report.md
- version-drift-report.json
- target-repo-health-report.md
- test-summary.md
- next-generation-candidates.md
- sprint38-final-summary.md (this file)
