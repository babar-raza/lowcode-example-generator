<!-- GENERATED — do not edit manually. -->
# PDF Pilot Fixture Requirements

**Date:** 2026-05-05
**Sprint:** PDF Fixture Strategy Review
**Phase:** Phase 2 — Fixture Requirements per Pilot Type
**Does not enable generation:** YES

---

## Overview

All 4 PDF pilot types (Merger, Splitter, Optimizer, TextExtractor) use **programmatic PDF creation** via
`Aspose.Pdf.Document()`. No external fixture files are needed. All inputs are created inline in the
example `Program.cs` before the LowCode API call. The `template_hints` section in `pdf.yml` already
documents the basic creation patterns.

---

## Fixture Requirements by Pilot Type

### PDF-001: Merger (`MergeOptions`)

| Field | Value |
|---|---|
| Operation | Merge two PDFs into one |
| Options type | `MergeOptions` |
| Fixture count | 2 |
| Fixture names | `input1.pdf`, `input2.pdf` |
| Strategy | `programmatic_pdf_pair` |
| Output | `output.pdf` |
| Validation | File exists, byte count > 0, `%PDF` header |
| Risk | LOW |

**Fixture creation code:**
```csharp
var doc1 = new Aspose.Pdf.Document();
doc1.Pages.Add();
doc1.Save("input1.pdf");
var doc2 = new Aspose.Pdf.Document();
doc2.Pages.Add();
doc2.Save("input2.pdf");
```

Source in `pdf.yml`: `template_hints.merger_input_creation_lines`

---

### PDF-002: Splitter (`SplitOptions`)

| Field | Value |
|---|---|
| Operation | Split a 3-page PDF into individual pages |
| Options type | `SplitOptions` |
| Fixture count | 1 |
| Fixture name | `input.pdf` (3 pages) |
| Strategy | `programmatic_pdf_multi_page` |
| Output | `output_1.pdf`, `output_2.pdf`, `output_3.pdf` (naming TBC in Phase 3) |
| Validation | At least 1 output file with `%PDF` header |
| Risk | LOW (output naming pattern is MEDIUM — to be confirmed) |

**Fixture creation code:**
```csharp
var doc = new Aspose.Pdf.Document();
doc.Pages.Add();
doc.Pages.Add();
doc.Pages.Add();
doc.Save("input.pdf");
```

Note: Output file naming pattern (`output_{0}.pdf`) needs confirmation during Phase 3 harness run.

---

### PDF-003: Optimizer (`OptimizeOptions`)

| Field | Value |
|---|---|
| Operation | Optimize a PDF for file size reduction |
| Options type | `OptimizeOptions` |
| Fixture count | 1 |
| Fixture name | `input.pdf` |
| Strategy | `programmatic_pdf_single` |
| Output | `output.pdf` |
| Validation | File exists, byte count > 0, `%PDF` header |
| Risk | LOW — simplest of the 4 pilot types |

**Fixture creation code:**
```csharp
var doc = new Aspose.Pdf.Document();
doc.Pages.Add();
doc.Save("input.pdf");
```

Source in `pdf.yml`: `template_hints.input_creation_lines`

---

### PDF-004: TextExtractor (`TextExtractorOptions`)

| Field | Value |
|---|---|
| Operation | Extract text content from a PDF |
| Options type | `TextExtractorOptions` |
| Fixture count | 1 |
| Fixture name | `input.pdf` (with known text) |
| Strategy | `programmatic_pdf_known_text` |
| Output | **None** — results in `ResultContainer` as `StringResult` |
| Validation | `result.IsSuccess == true` AND extracted text contains `"Hello LowCode PDF"` |
| Risk | MEDIUM — non-standard output pattern |

**CRITICAL:** TextExtractor does NOT use `AddOutput()`. Results are read from `result.OperationResult[0]` cast to `StringResult`.

**Fixture creation code:**
```csharp
var doc = new Aspose.Pdf.Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new Aspose.Pdf.Text.TextFragment("Hello LowCode PDF"));
doc.Save("input.pdf");
```

---

## Cross-Cutting Requirements

| Requirement | Detail |
|---|---|
| All inputs created in code | YES — no external file fixtures |
| NuGet package | `Aspose.PDF` (same as source-of-truth) |
| Minimum usings | `Aspose.Pdf`, `Aspose.Pdf.LowCode` |
| TextExtractor also needs | `Aspose.Pdf.Text` |
| PDF header validation | Applies to Merger, Splitter, Optimizer |
| StringResult validation | Applies only to TextExtractor |
| License for simple PDFs | Not required (evaluation mode acceptable for testing) |

---

## Fixture Strategy Types Needed

1. `programmatic_pdf_single` — single-page blank PDF
2. `programmatic_pdf_multi_page` — 3-page blank PDF
3. `programmatic_pdf_pair` — two single-page blank PDFs
4. `programmatic_pdf_known_text` — single-page PDF with known TextFragment

---

## Next Step: Phase 3 Validation Harness

Phase 3 creates a C# project that exercises all 4 fixture patterns and validates:
- All 5 fixture PDFs are created successfully (`%PDF` header confirmed)
- Merger produces a merged output
- Splitter produces split output files
- Optimizer produces an optimized output
- TextExtractor returns the known text string
