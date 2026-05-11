# Words Excluded Scenarios Root-Cause Deep Dive

**Date:** 2026-05-06
**Evidence:** `workspace/verification/latest/words-excluded-scenarios-root-cause-deep-dive.json`
**Verdict:** WORDS_ROOT_CAUSES_IDENTIFIED

## 5 Excluded Runnable Scenarios

| Type | Root Cause | Fix Effort |
|------|-----------|------------|
| Comparer | MISSING_FIXTURE_STRATEGY (needs 2 different docs) | Medium |
| Merger | MISSING_FIXTURE_STRATEGY (needs array input) | Medium |
| MailMerger | MISSING_FIXTURE_STRATEGY (needs merge field template) | High |
| ReportBuilder | MISSING_FIXTURE_STRATEGY (needs LINQ tag template) | High |
| Processor | MISSING_OPTIONS_STRATEGY (builder pattern API) | Low |

## Additional: WORDS-005 Splitter.Split

Blocked by MISSING_ENUM_VALUES — SplitCriteria enum not in DllReflector output.

## System Gaps

1. No paired fixture strategy (Comparer, Merger)
2. No template-with-merge-fields fixture (MailMerger)
3. No template-with-data fixture (ReportBuilder)
4. No builder-pattern API support (Processor)
5. No SplitCriteria enum enumeration (DllReflector)
6. No automated DOCX semantic validation

## Path to 100%

All 5 gaps are fixable. Estimated 2-3 sprints for full Words coverage (9/9 candidates).
