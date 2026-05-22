# EV Rule Change Log — Sprint 68

Date: 2026-05-22
Sprint: sprint68

## Summary

| Metric | Before (Sprint 67) | After (Sprint 68) |
|--------|-------------------|--------------------|
| Total rules | 52 | 57 |
| validate_for_storage rules | 51 | 56 |
| New rules added | — | 5 |

## New Rules (53-57)

| Rule ID | Rule Method | Purpose |
|---------|-------------|---------|
| 53 | `pdf_root_readme_complete` | S67-D1: PDF root README must have >=19 rows in examples table |
| 54 | `splitter_cardinality_reconciled` | S67-D2: splitter-resolution.md must exist in legacy-reconciliation/ |
| 55 | `canonical_content_audit_no_stale_pdf_version` | S67-D3: sprint content audit must have no PDF 26.4.0 records |
| 56 | `pdf_version_proof_chain_present` | S67-D4: version/pdf-version-proof-chain.md must exist |
| 57 | `all_family_cardinality_display_validated` | S67-D5: words-root-readme.md must have ×N/2× cardinality markers |

## ECC Contract Update

Sprint 68 ECC contract: 46 categories (EC01-EC46)
Sprint 67 ECC contract: 57 categories

Note: Sprint 68 ECC has fewer categories than Sprint 67 because sprint68 focuses on
targeted defect repair (5 phases vs 11 phases in sprint67). The ECC is scoped to
sprint68 artifacts only.

## Test Coverage

84 unit tests in test_evidence_validator.py — all passing.
5 unit tests in test_pipeline_evidence_gate.py — all passing.

## Sprint 67 Revalidation

Sprint 67 bundle under Sprint 68 rules: overall_valid=false
Expected failures:
- pdf_root_readme_complete: FAIL (3/19 rows)
- splitter_cardinality_reconciled: FAIL (no splitter-resolution.md in sprint67)
- canonical_content_audit_no_stale_pdf_version: FAIL (content-audit-sprint67.json has no legacy-reconciliation/splitter-resolution.md)
- pdf_version_proof_chain_present: FAIL (no pdf-version-proof-chain.md in sprint67)
- all_family_cardinality_display_validated: PASS (words-root-readme.md has xN markers)
