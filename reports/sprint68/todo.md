# Sprint 68 Todo

Sprint: sprint68-pdf-readme-splitter-cardinality-content-audit-repair

## Phase 0: Sprint 67 Audit and Reopen

- [x] Create reports/sprint68/00-sprint67-evidence-audit.md
- [x] Create reports/sprint68/01-sprint67-claim-vs-proof-matrix.md
- [x] Create reports/sprint68/02-corrected-sprint67-state.md
- [x] Create reports/sprint68/todo.md
- [x] Create reports/sprint68/commands.log
- [x] Create reports/sprint68/evidence-contract.json
- [x] Classify all 5 Sprint 67 defects (S67-D1 through S67-D5)

## Phase 1: Exact Legacy Reconciliation (S67-D2)

- [x] Audit all 6 family contracts for splitter output_cardinality field
- [x] Create legacy-reconciliation/splitter-cardinality-matrix.json (per-type: contract vs Program.cs)
- [x] Determine correct resolution for each splitter (single-file extraction = valid or multi-output required)
- [x] Create legacy-reconciliation/splitter-resolution.md (per-type decision + rationale)
- [x] Create legacy-reconciliation/cardinality-reconciliation-final.json
- [x] Update reconciliation-index.md to include splitter per-type decisions

## Phase 2: PDF Root README Repair (S67-D1)

- [x] Read all 19 PDF handoff Program.cs files to extract I/O data
- [x] Create root-readme/pdf-readme-row-data.json (19 entries: type, input, output, operation)
- [x] Write reports/sprint68/root-readme/per-family/pdf-root-readme.md with 19/19 rows
- [x] Carry forward all other 5 family root READMEs from sprint67 (unchanged)
- [x] Create root-readme/pdf-readme-fix-proof.md

## Phase 3: Canonical Content Audit (S67-D3)

- [x] Read destination/content-audit-final.json — identify all stale records
- [x] Read destination/content-audit-sprint67.json — confirm sprint67 schema
- [x] Create destination/content-audit-sprint68.json (42 entries, all sprint68 paths, no stale versions)
- [x] Create destination/content-audit-unification-proof.md (content-audit-final.json retired)

## Phase 4: PDF Version Final Proof (S67-D4)

- [x] Read handoff PDF family Directory.Packages.props for version reference
- [x] Read sprint67 PDF handoff Program.cs files for Aspose.PDF using directive
- [x] Create version/pdf-version-proof-chain.md (package ref → 26.5.0 chain of evidence)
- [x] Update content-audit-sprint68.json PDF records to version 26.5.0

## Phase 5: EV/ECC Hardening (5 new rules)

- [x] Add EV rule 53: pdf_root_readme_complete (>=19 rows in PDF root README)
- [x] Add EV rule 54: splitter_cardinality_reconciled (splitter-resolution.md must exist)
- [x] Add EV rule 55: canonical_content_audit_no_stale_pdf_version (no PDF 26.4.0 in sprint content audit)
- [x] Add EV rule 56: pdf_version_proof_chain_present (version/pdf-version-proof-chain.md must exist)
- [x] Add EV rule 57: all_family_cardinality_display_validated (words README must have ×N/2× markers)
- [x] Create evidence/ev-rule-change-log.md
- [x] Create evidence/ev-source-proof.patch (git diff of evidence_validator.py)
- [x] Update test_evidence_validator.py: add sprint68 artifacts to _make_bundle, update counts to 57/56
- [x] Update test_pipeline_evidence_gate.py: add sprint68 artifacts to _make_valid_bundle
- [x] Run EV tests — 84 passed, 0 failed
- [x] Write evidence/sprint67-revalidation-result.json (sprint67 under sprint68 rules: 3 failures)

## Phase 6: Sprint 68 Self-Contained Handoff

- [x] Copy sprint67 handoff/per-family/ to reports/sprint68/handoff/per-family/
- [x] Update all handoff-index.json paths from sprint67 → sprint68
- [x] Create handoff/handoff-index.json (42 examples, 6 families)
- [x] Create handoff/path-normalization-proof.md (no sprint64/sprint66/sprint67 path refs)

## Phase 7: Remote Truth Refresh

- [x] Carry forward sprint67 remote artifacts (no new PRs in interval)
- [x] Create remote/remote-repo-state.json (carried forward)
- [x] Create remote/remote-example-inventory.json (carried forward)
- [x] Create remote/remote-readme-io-audit.json (carried forward)
- [x] Create remote/remote-proof-summary.md

## Phase 8: Live Publication Check

- [x] Check for APPROVE_LIVE_PR token in environment (NOT_SET)
- [x] Create publication/live-publication-check.md (BLOCKED_BY_APPROVAL)
- [x] Create publication/publication-state-model.md

## Phase 9: Full Test Run

- [x] Run full test suite
- [x] Capture logs/test-run.log
- [x] Confirm 0 failed, >=2993 passed (actual: 3025 passed, 0 failed)

## Phase 10: Final Evidence Bundle

- [x] Run EV Phase A bootstrap
- [x] Write evidence/sprint68-bundle-validation-result.json
- [x] Seed evidence-contract-computed.json for ECC self-reference
- [x] Run ECC → write evidence-contract-computed.json
- [x] Run EV Phase B (all rules)
- [x] Write evidence/sprint68-final-validation-result.json
- [x] Write final-verdict.md
- [x] Write sprint-state.json
- [x] Write bundle-manifest.json (SHA256)
- [x] Commit all bundle files
- [x] Capture git/final-clean-proof.txt
- [x] Commit proof file
- [x] Confirm working tree clean
