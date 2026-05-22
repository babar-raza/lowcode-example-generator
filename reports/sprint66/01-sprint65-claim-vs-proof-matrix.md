# Sprint 66 — Sprint 65 Claim vs Proof Matrix

Sprint: sprint66-remote-truth-repair-self-contained-artifacts-readme-io-publication-proof
Date: 2026-05-22

## Classification Legend

| Code | Meaning |
|------|---------|
| VERIFIED | Claim is supported by reproducible evidence |
| PARTIALLY_VERIFIED | Claim is true but incomplete or narrower than stated |
| CONTRADICTED | Claim is false — direct evidence contradicts it |
| INVALID_CLOSURE | Claim was used to justify sprint closure but is not valid proof |
| REPAIRED_IN_SPRINT66 | Defect closed in Sprint 66 |
| CARRIED_FORWARD_WITH_TASKCARD | Known gap, carried forward with explicit task |

## Claim Classification Matrix

| # | Sprint 65 Claim | Evidence Check | Classification | Sprint 66 Action |
|---|----------------|----------------|---------------|-----------------|
| 1 | 42/42 examples remote-published | GH API: cells=9, words=8, pdf=19, diagram=2, email=1, slides=3 = 42 present | PARTIALLY_VERIFIED | Phase 1: per-example path+hash proof |
| 2 | Remote proof via 6 PRs (one per family) | Words PR#6=1 example; PDF PR#4=1 example; multi-PR history not captured | CONTRADICTED | Phase 1: per-PR per-example coverage map |
| 3 | Remote README I/O status verified | Sampled: words/report-builder, pdf/optimizer — no I/O section found | CONTRADICTED | Phase 1: full audit all 42 remote READMEs |
| 4 | Self-contained package artifacts | handoff/per-family/ empty; no Program.cs/csproj in bundle | CONTRADICTED | Phase 3: build full handoff bundle |
| 5 | Missing destination-packages/ artifacts | sprint65/ has no destination-packages/ dir | CONTRADICTED | Phase 3: copy sprint64 packages into sprint66 handoff |
| 6 | Special-case placement: pdf-pdfa-converter | GH API: examples/pdf/lowcode/pdfa-converter path exists | VERIFIED | Carry forward |
| 7 | Special-case placement: pdf-text-extractor | GH API: examples/pdf/lowcode/text-extractor path exists | VERIFIED | Carry forward |
| 8 | Destination audit output_kind complete | 3 blank: pdf-html-converter, pdf-pdfa-converter, pdf-text-extractor | CONTRADICTED | Phase 4: repair |
| 9 | PDF version policy POLICY_CLASSIFIED | version-policy-final.json total_drift_unresolved=0; classification correct | VERIFIED | Carry forward |
| 10 | EV/ECC rules adequate | Rules 23-32 pass for Sprint 65 bundle; Sprint 64 fails under Sprint 65 rules | PARTIALLY_VERIFIED | Phase 6: add Sprint 65 failure rules |
| 11 | Final clean proof non-empty | reports/sprint65/git/final-clean-proof.txt: "nothing to commit" | VERIFIED | Carry forward |
| 12 | 2993 tests passed | reports/sprint65/lanes/lane-I/test-run.log confirms 2993 passed, 0 failed | VERIFIED | Phase 7: rerun under Sprint 66 |
| 13 | 42 destination audit records | content-audit-final.json has 42 records | VERIFIED | Phase 4: repair missing fields |
| 14 | Root READMEs for 6 families | reports/sprint65/root-readme/per-family/: 6 files present | VERIFIED | Phase 3: include in handoff |
| 15 | Final verdict distinguishes states | Verdict says "all 42 already published" AND "approval blocked" — no per-field separation | CONTRADICTED | Phase 2: build per-field state model |

## Summary Statistics

| Classification | Count |
|---------------|-------|
| VERIFIED | 6 |
| PARTIALLY_VERIFIED | 2 |
| CONTRADICTED | 7 |
| INVALID_CLOSURE | 0 |
| REPAIRED_IN_SPRINT66 | (TBD) |
| CARRIED_FORWARD_WITH_TASKCARD | 0 |

## Sprint 65 Corrected Verdict

`LOWCODE_REMOTE_EXAMPLE_PATHS_PRESENT_README_IO_NOT_PUBLISHED_HANDOFF_MISSING`

5 blocking defects (S65-D1 through S65-D5) require repair in Sprint 66.
