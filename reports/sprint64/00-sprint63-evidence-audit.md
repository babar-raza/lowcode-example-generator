# Sprint 63 Evidence Audit — Sprint 64 Phase 0

**Audited by:** Sprint 64 independent review
**Date:** 2026-05-22
**Sprint being audited:** Sprint 63 (`sprint63-sprint62-closure-repair-validator-package-evidence-publication-handoff`)

---

## Verdict Downgrade

Sprint 63 is NOT accepted as closed.

**Sprint 63 claimed verdict:** `LOWCODE_README_IO_DRY_RUN_PACKAGES_VERIFIED_PUBLICATION_BLOCKED_BY_APPROVAL`
**Corrected status:** `EVIDENCE_GATE_REPAIR_REQUIRED_NOT_CLOSED`

---

## Blocking Defects Found

### S63-D1 — EvidenceValidator and EvidenceContractComputer Disagree (CRITICAL)

**EvidenceValidator reports:** `overall_valid=true`, 21/21 PASS
**EvidenceContractComputer reports:** `closure_valid=false`, 11 blocking failures

When these two disagree, neither can be trusted. This is the core closure defect.

**Root cause A — Timing:** ECC was computed at `2026-05-22T07:18:19Z` but the final bundle
files were committed at 07:19-07:21. All 7 "MISSING" categories in ECC actually exist now.

**Root cause B — Semantic rule bugs in ECC:**
- `_TEST_ZERO_FAILED_PATTERN` requires literal "0 failed" but pytest omits this when there are no failures. `76 passed in 12.07s` is a passing test run.
- `"6 families"` check looks for `data.get("families", [])` but package-artifact-index.json uses family names as top-level keys.
- `content-audit-deep.json` legitimately lacks `output_format` field (real data gap).

### S63-D2 — Package Artifacts Cover 40/42 Scenarios

`pdf-pdfa-converter` and `pdf-text-extractor` have no dry-run package source files.
Phase 3 documented these as "special cases" but did NOT provide equivalent artifacts.

### S63-D3 — Package Artifacts Include obj/ Files

`reports/sprint63/destination-packages/per-family/` includes generated build artifacts (`obj/` intermediate files). These should not be in publication artifacts.

### S63-D4 — Program.cs Authority Has 3 Mismatches and 2 No-Authority Records

| Scenario | Issue | Root Cause |
|----------|-------|------------|
| cells-text-converter | programcs=`.xlsx` vs authority=`.csv` | Ledger error: authority uses output format as input |
| words-mail-merger | programcs=`.docx` vs authority=`template.docx+data` | Known special case not classified |
| words-report-builder | programcs=`.docx` vs authority=`template.docx+data` | Known special case not classified |
| pdf-html-converter | programcs=`None` | Missing input classification in S62 audit |
| pdf-pdfa-converter | programcs=`None` | No dry-run package (see S63-D2) |

### S63-D5 — README I/O Corrections Not Applied to Dry-Run Packages

Sprint 63 reports 40/42 corrections available but 0/42 applied.
The dry-run package README files still have no I/O section.
The README audit correctly says 0/42 match — but this makes the package NOT publication-ready.

### S63-D6 — PDF Version Drift Unresolved

PDF dry-run packages use Aspose.PDF 26.4.0.
Current intended version is 26.5.0.
Sprint 63 noted this as "non-blocking gap" but it blocks publication readiness.

### S63-D7 — content-audit-deep.json Lacks output_format

The deep audit has 42 records but missing `output_format`, `api_type`, and README status per record.
ECC correctly flags this as SEMANTIC_FAILED.

---

## What Sprint 63 Actually Delivered (Preserved)

| Claim | Status | Detail |
|-------|--------|--------|
| Sprint 62 reclassified | VERIFIED | 6 defects documented, verdict downgraded |
| EvidenceContractComputer built | VERIFIED | 13 tests pass, no PENDING at closure |
| EV two-phase validation | VERIFIED | `validate_for_storage()` eliminates bootstrap contradiction |
| Sprint 62 revalidation fails | VERIFIED | `overall_valid=false`, contradiction detected |
| Dry-run package source files in bundle | PARTIALLY_VERIFIED | 40/42, 2 PDF special cases missing |
| Package authority label corrected | VERIFIED | PROGRAMCS_USAGE_CONFIRMED |
| No unauthorized publication | VERIFIED | Approval gates unset, no push |
| Test suite: 2976/0 | VERIFIED | log present, real pytest output |
| Final clean proof nonzero | VERIFIED | "nothing to commit" captured |
