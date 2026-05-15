# All-Family LowCode Launch Scoreboard — Sprint 19

**Date:** 2026-05-15
**Total Published:** 28 examples across 6 families

## Family Status

| Family | Status | Published | Pilot Coverage | Workflow Root | Post-Merge | Regression Risk |
|--------|--------|-----------|----------------|---------------|------------|----------------|
| **Cells** | FAMILY_COMPLETE | 9 | N/A | 9/9 (100%) | VERIFIED | NONE |
| **Words** | PILOT_COMPLETE | 8 | 8/8 (100%) | 8/9 (89%) | VERIFIED | NONE |
| **PDF** | PARTIAL_CANARY | 5 | 5/14 → 14/14* | 5/24 → 14/24* | VERIFIED | LOW |
| **Diagram** | PILOT_COMPLETE | 2 | 2/2 (100%) | 2/2 (100%) | VERIFIED | NONE |
| **Email** | PILOT_COMPLETE | 1 | 1/1 (100%) | 1/1 (100%) | NOT RUN | LOW |
| **Slides** | PILOT_COMPLETE | 3 | 3/3 (100%) | 3/3 (100%) | NOT RUN | LOW |

*After PR#3+PR#5+PR#6 are approved and merged.

## PDF Publication Frontier

| PR | Types | Examples | Status |
|----|-------|----------|--------|
| PR#3 | DocConverter, XlsConverter, Html | 3 | DRY_RUN_READY — approval blocked |
| PR#5 | Jpeg, Tiff, Png | 3 | PACKAGE_ASSEMBLED — approval blocked |
| PR#6 | TableGenerator, TocGenerator, ImageExtractor | 3 | PACKAGE_ASSEMBLED — approval blocked |

**Blocker:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` not set.

## Next Actions

1. **PDF PR#3**: Set `APPROVE_LIVE_PR`, run `publish-pr --family pdf --publish`
2. **PDF PR#5**: Update `pdf-controlled-pilot` contents to jpeg/tiff/png, publish
3. **PDF PR#6**: Update `pdf-controlled-pilot` contents to table-generator/toc-generator/image-extractor, publish
4. **Email/Slides post-merge validation**: Run post-merge validation scripts for email and slides
5. **PDF denominator update**: Update `pdf.json` to reflect 14 pilot types (was 11)
6. **PDF next wave**: XmlProcessor (MEDIUM feasibility) is the best next candidate after pilot completion
