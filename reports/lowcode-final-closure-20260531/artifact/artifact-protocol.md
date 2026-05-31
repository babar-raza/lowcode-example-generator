# Artifact Protocol — lowcode-final-closure-20260531

Sprint 1F+ convention:
1. Tracked files committed first (pre-commit: B1 fixes, G1 fixes)
2. Evidence collected to reports/ (untracked new sprint files)
3. Evidence committed (git add -f reports/lowcode-final-closure-20260531/)
4. ZIP built AFTER final commit (build_final_closure_zip.py)
5. Sidecar .sha256 and .size-count.json written OUTSIDE ZIP
6. No commit after ZIP build
7. ZIP SHA NOT embedded in tracked files (no circular reference)
