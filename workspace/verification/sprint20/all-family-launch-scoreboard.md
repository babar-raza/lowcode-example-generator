# All-Family LowCode Launch Scoreboard — Sprint 20

**Date:** 2026-05-16
**Total Published:** 28 examples across 6 families (unchanged; PR#3/5/6 approval-blocked)

## Family Status

| Family | Status | Published | Pilot Coverage | Workflow Root | Post-Merge | Regression Risk |
|--------|--------|-----------|----------------|---------------|------------|----------------|
| **Cells** | FAMILY_COMPLETE | 9 | N/A | 9/9 (100%) | VERIFIED | NONE |
| **Words** | PILOT_COMPLETE | 8 | 8/8 (100%) | 8/9 (89%) | VERIFIED | NONE |
| **PDF** | PARTIAL_CANARY | 5 | 5/14 → 14/14* | 5/24 → 14/24* | VERIFIED | LOW |
| **Diagram** | PILOT_COMPLETE | 2 | 2/2 (100%) | 2/2 (100%) | VERIFIED | NONE |
| **Email** | PILOT_COMPLETE | 1 | 1/1 (100%) | 1/1 (100%) | MERGE_CONFIRMED | LOW |
| **Slides** | PILOT_COMPLETE | 3 | 3/3 (100%) | 3/3 (100%) | MERGE_CONFIRMED | LOW |

*After PR#3+PR#5+PR#6 are approved and merged.

## Sprint 20 Changes

| Change | Lane | Status |
|--------|------|--------|
| pdf.json allowed_pilot_count 11→14 | A | COMPLETE |
| `--package-path` added to publish-pr CLI | B | COMPLETE |
| Sprint 19 ZIP/HEAD conflict resolved | 0 | COMPLETE |
| PR#3 dry-run re-verified | C/D | PASS |
| PR#5 dry-run re-verified | C/E | PASS |
| PR#6 dry-run re-verified | C/F | PASS |
| Email PR#1 post-merge confirmed | H | MERGE_CONFIRMED |
| Slides PR#1 post-merge confirmed | H | MERGE_CONFIRMED |
| PDF post-pilot frontier planned | I | COMPLETE |

## PDF Publication Frontier

| PR | Types | Examples | Status |
|----|-------|----------|--------|
| PR#3 | DocConverter, XlsConverter, Html | 3 | DRY_RUN_READY — approval blocked |
| PR#5 | Jpeg, Tiff, Png | 3 | DRY_RUN_READY — approval blocked |
| PR#6 | TableGenerator, TocGenerator, ImageExtractor | 3 | DRY_RUN_READY — approval blocked |

**Blocker:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` not set.
**New in Sprint 20:** Each PR now has its own `--package-path` — no more manual package swapping.

## Next Actions (Sprint 21)

1. **PDF PR#3**: Set `APPROVE_LIVE_PR`, set `GITHUB_TOKEN` (GH_TOKEN classic PAT), run `publish-pr --family pdf --publish --package-path workspace/pr-dry-run/pdf-controlled-pilot`
2. **PDF PR#5**: `publish-pr --family pdf --publish --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr5`
3. **PDF PR#6**: `publish-pr --family pdf --publish --package-path workspace/pr-dry-run/pdf-controlled-pilot-pr6`
4. **PDF XmlProcessor**: Add to pdf.yml allowed_types, define per_type_constraints, run pilot (next best candidate)
5. **PDF AcroForm fixture**: Design standalone harness for FormEditor/FormExporter/FormFlattener/FormImporter/SelectField

## PDF Workflow Root Coverage

| Group | Types | Status |
|-------|-------|--------|
| Wave A (5) | Merger, TextExtractor, Splitter, Optimizer, PdfAConverter | PUBLISHED |
| Wave B (3) | DocConverter, XlsConverter, Html | PR#3 DRY_RUN_READY |
| Wave C (3) | Jpeg, Png, Tiff | PR#5 DRY_RUN_READY |
| Wave D (3) | TocGenerator, TableGenerator, ImageExtractor | PR#6 DRY_RUN_READY |
| XmlProcessor | 1 | NEXT CANDIDATE (Sprint 21) |
| AcroForm (5) | FormEditor, FormExporter, FormFlattener, FormImporter, SelectField | DEFERRED (fixture sprint needed) |
| Blocked (4) | Security, Signature, Timestamp, Ofd | PERMANENTLY_BLOCKED |
