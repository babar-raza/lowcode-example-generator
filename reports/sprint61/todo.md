# Sprint 61 TODO — False Closure Kill-Switch, Pipeline Gates

**Sprint:** 61
**Sprint ID:** sprint61-sprint60-false-closure-kill-switch-20260521
**Date:** 2026-05-21

---

## Phase Checklist

### Phase 0 — Sprint 60 Evidence Audit ✓
- [x] Sprint 60 claim-vs-proof audit (23 claims classified)
- [x] Claim-vs-proof matrix created
- [x] Corrected Sprint 60 state documented
- [x] Sprint 61 todo.md created
- [x] Sprint 61 commands.log created
- [x] Sprint 61 evidence-contract.json created

**Acceptance:** Sprint 60 state truthfully corrected. 8 defects SD60-01 through SD60-08 classified.

---

### Phase 1 — Real Clean Git State ✓
- [x] `git status` captured to `git/dirty-state-before.txt` (real command output)
- [x] All dirty files classified
- [x] Staging plan and commit plan created
- [x] `git/dirty-state-after.txt` captured after Phase 1 commits
- [ ] `git/final-clean-proof.txt` captured AFTER final bundle commit (must be nonzero)

**Acceptance:** final-clean-proof.txt must contain at least "On branch main" + "nothing to commit" text or empty status line. Cannot be 0 bytes.

---

### Phase 2 — Harden EvidenceValidator Semantics ✓
- [x] Rule: final-clean-proof.txt nonzero bytes required
- [x] Rule: final-clean-proof.txt must contain branch/HEAD header
- [x] Rule: required evidence files must be nonzero bytes
- [x] Rule: README MATCH cannot be claimed if input/output format fields are false without policy
- [x] Rule: README gate not-wired = FAIL (check pipeline imports)
- [x] Rule: EvidenceValidator not-wired = FAIL (check pipeline imports)
- [x] Rule: destination input_format_in_programcs null for all = FAIL
- [x] Rule: P1 open items in next-work-register while verdict = complete
- [x] Tests for all new rules (Sprint 60-style false closure must FAIL) — 64 tests passing
- [x] `evidence/validator-gap-analysis.md`
- [x] `evidence/validator-source-proof.patch`
- [x] `evidence/validator-test-results.txt`
- [x] `evidence/sprint60-bundle-validation-result.json`

**Acceptance:** Sprint 60 bundle fails under improved validator. Sprint 61 bundle passes.

---

### Phase 3 — Wire EvidenceValidator into Pipeline ✓
- [x] Added --validate-bundle flag to release-status command in __main__.py
- [x] EvidenceValidator called by release-status --validate-bundle
- [x] Exit code 1 if any FAILURE-severity rule fails
- [x] Failing test: invalid bundle returns exit code 1
- [x] Passing test: valid bundle returns exit code 0 — 5 tests passing
- [x] `evidence/pipeline-integration-proof.md`
- [x] `evidence/pipeline-integration-test-results.txt`

**Acceptance:** Pipeline cannot produce COMPLETE with invalid evidence. Tests prove both paths.

---

### Phase 4 — Strict README I/O Documentation Audit ✓
- [x] Defined README I/O documentation policy (strict prose-context matching)
- [x] `readme/readme-io-documentation-policy.md` created
- [x] For each of 42 examples: classified (0/42 IO_DOC_MATCH before; 38/42 achievable after)
- [x] `readme/example-readme-io-audit-before.json` (0/42 IO_DOC_MATCH — all BOTH_DOC_MISSING)
- [x] `readme/example-readme-io-audit-after.json` (38/42 IO_DOC_MATCH target state)
- [x] `readme/readme-io-correction-plan.md` + `.json`
- [x] Audit result used in EvidenceValidator I/O format rule

**Acceptance:** README audit separates basic content from I/O documentation. No false 42/42 claim.

---

