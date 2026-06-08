# Healing Repair Taskcards

## Loop 1 (Applied — all 7 defects repaired)

### TC-HEAL-001: Source Evidence
- Create source/snapshot-manifest.json with real SHA256 for 38 source/test/probe files
- Run git diff for modified files; save to source/source-diffs.patch (166 lines)
- Create source/changed-files-list.json
- Status: DONE

### TC-HEAL-002: Raw Test Logs
- Run 10 test files individually via subprocess; capture to tests/raw/*.log
- Build tests/test-summary.json from parsed log results
- Status: DONE — 94 tests, all pass

### TC-HEAL-003: Command Ledger
- Run all key commands (git diff, pytest, ruff) via subprocess
- Capture stdout/stderr per command to commands/stdout-stderr/
- Build command-index.json with 16 entries + timestamps + exit codes
- Status: DONE

### TC-HEAL-004: Bundle Hygiene
- Define evidence/bundle-hygiene-policy.md
- Enumerate 59 excluded files (bin/obj/.dll/.exe/.pdb)
- Build clean ZIP without binaries in MEGA-TRAIN-H
- Status: DONE

### TC-HEAL-005: Complete Manifest
- Build new source-bundle-manifest.json covering source + evidence files
- Status: DONE (in MEGA-TRAIN-H)

### TC-HEAL-006: Pilot Replay
- Run all 3 pilots using actual Python modules (not hand-written JSON)
- Capture per-step stdout to raw-command-logs/
- Write final-verdict.json per pilot from real execution
- Status: DONE — all 3 pilots pass

### TC-HEAL-007: Git Diff Proof
- Capture git diff output for all protected files to command ledger stdout
- Status: DONE — all 7 protected files have empty diff (confirmed)
