Sprint 86 — Sprint 85 Evidence Hygiene Normalization
=====================================================
Date: 2026-05-25
Author: Lane G

## Items Normalized

### S85-G1: todo.md validator test count
- File: reports/sprint85/todo.md line 27
- Was: "3120 pass" (preliminary count before final run)
- Actual: 3123 pass (confirmed in test-run.log and sprint-state.json)
- Note: Historical artifact — todo.md was written mid-sprint before final test run.
  Not patched (todo.md is a planning document, not an evidence artifact).
  Correct values documented in test-run.log, sprint-state.json, and final-consistency-check.json.

### S85-G2: todo.md ECC category count
- File: reports/sprint85/todo.md line 91
- Was: "68 ECC categories" (before duplicate EC60 was removed)
- Actual: 67 ECC categories (confirmed in evidence-contract.json and sprint-state.json)
- Note: Historical artifact — todo.md reflected intermediate state before EC60 duplicate removal.
  Not patched. Correct values in evidence-contract.json (67 categories).

### S85-G3: commands.log preliminary counts
- File: reports/sprint85/commands.log lines 65-66, 86
- Was: "179 tests", "3120 tests", "68 ECC categories"
- Actual: 182 validator tests, 3123 full suite, 67 ECC categories
- Note: commands.log recorded at execution time; later runs produced higher counts.
  Not patched (commands.log is a chronological record). Correct values in test-run.log.

### S85-G4: bundle-manifest.json source_sha format
- File: reports/sprint85/bundle-manifest.json
- Was: source_sha "9deeaf6" (7-char short SHA)
- Preferred: Full 40-char SHA for consistency
- Note: Rule 120 checks for TBD_AFTER_COMMIT, not format. Short SHA is valid per Rule 124
  (source_sha appears in final-clean-proof.txt via git log output). No patch needed.

## Verdict
All 4 items are historical artifacts from mid-sprint execution. No patches applied
to Sprint 85 files — correct final values are documented in authoritative evidence
files (sprint-state.json, test-run.log, evidence-contract.json, final-clean-proof.txt).
The todo.md and commands.log are chronological records and should not be retroactively edited.