### Phase 5 — Wire README Gate into Publication Flow ✓
- [x] Found publish-pr code in __main__.py (live_mode block)
- [x] Added check_readme_audit_gate before create_github_pr (line 1071)
- [x] Gate blocks if audit missing, shallow, or failed
- [x] Failing test: gate blocks on missing/shallow audit — 14 tests passing
- [x] Passing test: gate passes with valid content-based audit
- [x] `readme/readme-gate-flow-integration.md`
- [x] `readme/readme-gate-flow-source-proof.patch`
- [x] `readme/readme-gate-flow-test-results.txt`

**Acceptance:** `publish-pr --publish` cannot run without passing README gate.

---

### Phase 6 — Destination Program.cs I/O Audit Repair ✓
- [x] Parsed Program.cs for all 42 examples with local packages
- [x] Detected input/output extensions from "input.EXT" / "output.EXT" patterns
- [x] Detected special cases: stdout (StringResult), directory (Directory.Create)
- [x] `destination/programcs-io-audit-before.json` (42/42 NULL_NOT_PARSED — SD60-05)
- [x] `destination/programcs-io-audit-after.json` (37/42 BOTH_KNOWN, 5 special)
- [x] `destination/programcs-io-policy.md`

**Acceptance:** 42/42 Program.cs records classified (37 BOTH_KNOWN, 5 special cases).

---

### Phase 7 — Package Authority Deepening ✓
- [x] Loaded 42 type contracts from format-authority/contracts
- [x] Built depth matrix: 41/42 DUAL_SOURCE, 1 CONTRACT_ONLY
- [x] Populated `io-authority/api-catalog-snippets/` (6 family files)
- [x] `io-authority/package-authority-depth-matrix.json`
- [x] `io-authority/package-authority-depth-summary.md`
- [x] `io-authority/contract-derived-assumptions.md`

**Acceptance:** 41/42 dual-source authority. No scenario overstated. All snippets written.

---

### Phase 8 — Destination README Update Packages ✓
- [x] Built correction entries for all 41 scenarios with known I/O
- [x] `publication/correction-package-ledger.json` (42 entries)
- [x] `publication/readme-update-package-summary.md`
- [x] `publication/live-publication-blockers.md`

**Acceptance:** All gaps have packages or explicit blockers. Push deferred to Sprint 62.

---

### Phase 9 — Full Tests and Real Execution Logs ✓
- [x] Full pytest suite: 2945 passed, 3 skipped, 0 failed in 95.97s
- [x] `lanes/lane-I/test-run.log` captured
- [x] `lanes/lane-I/git-status.txt` captured

**Acceptance:** 0 failed. All logs captured.

---

### Phase 10 — Final Evidence Bundle ✓
- [x] Bundle validator runs and passes all rules (post-commit validation below)
- [x] SHA256 per file computed (54 files)
- [x] `bundle-manifest.json` created
- [x] `final-verdict.md` written with truth-first verdict
- [x] Evidence contract 100% PRESENT (36/36)
- [x] `sprint-state.json` created
- [x] `git/final-clean-proof.txt` captured AFTER commit: "On branch main... nothing to commit, working tree clean"
- [x] Final commit staged and committed (e1aaf2d)

**Acceptance:** All bundle validation rules pass. final-clean-proof.txt is nonzero. Verdict reflects actual state.

---

## Closure Conditions (Sprint 61)

1. final-clean-proof.txt is nonzero bytes with branch+status output
2. Sprint 60 bundle fails under improved EvidenceValidator
3. EvidenceValidator wired into at least one real pipeline command
4. README gate wired into publish-pr live mode
5. README I/O documentation audit is separated from basic content audit
6. Destination Program.cs input classification is non-null
7. EvidenceValidator rejects: empty clean proof, README MATCH without I/O, standalone-only gate/validator
8. test suite: 0 failed
9. commands.log complete, no IN_PROGRESS
10. bundle ≥40 files
