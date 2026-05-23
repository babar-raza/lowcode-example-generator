# Sprint 75 — Staging Plan

**Date:** 2026-05-23

## Files to Stage (exact paths)

### Sprint 75 bundle directory
```
reports/sprint75/
```
All files under `reports/sprint75/` will be staged by exact path at bundle commit time.
No broad `git add .` will be used.

## Files Explicitly Excluded From Staging

| File | Reason |
|------|--------|
| workspace/verification/latest/cells-readme-backfill-simulation.json | Runtime-generated; not sprint75 artifact |
| workspace/verification/latest/cells-root-readme-audit.json | Runtime-generated; not sprint75 artifact |
| workspace/verification/latest/cells-root-readme-render-result.json | Runtime-generated; not sprint75 artifact |
| workspace/verification/latest/release-status.json | Runtime-generated; not sprint75 artifact |
| workspace/verification/latest/words-readme-backfill-simulation.json | Runtime-generated; not sprint75 artifact |
| workspace/verification/latest/words-root-readme-audit.json | Runtime-generated; not sprint75 artifact |
| workspace/verification/latest/words-root-readme-render-result.json | Runtime-generated; not sprint75 artifact |

## Commands to be Used at Commit Time

```bash
# Stage exact sprint75 bundle paths
git add reports/sprint75/

# Commit with message
git commit -m "feat(sprint75): ..."

# Verify
git status
```

## Not Used
- `git add .` — PROHIBITED
- `git add -A` — PROHIBITED
- `git reset --hard` — PROHIBITED
- `git clean` — PROHIBITED
