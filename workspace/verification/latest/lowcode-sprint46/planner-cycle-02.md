# Next Actions

Generated: 2026-05-19T13:09:23.793731+00:00
HEAD: fe5fb4e
Dirty: 21 evidence

| Rank | ID | Family | Type | Impact | Safe | Blocker |
|------|----|--------|------|--------|------|---------|
| 1 | PDF_MERGE_PRS | pdf | MERGE_READY_PR | 95 | NO | merge approval gate absent |
| 2 | PDF_PR_CONFLICT_RECOVERY | pdf | PDF_PR_CONFLICT_RECOVERY | 92 | NO | live publish approval gate absent |
| 3 | PORTFOLIO_CONSERVATION_CHECK | cross-family | DENOMINATOR_RECONCILIATION | 75 | YES | - |
| 4 | VERSION_DRIFT_CHECK | cross-family | VERSION_DRIFT_RERUN | 60 | YES | - |
| 5 | FORMIMPORTER_RETEST | pdf | BLOCKER_RETEST | 40 | YES | requires Aspose.PDF > 26.5.0 |
| 6 | OCR_DEPENDENCY_RECHECK | ocr | BLOCKER_RETEST | 30 | YES | internal Aspose assembly |
| 7 | PSD_DEPENDENCY_RECHECK | psd | BLOCKER_RETEST | 30 | YES | internal Aspose assembly |
| 8 | PERMANENTLY_BLOCKED_WATCH | cross-family | BLOCKER_RETEST | 20 | YES | - |

- 6 safe actions, 2 blocked actions
- Active families: 6
- Total contracts: 42
