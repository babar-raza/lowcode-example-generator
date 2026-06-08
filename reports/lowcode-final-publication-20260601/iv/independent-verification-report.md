# Independent Verification Report

Sprint: lowcode-final-publication-20260601
Date: 2026-06-01
Decision Authority: AGENT_DELEGATED

## Classification
LOWCODE_FINAL_PUBLICATION_DECISION_COMPLETE_APPROVAL_BLOCKED

## Evidence Summary

### A. Preflight
- A0: Dirty state classified — no tracked files modified
- A1: Previous bundle audited — PROGRESS_ACCEPTED with 6 items resolved

### B. Decision Board
- 56 items with final agent decisions
- 44 PUBLISH (42 main-class + 1 companion + 1 environment-dependent)
- 12 EXCLUDE (4 duplicate + 3 not-a-main-class + 2 unsupported-format + 1 non-runnable-helper + 1 not-in-api-catalog + 1 upstream-bug)
- 0 human-deferred items

### C. Policies
- Main-class publication policy: WRITTEN
- Companion example policy: WRITTEN (1 companion: words/signer)
- Environment-dependent example policy: WRITTEN (1 env-dep: pdf/timestamp)
- Duplicate example policy: WRITTEN (4 duplicates excluded)

### D. Denominators
- Canonical: 42 main-class examples across 6 families
- Publishable: 44 (42 + 1 companion + 1 env-dep)
- E2E universe: 49 (all tested)
- Consistency: format-authority, completion queue, and E2E all agree on 42

### E. Package Artifacts
- 44 publishable examples manifested with Program.cs + .csproj
- All source snapshots included in ZIP

### F. Fixtures
- PFX: Runtime-only policy enforced, 4 static PFX removed (commit 97e1173)
- TSA: DigiCert endpoint documented, graceful degradation confirmed
- FormImporter: Upstream bug documented with retry condition

### G. E2E
- 49/49 PASS, 0 FAIL
- Output validation: all examples produce output files
- Per-example restore/build/run logs captured

### H. Tests
- pytest: 3222 passed, 18 skipped, 0 failed (335.20s)
- Raw log captured

### I. Validators
- 10/10 rules PASS
- V01-V10 all green

### J. Command Ledger
- 22 commands documented in central-command-ledger.json

### K. ZIP
- Path: .local/evidence-bundles/lowcode-final-publication-20260601-evidence.zip
- Entries: 335
- Size: 198,421 bytes
- SHA-256: eb56636f18bc4c314d5053d49bbee324c0c0f29be4bb177f49b244a46979683f
- 2-pass build with artifact-metadata included

## Resolved Rejections (from previous sprint)
| Previous Rejection | Resolution |
|---|---|
| Artifact metadata self-referential mismatch | 2-pass ZIP build: pass1 computes SHA, pass2 includes verification |
| No central command ledger | central-command-ledger.json with 22 entries |
| No separate package artifacts | package-manifest.json with 44 examples enumerated |
| Denominator model not publication-final | final-denominator-model.md with consistency check |
| Publication policy ambiguous | 4 policy documents written (main-class, companion, env-dep, duplicate) |
| Some blockers are classification decisions | All 56 items have final agent decisions, 0 deferred |

## Approval Gates
- PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL: NOT_SET
- PLUGIN_EXAMPLES_MERGE_PR_APPROVAL: NOT_SET
- No PRs created, no remote actions taken

## Verdict
LOWCODE_FINAL_PUBLICATION_DECISION_COMPLETE_APPROVAL_BLOCKED
All decisions made. All evidence collected. All validations pass.
Publication awaits approval gate activation.
