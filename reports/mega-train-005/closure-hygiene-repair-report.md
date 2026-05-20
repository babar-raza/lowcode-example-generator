# Lane A: Closure Hygiene Repair Report

**Sprint:** LOWCODE-MEGA-TRAIN-005
**Date:** 2026-05-20
**Verdict:** CLOSURE_HYGIENE_REPAIRED

## Prior Caveats (from cross-family-pipeline-matrix bundle)

### Caveat 1: release-status.json dirty
- **Status:** RESOLVED (timestamp-only)
- **Evidence:** `git diff workspace/verification/latest/release-status.json` shows only `generated_at` timestamp change (2026-05-19 -> 2026-05-20)
- **Classification:** GENERATED_EVIDENCE — pipeline refresh, not content change

### Caveat 2: 7 generated-evidence dirty files
- **Status:** RESOLVED (all timestamp-only)
- **Evidence:** All 7 files in workspace/verification/latest/ show only date/timestamp changes
- **Files:** cells-readme-backfill-simulation.json, cells-root-readme-audit.json, cells-root-readme-render-result.json, release-status.json, words-readme-backfill-simulation.json, words-root-readme-audit.json, words-root-readme-render-result.json
- **Classification:** GENERATED_EVIDENCE — safe to stage with source changes

### Caveat 3: unknown_dirty_count=1 for scripts/cross_family_pipeline_matrix.py
- **Status:** RESOLVED (stale pre-commit metadata)
- **Evidence:** `git log --oneline scripts/cross_family_pipeline_matrix.py` shows committed in f94cb97
- **Explanation:** The file was dirty at pre-commit time in the prior bundle's pre-commit snapshot, but was committed by the prior bundle. The action board metadata was not updated post-commit.

### Caveat 4: sha256-manifest excludes itself and evidence-contract-validation.json
- **Status:** DOCUMENTED (intentional policy)
- **Explanation:** The sha256-manifest.txt cannot include its own hash (self-referential). evidence-contract-validation.json is generated after the manifest and verifies against it. Both exclusions are intentional and documented here as explicit policy.
- **Policy:** sha256-manifest.txt ALWAYS excludes:
  1. Itself (self-referential)
  2. evidence-contract-validation.json (generated after manifest, verifies against it)

## Additional Repair: Test Failure Fix

- **File:** tests/unit/test_code_quality_sprint.py
- **Issue:** `test_input_format_map_text_converter` called `_infer_input_format("TextConverter", ".xlsx")` without `family="cells"` argument, so FormatContract lookup was skipped and legacy map returned `.csv` instead of expected `.xlsx`
- **Fix:** Added `family="cells"` to both `test_input_format_map_text_converter` and `test_input_format_map_html_converter` calls to activate FormatContract authority path
- **Verification:** 4/4 tests in class pass after fix

## New Dirty State Classification (This Sprint)

### Source code changes (10 files)
All part of FormatAuthority/FormatContract feature integration:
- 7 modified source files: planner, codegen, packet_builder, project_generator, populator, runner, readme_auditor
- 3 new source files: format_authority/__init__.py, contracts.py, store.py

### Gate/validator additions (2 files)
- gates/code_contract_validator.py — validates Program.cs against FormatContract
- gates/publication_gate.py — blocks publication without FormatContract authority

### Test changes (6 files)
- 3 modified: test_code_quality_sprint.py, test_format_capability.py, test_format_map_completeness.py
- 3 new: test_code_contract_validator.py, test_format_authority_no_stale_maps.py, test_format_authority_store.py

### Generated evidence (7 files)
- Timestamp-only refreshes in workspace/verification/latest/

## FormatContract Store Verification

- **Authority file:** workspace/verification/lowcode-api-format-authority-20260519-153439/reports/api-backed-format-contracts.json
- **Contracts loaded:** 42/42
- **All 6 families covered:** cells(9), words(8), pdf(19), diagram(2), email(1), slides(3)
- **Validation:** All contracts pass FormatContract.validate()
