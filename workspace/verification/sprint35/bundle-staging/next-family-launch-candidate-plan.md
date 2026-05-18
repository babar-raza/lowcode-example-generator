# Next LowCode Family Launch Candidate Plan — Sprint 35

## Summary
No new LowCode families discovered in Sprint 35. All 6 confirmed LowCode families are at PILOT_COMPLETE or higher.

## Confirmed LowCode Families (6)
| Family | Status | Published | Pending |
|--------|--------|-----------|---------|
| Cells | FAMILY_COMPLETE | 9/9 | 0 |
| Words | PILOT_COMPLETE | 8/8 | 0 |
| PDF | PARTIAL_CANARY | 5/19 | 14 PR-ready |
| Diagram | PILOT_COMPLETE | 2/2 | 0 |
| Email | PILOT_COMPLETE | 1/1 | 0 |
| Slides | PILOT_COMPLETE | 3/3 | 0 |

## Blocked Families
- **OCR**: Aspose.AI.LLM private assembly required — not on NuGet
  - TC-OCR-01: Wait for NuGet publication or installer extraction
- **PSD**: Aspose.JavaAttributes private assembly required — not on NuGet
  - TC-PSD-01: Escalate to Aspose PSD team

## No-LowCode Families (16)
barcode, cad, drawing, finance, font, gis, imaging, note, page, tasks, tex, threed, zip, html, svg, omr — all confirmed via DLL reflection.

## No-Package Families
- EPUB: No standalone Aspose.Epub NuGet package exists.

## Next Expansion Opportunities (for existing families)
- **PDF**: Publish 14 pending examples (PR#3/#5/#6/#7/#8/#9) when APPROVE_LIVE_PR set
- **PDF FormImporter**: Retest when Aspose.PDF > 26.5.0 (TC-PDF-FORMIMPORTER-RETEST)
- **Words Processor**: Investigate ProcessorContext factory pattern (TC-WORDS-PROCESSOR)
