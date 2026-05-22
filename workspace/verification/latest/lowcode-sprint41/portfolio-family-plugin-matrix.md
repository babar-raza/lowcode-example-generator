# Lane E — Whole-Portfolio Family/Plugin Matrix

**Date:** 2026-05-19
**Status:** ALL_FAMILIES_VERIFIED

## Active Families (6)

| Family | Package | Version | NuGet | Total Types | WF Roots | Pilot Allowed | Published | Pending | Blocked | Contracts | Status | Drift | Target Repo | Repo Health |
|--------|---------|---------|-------|-------------|----------|---------------|-----------|---------|---------|-----------|--------|-------|-------------|-------------|
| Cells | Aspose.Cells | 26.5.1 | Available | 22 | 9 | 9 | 9 | 0 | 0 | 9 | FAMILY_COMPLETE | CURRENT | aspose-cells-net | HEALTHY |
| Words | Aspose.Words | 26.5.0 | Available | 25 | 9 | 8 | 8 | 0 | 1 | 8 | PILOT_COMPLETE | CURRENT | aspose-words-net | HEALTHY |
| PDF | Aspose.PDF | 26.5.0 | Available | 101 | 22 | 19 | 5 | 14 | 3 | 19 | PARTIAL_CANARY | CURRENT | aspose-pdf-net | HEALTHY (6 open PRs) |
| Diagram | Aspose.Diagram | 26.5.0 | Available | 5 | 2 | 2 | 2 | 0 | 0 | 2 | PILOT_COMPLETE | CURRENT | aspose-diagram-net | HEALTHY |
| Email | Aspose.Email | 26.4.0 | Available | 3 | 1 | 1 | 1 | 0 | 0 | 0 | PILOT_COMPLETE | CURRENT | aspose-email-net | HEALTHY |
| Slides | Aspose.Slides.NET | 26.5.0 | Available | 5 | 3 | 3 | 3 | 0 | 0 | 0 | PILOT_COMPLETE | CURRENT | aspose-slides-net | HEALTHY |

## Discovery-Only Families (2)

| Family | Package | NuGet Status | Block Reason | LowCode Namespace | Next Action |
|--------|---------|-------------|-------------|-------------------|-------------|
| OCR | Aspose.OCR | Available | Aspose.AI.LLM NuGet 404 | Unknown (dependency blocked) | TC-OCR-DEPENDENCY-BLOCKED |
| PSD | Aspose.PSD | Available | Aspose.JavaAttributes NuGet 404 | Unknown (dependency blocked) | TC-PSD-DEPENDENCY-BLOCKED |

## Aggregated Totals

| Metric | Value |
|--------|-------|
| Active families | 6 |
| Discovery-only families | 2 |
| Total LowCode types | 161 (across active families) |
| Total workflow roots | 46 |
| Total pilot-allowed | 42 |
| Total published | 28 |
| Total pending (PR) | 14 |
| Total blocked | 4 (Words Processor + PDF FormImporter/Timestamp/Ofd) |
| Total permanently blocked | 3 (Words Processor + PDF Timestamp + PDF Ofd) |
| Total contracts | 38 (filesystem) / 36 (test scope cells+words+pdf) |
| Target repos healthy | 6/6 |
| Version drift | ALL_CURRENT |

## README State

| Family | README Published | README Audit |
|--------|-----------------|-------------|
| Cells | PUSHED to main | POST_MERGE_VERIFIED |
| Words | PUSHED to main | POST_MERGE_VERIFIED |
| PDF | 5 examples in main README | Audit needed after PR merge |
| Diagram | PUSHED to main | ALL_PASS |
| Email | PUSHED to main | NOT_RUN |
| Slides | PUSHED to main | NOT_RUN |

## Next Actions per Family

| Family | Next Action |
|--------|-------------|
| Cells | None — FAMILY_COMPLETE |
| Words | TC-WORDS-PROCESSOR-API-INVESTIGATION (PERMANENTLY_BLOCKED) |
| PDF | Merge PRs #5-#10 (requires APPROVE_MERGE_PR), then TC-PDF-FORMIMPORTER-RETEST |
| Diagram | None — PILOT_COMPLETE |
| Email | None — PILOT_COMPLETE |
| Slides | None — PILOT_COMPLETE |
| OCR | Monitor Aspose.AI.LLM NuGet availability |
| PSD | Monitor Aspose.JavaAttributes NuGet availability |
