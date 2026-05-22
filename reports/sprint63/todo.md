# Sprint 63 TODO — Sprint 62 Closure Repair, Validator Self-Consistency, Package Evidence

**Sprint:** 63
**Sprint ID:** sprint63-sprint62-closure-repair-validator-package-evidence-publication-handoff
**Date:** 2026-05-22

---

## Phase Checklist

### Phase 0 — Reopen Sprint 62 and Correct State
- [x] Sprint 62 evidence bundle audited (6 blocking defects found)
- [x] Sprint 62 verdict downgraded to README_IO_DRY_RUN_READY_WITH_...
- [x] 14 claims classified (VERIFIED/PARTIALLY/CONTRADICTED/INVALID_CLOSURE)
- [x] 00-sprint62-evidence-audit.md created
- [x] 01-sprint62-claim-vs-proof-matrix.md created
- [x] 02-corrected-sprint62-state.md created
- [x] commands.log created
- [x] todo.md created
- [x] evidence-contract.json created

**Acceptance:** Sprint 62 not closed; corrected baseline established.

---

### Phase 1 — Fix Evidence Contract Status Generation
- [x] EvidenceContractComputer module created
- [x] Computes PRESENT/MISSING/ZERO_BYTES/SEMANTIC_FAILED for each category
- [x] evidence-contract-repair.md documents root cause and fix
- [x] evidence-contract-source-proof.patch
- [x] evidence-contract-test-results.txt (13 tests, 0 failed)
- [x] evidence-contract-computed.json created at Phase 9

**Acceptance:** No blocking category is PENDING at closure; status is computed.

---

### Phase 2 — Fix EvidenceValidator Self-Contradiction
- [x] Two-phase validation added (exclude rule 21 for pre-result phase, validate_for_storage())
- [x] Contradiction detection added: overall_valid=true + embedded passed=false rule FAIL
- [x] Sprint 62 revalidation result written (overall_valid=false, 1 rule FAILED)
- [x] validator-self-consistency.md documents fix
- [x] validator-source-proof.patch
- [x] validator-test-results.txt (76 tests, 0 failed — +7 new TestTwoPhaseValidation)
- [x] sprint62-revalidation-result.json
- [x] sprint63-bundle-validation-result.json (Phase 9)

**Acceptance:** Sprint 62 bundle fails under repaired validator (CONFIRMED: overall_valid=false).

---

### Phase 3 — Include Actual Destination PR Package Artifacts
- [x] 6/6 dry-run packages enumerated with file lists
- [x] Per-family Program.cs, README.md, .csproj files collected
- [x] Directory.Packages.props per family
- [x] package-artifact-index.json
- [x] package-hashes.json (SHA256 per source file)
- [x] package-artifact-validation.md
- [x] Per-family content folders in destination-packages/per-family/

**Acceptance:** 40/42 scenarios verifiable from bundle (2 PDF special cases documented).

---

### Phase 4 — Deep Destination Content Audit
- [x] 42/42 examples with full field set
- [x] content-audit-deep.json (all fields)
- [x] programcs-vs-authority-deep.json (37/42 match, 3 mismatch, 2 no authority)
- [x] readme-vs-authority-deep.json (40/42 corrections available, 0 applied)
- [x] destination/content-audit-repaired.json (enriched from Sprint 62)
- [x] deep-audit-summary.md

**Acceptance:** 42/42 records have content status, API usage, README correction availability, version.

---

### Phase 5 — Correct Package Authority Labeling
- [x] api_verified renamed from CONFIRMED_FROM_PROGRAMCS to PROGRAMCS_USAGE_CONFIRMED
- [x] programcs_api_usage_verified field added (True for 42/42)
- [x] package_api_authority field added (False for 42/42)
- [x] authority-label-correction.md
- [x] package-authority-matrix-corrected.json

**Acceptance:** No scenario overstates package authority.

---

### Phase 6 — Final Verdict Semantics
- [x] final-verdict-semantics.md
- [x] Truthful verdict: LOWCODE_README_IO_DRY_RUN_PACKAGES_VERIFIED_PUBLICATION_BLOCKED_BY_APPROVAL

**Acceptance:** Verdict cannot overclaim publication or package authority.

---

### Phase 7 — Live Publication Check
- [x] Approval check (no secrets printed)
- [x] publication/live-approval-check.md
- [x] publication/live-publication-result.json

**Acceptance:** No unauthorized remote mutation.

---

### Phase 8 — Tests and Command Logs
- [x] Full unit suite run: 2976 passed, 3 skipped, 0 failed
- [x] EV self-consistency tests (7 new, TestTwoPhaseValidation)
- [x] Evidence contract tests (13 new, TestEvidenceContractComputer)
- [x] lanes/lane-I/test-run.log
- [x] lanes/lane-I/git-status.txt

**Acceptance:** All tests logged; no failures uncaptured.

---

### Phase 9 — Final Evidence Bundle
- [x] sprint63-bundle-validation-result.json (EV 21/21 PASS)
- [x] bundle-manifest.json
- [x] final-verdict.md
- [x] sprint-state.json
- [x] git/final-clean-proof.txt (AFTER commit)
- [x] evidence-contract.json 100% PRESENT
- [x] Final commit

**Acceptance:** EV 21/21 PASS; verdict truthful; bundle self-contained.

---

## Sprint 63 Closure Conditions

1. [x] Sprint 62 correctly audited and downgraded
2. [x] Evidence contract computation: no PENDING at closure
3. [x] Validator result: no internal contradiction
4. [x] Dry-run package artifacts: in bundle or fully represented
5. [x] Destination audit: 42/42 with content status, API usage, README, version
6. [x] Package authority: correctly labelled (not overstated)
7. [x] Verdict: truthful, matches actual delivery state
8. [x] Tests: 0 failed
9. [x] commands.log: no IN_PROGRESS at closure
10. [x] Bundle: >= 50 files
11. [x] final-clean-proof.txt: nonzero, "nothing to commit"
