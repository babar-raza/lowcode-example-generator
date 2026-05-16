# All-Family Launch Scoreboard — Sprint 21

**Date:** 2026-05-16
**Sprint:** SPRINT21-PDF-LIVE-PUBLISH-OR-XMLPROCESSOR-FRONTIER
**Total Published:** 28

| Family | Status | Published | PR Ready | Post-Merge | Next Action |
|--------|--------|-----------|----------|------------|-------------|
| Cells | FAMILY_COMPLETE | 9/9 | — | POST_MERGE_VERIFIED | Monitor package updates |
| Words | PILOT_COMPLETE | 8/8 | — | POST_MERGE_VERIFIED | Expand pilot (5 backlogged) |
| PDF | PARTIAL_CANARY | 5/14 | 9 (3 PRs) | ALL_PASS | Set APPROVE_LIVE_PR |
| Diagram | PILOT_COMPLETE | 2/2 | — | ALL_PASS | Monitor package updates |
| Email | PILOT_COMPLETE | 1/1 | — | MERGE_CONFIRMED | Runtime validation deferred |
| Slides | PILOT_COMPLETE | 3/3 | — | MERGE_CONFIRMED | Runtime validation deferred |

## PDF Publication Queue

| PR Group | Examples | Status |
|----------|----------|--------|
| PR#3 | DocConverter, Html, XlsConverter | DRY_RUN_READY_APPROVAL_BLOCKED |
| PR#5 | Jpeg, Png, Tiff | DRY_RUN_READY_APPROVAL_BLOCKED |
| PR#6 | ImageExtractor, TableGenerator, TocGenerator | DRY_RUN_READY_APPROVAL_BLOCKED |

**Blocker:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` not set

## PDF Next Frontier

| Type | Status | Blocker |
|------|--------|---------|
| Security | DESIGN_READY | Harness verification needed (EncryptionOptions.AddInput/AddOutput) |
| FormFlattener | DESIGN_READY | AcroForm fixture harness needed |
| PdfToImage | RECLASSIFY_PENDING | abstract_class — must move to ABSTRACT_BASE in Sprint 22 |
