# All-Family LowCode Launch Scoreboard

**Sprint:** 28 | **Date:** 2026-05-17

## Family Status

| Family | Status | Published | PR_DRY_RUN_READY | Package |
|--------|--------|-----------|-----------------|---------|
| Cells | FAMILY_COMPLETE | 9/9 | 0 | 26.4.0 |
| Words | PILOT_COMPLETE | 8/8 | 0 | 26.5.0 |
| **PDF** | **PARTIAL_CANARY** | **5/19** | **14** | **26.5.0** |
| Diagram | PILOT_COMPLETE | 2/2 | 0 | 26.4.0 |
| Email | PILOT_COMPLETE | 1/1 | 0 | 26.4.0 |
| Slides | PILOT_COMPLETE | 3/3 | 0 | 26.5.0 |

## Portfolio Totals

| Metric | Value |
|--------|-------|
| Total published | **28** |
| Total PR_DRY_RUN_READY | **14** |
| Total pending APPROVE_LIVE_PR | 14 |
| Permanently blocked | 2 (Timestamp, Ofd) |
| Library defect deferred | 1 (FormImporter) |
| Families complete/pilot-complete | 5/6 |

## PDF PR Packages Pending Approval

| PR | Types | Version | Status |
|----|-------|---------|--------|
| PR#3 | DocConverter, XlsConverter, Html | 26.4.0 | PR_DRY_RUN_READY |
| PR#5 | Jpeg, Tiff, Png | 26.4.0 | PR_DRY_RUN_READY |
| PR#6 | TocGenerator, TableGenerator, ImageExtractor | 26.4.0 | PR_DRY_RUN_READY |
| PR#7 | Security, FormFlattener | 26.5.0 | PR_DRY_RUN_READY |
| PR#8 | FormEditor, FormExporter | 26.5.0 | PR_DRY_RUN_READY |
| PR#9 | Signature | 26.5.0 | PR_DRY_RUN_READY |

## Infrastructure Milestones Sprint 28

- Strict evidence contract implemented: `src/plugin_examples/evidence_contract.py`
- Contract tests: 26/26 PASS
- Thin 17-file Sprint 27 bundle confirmed FAILS contract validation
- FormImporter defect upstream issue package finalized

## To Advance PDF to Pilot Complete

Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` and run `publish-pr` with `--package-path` for PR#3 through PR#9. This achieves 19/19 pilot = 19/22 workflow_root types maximum achievable coverage.
