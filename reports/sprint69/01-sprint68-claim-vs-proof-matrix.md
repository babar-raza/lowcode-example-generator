# Sprint 68 Claim vs Proof Matrix

Date: 2026-05-22
Sprint: sprint69

## Classification Key

- VERIFIED: Claim is supported by current file evidence
- PARTIALLY_VERIFIED: Claim is true in part but incomplete or ambiguous
- CONTRADICTED: File evidence directly contradicts the claim
- INVALID_CLOSURE: Claim was accepted as closure but does not meet closure criteria
- REPAIRED_IN_SPRINT69: Defect from sprint68 being repaired in sprint69

| # | Sprint 68 Claim | Evidence File(s) | Classification | Sprint 69 Task |
|---|-----------------|-----------------|---------------|----------------|
| C01 | PDF root README 19/19 rows | root-readme/per-family/pdf-root-readme.md | VERIFIED | — |
| C02 | 42/42 handoff examples present with Program.cs/README/csproj | handoff/per-family/ (all 42) | VERIFIED | — |
| C03 | 6/6 root README artifacts exist | root-readme/per-family/ (6 files) | PARTIALLY_VERIFIED | Phase 2: integrate into handoff index |
| C04 | Final verdict SPRINT68_COMPLETE is accurate | final-verdict.md | INVALID_CLOSURE | Phase 0/10: fix verdict to allowed precise form |
| C05 | Publication truth matrix is current Sprint 68 state | publication/publication-truth-matrix-final.json | CONTRADICTED | Phase 4: rebuild with sprint69 paths |
| C06 | No stale sprint path leakage in publication matrix | publication/publication-truth-matrix-final.json | CONTRADICTED | Phase 4: all 42 records use sprint67 paths |
| C07 | One canonical final destination audit exists | destination/ (two files: final.json + sprint68.json) | CONTRADICTED | Phase 1: retire stale, rename sprint68 to final |
| C08 | Words/PDF/Diagram handoff indexes match package files | handoff-index.json vs Directory.Packages.props | CONTRADICTED | Phase 3: fix 3 mismatches (26.4.0 → 26.5.0) |
| C09 | Root README artifacts are tracked in handoff package | handoff/per-family/*/handoff-index.json | PARTIALLY_VERIFIED | Phase 2: add root_readme field to handoff index |
| C10 | Legacy reconciliation is consolidated | legacy-plan-reconciliation/ + legacy-reconciliation/ | PARTIALLY_VERIFIED | Phase 5: produce one final authority report |
| C11 | EV/ECC rule coverage is adequate | evidence/ev-rule-change-log.md | PARTIALLY_VERIFIED | Phase 7: add 10 new rules |
| C12 | Remote README I/O status is 0/42 | remote/remote-readme-io-audit.json | VERIFIED | — |
| C13 | Publication is correctly approval-blocked | publication/live-publication-check.md | VERIFIED | — |
| C14 | Splitter cardinality SINGLE_OUTPUT_VALID | legacy-reconciliation/splitter-resolution.md | VERIFIED | — |
| C15 | PDF version 26.5.0 proven via handoff DPP | version/pdf-version-proof-chain.md | VERIFIED | — |
| C16 | EV 57/57 PASS | evidence/sprint68-final-validation-result.json | PARTIALLY_VERIFIED | Passes but misses 8 defects — needs hardening |
| C17 | ECC 46/46 PRESENT | evidence/evidence-contract-computed.json | PARTIALLY_VERIFIED | Passes but contract does not cover defect areas |
| C18 | No bin/obj clutter in handoff | handoff/per-family/ tree | VERIFIED | — |
| C19 | Tests 3025 passed, 0 failed | logs/test-run.log | VERIFIED | — |
| C20 | Working tree clean at sprint close | git/final-clean-proof.txt | VERIFIED | — |

## Contradicted Claim Detail

### C04 — INVALID_CLOSURE
Sprint 68 final verdict: `SPRINT68_COMPLETE`
Allowed verdicts list (sprint69 rules): `LOWCODE_PREPUBLICATION_HANDOFF_READY_APPROVAL_BLOCKED`
Remote READMEs have 0/42 I/O sections. Publication is blocked. "COMPLETE" is false.

### C05+C06 — CONTRADICTED
All 42 `dry_run_package_path` values: `reports\sprint67\destination-packages\per-family\...`
Sprint 68 handoff lives at: `reports/sprint68/handoff/per-family/...`
The sprint68 publication truth matrix was never updated to use sprint68 paths.

### C07 — CONTRADICTED
`content-audit-final.json` (stale sprint67 data) co-exists with `content-audit-sprint68.json`.
The unification proof claims `content-audit-final.json` is "retired" but the file is still present.
EV rule `canonical_content_audit_no_stale_pdf_version` only checked PDF version, not path currency.

### C08 — CONTRADICTED
| Family | handoff-index nuget_version | DPP Version | Result |
|--------|---------------------------|-------------|--------|
| words | 26.4.0 | 26.5.0 | MISMATCH |
| pdf | 26.4.0 | 26.5.0 | MISMATCH |
| diagram | 26.4.0 | 26.5.0 | MISMATCH |
| cells | 26.5.1 | 26.5.1 | OK |
| email | 26.4.0 | 26.4.0 | OK |
| slides | 26.5.0 | 26.5.0 | OK |
