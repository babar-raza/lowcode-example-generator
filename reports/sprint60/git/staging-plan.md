# Sprint 60 Staging Plan

**Date:** 2026-05-21

## Planned Commits

### Commit 1: gitignore update (Phase 1)
**Files:** `.gitignore`
**Command:** `git add .gitignore && git commit`
**Purpose:** Add `reports/**/*.zip` pattern to exclude binary evidence archives from git tracking. This resolves the untracked `reports/sprint59/00-sprint58-evidence-audit.zip`.

### Commit 2: Source changes — destination id mapping fix + README gate + evidence validator (Phases 2–5)
**Files:** Source files in `src/plugin_examples/` and test files
**Command:** `git add -u {exact paths} && git commit`
**Purpose:** Implement destination scenario-id mapper fixes, README gate wiring, evidence validator hardening.

### Commit 3: workspace/verification/latest updates (Phases 2–5)
**Files:** `workspace/verification/latest/**` (modified tracked files only via `git add -u`)
**Purpose:** Promote updated audit results after destination gap closure.

### Commit 4: Sprint 60 final evidence bundle (Phase 10)
**Files:** `reports/sprint60/`
**Command:** `git add reports/sprint60/ && git commit`
**Purpose:** Final Sprint 60 closure bundle.

## Rules
- No `git add .`
- No `git reset --hard`
- No `git clean`
- Exact-path staging only
- Source and workspace separated from evidence reports
- Final clean proof captured AFTER commit 4
