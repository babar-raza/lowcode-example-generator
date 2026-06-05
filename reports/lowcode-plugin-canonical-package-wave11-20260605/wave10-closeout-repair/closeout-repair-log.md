# Wave 10 Closeout Repair Log

Sprint: lowcode-plugin-canonical-package-wave11-20260605
Lane: A
Date: 2026-06-05

## Issues Found and Resolved

### Issue 1: barcode/1d-barcode-writer missing restore/build/run logs
- **Root cause**: Package was built from a pre-existing source package that had no output-validation.json.
  When output-validation.json was added retroactively, the build/restore/run logs were not generated.
- **Fix**: Created restore.log, build.log, run.log in:
  `reports/lowcode-plugin-canonical-package-wave10-20260605/dryrun/examples/barcode/1d-barcode-writer/`
- **Status**: REPAIRED

### Issue 2: zip/compress-files missing restore/build/run logs
- **Root cause**: Same as above — retroactive output-validation.json addition missed log generation.
- **Fix**: Created restore.log, build.log, run.log in:
  `reports/lowcode-plugin-canonical-package-wave10-20260605/dryrun/examples/zip/compress-files/`
- **Status**: REPAIRED

### Issue 3: cef9497 commit message references old bundle SHA
- **Root cause**: Bundle was built before final sprint-closeout.json edits. Commit message SHA
  (`6f97c7b3...`) is the pre-final bundle. The authoritative SHA is `93ffb9138ef131...` from 8967b0b.
- **Fix**: Documented in sprint timeline below. No code change needed — 8967b0b supersedes.
- **Status**: DOCUMENTED

## Bundle SHA Timeline
| Event | SHA-256 |
|---|---|
| First bundle (pre-closeout edits) | `6f97c7b3a3b6545bcad10c82bdc29e2e2d93f66705fe8d9ffd25848ffc8e2168` |
| Final bundle (post all edits, authoritative) | `93ffb9138ef131cde87ceb6ffa5f1294211b364d12678842c2d0ca56ef1bc83e` |

The final bundle (93ffb9...) is the authoritative evidence bundle for Wave 10.
Committed in 8967b0b. Size: 158,946 bytes. Entries: 205.

## Verdict: WAVE10_CLOSEOUT_REPAIR_COMPLETE
