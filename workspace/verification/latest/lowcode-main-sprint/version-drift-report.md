# Lane E — Version Drift Report

**Date:** 2026-05-19
**Overall Verdict:** DRIFT_DETECTED (2 families drifted, 4 current)

## Per-Family Results

| Family | Package | Denominator Version | Latest NuGet | Drift | Severity | Status |
|--------|---------|-------------------|-------------|-------|----------|--------|
| cells | Aspose.Cells | 26.4.0 | 26.5.1 | YES | MAJOR | Sprint 37 pilot PASS |
| words | Aspose.Words | 26.5.0 | 26.5.0 | NO | NONE | CURRENT |
| pdf | Aspose.PDF | 26.5.0 | 26.5.0 | NO | NONE | CURRENT |
| diagram | Aspose.Diagram | 26.4.0 | 26.5.0 | YES | MAJOR | Sprint 37 pilot PASS |
| email | Aspose.Email | 26.4.0 | 26.4.0 | NO | NONE | CURRENT |
| slides | Aspose.Slides.NET | 26.5.0 | 26.5.0 | NO | NONE | CURRENT |

## Drift Actions

### Cells (26.4.0 -> 26.5.1)
- Sprint 37 drift pilot: BUILD+RUN PASS
- Recommendation: SAFE_TO_UPDATE_DENOMINATOR
- Action: Update denominator source_version to 26.5.1 in a controlled rerun sprint
- Risk: MAJOR drift (month change 4->5, plus patch 0->1)

### Diagram (26.4.0 -> 26.5.0)
- Sprint 37 drift pilot: BUILD+RUN PASS
- Recommendation: SAFE_TO_UPDATE_DENOMINATOR
- Action: Update denominator source_version to 26.5.0 in a controlled rerun sprint
- Risk: MAJOR drift (month change 4->5)

### Blocked Family Dependency Status
- OCR: Aspose.AI.LLM still missing from NuGet
- PSD: Aspose.JavaAttributes still missing from NuGet
