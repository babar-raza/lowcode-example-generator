# Lane I: Publication / README Readiness Report

**Sprint:** LOWCODE-MEGA-TRAIN-005
**Date:** 2026-05-20

## Portfolio Summary

| Family | Published | PR-Ready | Total Runnable | README Status |
|--------|-----------|----------|---------------|---------------|
| Cells | 9 | 0 | 9 | PUBLISHED (version drift) |
| Words | 8 | 0 | 8 | PUBLISHED (version drift) |
| PDF | 5 | 14 | 19 | PUBLISHED (partial) |
| Diagram | 2 | 0 | 2 | PUBLISHED (version drift) |
| Email | 1 | 0 | 1 | PUBLISHED_CURRENT |
| Slides | 3 | 0 | 3 | PUBLISHED_CURRENT |
| **Total** | **28** | **14** | **42** | |

## FormatContract Authority Gate (NEW)

This sprint introduces a **publication gate** that blocks publishing unless:
1. FormatContract exists for the type
2. Generated code validates against the contract
3. Manifest contains contract snapshot (contract_id, contract_hash)

### Gate Status
- **42/42** types have FormatContracts in store
- **Code contract validator** implemented (code_contract_validator.py)
- **Publication gate** implemented (publication_gate.py)
- **Unfreeze criteria:** 2/7 verifiable locally, 5 require test execution

### Unfreeze Criteria
1. All 42 active types have FormatContract in store — MET
2. All components consume FormatContract — MET (planner, codegen, manifest, populator)
3. Contract-vs-system drift matrix has zero critical mismatches — REQUIRES_VERIFICATION
4. Code contract validator passes for all generated examples — REQUIRES_VERIFICATION
5. Stale-map guard tests pass — REQUIRES_VERIFICATION (via test suite)
6. Full test regression passes with no new failures — REQUIRES_VERIFICATION
7. Target repo correction plan documented — REQUIRES_VERIFICATION

## README Audit Status

### Published Families
- Cells: README audit passes, 14692 bytes
- Words: README audit passes, 17901 bytes
- PDF: README partial (5 of 19 types in target repo)
- Diagram: README audit passes
- Email: README audit passes
- Slides: README audit passes

### README Push Blockers
- Cells, Words, Diagram: version drift README push blocked by APPROVE_README_PUSH
- PDF: README complete locally but 14 examples not yet in target repo

## Dry-Run Verification
- All family packages exist in workspace/pr-dry-run/
- README renderer produces valid output for all 6 families
- Auditor runs 15 checks per README (format-claim, snippet, xlsx guard, etc.)

## New Contract-Level README Cross-Check
- readme_auditor.py now has `contract_format_mismatches` field (V9)
- Will cross-check README format claims against FormatContract authority
- Not yet populated — requires next publication cycle

## Verdict
**PUBLICATION_FROZEN** — FormatContract authority layer integrated but publication unfreeze requires test verification. No push/publish/merge actions taken.
