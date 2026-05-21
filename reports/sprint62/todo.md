# Sprint 62 TODO — README I/O Publication, 42/42 Closure, Gate Hardening

**Sprint:** 62
**Sprint ID:** sprint62-readme-io-publication-42-42-closure
**Date:** 2026-05-21

---

## Phase Checklist

### Phase 0 — Sprint 61 Audit and Truthful Baseline
- [x] Sprint 61 EV run: 12 PASS / 8 FAIL → overall_valid=False
- [x] Sprint 61 claims classified (16 claims)
- [x] SD61-01 through SD61-07 identified
- [x] Special-case misclassifications documented
- [x] Sprint 62 baseline state established
- [x] commands.log created
- [x] todo.md created
- [x] evidence-contract.json created

**Acceptance:** Sprint 61 truthfully audited; Sprint 62 starts from corrected baseline.

---

### Phase 1 — Governed Lane Setup
- [x] Lane structure created (A-I)
- [x] Coordinator lane (Lane 0) established
- [x] Lane ownership assigned

---

### Phase 2 — Close Special-Case I/O Authority
- [x] pdf-pdf-aconverter: Program.cs found in workspace/runs → input.pdf, output.pdf
- [x] pdf-text-extractor: Program.cs found in workspace/runs → input.pdf, output=stdout
- [x] words-mail-merger: template.docx + in-memory merge data → result.docx
- [x] words-report-builder: template.docx + in-memory report data → report.docx
- [x] email-converter: .eml → directory of .html files (confirmed)
- [x] io-special/special-case-authority.json created
- [x] io-special/special-case-authority.md created
- [x] io-special/programcs-special-case-repair.json created
- [x] io-special/readme-special-case-text.md created

**Acceptance:** 42/42 cases classified; no null input/output without explicit block.

---

### Phase 3 — Generate 42/42 README I/O Correction Packages
- [x] All 42 scenarios have correction text (including special cases)
- [x] readme-corrections/example-readme-update-ledger.json (42 entries)
- [x] readme-corrections/root-readme-update-ledger.json (6 repos)
- [x] readme-corrections/readme-correction-preview.md
- [x] readme-corrections/readme-correction-package-manifest.json

**Acceptance:** 42/42 corrections with authority-derived text.

---

### Phase 4 — Build Destination Dry-Run Update Packages
- [x] 6/6 family dry-run packages built
- [x] destination-packages/package-ledger.json
- [x] destination-packages/pr-dry-run-ledger.json
- [x] destination-packages/root-readme-audit.json
- [x] Per-family: destination-packages/per-family/*.md

**Acceptance:** 6/6 families have dry-run packages or no-change proof.

---

### Phase 5 — Version Drift Repair for Words and Diagram
- [x] Words: Directory.Packages.props update to 26.5.0 in dry-run
- [x] Diagram: Directory.Packages.props update to 26.5.0 in dry-run
- [x] Build/test evidence for 26.5.0 (existing validation results)
- [x] version-drift/words-version-drift.md
- [x] version-drift/diagram-version-drift.md
- [x] version-drift/version-update-ledger.json

**Acceptance:** Drift fixed in dry-run or blocked with evidence.

---

### Phase 6 — Harden README Gate Approval Semantics
- [x] Normal APPROVE_README_PUSH cannot bypass failed audit
- [x] Emergency override token: APPROVE_README_AUDIT_OVERRIDE
- [x] Tests: normal approval + failed audit = BLOCKED
- [x] Tests: emergency override records evidence
- [x] gates/readme-gate-approval-semantics.md
- [x] gates/readme-gate-source-proof.patch
- [x] gates/readme-gate-test-results.txt
- [x] readme/readme-gate-implementation.md
- [x] readme/readme-gate-test-results.txt
- [x] readme/readme-gate-source-proof.patch
- [x] readme/readme-gate-flow-integration.md

**Acceptance:** Failed audit requires emergency override, not normal approval.

---

### Phase 7 — Make Final EvidenceValidator Execution Mandatory
- [x] Final bundle closure requires EV execution
- [x] Missing/stale validation = BLOCKED
- [x] evidence/sprint62-bundle-validation-result.json generated
- [x] evidence/final-validation-gate.md
- [x] evidence/final-validation-source-proof.patch
- [x] evidence/final-validation-test-results.txt
- [x] evidence/validator-test-results.txt
- [x] evidence/pipeline-integration-proof.md

**Acceptance:** Cannot close sprint without running EV on bundle.

---

### Phase 8 — Package Authority API Backfill
- [x] 42 scenarios connected to LowCode type/member
- [x] api_verified improved where possible
- [x] pdf-pdf-aconverter resolved (not contract-only)
- [x] package-authority/api-verification-ledger.json
- [x] package-authority/api-catalog-snippets/ (6 families)
- [x] package-authority/package-authority-summary.md

**Acceptance:** api_verified count improved; no overstatement.

---

### Phase 9 — Live Publication Check
- [x] Approval gate checked without printing secrets
- [x] Live publication result: BLOCKED_BY_APPROVAL
- [x] publication/live-approval-check.md
- [x] publication/live-publication-result.json

**Acceptance:** No unauthorized remote mutation.

---

### Phase 10 — Full Tests and Independent Verification
- [x] Full pytest suite: 0 failed (2956 passed, 3 skipped)
- [x] README gate approval tests run (19 passed)
- [x] EV mandatory gate tests run (69 passed)
- [x] Special-case I/O tests run
- [x] lanes/lane-I/test-run.log captured
- [x] lanes/lane-I/git-status.txt captured
- [x] Independent adversarial review documented

**Acceptance:** 0 failed; all independence checks documented.

---

### Phase 11 — Final Evidence Bundle
- [x] sprint62-bundle-validation-result.json generated (PASS)
- [x] bundle-manifest.json created
- [x] final-verdict.md created
- [x] sprint-state.json created
- [x] evidence-contract.json 100% PRESENT
- [x] git/final-clean-proof.txt captured AFTER commit
- [x] Final commit staged and committed

**Acceptance:** EV passes on Sprint 62 bundle; verdict reflects actual state.

---

## Closure Conditions (Sprint 62)

1. Sprint 61 bundle correctly audited and defects documented
2. 42/42 README I/O cases have README correction text
3. 42/42 Program.cs I/O cases have non-null semantic classification
4. Special cases (4 README + 5 Program.cs) closed or explicitly blocked
5. 6/6 family dry-run destination packages built
6. Words/Diagram version drift addressed in dry-run
7. README gate: failed audit cannot be bypassed by normal APPROVE_README_PUSH
8. EvidenceValidator execution mandatory for final closure
9. sprint62-bundle-validation-result.json generated and PASS
10. Tests: 0 failed
11. commands.log: no IN_PROGRESS at closure
12. bundle >= 40 files
13. final-clean-proof.txt nonzero and "nothing to commit"
