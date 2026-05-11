<!-- GENERATED — do not edit manually. -->
# PDF Fixture Strategy Review

**Date:** 2026-05-05
**Sprint:** PDF Fixture Strategy Review
**Phase:** Phase 4 — Repeatable Fixture Strategy Definition
**Verdict:** `PDF_FIXTURE_STRATEGY_REVIEW_COMPLETE_GENERATION_STILL_BLOCKED`
**Does not enable generation:** YES

---

## Summary

All 4 PDF pilot types (Merger, Splitter, Optimizer, TextExtractor) have validated, repeatable fixture strategies using programmatic PDF creation via `Aspose.Pdf.Document()`.

**Critical API corrections discovered in Phase 3:**
1. `AddOutput()` takes `FileDataSource`, NOT `FileSaveTarget`
2. `ResultContainer.ResultCollection` (not `OperationResult`), no `IsSuccess`
3. Splitter output: plain filename only, no format string expansion
4. `StringResult.Text` for extracted text

---

## Fixture Strategies

### 1. `programmatic_pdf_single` — Optimizer

```csharp
var doc = new Aspose.Pdf.Document();
doc.Pages.Add();
doc.Save("input.pdf");
```

Source in `pdf.yml`: `template_hints.input_creation_lines` — already documented.

---

### 2. `programmatic_pdf_multi_page` — Splitter

```csharp
var doc = new Aspose.Pdf.Document();
doc.Pages.Add();
doc.Pages.Add();
doc.Pages.Add();
doc.Save("input.pdf");
```

Extends `template_hints.input_creation_lines` with extra `Pages.Add()` calls.

---

### 3. `programmatic_pdf_pair` — Merger

```csharp
var doc1 = new Aspose.Pdf.Document();
doc1.Pages.Add();
doc1.Save("input1.pdf");
var doc2 = new Aspose.Pdf.Document();
doc2.Pages.Add();
doc2.Save("input2.pdf");
```

Source in `pdf.yml`: `template_hints.merger_input_creation_lines` — already documented.

---

### 4. `programmatic_pdf_known_text` — TextExtractor

```csharp
var doc = new Aspose.Pdf.Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new Aspose.Pdf.Text.TextFragment("Hello LowCode PDF"));
doc.Save("input.pdf");
```

Extends `template_hints.input_creation_lines` with `TextFragment` for text extraction validation.

---

## Corrected API Patterns (Required for LLM Code Generation)

### Standard Pattern (Merger, Splitter, Optimizer)

```csharp
var options = new XxxOptions();
options.AddInput(new FileDataSource("input.pdf"));    // FileDataSource
options.AddOutput(new FileDataSource("output.pdf")); // FileDataSource — NOT FileSaveTarget
var plugin = new XxxPlugin();
var result = plugin.Process(options);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Succeeded" : "Failed");
```

### TextExtractor (no output file)

```csharp
var textOptions = new TextExtractorOptions();
textOptions.AddInput(new FileDataSource("input.pdf"));
// NO AddOutput() — result is in ResultCollection
var extractor = new TextExtractor();
var result = extractor.Process(textOptions);
if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)
    Console.WriteLine($"Extracted: {sr.Text}");
```

---

## Updated LLM Code Generation Rules

The 10 rules from `pdf-options-aware-review.json` must be amended:

| Rule | Original | Corrected |
|---|---|---|
| Output method | `options.AddOutput(new FileSaveTarget("output.pdf"))` | `options.AddOutput(new FileDataSource("output.pdf"))` |
| Success check | `result.IsSuccess` | `result.ResultCollection.Count > 0` |
| String result | `((StringResult)result.OperationResult[0]).Data` | `((StringResult)result.ResultCollection[0]).Text` |
| Splitter output | `"output_{0}.pdf"` format string | Simple `"output.pdf"` — no format expansion |

---

## Output Validation by Type

| Type | Validation Method |
|---|---|
| Merger | `File.Exists(outputPath)` + `%PDF` header check |
| Splitter | `File.Exists(outputPath)` + `%PDF` header check |
| Optimizer | `File.Exists(outputPath)` + `%PDF` header check |
| TextExtractor | `result.ResultCollection.Count > 0` + `sr.Text.Contains(knownText)` |

---

## Generation Status

PDF generation remains **BLOCKED**:
1. `pdf.yml` status is `discovery_only` — must not change until human approval
2. `followup-pdf-family-repo-target-mapping` — open (target repo not mapped)
3. `followup-pdf-controlled-pilot-enablement` — open (requires human approval after all prerequisites)
