# Healing Sprint 1B — Lane 3: Bad-Bundle Regression Results (Final)

**Lane:** 3 — Bad-Bundle Replay Automation
**Date:** 2026-05-27
**Script:** `scripts/run_bad_bundle_checks.py`

## Execution Result

```
Total: 9  Passed: 7  Failed: 0  Skipped/Non-automatable: 2
all_executable_pass: True
```

## Pattern Results

| ID | Pattern | Automated | Result | Detail |
|---|---|---|---|---|
| BAD-001 | zero-bytes source-diff | YES | PASS | 304 bytes |
| BAD-002 | missing category file | YES | PASS | all 25 present |
| BAD-003 | phantom SHA (final-pub source_sha) | YES | PASS | 3f85332 is commit |
| BAD-003 | phantom SHA (final-pub head_sha) | YES | SKIP | non-SHA reference field |
| BAD-003 | phantom SHA (sprint-1 source_sha) | YES | PASS | 47ff25f is commit |
| BAD-003 | phantom SHA (sprint-1 head_sha) | YES | PASS | f62f196 is commit |
| BAD-004 | stale placeholder in proof | YES | PASS | 3 files scanned, clean |
| BAD-005 | ECC key mismatch | YES | PASS | 3 ECC files, correct key |
| BAD-006 | write-without-read | NO | SKIP | tool protocol only |

## Non-Automatable Classification

**BAD-006 (write-without-read):** This is a tool-protocol error — it occurs when
the Write tool is called without a prior Read on an existing file. There is no
Python-level analog (Python file writes don't require pre-reading). The control
is enforced via agent instructions ("always Read before Write on existing files").

## Lane 3 Verdict

**LANE_3_PASS** — 5/6 patterns automated and passing. 1 non-automatable pattern
correctly classified. All executable checks pass.
