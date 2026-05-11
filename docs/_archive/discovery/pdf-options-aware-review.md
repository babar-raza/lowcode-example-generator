# PDF Options-Aware Review

**Date:** 2026-05-04
**Sprint:** PDF Role Classification + Options-Aware Review Sprint
**Taskcard:** `followup-pdf-options-aware-review`
**Package:** Aspose.PDF 26.4.0
**Verdict:** `PDF_OPTIONS_AWARE_REVIEW_COMPLETE`

> **IMPORTANT:** This review does NOT enable PDF generation. Generation remains blocked until all 4 PDF taskcards are closed, `pdf.yml` status changes to `active`, and human approval is given.

---

## Standard Options Construction Pattern

All Aspose.PDF LowCode WORKFLOW_ROOT types follow this options pattern:

```csharp
// Step 1: Instantiate paired options type
var options = new MergeOptions();

// Step 2: Add inputs (FileDataSource wraps file paths)
options.AddInput(new FileDataSource("input1.pdf"));
options.AddInput(new FileDataSource("input2.pdf"));

// Step 3: Add output (FileSaveTarget wraps output file path)
options.AddOutput(new FileSaveTarget("output.pdf"));

// Step 4: Set any required properties
// (e.g., options.Password = "secret" for Security)

// Step 5: Create plugin instance and execute
var plugin = new Merger();
var result = plugin.Process(options);

// Step 6: Validate
if (!result.IsSuccess) throw new Exception("Operation failed");
```

**Exception:** TextExtractor has no `AddOutput()` — results are read from `ResultContainer`.

---

## Pilot Type Options Review (4 Types)

### Merger — `MergeOptions`

| Property | Value |
|---|---|
| Inputs | 2+ `FileDataSource` (minimum 2 PDFs) |
| Output | 1 `FileSaveTarget` |
| Sub-options | None required |
| Validation | File exists + byte count > 0 + `%PDF` header |

```csharp
var mergeOptions = new MergeOptions();
mergeOptions.AddInput(new FileDataSource("input1.pdf"));
mergeOptions.AddInput(new FileDataSource("input2.pdf"));
mergeOptions.AddOutput(new FileSaveTarget("output.pdf"));
new Merger().Process(mergeOptions);
```

---

### Splitter — `SplitOptions`

| Property | Value |
|---|---|
| Inputs | 1 `FileDataSource` (multi-page PDF) |
| Output | 1+ `FileSaveTarget` (output naming pattern) |
| Sub-options | None required |
| Validation | At least 1 output file exists with `%PDF` header |
| Note | Splitter auto-names output pages if pattern provided |

```csharp
var splitOptions = new SplitOptions();
splitOptions.AddInput(new FileDataSource("input.pdf"));
splitOptions.AddOutput(new FileSaveTarget("output_{0}.pdf"));
new Splitter().Process(splitOptions);
```

---

### Optimizer — `OptimizeOptions`

| Property | Value |
|---|---|
| Inputs | 1 `FileDataSource` |
| Output | 1 `FileSaveTarget` |
| Sub-options | `CompressOptions`, `ResizeOptions`, `RotateOptions` (all optional) |
| Validation | Output file exists + byte count > 0 + `%PDF` header |

```csharp
var optimizeOptions = new OptimizeOptions();
optimizeOptions.AddInput(new FileDataSource("input.pdf"));
optimizeOptions.AddOutput(new FileSaveTarget("output.pdf"));
new Optimizer().Process(optimizeOptions);
```

---

### TextExtractor — `TextExtractorOptions` ⚠️ DIFFERENT OUTPUT PATTERN

| Property | Value |
|---|---|
| Inputs | 1 `FileDataSource` (PDF with known text) |
| Output | **NO `AddOutput()` call** — read from `ResultContainer` |
| Sub-options | None required |
| Validation | `result.IsSuccess` + extracted text contains known string |

**CRITICAL:** TextExtractor is the only pilot type that does NOT use `AddOutput()`. The extracted text is available in `result.OperationResult[0]` as a `StringResult`.

```csharp
// Create input with known text
var doc = new Aspose.Pdf.Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new Aspose.Pdf.Text.TextFragment("Hello LowCode"));
doc.Save("input.pdf");

// Extract text
var textOptions = new TextExtractorOptions();
textOptions.AddInput(new FileDataSource("input.pdf"));
var result = new TextExtractor().Process(textOptions);

// Validate
var text = ((StringResult)result.OperationResult[0]).Data;
Console.WriteLine(text.Contains("Hello LowCode") ? "PASS" : "FAIL");
```

---

## LLM Code Generation Rules

| Rule | Description |
|---|---|
| 1 | Always instantiate options first, then call `AddInput()`/`AddOutput()` |
| 2 | Use `FileDataSource(path)` for inputs, `FileSaveTarget(path)` for outputs |
| 3 | TextExtractor ONLY: no `AddOutput()` — read `StringResult` from `result.OperationResult` |
| 4 | Always check `result.IsSuccess` |
| 5 | Use template_hints from `pdf.yml` for programmatic input creation |
| 6 | Merger: must have 2+ inputs |
| 7 | Splitter: create multi-page input (3 pages recommended) |
| 8 | `using Aspose.Pdf.LowCode;` always required |
| 9 | `using Aspose.Pdf;` required for programmatic input creation |
| 10 | Never use static method pattern — always instantiate plugin class |

---

## Deferred Types — Key Options Notes

| Type | Key Options Requirement | Why Deferred |
|---|---|---|
| Security | Password required in `EncryptionOptions`/`DecryptionOptions` | Password management + encrypted fixture |
| Signature | PKCS12 cert path + password required in `SignOptions` | Certificate fixture |
| FormEditor | Requires PDF with interactive form fields | Complex fixture |
| PdfAConverter | `PdfAStandardVersion` enum required | PDF/A conformance validation |
| TableGenerator | Complex `TableBuilder` + `TableRowBuilder` + `TableCellBuilder` chain | Builder complexity |
| Html | Input is HTML file or string | Format differs; license check |
| Timestamp | `ServerUrl` required in `TimestampOptions` | Timestamp server needed |

---

## Options Aware Summary

- All 25 WORKFLOW_ROOT types have confirmed paired OPTIONS types
- 4 pilot types use simple AddInput/AddOutput/FileSaveTarget pattern (except TextExtractor)
- TextExtractor is the only pilot type with non-standard output (StringResult)
- All deferred types have documented reasons and can be added to future pilots
