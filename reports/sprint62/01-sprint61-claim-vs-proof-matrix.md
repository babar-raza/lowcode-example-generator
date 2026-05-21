# Sprint 61 Claim vs Proof Matrix — Sprint 62

**Legend:**
- VERIFIED: claim backed by artifact that exists and matches the claim
- PARTIALLY_VERIFIED: claim partially backed; gaps documented
- CARRIED_FORWARD: unresolved from Sprint 61; Sprint 62 must close
- CONTRADICTED: claim conflicts with observed evidence
- REPAIRED_IN_SPRINT62: Sprint 62 directly repairs this item

---

| # | Claim | Classification | Evidence File | Gap / Action |
|---|-------|----------------|---------------|-------------|
| C01 | Sprint 60 bundle fails EV (7/20) | VERIFIED | evidence/sprint60-bundle-validation-result.json | None |
| C02 | EV has 20 rules | VERIFIED | evidence/validator-test-results.txt (64 passed) | None |
| C03 | EV wired into release-status --validate-bundle | VERIFIED | evidence/pipeline-integration-proof.md | None |
| C04 | README gate wired into publish-pr --publish | VERIFIED | readme/readme-gate-flow-integration.md | None |
| C05 | final-clean-proof.txt nonzero + "nothing to commit" | VERIFIED | git/final-clean-proof.txt | None |
| C06 | 2945/2945 tests passing | VERIFIED | lanes/lane-I/test-run.log | None |
| C07 | README I/O audit: 0/42 before, 38/42 target | PARTIALLY_VERIFIED | readme/example-readme-io-audit-before.json | Special cases wrong; push not done |
| C08 | Program.cs I/O: 37/42 BOTH_KNOWN | PARTIALLY_VERIFIED | destination/programcs-io-audit-after.json | pdf-pdf-aconverter, pdf-text-extractor misclassified |
| C09 | Package authority: 41/42 DUAL_SOURCE | PARTIALLY_VERIFIED | io-authority/authority-depth-matrix.json | 0/42 api_verified; pdf-pdf-aconverter misclassified |
| C10 | Correction plan: 41 entries | PARTIALLY_VERIFIED | readme/readme-io-correction-plan.json | 4 special cases had wrong authority |
| C11 | Version drift documented (words/diagram 26.4.0) | CARRIED_FORWARD | publication/live-publication-blockers.md | Destination repos not updated → REPAIRED_IN_SPRINT62 |
| C12 | README APPROVE_README_PUSH semantics safe | CONTRADICTED | src/publisher/readme_audit_gate.py | Bypass too loose — REPAIRED_IN_SPRINT62 |
| C13 | EvidenceValidator integration mandatory | CONTRADICTED | src/__main__.py | Optional flag only — REPAIRED_IN_SPRINT62 |
| C14 | Sprint 61 bundle validation result exists | CONTRADICTED | (missing) | sprint61-bundle-validation-result.json absent — REPAIRED_IN_SPRINT62 |
| C15 | EV rules match Sprint 61 artifact naming | CONTRADICTED | evidence_validator.py | Rules look for Sprint 60 names → REPAIRED_IN_SPRINT62 |
| C16 | Phase 1 todo fully checked | CONTRADICTED | todo.md line 28 | `- [ ]` checkbox on final-clean-proof.txt line |

---

## Sprint 62 Actions Per Classification

### REPAIRED_IN_SPRINT62 (6 items)
- C11: Version drift — dry-run packages with 26.5.0 Directory.Packages.props
- C12: README gate hardening — separate emergency override token
- C13: Mandatory EV integration — final bundle closure requires validator execution
- C14: Sprint 62 bundle validation result generated
- C15: EV rules updated to recognize Sprint 61/62 artifact naming
- C16: Sprint 61 Phase 1 todo item checked (trivial cosmetic fix)

### CARRIED_FORWARD (0 items)
All carried-forward items are being actively closed in Sprint 62.

### PARTIALLY_VERIFIED → Sprint 62 closure
- C07: 42/42 README corrections with correct special-case authority
- C08: 42/42 Program.cs I/O with corrected special-case classification
- C09: Package authority with api_verified backfill where possible
- C10: 42/42 correction entries with corrected authority
