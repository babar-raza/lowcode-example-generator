# Pipeline Parity Architecture

Date: 2026-06-08

## Core Principle

Only candidate discovery differs between LowCode and non-LowCode pipelines.
After discovery, both pipelines use identical downstream stages.

## Discovery Methods

| Pipeline | Discovery Method | Field |
|----------|-----------------|-------|
| LowCode | namespace_scan | PluginDetection.namespace_patterns |
| Non-LowCode | capability_registry_fallback | PluginDetection.fallback_strategy |

## Shared Downstream Stages

1. canonical_identity_verification
2. fixture_acquisition
3. example_generation
4. readme_generation
5. manifest_generation
6. expected_output_generation
7. restore_build_run_validation
8. output_validation
9. pr_packet_generation
10. target_repo_publication
11. pr_creation
12. pr_review_merge_lifecycle
13. branch_deletion_after_merge
14. state_registry_update
15. evidence_bundle
16. external_sidecar_final_attestation
17. independent_verification

## Wave 22 Changes

- PluginDetection: +discovery_method, +target_repo, +branch_prefix, +effective_discovery_method, +effective_branch_prefix
- PLV-01..15 validators added
- All 13 per-example READMEs enhanced with purpose/prerequisites/expected output
- Branch naming policy ADR written
- PR lifecycle governance documented
- Branch cleanup approval packets prepared
