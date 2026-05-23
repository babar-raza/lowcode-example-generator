# Sprint 72 TODO

## Phase 0 — Baseline Audit [DONE]
- [x] 00-sprint71-evidence-audit.md
- [x] 01-sprint71-claim-vs-proof-matrix.md
- [x] 02-corrected-sprint71-state.md
- [x] todo.md
- [x] commands.log
- [x] evidence-contract.json

## Phase 1 — Remote Proof Cleanup [DONE]
- [x] Create corrected remote/remote-proof-summary.md (0/42 truthful)
- [x] Create remote/remote-proof-consistency-audit.json
- [x] Create history/remote-proof-summary-superseded.md
- [x] S71-D1 CLOSED

## Phase 2 — Remote Truth Refresh [DONE]
- [x] Create remote/remote-repo-state-final.json (fresh or PARTIAL)
- [x] Create remote/remote-readme-io-audit-final.json
- [x] Create remote/remote-vs-handoff-final.json
- [x] Create remote/remote-refresh-proof.md

## Phase 3 — Rebuild Sprint 72 Handoff [DONE]
- [x] Copy sprint71 handoff to sprint72 with updated paths
- [x] Update all 6 handoff-index.json files
- [x] Update handoff/publication-handoff-index.json
- [x] Update handoff/package-artifact-hashes.json
- [x] Update handoff/self-contained-artifact-validation.md
- [x] Update handoff/root-readme-path-audit.json

## Phase 4 — Repair Destination Content Audit and Publication Matrix [DONE]
- [x] Create destination/content-audit-final.json with sprint72 paths
- [x] Create publication/publication-truth-matrix-final.json with sprint72 paths
- [x] Create publication/publication-summary.md

## Phase 5 — EV/ECC Hardening [DONE]
- [x] Add EV rules 79–85 (remote proof consistency)
- [x] Create evidence/validator-gap-analysis.md
- [x] Create evidence/validator-source-proof.patch
- [x] Run sprint71 revalidation (fails expected rules)
- [x] Create evidence/sprint71-revalidation-result.json
- [x] Create evidence/sprint72-bundle-validation-result.json
- [x] Create evidence/sprint72-final-validation-result.json
- [x] Create evidence/stale-path-scan.json (no_stale_paths=true)
- [x] S71-D1 CLOSED (via EV rules)

## Phase 6 — Live PR Check [DONE]
- [x] Check approval env var (ABSENT)
- [x] Create publication/live-approval-check.md (BLOCKED_BY_APPROVAL)
- [x] Create publication/pr-package-ledger.json
- [x] Create publication/live-publication-result.json
- [x] Create publication/post-merge-verification.json
- [x] Create publication/branch-delete-result.json

## Phase 7 — Testing [DONE]
- [x] Full test suite: 3025/3025 PASS, 3 skipped, 0 failed
- [x] Validator tests: pass
- [x] Capture logs/test-run.log
- [x] Capture evidence/validator-test-results.txt

## Phase 8 — Final Bundle [DONE]
- [x] ECC bootstrap
- [x] EV Phase A (84 rules)
- [x] ECC (50 categories)
- [x] EV Phase B (85 rules)
- [x] Recompute bundle manifest
- [x] Final verdict
- [x] Commit bundle
- [x] Capture git/final-clean-proof.txt
- [x] Commit proof
