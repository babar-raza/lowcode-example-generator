# Scripts Directory

Helper and operational scripts for the lowcode-example-generator pipeline.

## Key Operational Scripts

These scripts are actively used for pipeline operations:

| Script | Purpose |
|---|---|
| `run_live_publication.py` | Approval-gated live PR publication sprint |
| `run_final_publication_e2e.py` | End-to-end final publication validation |
| `run_final_publication_validators.py` | Run validators for final publication |
| `validate_published_examples_build.py` | Verify published examples still build with dotnet |
| `run_final_megasprint.py` | Full megasprint evidence and validation |
| `canonical_packager.py` | Generalized assembly of LowCode example packages |
| `fallback_reviewer.py` | Deterministic fallback reviewer for LowCode examples |
| `pilot_run.py` | Repeatable pilot run with diagnostic evidence |

## Full Script Index

### OPERATIONAL — Current pipeline operations

| Script | Purpose |
|---|---|
| `canonical_packager.py` | Generalized LowCode example package assembly |
| `cross_family_pipeline_matrix.py` | Cross-family AI pipeline proof matrix |
| `fallback_reviewer.py` | Deterministic fallback reviewer for examples |
| `pilot_run.py` | Repeatable pilot run with diagnostics |
| `run_final_megasprint.py` | Full megasprint evidence and validation run |
| `run_final_publication_e2e.py` | End-to-end final publication validation |
| `run_final_publication_validators.py` | Run validators for final publication |
| `run_live_publication.py` | Approval-gated live PR publication |
| `sync_taskcards.py` | Sync taskcard JSON matrix to markdown |
| `validate_published_examples_build.py` | Verify published examples build with dotnet |
| `write_taskcard_sync.py` | Write taskcard sync updates |

### UTILITY — Build, packaging, and development helpers

| Script | Purpose |
|---|---|
| `build_blocker_closure_zip.py` | Build blocker closure evidence ZIP |
| `build_bundle_manifest_sprint66.py` | Build bundle manifest for sprint 66 |
| `build_clean_packages.py` | Build clean example packages |
| `build_closure_repair_bundle.py` | Build closure repair evidence bundle |
| `build_content_audit_final.py` | Build final content audit |
| `build_destination_audit_sprint66.py` | Build destination audit for sprint 66 |
| `build_durable_closure_zip.py` | Build durable closure evidence ZIP |
| `build_final_closure_zip.py` | Build final closure evidence ZIP |
| `build_final_publication_bundle.py` | Build final publication evidence bundle |
| `build_final_publication_zip.py` | Build final publication evidence ZIP |
| `build_handoff_sprint66.py` | Build handoff bundle for sprint 66 |
| `build_mega_train_zip.py` | Build mega-train evidence ZIP |
| `build_multi_mega_train_zip.py` | Build multi mega-train evidence ZIP |
| `build_no_lowcode_registry.py` | Build registry of non-LowCode families |
| `build_pass3_zip.py` | Build pass 3 evidence ZIP |
| `build_pass4_multi_mega_train_zip.py` | Build pass 4 multi mega-train ZIP |
| `build_pass4_zip.py` | Build pass 4 evidence ZIP |
| `build_post_discovery_bundle.py` | Build post-discovery evidence bundle |
| `build_pub_closure_zip.py` | Build publication closure ZIP |
| `build_sprint65_contract.py` | Build sprint 65 contract artifacts |
| `build_sprint67_handoff.py` | Build sprint 67 handoff bundle |
| `build_sprint67_root_readmes.py` | Build sprint 67 root README files |
| `build_sprint91_bundle.py` | Build sprint 91 evidence bundle |
| `build_sysqual_repair_zip.py` | Build system qualification repair ZIP |
| `build_sysqual_zip.py` | Build system qualification evidence ZIP |
| `build_system_repair_zip.py` | Build system repair evidence ZIP |
| `build_systemization_26family_zip.py` | Build 26-family systemization ZIP |
| `build_systemization_pass2_zip.py` | Build systemization pass 2 ZIP |
| `build_systemization_pass3_zip.py` | Build systemization pass 3 ZIP |
| `build_true_closure_zip.py` | Build true closure evidence ZIP |

### SPRINT-HISTORICAL — One-time sprint scripts (preserved for audit trail)

