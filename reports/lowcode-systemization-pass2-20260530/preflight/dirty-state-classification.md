# Dirty State Classification — lowcode-systemization-pass2-20260530

**Date:** 2026-05-30
**Sprint ID:** lowcode-systemization-pass2-20260530

## Modified Tracked Files (30 total)

All 30 modified tracked files are binary build artifacts in `workspace/pr-dry-run/*/bin/Debug` and `workspace/pr-dry-run/*/obj/Debug`.

These are .dll, .exe, .pdb, .cache, and generated .cs files produced by `dotnet build` during prior sprint E2E runs. They are tracked from prior sprints (committed before the `.gitignore` exclusion policy was established) but are rebuilt each time examples are built.

**Classification: KNOWN_BINARY_BUILD_ARTIFACTS — EXCLUDED FROM SPRINT SCOPE**

Affected packages:
- `diagram-controlled-pilot` (10 files)
- `email-controlled-pilot` (10 files)
- (remaining 10 across other packages)

**Policy:** Per artifact-staging convention, these binary artifacts will NOT be re-staged or committed in this sprint. They are excluded from the clean-tree check in all ZIP build scripts.

## Untracked Files (3 items)

| Path | Classification |
|------|---------------|
| `.kilo/` | IDE configuration (VSCode/Kilo) — not committed |
| `docs/development/open-taskcard-closure-matrix.md` | Stale prior-sprint doc — not committed |
| `reports/lowcode-systemization-pass2-20260530/` | This sprint's reports — will be committed at sprint end |

## Verdict

**No source-level modifications at sprint start.** Working tree is clean for sprint source files. Sprint proceeds on a clean tracked-source baseline.
