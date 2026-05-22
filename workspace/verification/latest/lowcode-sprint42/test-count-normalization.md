# Test Count Normalization — Sprint 42

Generated: 2026-05-19

## Sprint 41 Discrepancy

| Metric | Value |
|--------|-------|
| Sprint 41 final-state-summary | 2217 passed |
| Sprint 41 raw-full-test-log | 2187 passed |
| Delta | 30 |

**Root cause**: Raw log captured before commit; final count captured after, with uncommitted V8 test files.

## Sprint 42 Canonical Count

| Metric | Value |
|--------|-------|
| Full suite (pytest tests/) | **2365 passed** |
| Skipped | 3 |
| Failed | 0 |

## Sprint 42 Growth

- From Sprint 41 raw: +178 tests
- From Sprint 41 reported: +148 tests

Sources of growth:
- `8f36449`: V8 evidence contract + README auditor semantic tests (~30)
- `06bb5a3`: Contract tests expanded 36→67 (6-family coverage, +31)
- `b0fee12`: 5 AI governance test suites (~80)
- Sprint 42 test fix: pdf-splitter status assertion updated (+0 net, 1 renamed)

## Normalization Rule

Sprint 42 canonical count = full-suite pytest run AFTER all fixes applied.
Raw log and summary counts are identical: **2365 passed, 3 skipped, 0 failed**.
