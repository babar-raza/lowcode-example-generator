# Sprint 69 Todo

Sprint: sprint69-final-state-consistency-repair-canonical-audit-publication-truth-live-pr-readiness

## Phase 0: Sprint 68 Audit and Reopen

- [x] Create reports/sprint69/00-sprint68-evidence-audit.md
- [x] Create reports/sprint69/01-sprint68-claim-vs-proof-matrix.md
- [x] Create reports/sprint69/02-corrected-sprint68-state.md
- [x] Create reports/sprint69/todo.md
- [x] Create reports/sprint69/commands.log
- [x] Create reports/sprint69/evidence-contract.json
- [x] Classify all 8 Sprint 68 defects (S68-D1 through S68-D8)

## Phase 1: One Canonical Final Destination Audit (S68-D4)

- [x] Read content-audit-sprint68.json — confirm 42 records, sprint68 paths
- [x] Create reports/sprint69/destination/content-audit-final.json (42 records, sprint69 paths)
- [x] Create reports/sprint69/destination/audit-conflict-resolution.md
- [x] Create reports/sprint69/destination/canonical-audit-source-map.json
- [x] Move stale audits to reports/sprint69/history/

## Phase 2: Sprint 69 Self-Contained Handoff Rebuild (S68-D6)

- [x] Copy sprint68 handoff per-family into sprint69/handoff/per-family/
- [x] Add root_readme field to all 6 family handoff-index.json files
- [x] Update all handoff-index.json paths sprint68 -> sprint69
- [x] Create reports/sprint69/handoff/publication-handoff-index.json (42 examples + 6 root READMEs)
- [x] Create reports/sprint69/handoff/package-artifact-hashes.json
- [x] Create reports/sprint69/handoff/self-contained-artifact-validation.md

## Phase 3: Fix Handoff Index Version Mismatches (S68-D5)

- [x] Audit all 6 family handoff-index.json vs Directory.Packages.props
- [x] Fix words/handoff-index.json nuget_version 26.4.0 -> 26.5.0
- [x] Fix pdf/handoff-index.json nuget_version 26.4.0 -> 26.5.0
- [x] Fix diagram/handoff-index.json nuget_version 26.4.0 -> 26.5.0
- [x] Create reports/sprint69/version/handoff-index-version-audit-before.json
- [x] Create reports/sprint69/version/handoff-index-version-audit-after.json
- [x] Create reports/sprint69/version/version-consistency-final.json
- [x] Add EV rule 58: handoff_index_version_matches_dpp

## Phase 4: Publication Truth Model Cleanup (S68-D2, S68-D3)

- [x] Rebuild publication-truth-matrix-final.json with sprint69 paths
- [x] Separate old example publication from README I/O update state
- [x] Create reports/sprint69/publication/publication-state-model.md
- [x] Create reports/sprint69/publication/publication-truth-matrix-final.json (42 records)
- [x] Create reports/sprint69/publication/publication-summary.md

## Phase 5: Consolidate Legacy Plan Reconciliation (S68-D7)

- [x] Read legacy-plan-reconciliation/* (5 files)
- [x] Read legacy-reconciliation/* (4 files)
- [x] Create reports/sprint69/legacy-reconciliation/exact-legacy-plan-reconciliation-final.md
- [x] Create reports/sprint69/legacy-reconciliation/exact-items-final.json

## Phase 6: Remote Truth Refresh

- [x] Carry forward sprint68 remote state (no new merges since sprint68 close)
- [x] Create reports/sprint69/remote/remote-repo-state-final.json
- [x] Create reports/sprint69/remote/remote-readme-io-audit-final.json
- [x] Create reports/sprint69/remote/remote-vs-handoff-final.json

## Phase 7: EV/ECC Hardening (S68-D8)

- [x] Add EV rules 58-67 (10 new rules)
- [x] Create reports/sprint69/evidence/validator-gap-analysis.md
- [x] Create reports/sprint69/evidence/validator-source-proof.patch
- [x] Create reports/sprint69/evidence/validator-test-results.txt
- [x] Create reports/sprint69/evidence/sprint68-revalidation-result.json (sprint68 fails under sprint69 rules)
- [x] Update test_evidence_validator.py — add sprint69 artifacts to _make_bundle, update counts
- [x] Update test_pipeline_evidence_gate.py — add sprint69 artifacts
- [x] Run EV tests — all pass

## Phase 8: Live PR Check

- [x] Check APPROVE_LIVE_PR token — NOT_SET
- [x] Create reports/sprint69/publication/live-approval-check.md (BLOCKED_BY_APPROVAL)
- [x] Create reports/sprint69/publication/pr-package-ledger.json
- [x] Create reports/sprint69/publication/live-publication-result.json
- [x] Create reports/sprint69/publication/post-merge-verification.json
- [x] Create reports/sprint69/publication/branch-delete-result.json

## Phase 9: Full Test Run

- [x] Run full test suite
- [x] Capture logs/test-run.log
- [x] Confirm 0 failed, >=3025 passed

## Phase 10: Final Evidence Bundle

- [x] Run EV Phase A bootstrap
- [x] Write evidence/sprint69-bundle-validation-result.json
- [x] Seed evidence-contract-computed.json
- [x] Run ECC -> write evidence-contract-computed.json
- [x] Run EV Phase B (all rules)
- [x] Write evidence/sprint69-final-validation-result.json
- [x] Write final-verdict.md
- [x] Write sprint-state.json
- [x] Write bundle-manifest.json (SHA256)
- [x] Commit all bundle files
- [x] Capture git/final-clean-proof.txt
- [x] Commit proof file
- [x] Confirm working tree clean
