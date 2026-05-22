# Sprint 67 — Sprint 66 Claim vs Proof Matrix

Sprint: sprint67-final-pre-publication-repair-legacy-plan-reconciliation-readme-io-live-pr-readiness
Date: 2026-05-22

## Classification Legend

| Code | Meaning |
|------|---------|
| VERIFIED | Claim is supported by reproducible evidence |
| PARTIALLY_VERIFIED | Claim is true but incomplete or narrower than stated |
| CONTRADICTED | Claim is false — direct evidence contradicts it |
| INVALID_CLOSURE | Claim was used to justify sprint closure but is not valid proof |
| REPAIRED_IN_SPRINT67 | Defect closed in Sprint 67 |
| CARRIED_FORWARD_WITH_TASKCARD | Known gap, carried forward with explicit task |

## Claim Classification Matrix

| # | Sprint 66 Claim | Evidence Check | Classification | Sprint 67 Action |
|---|----------------|----------------|---------------|-----------------|
| 1 | 42/42 remote examples present via GitHub API | GH API confirmed: cells=9, words=8, pdf=19, diagram=2, email=1, slides=3 | VERIFIED | Phase 7: refresh remote truth |
| 2 | 0/42 remote READMEs have I/O sections | remote/remote-readme-io-audit.json: all 42 records remote_readme_has_io=false | VERIFIED | Phase 7: re-audit after any PRs |
| 3 | 42/42 local corrected handoff packages in sprint66/ | reports/sprint66/handoff/per-family/: 6 family dirs with packages | VERIFIED | Phase 4: copy to sprint67 handoff |
| 4 | Root README artifacts for 6 families | 6 files present in root-readme/per-family/; content exists | PARTIALLY_VERIFIED | Phase 2: repair cardinality display |
| 5 | Root README shows correct I/O display for all operation kinds | cells readme: merger=xlsx→xlsx (no N→1), splitter=xlsx→xlsx (no 1→N) | CONTRADICTED | Phase 2 (S66-D1): add cardinality annotations |
| 6 | PDF version consistent across handoff and audit | handoff/pdf/Directory.Packages.props=26.5.0; content-audit-final.json=26.4.0 | CONTRADICTED | Phase 3 (S66-D2): resolve with version decision |
| 7 | Sprint 64 path leakage resolved — local_package_path refs sprint66 | content-audit-final.json: local_package_path=reports/sprint64/... for all 42 | CONTRADICTED | Phase 4 (S66-D3): update to sprint67 paths |
| 8 | Live README I/O PRs created (or explicitly blocked) | 0 PRs created; no approval token activated; S66-D4 open | CONTRADICTED | Phase 8 (S66-D4): activate or document BLOCKED state |
| 9 | Legacy plans reconciled | Sprint 62 Format Capability + Sprint 61 README Sync plans not addressed | CONTRADICTED | Phase 1 (S66-D5): full reconciliation |
| 10 | EV 42 rules adequate for all Sprint 66 defects | 42 rules pass but no rules for cardinality, version consistency, path leakage | PARTIALLY_VERIFIED | Phase 9: add 10 new rules |
| 11 | S65-D1: Remote proof index per-PR per-example | remote/remote-pr-proof-index.json covers 6 families with PR lists | VERIFIED | Carry forward |
| 12 | S65-D2: Remote README audit 0/42 I/O | remote/remote-readme-io-audit.json confirmed | VERIFIED | Carry forward |
| 13 | S65-D3: Self-contained handoff bundle | 42 packages in reports/sprint66/handoff/per-family/ | VERIFIED | Phase 4: migrate to sprint67 |
| 14 | S65-D4: output_kind repaired for 3 PDF records | pdf-html-converter=converter, pdf-pdfa-converter=converter, pdf-text-extractor=extractor | VERIFIED | Carry forward |
| 15 | S65-D5: Per-field publication state model | publication/publication-truth-matrix-final.json with 11 per-example fields | VERIFIED | Carry forward |
| 16 | Final clean proof non-empty | reports/sprint66/git/final-clean-proof.txt: "nothing to commit, working tree clean" | VERIFIED | Phase 11: new proof for sprint67 |
| 17 | 2993 tests passed | reports/sprint66/lanes/lane-I/test-run.log: 2993 passed, 0 failed | VERIFIED | Phase 10: rerun under Sprint 67 |
| 18 | ECC 50/50 categories PRESENT | evidence-contract-computed.json: closure_valid=true, blocking_failures=0 | VERIFIED | Phase 11: new ECC for sprint67 |

## Summary Statistics

| Classification | Count |
|---------------|-------|
| VERIFIED | 10 |
| PARTIALLY_VERIFIED | 2 |
| CONTRADICTED | 5 (S66-D1 through S66-D5) |
| INVALID_CLOSURE | 0 |
| REPAIRED_IN_SPRINT67 | (TBD at closure) |
| CARRIED_FORWARD_WITH_TASKCARD | 0 |

## Sprint 66 Corrected Verdict

`LOWCODE_HANDOFF_READY_ROOT_README_CARDINALITY_DEFECTIVE_VERSION_CONTRADICTION_PATH_LEAKAGE`

5 blocking defects (S66-D1 through S66-D5) require repair in Sprint 67.
