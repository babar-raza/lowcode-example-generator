# Healing Sprint 1F -- Sprint 1E Rejection

## Rejection Basis

Healing Sprint 1E was NOT accepted due to dirty tracked files at ZIP build time.

### Blocker 1: Dirty tracked files at ZIP build time

`git status --short` at ZIP build time showed 5 modified tracked files:
```
 M reports/healing-sprint-1e/bundle-manifest.json
 M reports/healing-sprint-1e/commands.log
 M reports/healing-sprint-1e/final-verdict.md
 M reports/healing-sprint-1e/git/final-clean-proof.txt
 M reports/healing-sprint-1e/sprint-state.json
```

### Blocker 2: Uncommitted on-disk SHA updates

Sprint 1E's `final-clean-proof.txt` explicitly documented:
> "This proof is updated on disk (not committed) after Commit_1, before ZIP build."

Sprint 1E's `bundle-manifest.json` explicitly documented:
> "SHA-dependent fields updated on disk after Commit_1 (uncommitted)."

This means the ZIP contained uncommitted tracked-file content — content that diverged from the
committed repo state.

### Blocker 3: Self-reference loop (unresolvable in tracked files)

The attempted Sprint 1E convention tried to embed `final_commit_sha` into files that are
part of that same commit. This is self-referential and cannot be resolved:

- To write `final_commit_sha` into a tracked file, the file must be modified on disk.
- A modification on disk requires either: (a) committing the change (changing the SHA),
  or (b) leaving it uncommitted (dirty working tree).
- Path (a) creates a new SHA, invalidating the value just written.
- Path (b) produces dirty tracked files, which Sprint 1E attempted — and which is the
  defect that caused rejection.

**There is no way to embed the current commit's own SHA into a tracked file of that commit.**

## Root Cause

Sprint 1E applied the correct insight (no post-ZIP commits) but implemented it incorrectly
by modifying tracked files on disk after the final commit without committing those changes.
The ZIP captured uncommitted on-disk content, not the committed repo state.

## Sprint 1F Resolution

Sprint 1F adopts the MANDATORY ARTIFACT-STAGING CONVENTION:

1. Tracked repo evidence files are committed first.
2. No tracked repo file is modified after the final commit.
3. `final_commit_sha` is NOT embedded into tracked files (self-reference is impossible).
4. Build-time metadata is generated outside tracked files, into a gitignored staging area.
5. The ZIP includes generated artifact-only metadata:
   - `artifact-metadata/bundle-manifest.json` (contains `final_commit_sha`, `artifact_build_head_sha`)
   - `artifact-metadata/final-clean-proof.txt` (git state proof showing CLEAN tracked repo)
   - `artifact-metadata/artifact-verification.json` (convention compliance checks)
   - `artifact-metadata/zip-file-list.txt` (manifest of ZIP contents)
6. `git status --short` MUST show empty (CLEAN) immediately before ZIP build.
7. No commit occurs after ZIP build.
8. No tracked file modifications are allowed after final commit.

## What is preserved from Sprint 1E

The Sprint 1E ZIP facts that ARE valid (extracted facts, not convention):
- ZIP entries: 13
- manifest file_count: 13
- ECC 13/13
- canonical_overall_valid: true
- source_sha: 86f557c093152b6ff05ba7a666966e5d678f9b3b (correct)
- final_commit_sha: 3978659b18ba83404fb371ee8608c96142d7a068 (correct commit SHA)

These facts are preserved as inherited context. The rejection is about the artifact
convention, not the product work or machinery validation.

## Supersedes

- `reports/healing-sprint-1e/` — NOT accepted (dirty tracked files at artifact build)
- All prior healing sprints (1D, 1C, 1B, 1) — superseded by 1E which is superseded by 1F
