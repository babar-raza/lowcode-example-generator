# Lane F — Test Summary

**Date:** 2026-05-19
**Result:** 1876/1876 PASS (0 failed)

## Test Execution Timeline

1. **Baseline (pre-fix):** 1876/1876 PASS
2. **After denominator fixes (first run):** 1873 passed, 3 failed
   - Failures: test_pdf_pilot_active_pipeline_in_queue, test_active_pipeline_entries_match_denominator, test_pdf_contract_count_matches_denominator_published_plus_pipeline
   - Root cause: PDF pr_dry_run_ready_count increased to 14 but only 14 pipeline contracts exist (5 published + 9 dry-run = 14 total, not 5+14=19)
   - Fix: Reverted pr_dry_run_ready_count to 9, added separate pr_packages_without_contracts_count=5
3. **After fix:** 3/3 previously-failing tests PASS
4. **Final full suite:** 1876/1876 PASS

## Targeted Test Modules

| Module | Tests | Result |
|--------|-------|--------|
| test_release_status.py | PASS | All pass |
| test_evidence_contract.py | PASS | All pass |
| test_target_repo_health.py | PASS | All pass |
| test_version_drift_checker.py | PASS | All pass |
| test_completion_queue.py | PASS | All pass (after fix) |
| test_scenario_contracts.py | PASS | All pass (after fix) |

## Evidence Contract Validation

- Sprint 37 bundle: V7 BUNDLE_CONTRACT_PASSED 69/69
- Current contract version: StrictEvidenceContractV7 (69 categories)
- No new contract version needed for Sprint 38 (reconciliation sprint, no new bundle format)

## Source Compile

- `python -m compileall src`: PASS (clean)
