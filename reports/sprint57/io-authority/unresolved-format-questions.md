# Unresolved Format Questions — Sprint 57

**Sprint 57 Lane C**
**Date:** 2026-05-21

## Resolved in Sprint 57

All format authority questions from Sprint 56 have been resolved. Zero open questions remain
for the 42 active types.

| Question | Resolution |
|----------|-----------|
| SpreadsheetConverter output: .xlsx or .csv? | RESOLVED: .csv (cross-format converter, contract canonical_output_format=.csv) |
| TextExtractor output kind: file or stdout? | RESOLVED: stdout — no AddOutput(), results via StringResult from ResultCollection[0] |
| email/Converter output kind: file or directory? | RESOLVED: directory — FolderOutputHandler, validated via Directory.Exists |
| pdf/Html input format: is it .html or .pdf? | RESOLVED: .html (converts HTML to PDF, input is .html not .pdf) |
| SpreadsheetMerger input cardinality: single or multi? | RESOLVED: multi (.xlsx multi — merges multiple spreadsheets) |
| PdfAConverter naming: PdfAConverter or PdfaConverter? | RESOLVED: PdfAConverter (capital A) — matches DLL reflection output |
| pdf/Html type_name: Html or HtmlConverter? | RESOLVED: Html — this is the actual class name in Aspose.Pdf.LowCode namespace |

## Open Questions for Future Sprints

### Q1: Words version drift (26.4.0 → 26.5.0)

- **Impact**: Words examples in destination repo are at 26.4.0. NuGet latest is 26.5.0.
- **Format risk**: None — checked changelogs; LowCode API surface unchanged between 26.4.0 and 26.5.0.
- **Resolution needed**: Directory.Packages.props update push requires APPROVE_README_PUSH. Deferred to Sprint 58.

### Q2: Diagram version drift (26.4.0 → 26.5.0)

- **Impact**: Diagram examples at 26.4.0. NuGet latest 26.5.0.
- **Format risk**: None — DiagramConverter and PdfConverter (diagram) APIs stable.
- **Resolution needed**: Same as Words — needs APPROVE_README_PUSH. Deferred to Sprint 58.

### Q3: pdf-pdf-aconverter LLM constraint

- **Impact**: PdfAConverter generation fails due to missing `using Aspose.Pdf.Text;` directive.
- **Fix path**: Add `"using Aspose.Pdf.Text;"` to `per_type_constraints.PdfAConverter.REQUIRED` in pdf.yml.
- **Priority**: High (backlogged at high priority).
- **Sprint 58 action**: Update per_type_constraints, rerun regeneration for pdf-pdf-aconverter.

### Q4: FormImporter (Wave H deferred)

- **Impact**: pdf-form-importer blocked by Aspose.PDF 26.5.0 library bug (ImportFormField bug).
- **Resolution**: Retry on Aspose.PDF 26.6.0+. Check release notes when 26.6.0 is available.
- **No format authority questions** — contract is defined, I/O formats are known.

## Evidence Authority Confidence

All 42 active contracts: `evidence_confidence = "api_verified"`
Source: DllReflector API catalog + pipeline contracts enrichment.
Zero format questions remain unresolved for active types.
