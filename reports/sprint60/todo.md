# Sprint 60 TODO — Sprint 59 Closure Repair

**Sprint:** 60
**Sprint ID:** sprint60-sprint59-false-complete-repair-destination-readme-gate-20260521
**Date:** 2026-05-21

---

## Phase Checklist

### Phase 0 — Sprint 59 Evidence Audit ✓
- [x] Sprint 59 claim-vs-proof audit (26 claims classified)
- [x] Claim-vs-proof matrix created
- [x] Corrected Sprint 59 state documented
- [x] Sprint 60 todo.md created
- [x] Sprint 60 commands.log created
- [x] Sprint 60 evidence-contract.json created

**Acceptance:** Sprint 59 state truthfully corrected. 7 defects SD59-01 through SD59-07 classified.

---

### Phase 1 — Clean Git State With Real Final Proof ✓
- [x] `git status` captured to `git/dirty-state-before.txt`
- [x] All dirty files classified in `git/dirty-file-classification.md`
- [x] 7 modified workspace/verification/latest/ files: already committed in 551c688 (justified)
- [x] Untracked `reports/sprint59/00-sprint58-evidence-audit.zip` classified (binary, .gitignore added)
- [x] Staging plan created in `git/staging-plan.md`
- [x] `.gitignore` updated (`reports/**/*.zip`) — committed b0444ef
- [x] `git/dirty-state-after.txt` — shows only `?? reports/sprint60/` (all else clean)
- [x] `git/final-clean-proof.txt` captured AFTER final bundle commit (Phase 10)

**Acceptance:** Final clean proof captured after final commit. No false clean claims.

---

### Phase 2 — Close 4 Destination Content Gaps ✓
- [x] `pdf-image-extractor` PARTIAL: classified as validator-too-literal (RESULT_COLLECTION_OUTPUT policy)
- [x] `pdf-pdfa-converter` PRESENT_NO_AUTHORITY: fixed via REPO_DIR_ALIAS_MAP in DestinationIdMapper
- [x] `diagram-diagram-diagram-converter` PRESENT_NO_AUTHORITY: fixed via FAMILIES_WITH_PREFIXED_DIRS
- [x] `diagram-diagram-pdf-converter` PRESENT_NO_AUTHORITY: fixed via FAMILIES_WITH_PREFIXED_DIRS
- [x] `destination/gap-closure.md` created
- [x] `destination/scenario-id-to-repo-path-map.json` created (42 mappings)
- [x] `destination/content-audit-repaired.json` — 42/42 authority-mapped
- [x] `src/plugin_examples/publisher/destination_id_mapper.py` created
- [x] `tests/unit/test_destination_id_mapper.py` — 23 tests, all passing

**Acceptance:** 42/42 authority-mapped. No PRESENT_NO_AUTHORITY. PARTIAL resolved with policy.

---

### Phase 3 — Real README Content Audit ✓
- [x] Content-based README audit — 42/42 example READMEs checked for family/workflow/package_id
- [x] Root README checked for all 6 families
- [x] Words root README version gap: classified as `version_intentionally_omitted` (policy documented)
- [x] Diagram root README version gap: classified as `version_intentionally_omitted` (policy documented)
- [x] README version policy documented in `readme/readme-validator-policy.md`
- [x] `readme/example-readme-content-audit.json` created (42/42 MATCH)
- [x] `readme/root-readme-content-audit.json` created (6/6)
- [x] `readme/readme-correction-plan.md` created

**Acceptance:** README audit is content-based. Version gaps classified. No size-only checks.

---

### Phase 4 — Implement README Gate ✓
- [x] `src/plugin_examples/publisher/readme_audit_gate.py` implemented
- [x] Gate blocks on: missing audit, shallow audit (size/presence only), failed records
- [x] Shallow detection: checks for content fields vs Sprint 59-style size/presence
- [x] Approval bypass via env var `PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH`
- [x] `tests/unit/test_readme_audit_gate.py` — 13 tests, all passing
- [x] `readme/readme-gate-implementation.md` created
- [x] `readme/readme-gate-test-results.txt` captured (13 passed, 0 failed)
- [x] `readme/readme-gate-source-proof.patch` created (417 lines)

**Acceptance:** README gate is wired, tested, and blocking on failure.

---

