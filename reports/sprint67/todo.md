# Sprint 67 Todo

Sprint: sprint67-final-pre-publication-repair-legacy-plan-reconciliation-readme-io-live-pr-readiness

## Phase 0: Sprint 66 Audit and Reopen

- [x] Create reports/sprint67/00-sprint66-evidence-audit.md
- [x] Create reports/sprint67/01-sprint66-claim-vs-proof-matrix.md
- [x] Create reports/sprint67/02-corrected-sprint66-state.md
- [x] Create reports/sprint67/todo.md
- [x] Create reports/sprint67/commands.log
- [x] Create reports/sprint67/evidence-contract.json
- [x] Classify all 18 Sprint 66 claims in matrix

## Phase 1: Legacy Plan Reconciliation

- [x] Read Sprint 62 format-capability plan details
- [x] Read Sprint 61 README sync plan details
- [x] Create legacy-plan-reconciliation/reconciliation-index.md
- [x] Create legacy-plan-reconciliation/sprint62-format-capability-plan.md
- [x] Create legacy-plan-reconciliation/sprint61-readme-sync-plan.md
- [x] Create legacy-plan-reconciliation/items-already-proven.json
- [x] Create legacy-plan-reconciliation/items-to-carry-forward.json
- [x] Create legacy-plan-reconciliation/items-superseded.json
- [x] Create legacy-plan-reconciliation/items-contradicted.json

## Phase 2: Root README Cardinality Repair (S66-D1)

- [x] Audit all 6 format-authority contracts for cardinality data
- [x] Audit all 6 root READMEs for current display
- [x] Create root-readme/cardinality-audit.json
- [x] Update cells-root-readme.md with merger (N→1) and splitter (1→N) markers
- [x] Update words-root-readme.md with merger/splitter cardinality
- [x] Update pdf-root-readme.md with merger/splitter/extractor cardinality
- [x] Update diagram-root-readme.md (check contracts for cardinality)
- [x] Update email-root-readme.md (check contracts for cardinality)
- [x] Update slides-root-readme.md (check contracts for cardinality)
- [x] Create root-readme/cardinality-fix-proof.md

## Phase 3: PDF Version Decision (S66-D2)

- [x] Confirm handoff PDF version (Directory.Packages.props)
- [x] Confirm content-audit PDF version records
- [x] Create version/pdf-version-decision.md (Path A: 26.5.0 canonical)
- [x] Create version/version-truth-matrix.json
- [x] Create version/version-policy-final.json
- [x] Update content-audit records if version decision requires it

## Phase 4: Sprint 67 Self-Contained Handoff (S66-D3)

- [x] Create handoff directory for sprint67 (per-family packages)
- [x] Copy/reference 42 corrected packages to reports/sprint67/handoff/
- [x] Create destination/content-audit-sprint67.json with sprint67 paths
- [x] Create handoff/handoff-index.json
- [x] Create handoff/path-normalization-proof.md (no sprint64/sprint66 refs)

## Phase 5: Operation-Kind/Cardinality Test Hardening

- [x] Create tests/unit/test_operation_kind_cardinality_matrix.py
- [x] Create tests/unit/test_readme_io_cardinality_display.py
- [x] Create tests/unit/test_contract_vs_constraints_semantics.py
- [x] Create tests/unit/test_destination_programcs_operation_semantics.py
- [x] Run new tests and confirm all pass

## Phase 6: README Sync Architecture IV Verification

- [x] Review readme_facts.py and readme_auditor.py current state
- [x] Create readme-sync/architecture-review.md
- [x] Create readme-sync/gap-analysis.md
- [x] Create readme-sync/sync-state.json
- [x] Create readme-sync/sync-proof.md

## Phase 7: Remote Truth Refresh

- [x] Refresh remote repo state via GitHub API
- [x] Create remote/remote-repo-state.json
- [x] Create remote/remote-example-inventory.json
- [x] Create remote/remote-readme-io-audit.json
- [x] Create remote/remote-proof-summary.md

## Phase 8: Live Publication Check (S66-D4)

- [x] Check for APPROVE_LIVE_PR token in environment
- [x] Create publication/live-publication-check.md
- [x] If token present: create PRs and record results
- [x] If token absent: document BLOCKED state with next-step plan
- [x] Create publication/publication-state-model.md

## Phase 9: EV/ECC Hardening (10 new rules)

- [x] Add EV rule: root_readme_cardinality_annotated
- [x] Add EV rule: root_readme_merger_shows_n_to_1
- [x] Add EV rule: root_readme_splitter_shows_1_to_n
- [x] Add EV rule: pdf_version_consistent_handoff_vs_audit
- [x] Add EV rule: no_cross_sprint_path_leakage
- [x] Add EV rule: legacy_plans_reconciled
- [x] Add EV rule: handoff_paths_sprint67_only
- [x] Add EV rule: version_decision_record_present
- [x] Add EV rule: cardinality_audit_json_present
- [x] Add EV rule: sprint67_bundle_validation_present_and_valid
- [x] Create evidence/ev-rule-change-log.md
- [x] Create evidence/ev-source-proof.patch
- [x] Create evidence/ev-test-results.txt
- [x] Create evidence/sprint67-revalidation-result.json (sprint66 under new rules)
- [x] Run ECC and write evidence-contract-computed.json

## Phase 10: Full Test Run

- [x] Run full test suite
- [x] Capture logs/test-run.log
- [x] Confirm 0 failed, >=2993 passed

## Phase 11: Final Evidence Bundle

- [x] Run EV Phase A bootstrap
- [x] Write evidence/sprint67-bundle-validation-result.json
- [x] Seed evidence-contract-computed.json for ECC self-reference
- [x] Run ECC → write evidence-contract-computed.json
- [x] Run EV Phase B (all rules)
- [x] Write evidence/sprint67-final-validation-result.json
- [x] Write final-verdict.md
- [x] Write sprint-state.json
- [x] Write bundle-manifest.json (SHA256)
- [x] Commit all bundle files
- [x] Capture git/final-clean-proof.txt
- [x] Commit proof file
- [x] Confirm working tree clean
