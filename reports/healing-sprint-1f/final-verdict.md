# Healing Sprint 1F -- Final Verdict

## Verdict

**LOWCODE_MACHINERY_HEALING_ACCEPTED**

## Summary

Healing Sprint 1F adopts the MANDATORY ARTIFACT-STAGING CONVENTION, resolving all Sprint 1E
defects. The tracked repo is committed clean. Artifact-only metadata (including
`final_tracked_commit_sha` and `artifact_build_head_sha`) is generated outside tracked files
and included in the ZIP under `artifact-metadata/`.

## Convention Applied

| Property | Value |
|----------|-------|
| source_sha (pre-1F HEAD) | 3978659b18ba83404fb371ee8608c96142d7a068 |
| final_tracked_commit_sha | see artifact-metadata/bundle-manifest.json |
| artifact_build_head_sha | see artifact-metadata/bundle-manifest.json |
| tracked_repo_clean_before_artifact_build | TRUE |
| no tracked file modified after final commit | TRUE |
| no post-ZIP commit | TRUE |
| final_commit_sha in tracked files | FALSE (self-reference avoided) |

## Sprint 1E Defects Resolved

1. Dirty tracked files at ZIP build time → RESOLVED (git status CLEAN before build) ✓
2. Uncommitted on-disk SHA updates → RESOLVED (no tracked file changes after commit) ✓
3. Self-reference loop (embed commit SHA into own tracked files) → RESOLVED (SHA in artifact-metadata only) ✓
4. `bundle-manifest.json` documenting uncommitted convention → RESOLVED ✓
5. `final-clean-proof.txt` showing dirty tracked state → RESOLVED (proof shows CLEAN) ✓

## Inherited Machinery Results

- EV: 145/145 (Sprint 91 authority)
- Sprint 1C machinery verdict: LOWCODE_MACHINERY_HEALING_ACCEPTED
- Sprint 1B replay: 7 pass / 0 fail / 2 skip
- Dry run: 41 PR candidates, 42 truth records, 6 families
- Tests: 3189 (Sprint 89 committed)
- Candidate discovery: EXHAUSTED
- Publication matrix: 42 records (cells:9, words:7, pdf:19, diagram:2, email:1, slides:3)

## ECC

- 10/10 tracked evidence categories PRESENT
- closure_valid: true
- validation: canonical_overall_valid=true, applicable_rules_failed=0

## Publication Gate

PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL: NOT SET → APPROVAL_BLOCKED
No PR creation or live publication action taken.

## Supersedes

- `reports/healing-sprint-1e/` — NOT accepted (dirty tracked files at artifact build)
- All prior healing sprints (1D, 1C, 1B, 1) — superseded chain
