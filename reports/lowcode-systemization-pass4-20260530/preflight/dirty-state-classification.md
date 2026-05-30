# Dirty State Classification — lowcode-systemization-pass4-20260530
Date: 2026-05-30

## Summary
- Total tracked dirty files: 30
- bin/obj build artifacts: 30
- Non-bin/obj dirty files: 0
- Untracked files: .kilo/ (irrelevant to sprint)

## Classification

### bin/obj Build Artifacts (30 files)
These are compiled binaries tracked from prior E2E runs in workspace/pr-dry-run:
- workspace/pr-dry-run/diagram-controlled-pilot/examples/.../bin/Debug/net8.0/diagram-converter.dll
- workspace/pr-dry-run/email-controlled-pilot/examples/.../bin/Debug/net8.0/email-converter.dll
- (and associated .exe, .pdb, obj/ artifacts)

**Classification:** KNOWN_BUILD_ARTIFACT_DRIFT
**Resolution:** These are dirty because E2E runs (from prior sprints) modified them.
They are tracked by git (committed in prior sprints). They will NOT be committed in pass4
as they are build artifacts, not source files. They do NOT affect canonical generation,
packaging, or evidence integrity for pass4 — pass4 uses isolated workspace roots.

### Non-bin/obj dirty files (0 files)

## Resolution
1. bin/obj artifacts: CLASSIFIED_ACCEPTABLE — not committed, not part of fresh pass4 evidence
2. Non-bin/obj: NONE — clean
3. pass4 uses isolated workspace roots (workspace/runs/pass4-*) — no stale workspace reads
4. Tracked dirty files will be 0 (excluding bin/obj) before final artifact build

## Pass3 Dirty State Root Cause
Pass3 final-clean-proof showed 30 tracked dirty files — all are bin/obj artifacts from
E2E runs in workspace/pr-dry-run. These were tracked in prior sprints via git add -f.
Pass4 will NOT re-commit these files and will use isolated workspaces.
