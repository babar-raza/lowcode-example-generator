# Next Actions

Generated: 2026-05-19T11:58:55.988689+00:00
HEAD: 22daa5c
Dirty: 1 test, 21 evidence

| Rank | ID | Family | Type | Impact | Safe | Blocker |
|------|----|--------|------|--------|------|---------|
| 1 | CLOSE_DIRTY_STATE | cross-family | CLOSE_PREVIOUS_SPRINT | 100 | YES | - |
| 2 | PDF_MERGE_PRS | pdf | MERGE_READY_PR | 95 | NO | merge approval gate absent |
| 3 | PDF_PR_CONFLICT_RECOVERY | pdf | PDF_PR_CONFLICT_RECOVERY | 92 | NO | live publish approval gate absent |
| 4 | PORTFOLIO_CONSERVATION_CHECK | cross-family | DENOMINATOR_RECONCILIATION | 75 | YES | - |
| 5 | VERSION_DRIFT_CHECK | cross-family | VERSION_DRIFT_RERUN | 60 | YES | - |
| 6 | FORMIMPORTER_RETEST | pdf | BLOCKER_RETEST | 40 | YES | requires Aspose.PDF > 26.5.0 |
| 7 | OCR_DEPENDENCY_RECHECK | ocr | BLOCKER_RETEST | 30 | YES | internal Aspose assembly |
| 8 | PSD_DEPENDENCY_RECHECK | psd | BLOCKER_RETEST | 30 | YES | internal Aspose assembly |
| 9 | PERMANENTLY_BLOCKED_WATCH | cross-family | BLOCKER_RETEST | 20 | YES | - |

- 7 safe actions, 2 blocked actions
- Active families: 6
- Total contracts: 42