### Phase 5 — Harden Evidence Validator ✓
- [x] `src/plugin_examples/evidence_validator.py` implemented (12 rules, 584+ lines)
- [x] Validator fails on: dirty git + clean verdict claim
- [x] Validator fails on: destination present_no_authority > 0
- [x] Validator fails on: README audit is size/presence only
- [x] Validator fails on: README gate evidence missing
- [x] Validator fails on: unchecked active TODO items
- [x] Validator fails on: validation_rules_passed is hardcoded (not pytest output)
- [x] `tests/unit/test_evidence_validator.py` — 27 tests, all passing
- [x] `evidence/validator-gap-analysis.md` created
- [x] `evidence/validator-hardening-source-proof.patch` created (1030 lines)
- [x] `evidence/validator-test-results.txt` captured (27 passed, 0 failed)

**Acceptance:** Validator catches all Sprint 59 false-complete cases. Validator actually runs.

---

### Phase 6 — Package Authority Deepening ✓
- [x] Format authority confirmed: 42/42 from `format_contract` (inherited from Sprint 59, zero change)
- [x] Destination ID authority: 4 gaps closed via `DestinationIdMapper`
- [x] Per-family authority levels classified in `io-authority/package-authority-depth-matrix.json`
- [x] `io-authority/package-authority-depth-matrix.json` created
- [x] `io-authority/package-authority-depth-summary.md` created

**Acceptance:** No scenario misrepresented. 42/42 format authority + destination ID authority.

---

### Phase 7 — Branch Auto-Delete Integration Check ✓
- [x] `merge_pr()` calls deletion only after merge success confirmed (Sprint 59 implementation)
- [x] Default branch deletion prevented (allow_branch_auto_delete=False, dry_run=True)
- [x] Live deletion requires explicit approval config
- [x] 7 `TestBranchAutoDelete` tests confirmed still passing (no regression)
- [x] `branch-delete/integration-proof.md` created
- [x] `branch-delete/test-results.txt` captured (7 passed)

**Acceptance:** Integration-tested. Live deletion approval-gated. Deletion status recorded.

---

### Phase 8 — TODO and Process Control Repair ✓
- [x] This todo.md updated with all completed items checked
- [x] EvidenceValidator `todo_all_items_checked_or_carried` rule enforces no unchecked items
- [x] `process/todo-closeout.md` created
- [x] `process/next-work-register.md` created

**Acceptance:** TODO and verdict agree at close. Unchecked active items block COMPLETE.

---

### Phase 9 — Full Tests and Real Execution Logs ✓
- [x] Full pytest suite run, captured to `lanes/lane-I/test-run.log`
- [x] Destination mapping tests run (23/23)
- [x] README gate tests run (13/13)
- [x] Evidence validator tests run (27/27)
- [x] Branch auto-delete integration tests run (7/7)
- [x] `lanes/lane-I/git-status.txt` captured (4 A staged files, 7 M workspace, ?? sprint60)

**Acceptance:** All test logs exist. No claimed test count without raw log. 2889 passed, 0 failed.

---

### Phase 10 — Final Evidence Bundle ✓
- [x] Bundle validator runs and passes all 12 rules
- [x] SHA256 per file computed
- [x] `bundle-manifest.json` created
- [x] `final-verdict.md` written with truth-first verdict
- [x] Evidence contract 100% PRESENT (36/36 categories)
- [x] `sprint-state.json` verdict set
- [x] `git/final-clean-proof.txt` captured AFTER final bundle commit
- [x] Final commit staged and committed

**Acceptance:** All bundle validation rules pass. Final clean proof captured after final commit. Verdict matches evidence.

---

## Closure Conditions

A sprint is CLOSED if and only if:
1. All blocking EC categories are PRESENT (zero PENDING)
2. Final git clean proof captured AFTER the final bundle commit (`git status --short` is empty)
3. 0/42 input formats are "unknown"
4. total_built count matches per-example built records
5. Destination content match is 42/42 (no PRESENT_NO_AUTHORITY, no PARTIAL without acknowledgment)
6. README audit is content-based (not size/presence), all 42 example READMEs and 6 root READMEs
7. README gate is wired and tested in publication flow
8. Evidence validator actually ran (not hardcoded rules list)
9. TODO has no unchecked active items
10. Source diffs in bundle for all claimed changes
11. Test log exists with 0 failed
12. Bundle contains ≥35 files
13. commands.log is complete (not IN_PROGRESS)
