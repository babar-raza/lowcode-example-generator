# Sprint 64 TODO — EV/ECC Alignment, 42/42 Packages, PDF Drift, README Readiness

**Sprint:** 64
**Sprint ID:** sprint64-ev-ecc-alignment-42-42-packages-pdf-drift-readme-publication-readiness
**Date:** 2026-05-22

---

## Phase Checklist

### Phase 0 — Reopen Sprint 63 and Correct State
- [x] Sprint 63 evidence bundle audited (7 blocking defects found)
- [x] Sprint 63 verdict downgraded to EVIDENCE_GATE_REPAIR_REQUIRED_NOT_CLOSED
- [x] 14 claims classified
- [x] 00-sprint63-evidence-audit.md created
- [x] 01-sprint63-claim-vs-proof-matrix.md created
- [x] 02-corrected-sprint63-state.md created
- [x] commands.log created
- [x] todo.md created
- [x] evidence-contract.json created

**Acceptance:** Sprint 63 not closed; corrected baseline established.

---

### Phase 1 — Fix EV+ECC Final Gate Alignment
- [x] Diagnose EV/ECC disagreement root causes documented
- [x] Fix ECC timing: computed AFTER all files exist
- [x] Fix ECC pytest "0 failed" detection (no failures = passing)
- [x] Fix ECC "6 families" check for dict-keyed index
- [x] Add EV rule: fails if computed ECC contract has blocking_failures > 0
- [x] Add EV rule: fails if ECC computed result is stale or missing
- [x] Tests: validator pass + contract fail => final fail
- [x] Tests: contract pass + validator fail => final fail
- [x] Tests: both pass => final pass
- [x] Tests: wrong root path => failure
- [x] final-gate-alignment.md
- [x] final-gate-source-proof.patch
- [x] final-gate-test-results.txt
- [x] sprint63-revalidation-result.json (must fail under repaired gate)
- [x] sprint64-final-validation-result.json (must pass under repaired gate)

**Acceptance:** EV and ECC can no longer disagree silently. Combined gate fails if either fails.

---

### Phase 2 — Repair ECC Semantic Rules
- [x] Fix pytest "0 failed" semantic: N passed with no failures = PASS
- [x] Fix package-artifact-index.json families check (dict keys, not array)
- [x] Fix deep audit semantic to handle output_format or output_kind
- [x] Add tests for all semantic validators
- [x] semantic-rule-repair.md
- [x] semantic-rule-source-proof.patch
- [x] semantic-rule-test-results.txt

**Acceptance:** No valid evidence fails semantic validation due to brittle string matching.

---

### Phase 3 — Clean and Complete 42/42 Package Artifacts
- [x] Rebuild package artifact extraction — exclude obj/, bin/, .vs/
- [x] Include only: Program.cs, README.md, .csproj, .props, root README, PR metadata
- [x] Resolve pdf-pdfa-converter: special-case artifact with source proof
- [x] Resolve pdf-text-extractor: special-case artifact with source proof
- [x] destination-packages/package-artifact-index.json (42/42)
- [x] destination-packages/package-source-manifest.json
- [x] destination-packages/package-hashes.json
- [x] destination-packages/package-cleanliness-audit.md
- [x] destination-packages/per-family/ (clean, no obj/bin)
- [x] destination-packages/special-cases/ (pdf-pdfa-converter, pdf-text-extractor)

**Acceptance:** 42/42 scenarios represented by clean artifacts or explicit special cases.

---

### Phase 4 — Close Program.cs vs Authority Gaps
- [x] cells-text-converter: verify input=.xlsx is correct (authority ledger bug?)
- [x] words-mail-merger: classify as known-special-case, document
- [x] words-report-builder: classify as known-special-case, document
- [x] pdf-html-converter: find Program.cs, classify input format
- [x] pdf-pdfa-converter: resolve via special-case artifact (Phase 3)
- [x] programcs-authority-gap-analysis.md
- [x] programcs-vs-authority-final.json (42/42 classified)
- [x] programcs-authority-test-results.txt

**Acceptance:** 42/42 records classified. No unexplained mismatch.

---

### Phase 5 — Apply README I/O Corrections to Dry-Run Packages
- [x] Apply corrections to 42/42 dry-run package READMEs
- [x] Handle special cases (mail-merger, report-builder, email-converter, pdfa, text-extractor)
- [x] Re-run README audit on corrected packages
- [x] readme-correction-application-ledger.json
- [x] example-readme-io-audit-after-application.json (42/42 with I/O section)
- [x] root-readme-audit-after-application.json
- [x] readme-diff-summary.md

**Acceptance:** Corrected dry-run packages show 42/42 I/O documented.

---

### Phase 6 — Repair PDF Version Drift
- [x] Verify intended PDF version from repo config
- [x] Regenerate PDF packages with Aspose.PDF 26.5.0
- [x] Rebuild and retest PDF examples
- [x] Rerun README and Program.cs audits for PDF
- [x] pdf-version-drift-resolution.md
- [x] pdf-regeneration-test-results.txt
- [x] version-policy.json

**Acceptance:** PDF version drift fixed or policy-classified. No unresolved drift at publication.

---

### Phase 7 — Final Publication Readiness
- [x] Check approval gates without printing secrets
- [x] Document gate status
- [x] live-approval-check.md
- [x] publication-readiness-result.json
- [x] live-publication-result.json
- [x] branch-delete-result.json

**Acceptance:** No unauthorized remote mutation.

---

### Phase 8 — Tests and Command Logs
- [x] Full unit suite (0 failed)
- [x] Combined gate tests
- [x] ECC semantic rule tests
- [x] Package cleanliness tests
- [x] Program.cs authority gap tests
- [x] README correction application tests
- [x] PDF version drift tests
- [x] lanes/lane-I/test-run.log
- [x] lanes/lane-I/git-status.txt

**Acceptance:** All tests logged; no failures uncaptured.

---

### Phase 9 — Final Evidence Bundle
- [x] Run ECC on Sprint 64 bundle (all files present)
- [x] Run EV Phase A (validate_for_storage)
- [x] Store Phase A result
- [x] Run EV Phase B (all rules including ECC-alignment rule)
- [x] bundle-manifest.json
- [x] final-verdict.md
- [x] sprint-state.json
- [x] git/final-clean-proof.txt (AFTER commit)
- [x] evidence-contract.json 100% PRESENT
- [x] Final commit

**Acceptance:** EV and ECC both pass. Combined gate passes. Verdict truthful.

---

## Sprint 64 Closure Conditions

1. EV and ECC agree (both pass or both fail with same root)
2. 42/42 package artifacts (clean, no obj/bin)
3. 42/42 README I/O documented in dry-run packages
4. Program.cs authority: 42/42 classified (no unexplained mismatch)
5. PDF version drift resolved or explicitly policy-classified
6. Deep audit has output_format for all 42 records
7. No unauthorized publication
8. Tests: 0 failed
9. Final verdict is truthful
