# Sprint 59 TODO — Sprint 58 Closure Repair

**Sprint:** 59
**Sprint ID:** sprint59-sprint58-closure-repair-io-authority-destination-content-20260521
**Date:** 2026-05-21

---

## Phase Checklist

### Phase 0 — Sprint 58 Evidence Audit ✓
- [x] Sprint 58 claim-vs-proof audit (27 claims classified)
- [x] Claim-vs-proof matrix created
- [x] Corrected Sprint 58 state documented
- [x] Sprint 59 todo.md created
- [x] Sprint 59 evidence-contract.json created

**Acceptance:** Sprint 58 state truthfully corrected. No false complete state remains.

---

### Phase 1 — Git/Source State Reconciliation
- [ ] `git status` captured to `git/dirty-state-before.txt`
- [ ] All dirty files classified in `git/dirty-file-classification.md`
- [ ] Staging plan created in `git/staging-plan.md`
- [ ] Commit plan created in `git/commit-plan.md`
- [ ] Source changes (pdf.yml, github_pr_merger.py, test files) staged and committed
- [ ] Workspace/latest classification complete (commit vs. exclude)
- [ ] Final git status captured to `git/dirty-state-after.txt`
- [ ] Evidence-contract EC corresponding to git state updated

**Acceptance:** All committed changes have exact-path staging evidence. Final git status clean OR every remaining dirty file has owner/reason/next action.

---

### Phase 2 — Source Diff / Source Proof Bundle
- [ ] `git diff` produced for all 4 changed source files
- [ ] `source/source-diff.patch` created
- [ ] `source/changed-files.txt` created
- [ ] `source/source-hashes.json` created (SHA256 per file post-commit)
- [ ] `source/source-proof.md` created
- [ ] Commit SHAs recorded if committed

**Acceptance:** Every implementation claim has source proof. Source proof is in bundle.

---

### Phase 3 — True Package I/O Authority Completion
- [ ] Input formats resolved for all 42 active types (0 "unknown" remaining)
- [ ] `io-authority/input-format-authority-matrix.json` created
- [ ] `io-authority/input-output-authority-matrix.json` created (42 types, full I/O)
- [ ] `io-authority/package-evidence-bundle-index.json` created
- [ ] `io-authority/runtime-io-probe-ledger.json` created
- [ ] `io-authority/unresolved-io-authority.md` created (must be empty or explicitly blocked)
- [ ] Authority level per type: runtime_verified / reflection_verified / xml_doc_verified / generated_fixture_verified
- [ ] No active runnable scenario remains with input_format unknown

**Acceptance:** 42/42 active types have resolved input_format. Evidence is included or reproducibly referenced.

---

### Phase 4 — Regeneration Ledger Repair
- [ ] Per-example records expanded to full field set (30+ fields)
- [ ] build_status "repaired" normalized to "passed_after_repair" or counted separately
- [ ] Summary counts derive from per-example records (not independently stated)
- [ ] `full-regeneration-ledger.json` corrected: total_built matches per-example count
- [ ] Per-example records include: project path, Program.cs path, contract hash, input/output format, build log path, run log path, semantic validator status
- [ ] Final counts: clean_pass / passed_after_repair / failed / blocked

**Acceptance:** No family-level-only proof. No contradictory counts. Per-example records are real proof, not status stubs.

---

### Phase 5 — Destination Content Audit (Not Count Audit)
- [ ] Program.cs fetched and inspected for all 42 destination examples
- [ ] README.md fetched and inspected for all 42 destination examples
- [ ] Root README.md audited for all 6 destination repos
- [ ] `destination/content-audit.json` created (42/42)
- [ ] `destination/programcs-vs-authority.json` created
- [ ] `destination/readme-vs-authority.json` created
- [ ] `destination/root-readme-audit.json` created
- [ ] `destination/correction-plan.md` created
- [ ] Per-family/ reports created (6 files)
- [ ] Stale/missing destination content identified

**Acceptance:** 42/42 destination examples content-audited. 6/6 root READMEs audited. No POST_MERGE_VERIFIED claim without content proof.

---

### Phase 6 — README Gate + Branch Auto-Delete Integration Proof
- [ ] README gate test added (publication cannot skip README audit)
- [ ] Branch auto-delete merge-flow integration tested
- [ ] Source diff for github_pr_merger.py in bundle
- [ ] Approval gate integration tested
- [ ] `lanes/lane-G/` updated with integration proof

**Acceptance:** README gate implemented and tested. Branch delete approval-gated. Source proof included.

---

### Phase 7 — Full Tests and Real Command Logs
- [ ] Full pytest suite run, output captured to `lanes/lane-I/test-run.log`
- [ ] Targeted PdfAConverter tests run
- [ ] Targeted branch auto-delete tests run
- [ ] I/O authority tests run (if new tests added)
- [ ] All commands in commands.log have exact command + exit code + output path
- [ ] `lanes/lane-I/git-status.txt` captured at close

**Acceptance:** Test logs exist. Commands reproducible. No claimed command lacks output evidence.

---

### Phase 8 — Final Evidence Bundle Validation
- [ ] Bundle validator runs and passes all 9 rules
- [ ] Source diffs in bundle
- [ ] Input formats 0 unknown
- [ ] Per-example records: all required fields present
- [ ] Destination content audit: 42/42
- [ ] README audit: 42/42 (or explicitly blocked with reason)
- [ ] `bundle-manifest.json` updated
- [ ] `final-verdict.md` written
- [ ] Evidence contract EC categories all PRESENT
- [ ] sprint-state.json verdict updated

**Acceptance:** All 9 bundle validation rules pass. Final verdict is `IO_AUTHORITY_COMPLETE_DESTINATION_CONTENT_VERIFIED` (or truthful alternative if blocked).

---

## Closure Conditions

A sprint is CLOSED if and only if:
1. All blocking EC categories are PRESENT (zero PENDING)
2. final git status is clean OR every remaining dirty file has classification
3. 0/42 input formats are "unknown"
4. total_built count matches per-example built records
5. Destination audit is content-verified (not count-only)
6. Source diffs are in bundle for all claimed changes
7. Test log exists with 0 failed
8. Lane J documents are present
9. Bundle contains ≥25 files
10. commands.log is not IN_PROGRESS at closure
