# Sprint 66 — EV/ECC Validator Gap Analysis

Generated: 2026-05-22
Sprint: sprint66-remote-truth-repair-self-contained-artifacts-readme-io-publication-proof

## Sprint 65 Validator Gaps (What Rules Were Missing)

Sprint 65 had 32 EV rules. Sprint 66 adds 10 new rules (33-42) to catch the 5 Sprint 65 blockers.

| New Rule | rule_id | Catches |
|----------|---------|---------|
| 33 | remote_proof_per_example_not_overclaimed | S65-D1: PR #6/PR #4 claimed all examples but covered 1 each |
| 34 | remote_proof_has_content_hashes | S65-D1: proof had only PR numbers, no per-example README/Program.cs SHAs |
| 35 | remote_readme_io_audit_present | S65-D2: no remote README I/O audit was performed |
| 36 | handoff_bundle_not_empty | S65-D3: handoff/per-family/ was empty despite "HANDOFF_READY" verdict |
| 37 | content_audit_output_kind_not_blank | S65-D4: output_kind blank for 3 PDF examples |
| 38 | publication_state_not_mixed | S65-D5: "published" + "approval_blocked" without separate state fields |
| 39 | remote_proof_not_workspace_only | S65-D1: remote-proof-index.json referenced workspace/ files not in bundle |
| 40 | root_readme_and_package_both_present | S65-D3: root READMEs present but package artifacts absent |
| 41 | remote_readme_io_not_overclaimed | S65-D2: verdict must not claim I/O published if remote audit shows 0 |
| 42 | handoff_all_examples_have_io_section | S65-D3: all handoff READMEs must have I/O section |

## Sprint 65 Revalidation Results

Sprint 65 bundle under Sprint 66 rules:
- total_rules: 42
- passed: 33
- failed: 9
- overall_valid: False

Failed rules map to 5 Sprint 65 blockers:
- S65-D1 (PR overclaim): rules 33, 34, 39 → 3 failures
- S65-D2 (remote README): rules 35, 41 → 1 failure (41 passed since no overclaim in S65 verdict text)
- S65-D3 (handoff empty): rules 36, 40, 42 → 3 failures
- S65-D4 (output_kind blank): rule 37 → 1 failure
- S65-D5 (mixed state): rule 38 → 1 failure

## ECC Additions

ECC semantic rule for "42 entries with scenario_id and output_kind and output_format and api_type":
Added `output_kind` check — returns SEMANTIC_FAILED if any record has blank output_kind.
This catches Sprint 65 defect S65-D4 at the ECC layer.

## Sprint 66 Rule Total

| Category | Rules |
|----------|-------|
| Sprint 60-61 original rules | 1-20 |
| Sprint 62 rule (bundle_validation_result_present_and_valid) | 21 |
| Sprint 64 rule (ecc_contract_computed_and_valid) | 22 |
| Sprint 65 rules (content audit, root README, special cases, remote proof) | 23-32 |
| Sprint 66 rules (remote truth, handoff, output_kind, mixed state) | 33-42 |
| **TOTAL** | **42** |
