# Sprint 66 Todo

Sprint: sprint66-remote-truth-repair-self-contained-artifacts-readme-io-publication-proof
Date: 2026-05-22

## Phase 0 — Reopen Sprint 65 / State Audit

- [x] Create reports/sprint66/ directory structure
- [x] Write reports/sprint66/00-sprint65-evidence-audit.md
- [x] Write reports/sprint66/01-sprint65-claim-vs-proof-matrix.md
- [x] Write reports/sprint66/02-corrected-sprint65-state.md
- [x] Write reports/sprint66/todo.md
- [x] Write reports/sprint66/commands.log
- [x] Write reports/sprint66/evidence-contract.json

## Phase 1 — Remote Truth Discovery

- [x] Fetch actual remote directory listings for all 6 repos
- [x] Fetch PR history for all 6 repos
- [x] Check remote README I/O status (sample)
- [x] Fetch README content + SHA for all 42 remote examples
- [x] Fetch Program.cs content + SHA for all 42 remote examples
- [x] Build per-PR per-example coverage map
- [x] Write reports/sprint66/remote/remote-repo-state.json
- [x] Write reports/sprint66/remote/remote-example-inventory.json
- [x] Write reports/sprint66/remote/remote-readme-io-audit.json
- [x] Write reports/sprint66/remote/remote-pr-proof-index.json
- [x] Write reports/sprint66/remote/remote-proof-summary.md

## Phase 2 — Repair Remote Proof / Publication Status Model

- [x] Build 11-field per-example publication state model
- [x] Classify all 42 examples
- [x] Write reports/sprint66/publication/publication-state-model.md
- [x] Write reports/sprint66/publication/publication-truth-matrix-final.json
- [x] Write reports/sprint66/publication/publication-summary.md

## Phase 3 — Self-Contained Package Artifacts

- [x] Copy sprint64 packages into reports/sprint66/handoff/per-family/ for all 6 families
- [x] Verify no obj/bin in packages
- [x] Create PR title/body drafts for all 6 families
- [x] Write reports/sprint66/handoff/publication-handoff-index.json
- [x] Write reports/sprint66/handoff/package-artifact-hashes.json
- [x] Write reports/sprint66/handoff/self-contained-artifact-validation.md

## Phase 4 — Final Destination Audit Repair

- [x] Repair output_kind for pdf-html-converter, pdf-pdfa-converter, pdf-text-extractor
- [x] Add missing fields: remote_path, remote_status, local_package_status
- [x] Write reports/sprint66/destination/content-audit-final.json
- [x] Write reports/sprint66/destination/programcs-vs-authority-final.json
- [x] Write reports/sprint66/destination/readme-vs-authority-final.json
- [x] Write reports/sprint66/destination/remote-vs-package-final.json
- [x] Write reports/sprint66/destination/deep-audit-summary.md

## Phase 5 — README I/O Publication Package

- [x] Write reports/sprint66/publication/live-approval-check.md
- [x] Write reports/sprint66/publication/pr-package-ledger.json
- [x] Write reports/sprint66/publication/live-publication-result.json
- [x] Write reports/sprint66/publication/post-merge-verification.json
- [x] Write reports/sprint66/publication/branch-delete-result.json

## Phase 6 — Harden EV/ECC

- [x] Add 10 new EV rules (33-42) to evidence_validator.py
- [x] Update ECC semantic checks in evidence_contract_computer.py
- [x] Write reports/sprint66/evidence/validator-gap-analysis.md
- [x] Write reports/sprint66/evidence/validator-source-proof.patch
- [x] Write reports/sprint66/evidence/validator-test-results.txt
- [x] Write reports/sprint66/evidence/sprint65-revalidation-result.json
- [x] Write reports/sprint66/evidence/sprint66-final-validation-result.json
- [x] Write reports/sprint66/evidence/evidence-contract-computed.json

## Phase 7 — Testing

- [x] Run full unit test suite
- [x] Write reports/sprint66/lanes/lane-I/test-run.log

## Phase 8 — Final Bundle

- [x] Capture final-clean-proof.txt
- [x] Write reports/sprint66/bundle-manifest.json (SHA256)
- [x] Write reports/sprint66/final-verdict.md
- [x] Write reports/sprint66/sprint-state.json
- [x] Commit
