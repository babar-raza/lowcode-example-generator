# Special-Case I/O Authority — Sprint 62

**Sprint:** 62
**Date:** 2026-05-21
**Purpose:** Close all 9 special cases (5 Program.cs + 4 README) with authoritative I/O classification.
**Status:** ALL 9 RESOLVED

---

## Background

Sprint 61 ended with 5 Program.cs special cases where input_format_in_programcs was null or missing:

| Scenario | Sprint 61 Classification | Root Cause |
|----------|--------------------------|------------|
| pdf-pdf-aconverter | NEITHER_KNOWN (programcs_found=false) | Program.cs in workspace/runs, not searched |
| pdf-text-extractor | OUTPUT_ONLY_KNOWN | Input detected as null in extraction |
| words-mail-merger | OUTPUT_ONLY_KNOWN | Input is template + in-memory data, no file arg |
| words-report-builder | OUTPUT_ONLY_KNOWN | Input is template + in-memory data, no file arg |
| email-converter | INPUT_KNOWN_OUTPUT_SPECIAL | Output is directory, not single file |

Additionally, Sprint 61 README I/O audit identified 4 README special cases needing explicit documentation text (the same 4 scenarios except email-converter, which has known README pattern):
- pdf-pdf-aconverter
- pdf-text-extractor
- words-mail-merger
- words-report-builder

---

## Program.cs Special Cases — Resolution

### SC-01: pdf-pdf-aconverter

**Root Cause:** Sprint 61 Phase 6 searched `generated/` directory only. Program.cs exists at:
`workspace/runs/pilot-pdf-20260514-211320/generated/pdf/pdf-pdf-aconverter/Program.cs`

**API:** `Aspose.Pdf.Plugins.PdfAConverter`
- Input: `input.pdf` via `FileDataSource`
- Output: `output.pdf` via `FileDataSource`
- Pattern: Standard file-to-file (PDF to PDF/A compliance conversion)

**Corrected Classification:** `BOTH_KNOWN` — input=.pdf, output=.pdf

---

### SC-02: pdf-text-extractor

**Root Cause:** Sprint 61 extraction script matched output=stdout from StringResult pattern but did not extract input from `new FileDataSource("input.pdf")`.

**API:** `Aspose.Pdf.Plugins.TextExtractor`
- Input: `input.pdf` via `FileDataSource` — confirmed in Program.cs
- Output: `StringResult` from `ResultCollection[0]` — printed to Console (no output file)
- Pattern: File to stdout

**Corrected Classification:** `BOTH_KNOWN_OUTPUT_IS_STDOUT` — input=.pdf, output=stdout

---

### SC-03: words-mail-merger

**Root Cause:** MailMerger.Execute() takes a `Document` template object + field data arrays. No file path string for input — the template is created programmatically via `new Document()`.

**API:** `Aspose.Words.LowCode.MailMerger`
- Input: `template.docx` (created programmatically) + `string[]` field names + `object[]` field values
- Output: `result.docx` via `SaveFormat.Docx`
- Pattern: Template + in-memory data → file

**Corrected Classification:** `BOTH_KNOWN_INPUT_IS_TEMPLATE` — input=template.docx+data, output=.docx

---

### SC-04: words-report-builder

**Root Cause:** ReportBuilder.BuildReport() takes a `Document` template object + arbitrary data source object (C# class). No file path for input.

**API:** `Aspose.Words.LowCode.ReportBuilder`
- Input: `template.docx` (created programmatically) + `Person` data object with nested `Manager` and `Order` lists
- Output: `report.docx` via `SaveFormat.Docx`
- Pattern: Template + in-memory data → file

**Corrected Classification:** `BOTH_KNOWN_INPUT_IS_TEMPLATE` — input=template.docx+data, output=.docx

---

### SC-05: email-converter

**Root Cause:** Output uses `FolderOutputHandler` which writes to a directory, not a single file. Sprint 61 classified this as `INPUT_KNOWN_OUTPUT_SPECIAL`.

**API:** Aspose.Email EML conversion
- Input: `.eml` email file
- Output: Directory of `.html` files via `FolderOutputHandler`
- Pattern: File to directory

**Corrected Classification:** `BOTH_KNOWN_OUTPUT_IS_DIRECTORY` — input=.eml, output=directory of .html

---

## README Special Cases — Authoritative Text

### SC-06: pdf-pdf-aconverter README Text

**Input sentence:** "The example takes a PDF file (`input.pdf`) as input."
**Output sentence:** "The converted PDF/A-compliant document is saved as `output.pdf`."

---

### SC-07: pdf-text-extractor README Text

**Input sentence:** "The example takes a PDF file (`input.pdf`) as input."
**Output sentence:** "The extracted text is printed to standard output (no output file is created)."

---

### SC-08: words-mail-merger README Text

**Input sentence:** "The example takes a Word template file (`template.docx`) and in-memory merge field data as input."
**Output sentence:** "The merged document is saved as `result.docx`."

---

### SC-09: words-report-builder README Text

**Input sentence:** "The example takes a Word template file (`template.docx`) and an in-memory data source object as input."
**Output sentence:** "The generated report is saved as `report.docx`."

---

## Summary

| Case | Scenario | Type | Status |
|------|----------|------|--------|
| SC-01 | pdf-pdf-aconverter | Program.cs location | RESOLVED |
| SC-02 | pdf-text-extractor | Output is stdout | RESOLVED |
| SC-03 | words-mail-merger | Input is template+data | RESOLVED |
| SC-04 | words-report-builder | Input is template+data | RESOLVED |
| SC-05 | email-converter | Output is directory | RESOLVED |
| SC-06 | pdf-pdf-aconverter | README text | RESOLVED |
| SC-07 | pdf-text-extractor | README text | RESOLVED |
| SC-08 | words-mail-merger | README text | RESOLVED |
| SC-09 | words-report-builder | README text | RESOLVED |

**9/9 special cases closed. No null input/output without explicit classification block.**
