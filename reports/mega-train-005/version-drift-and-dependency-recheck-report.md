# Lane E: Version Drift and Dependency Recheck Report

**Sprint:** LOWCODE-MEGA-TRAIN-005
**Date:** 2026-05-20

## Version Drift Status

| Family | Target Repo Version | Latest NuGet | Drift | Status |
|--------|-------------------|-------------|-------|--------|
| Cells | 26.4.0 | 26.5.1 | MAJOR | PUBLISHED_VERSION_DRIFT |
| Words | 26.4.0 | 26.5.0 | MAJOR | PUBLISHED_VERSION_DRIFT |
| PDF | 26.5.0 | 26.5.0 | None | PUBLISHED_CURRENT |
| Diagram | 26.4.0 | 26.5.0 | MAJOR | PUBLISHED_VERSION_DRIFT |
| Email | 26.4.0 | 26.4.0 | None | PUBLISHED_CURRENT |
| Slides | 26.5.0 | 26.5.0 | None | PUBLISHED_CURRENT |

**Note:** Aspose uses calendar versioning where month change (26.4 -> 26.5) is classified as MAJOR drift per project convention.

### Version Drift Resolution
Cells/Words/Diagram need Directory.Packages.props update and README push to target repos.
- **Blocked by:** APPROVE_README_PUSH gate absent
- **Safe local action:** None — push required

## Dependency Blockers

### OCR — DEPENDENCY_BLOCKED
- **Package:** Aspose.OCR 26.4.0
- **Missing assembly:** Aspose.AI.LLM Version=25.12.0.0
- **Root cause:** Internal Aspose assembly not published on NuGet.org
- **NuGet availability:** NOT_ON_NUGET (api.nuget.org returns BlobNotFound)
- **Verified at:** 2026-05-09
- **Retest trigger:** Aspose publishes Aspose.AI.LLM to NuGet
- **Taskcard:** TC-OCR-REFLECTION

### PSD — DEPENDENCY_BLOCKED
- **Package:** Aspose.PSD 26.4.0
- **Missing assembly:** Aspose.JavaAttributes Version=1.0.0.0
- **Root cause:** Internal Aspose assembly not published on NuGet.org
- **NuGet availability:** NOT_ON_NUGET (api.nuget.org returns BlobNotFound)
- **Verified at:** 2026-05-09
- **Retest trigger:** Aspose publishes Aspose.JavaAttributes to NuGet
- **Taskcard:** TC-PSD-REFLECTION

## Permanently Blocked Types

| Type | Family | Reason |
|------|--------|--------|
| Timestamp | PDF | External TSA ServerUrl required |
| Ofd | PDF | OFD input format, no programmatic fixture |
| Processor | Words | No public constructor, no static entrypoint (CS1729+CS0120) |

All 3 permanently blocked types confirmed unchanged.

## Verdict
- Version drift: 3 families drifted (Cells, Words, Diagram), blocked by push approval
- OCR: STILL_BLOCKED (Aspose.AI.LLM not on NuGet)
- PSD: STILL_BLOCKED (Aspose.JavaAttributes not on NuGet)
- Permanently blocked: 3 types, all confirmed unchanged
- No packages mutated, no unsafe actions taken
