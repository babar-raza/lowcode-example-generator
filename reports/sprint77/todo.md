# Sprint 77 TODO

## Phase 0 — Sprint 76 Audit [DONE]
- [x] Create 00-sprint76-evidence-audit.md
- [x] Create 01-sprint76-claim-vs-proof-matrix.md
- [x] Create 02-corrected-sprint76-state.md

## Phase 1 — Handle Untracked output.pptx [DONE]
- [x] Copy output.pptx to reports/sprint77/post-merge-runtime/artifacts/
- [x] Create slides-compress-output-artifact-decision.md
- [x] Create slides-compress-output-artifact-hash.json
- [x] Remove original untracked file (working tree clean)

## Phase 2 — Raw Final Git Status Proof [DONE]
- [x] Capture dirty-state-before.txt (raw git status)
- [x] Create dirty-file-classification.md
- [x] Capture dirty-state-after.txt (post-commit)
- [x] Create final-clean-proof.txt with embedded raw git output

## Phase 3 — Commands Log Repair [DONE]
- [x] Write complete commands.log with no PENDING entries

## Phase 4 — EV Hardening (Rules 102-105) [DONE]
- [x] Add commands_log_no_pending (Rule 102)
- [x] Add final_clean_proof_has_raw_git_lines (Rule 103)
- [x] Add dirty_state_untracked_acknowledged (Rule 104)
- [x] Add validation_authority_unambiguous (Rule 105)
- [x] Update tests (TestSprint77EvidenceConsistencyRules)
- [x] Sprint 76 correctly fails all 4 new rules

## Phase 5 — Preserve Sprint 76 Technical Repair [DONE]
- [x] Create slides-compress-runtime-validation.md (carry forward)
- [x] Create post-merge-validation-matrix.json
- [x] Create weekly-review-claim-vs-proof-final.md

## Phase 6 — Publication Check [DONE]
- [x] Check PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL — NOT_SET
- [x] Create live-approval-check.md

## Phase 7 — Test Suite [DONE]
- [x] Run full test suite
- [x] Capture test-run.log

## Phase 8 — Final Evidence Bundle [DONE]
- [x] Run ECC (31/31)
- [x] Run EV Phase A + Phase B
- [x] Commit sprint77 bundle
- [x] Capture post-commit dirty-state-after.txt
- [x] Capture final-clean-proof.txt with raw git output
- [x] Second commit for proof files