| Script | Purpose |
|---|---|
| `add_taskcards_new19_28.py` | Add taskcards 19-28 for a sprint |
| `assemble_controlled_pilots.py` | Assemble controlled pilot packages |
| `assemble_pdf_pr10_pilot.py` | Assemble PDF PR10 pilot package |
| `build_healing_sprint_1_bundle.py` | Build healing sprint 1 evidence bundle |
| `build_healing_sprint_1b_bundle.py` | Build healing sprint 1b evidence bundle |
| `build_healing_sprint_1c_bundle.py` | Build healing sprint 1c evidence bundle |
| `build_healing_sprint_1d_bundle.py` | Build healing sprint 1d evidence bundle |
| `build_healing_sprint_1e_bundle.py` | Build healing sprint 1e evidence bundle |
| `build_healing_sprint_1f_bundle.py` | Build healing sprint 1f evidence bundle |
| `build_mega_train_evidence.py` | Generate all evidence for mega-train sprint |
| `build_mt005_bundle.py` | Build MEGA-TRAIN-005 evidence bundle |
| `closure_pipeline_proof.py` | Pipeline closure proof generation |
| `collect_lane2_lane4_evidence.py` | Collect lane 2 and lane 4 evidence |
| `ecc_sprint66.py` | ECC checks for sprint 66 |
| `ev_bootstrap_sprint66.py` | Evidence bootstrap for sprint 66 |
| `gen_lane3_evidence.py` | Generate lane 3 evidence |
| `gen_lane4_evidence.py` | Generate lane 4 evidence |
| `gen_source_hashes_sprint91.py` | Generate source hashes for sprint 91 |
| `mega_sprint_lane0_preflight.py` | Mega-sprint lane 0 preflight checks |
| `mega_sprint_lane1_audit.py` | Mega-sprint lane 1 prior bundle audit |
| `mega_sprint_lane2_discovery.py` | Mega-sprint lane 2 product universe discovery |
| `mega_sprint_lane3_e2e.py` | Mega-sprint lane 3 full E2E validation |
| `mega_sprint_lanes4_to_final.py` | Mega-sprint lanes 4-10 supervisor through final |
| `patch_completion_queue.py` | Patch completion queue entries |
| `patch_content_audit_sprint66.py` | Patch content audit for sprint 66 |
| `patch_final_closure.py` | Patch final closure artifacts |
| `publication_readiness_proof.py` | Publication readiness proof for MEGA-TRAIN-005 |
| `run_b1_restore_probe.py` | Run B1 restore probe check |
| `run_bad_bundle_checks.py` | Run bad bundle validation checks |
| `run_e1_idempotency_proof.py` | Run E1 idempotency proof |
| `run_e2e_recheck.py` | Re-run E2E checks |
| `run_ecc_durable_full_closure.py` | Run ECC for durable full closure |
| `run_ecc_final_publication.py` | Run ECC for final publication |
| `run_ecc_healing_sprint_1.py` | Run ECC for healing sprint 1 |
| `run_ecc_healing_sprint_1b.py` | Run ECC for healing sprint 1b |
| `run_ecc_mega_train.py` | Run ECC for mega-train sprint |
| `run_ecc_pass3.py` | Run ECC for pass 3 |
| `run_ecc_sprint91.py` | Run ECC for sprint 91 |
| `run_ecc_sysqual_repair.py` | Run ECC for system qualification repair |
| `run_final_closure_evidence.py` | Run final closure evidence generation |
| `run_pass3_a1_audit.py` | Pass 3 lane A1 audit |
| `run_pass3_b1_universe_policy.py` | Pass 3 lane B1 universe policy check |
| `run_pass3_b2_reflection.py` | Pass 3 lane B2 reflection check |
| `run_pass3_c1_design_docs.py` | Pass 3 lane C1 design documentation |
| `run_pass3_c1_generation.py` | Pass 3 lane C1 code generation |
| `run_pass3_d1_manifest_repair.py` | Pass 3 lane D1 manifest repair |
| `run_pass3_e1_idempotency.py` | Pass 3 lane E1 idempotency proof |
| `run_pass3_lanes_f_to_m.py` | Pass 3 lanes F through M |
| `run_pass4_a0_preflight.py` | Pass 4 lane A0 preflight |
| `run_pass4_a1_truth_normalization.py` | Pass 4 lane A1 truth normalization |
| `run_pass4_b1_catalog_hash.py` | Pass 4 lane B1 catalog hash |
| `run_pass4_b1_evidence.py` | Pass 4 lane B1 evidence generation |
| `run_pass4_evidence_c_to_h.py` | Pass 4 evidence lanes C through H |
| `run_pass4_lanes_i_to_l.py` | Pass 4 lanes I through L |
| `run_pdf_repair_pilot.py` | Run PDF repair pilot |
| `run_pub_closure_evidence.py` | Run publication closure evidence |
| `run_pub_proof_pass3.py` | Run publication proof pass 3 |
| `run_pub_proof_repair.py` | Run publication proof repair |
| `run_pub_proof_repair_pass2.py` | Run publication proof repair pass 2 |
| `run_system_repair_e2e.py` | Run system repair E2E validation |
| `run_true_closure_evidence.py` | Run true closure evidence generation |
| `sysqual_discovery.py` | System qualification discovery |
| `sysqual_iv_and_verdict.py` | System qualification IV and verdict |
| `sysqual_reports.py` | System qualification reports |
| `sysqual_support_reports.py` | System qualification support reports |

## Summary

| Category | Count |
|---|---|
| OPERATIONAL | 11 |
| UTILITY | 30 |
| SPRINT-HISTORICAL | 65 |
| **Total** | **106** |

SPRINT-HISTORICAL scripts are preserved for audit trail and evidence reproducibility. They are not part of current pipeline operations.
