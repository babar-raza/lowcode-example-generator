# Package Authority Summary — Sprint 62

**Sprint:** 62
**Date:** 2026-05-21
**Status:** 42/42 DUAL_SOURCE, api_verified upgraded from 0 to 42

---

## Sprint 61 → Sprint 62 Upgrade

| Metric | Sprint 61 | Sprint 62 |
|--------|-----------|-----------|
| Total scenarios | 42 | 42 |
| DUAL_SOURCE | 41 | 42 |
| CONTRACT_ONLY | 1 (pdf-pdf-aconverter) | 0 |
| api_verified (contract) | 0 | 0 |
| api_verified (Program.cs) | 0 | 42 |
| No authority | 0 | 0 |

**Key improvement:** pdf-pdf-aconverter upgraded from CONTRACT_ONLY to DUAL_SOURCE.
Program.cs found at `workspace/runs/pilot-pdf-20260514-211320/generated/pdf/pdf-pdf-aconverter/Program.cs`.

---

## api_verified Definition

In Sprint 62, `api_verified=CONFIRMED_FROM_PROGRAMCS` means:
- The LowCode type and method usage was confirmed in an actual Program.cs file
- This is stronger than contract-only (which derives from manifest.json entries)
- This does NOT mean the NuGet API was formally introspected via reflection or docs

This is honest: we confirmed API usage by reading the generated C# code, not by
querying the NuGet package's public API surface directly.

---

## Family Breakdown

| Family | Scenarios | LowCode Namespace | Authority |
|--------|-----------|------------------|-----------|
| Cells | 9 | Aspose.Cells.LowCode.* | DUAL_SOURCE (all) |
| Words | 8 | Aspose.Words.LowCode.* | DUAL_SOURCE (all) |
| PDF | 19 | Aspose.Pdf.Plugins.* | DUAL_SOURCE (all) |
| Diagram | 2 | Aspose.Diagram.LowCode.* | DUAL_SOURCE (all) |
| Email | 1 | Aspose.Email.LowCode.* | DUAL_SOURCE |
| Slides | 3 | Aspose.Slides.LowCode.* | DUAL_SOURCE (all) |

---

## No Overstatement Policy

- api_verified counts are conservative (CONFIRMED_FROM_PROGRAMCS, not "NuGet-introspected")
- Special case scenarios (mail-merger, report-builder, text-extractor, email-converter) are noted with their actual API patterns
- No scenario is marked api_verified=true in the format-authority contracts (that requires external API verification beyond this sprint's scope)
