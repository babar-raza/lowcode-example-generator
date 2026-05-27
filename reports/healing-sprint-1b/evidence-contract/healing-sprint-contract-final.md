# Healing Sprint 1B — Lane 5: Final Healing Sprint Contract

**Lane:** 5 — Validator / Evidence Contract Hardening
**Date:** 2026-05-27

## Contract Template for Future Healing Sprints

Any future healing sprint MUST include these categories:

| # | Category | Description | Required |
|---|---|---|---|
| 1 | baseline | Prior sprint baseline confirmation | YES |
| 2 | sprint_audit | Audit of prior sprint blockers | YES |
| 3 | plan | Sprint plan with stop conditions | YES |
| 4 | overlap_check | File ownership matrix | YES |
| 5 | git_dirty_before | Git state before sprint | YES |
| 6 | git_dirty_after | Git state after dirty-file resolution | YES |
| 7 | dirty_classification | Classification of each dirty file | YES |
| 8 | git_final_proof | Final-clean-proof.txt (post-commit, no placeholders) | YES |
| 9 | sha_authority | SHA chain document | YES |
| 10 | proof_repair_report | Evidence consistency repair report | YES |
| 11 | taskcard_final | Final taskcard with all tasks DONE | YES |
| 12 | next_gate_register | Outstanding gates | YES |
| 13 | state_sync | Cross-sprint state consistency | YES |
| 14 | replay_automation | Automated regression checks for known patterns | YES |
| 15 | gate_simulation | Approval gate no-op proof | YES |
| 16 | dry_run | Local machinery dry-run result | YES |
| 17 | validator_gap | Validator audit and gap analysis | YES |
| 18 | ecc_computed | Evidence contract computed results | YES |
| 19 | healing_validation | Healing validation result | YES |
| 20 | iv_report | Independent verification report | YES |
| 21 | adversarial_review | Adversarial review | YES |
| 22 | final_verdict | Final verdict | YES |
| 23 | sprint_state | Sprint state JSON | YES |
| 24 | bundle_manifest | Bundle manifest | YES |
| 25 | bundle_zip | Evidence ZIP bundle | YES |

## Key Rules (from PROOF-TEMPLATE-001 and Sprint 1B experience)

1. `final-clean-proof.txt` must NOT contain "will be updated", "will be committed",
   "[to be captured]", or "[to be set after]" in ANY committed version.
2. `bundle-manifest.json` `head_sha` must be the FINAL 3-commit HEAD (step 3 SHA),
   not the intermediate step-2 SHA.
3. All SHA values in manifests must be verifiable via `git cat-file -t`.
4. `source-diff.patch` must be non-zero bytes.
5. `taskcard-state-audit.md` must be written AFTER all tasks complete (not during).
6. Bundle ZIP must be rebuilt AFTER the 3-commit sequence completes.
7. Dirty tracked files must be committed or formally deferred before final proof.

## Lane 5 Verdict

**LANE_5_CONTRACT_COMPLETE** — Contract template established. All key rules documented.
