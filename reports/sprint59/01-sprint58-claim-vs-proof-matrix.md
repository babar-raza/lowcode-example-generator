# Sprint 58 Claim vs Proof Matrix — Sprint 59 Phase 0

**Date:** 2026-05-21
**Purpose:** Tabular classification of all Sprint 58 final verdict claims.

---

## Matrix

| # | Sprint 58 Claim | Proof Available | Classification | Defect |
|---|-----------------|----------------|---------------|--------|
| 1 | Sprint 57 evidence audit completed (D01–D11 classified) | 3 audit files present and substantive | VERIFIED | — |
| 2 | PdfAConverter fixed: `using Aspose.Pdf.Text;` added to pdf.yml | File exists, test passes | VERIFIED | — |
| 3 | 3 regression tests added for PdfAConverter constraint | tests/unit/test_llm_generation.py modified; 2826 tests pass | VERIFIED | SD04 (no source diff) |
| 4 | DLL reflection ledger built from actual api-catalog.json | reflection-ledger.json present; catalog_file paths referenced | VERIFIED | — |
| 5 | I/O authority matrix has zero contract_only entries | io-authority-evidence-matrix.json: authority_source all "reflection" or "reflection+xml_doc" | VERIFIED (claim) / CONTRADICTED (implication) | SD01 |
| 6 | I/O authority matrix covers 42 types | 42 entries present | VERIFIED | — |
| 7 | All 42 input formats resolved | `input_format: "unknown"` for ALL 42 entries | CONTRADICTED | SD01 |
| 8 | Consistency scan: ALL_PASS_WITH_NAMING_NOTES | consistency-scan-report.json present | VERIFIED | — |
| 9 | 42/42 examples generated | 42 per-example files, all generation_status=passed | VERIFIED | — |
| 10 | 42/42 examples built | full-regeneration-ledger total_built=35; 7 records show build_status="repaired" | CONTRADICTED | SD02 |
| 11 | 42/42 runtime passed | per-example records: all run_status=passed | VERIFIED | — |
| 12 | Per-example directory: 42 JSON files | 42 files present | VERIFIED | — |
| 13 | Per-example records contain full field set | Only 15 fields per record; ~20 required fields missing | CONTRADICTED | SD05 |
| 14 | Destination audit: 42/42 FULLY_VERIFIED | Counts and versions verified | PARTIALLY_VERIFIED | SD06 |
| 15 | Destination Program.cs content verified | No Program.cs content fetched or compared | CONTRADICTED | SD06 |
| 16 | Destination README content verified | 15/42 sampled only | PARTIALLY_VERIFIED | SD07 |
| 17 | README audit: SAMPLED_AUDIT_PASSED | 15 examples checked; 42 is true denominator | PARTIALLY_VERIFIED | SD07 |
| 18 | delete_branch_after_merge() implemented | Implementation present in github_pr_merger.py | VERIFIED | SD04, SD08 |
| 19 | 7 branch auto-delete tests pass | 2826 tests pass; 7 TestBranchAutoDelete cases confirmed | VERIFIED | SD04 |
| 20 | Source diffs included in bundle | No source diffs in bundle-manifest.json file list | CONTRADICTED | SD04 |
| 21 | Hygiene: root clean at Sprint 58 start and end | hygiene audit files present | VERIFIED | — |
| 22 | 9 Lane J process documents created | 10 files present in lane-J/ (README + 9 docs) | VERIFIED | — |
| 23 | Full test suite: 2826 passed, 0 failed | test-run.log present; output confirms count | VERIFIED | — |
| 24 | Git status proves committed clean state | git-status.txt shows dirty tree: source files unstaged, workspace/latest files unstaged, reports/sprint58/ untracked | CONTRADICTED | SD03 |
| 25 | api-catalog.json evidence included in bundle | catalog_file paths reference workspace/runs/… but those files are NOT in the 76-file bundle | CONTRADICTED | SD04 |
| 26 | Bundle contains ≥25 files | 76 files in manifest | VERIFIED | — |
| 27 | Overall verdict: LOWCODE_SPRINT58_CLOSURE_REPAIR_42_42_REGENERATION_PACKAGE_AUTHORITY_PROVEN | 8 blocking defects remain | INVALID_CLOSURE | All above |

---

## Summary

| Classification | Count |
|---------------|-------|
| VERIFIED | 13 |
| PARTIALLY_VERIFIED | 3 |
| CONTRADICTED | 8 |
| INVALID_CLOSURE | 1 |

**Sprint 58 final verdict: INVALID_CLOSURE**

Corrected status: `EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED`
