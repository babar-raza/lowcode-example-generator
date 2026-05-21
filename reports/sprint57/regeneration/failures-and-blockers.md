# Sprint 57 Regeneration Failures and Blockers

**Sprint 57 Phase 6**
**Date:** 2026-05-21

## Generation Failures (1 of 42)

### pdf-pdf-aconverter

- **Scenario ID:** `pdf-pdf-aconverter`
- **Family:** pdf
- **Classification:** `GENERATION_FAILED`
- **Stage:** generation (post-repair validation)
- **Root Cause:** LLM generated code uses `TextFragment` (from `Aspose.Pdf.Text` namespace) but the auto-repair pass did not add the `using Aspose.Pdf.Text;` directive. Post-repair constraint check caught the missing using directive and blocked promotion.
- **Error:** `PDF: uses TextFragment but is missing 'using Aspose.Pdf.Text;' directive`
- **Status:** BACKLOGGED, priority=high
- **Fix:** Add `using Aspose.Pdf.Text;` to the REQUIRED constraints in `per_type_constraints` for `PdfAConverter`, or add a few-shot example that demonstrates this import.

## Build Repairs (5 in pdf, 2 in slides)

Build repairs are auto-repairs that succeeded — examples are still classified as PASS.

| Scenario ID | Repair Outcome |
|------------|---------------|
| pdf-table-generator | build repaired → run passed |
| pdf-text-extractor | build repaired → run passed |
| pdf-tiff | build repaired → run passed |
| pdf-toc-generator | build repaired → run passed |
| pdf-xls-converter | build repaired → run passed |
| slides-convert | build repaired → run passed |
| slides-merger | build repaired → run passed |

## Permanent Blockers (unchanged from Sprint 56)

| Scenario ID | Reason |
|------------|--------|
| pdf-processor | API_ACCESS_PARADOX (requires PluginOptions which is abstract) |
| pdf-pdf-extractor | ABSTRACT_BASE (PdfExtractor is abstract) |
| words-splitter-split-criteria | ENUM (SplitCriteria is an enum) |
| pdf-pdf-to-image | ABSTRACT_BASE (PdfToImage is abstract) |
| diagram-options-* (3 types) | NON_RUNNABLE OPTIONS_CLASS |

## Backlogged (deferred, not permanently blocked)

| Scenario ID | Reason |
|------------|--------|
| pdf-form-importer | Library bug: Aspose.PDF 26.5.0 — retry on 26.6.0+ |
| pdf-ofd | PERMANENTLY_BLOCKED (OFD format not supported on .NET) |
| pdf-timestamp | Dependency not available (certificates) |
| pdf-select-field | API surface incomplete |
| words-comparer | Deferred to Wave 2 |
| words-merger | Deferred to Wave 2 |
| words-mail-merger | Deferred to Wave 2 |
| words-splitter-split | Deferred to Wave 2 |
| words-report-builder | Missing input.docx fixture |

## Summary

- **Total denominator:** 42 runnable
- **Active pass:** 41/42 (97.6%)
- **Blocked/deferred (separate from denominator):** multiple PERMANENTLY_BLOCKED + BACKLOGGED entries tracked in completion queue
