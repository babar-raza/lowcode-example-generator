<!-- GENERATED — do not edit manually. -->
# PDF Programmatic Fixture Validation

**Date:** 2026-05-05
**Sprint:** PDF Fixture Strategy Review
**Phase:** Phase 3 — Programmatic Fixture Validation
**Result:** ALL_PASS (8/8)
**Does not enable generation:** YES

---

## Harness

Project: `workspace/fixture-validation/pdf-harness/PdfFixtureHarness.csproj`
- Build: 0 errors, 0 warnings
- Target: `net8.0`, `Aspose.PDF 26.4.0`
- All 4 fixture types + all 4 LowCode API tests: PASS

---

## Fixture Creation Results

| Fixture | Filename(s) | Bytes | Header Valid | Status |
|---|---|---|---|---|
| `programmatic_pdf_single` | `input-single.pdf` | 28837 | ✓ | **PASS** |
| `programmatic_pdf_multi_page` | `input-three-page.pdf` | 30192 | ✓ | **PASS** |
| `programmatic_pdf_pair` | `input-merge-a.pdf` + `input-merge-b.pdf` | 28837 + 28837 | ✓ | **PASS** |
| `programmatic_pdf_known_text` | `input-text.pdf` | 29359 | ✓ | **PASS** |

---

## LowCode API Test Results

| Test | API Pattern | Result | Output |
|---|---|---|---|
| Merger | `new MergeOptions() + AddInput x2 + AddOutput + new Merger().Process()` | **PASS** | 84533 bytes |
| Splitter | `new SplitOptions() + AddInput + AddOutput + new Splitter().Process()` | **PASS** | 1 file |
| Optimizer | `new OptimizeOptions() + AddInput + AddOutput + new Optimizer().Process()` | **PASS** | 56521 bytes |
| TextExtractor | `new TextExtractorOptions() + AddInput [no AddOutput] + new TextExtractor().Process()` | **PASS** | Text found |

---

## Critical API Corrections Found

### 1. `AddOutput()` Takes `FileDataSource`, NOT `FileSaveTarget` (HIGH)

Prior sprint documentation stated `AddOutput(new FileSaveTarget("output.pdf"))`. This is **INCORRECT**.

`AddOutput()` is defined as `void AddOutput(IDataSource saveDataSource)` — it takes `IDataSource`.
`FileSaveTarget` implements `ISaveTarget`, NOT `IDataSource`. The compiler rejects `FileSaveTarget`.

**Correct pattern:**
```csharp
options.AddOutput(new FileDataSource("output.pdf"));  // CORRECT
options.AddOutput(new FileSaveTarget("output.pdf"));  // WRONG — compiler error
```

All code templates from `pdf-options-aware-review.json` and `pdf-controlled-pilot-recommendation.json` must be updated.

### 2. Splitter Output Naming — No Format String Expansion (MEDIUM)

`SplitOptions.AddOutput(new FileDataSource("output_{0}.pdf"))` does NOT expand `{0}`.
The filename is used **literally**, producing a single file named `output_{0}.pdf`.

**Correct pattern:**
```csharp
splitOptions.AddOutput(new FileDataSource("output.pdf"));  // Simple filename
```

The Splitter writes its output to the provided filename directly.

### 3. `ResultContainer.ResultCollection` (MEDIUM)

`ResultContainer` has `ResultCollection: List<IOperationResult>`, NOT `OperationResult`.
`ResultContainer` has no `IsSuccess` property.

**Correct success check:**
```csharp
bool success = result.ResultCollection.Count > 0;
```

### 4. `StringResult.Text` for Extracted Text

`StringResult` inherits from `IOperationResult`. The extracted text is in `StringResult.Text`.

```csharp
if (result.ResultCollection[0] is StringResult sr)
{
    var text = sr.Text;
    Console.WriteLine(text.Contains("Hello LowCode PDF") ? "Found" : "Not found");
}
```

---

## Corrected Code Templates

### Merger
```csharp
var mergeOptions = new MergeOptions();
mergeOptions.AddInput(new FileDataSource("input1.pdf"));
mergeOptions.AddInput(new FileDataSource("input2.pdf"));
mergeOptions.AddOutput(new FileDataSource("output.pdf"));  // FileDataSource, not FileSaveTarget
var merger = new Merger();
var result = merger.Process(mergeOptions);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Merge succeeded" : "Merge failed");
```

### Splitter
```csharp
var splitOptions = new SplitOptions();
splitOptions.AddInput(new FileDataSource("input.pdf"));
splitOptions.AddOutput(new FileDataSource("output.pdf"));  // Simple filename, no format string
var splitter = new Splitter();
var result = splitter.Process(splitOptions);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Split succeeded" : "Split failed");
```

### Optimizer
```csharp
var optimizeOptions = new OptimizeOptions();
optimizeOptions.AddInput(new FileDataSource("input.pdf"));
optimizeOptions.AddOutput(new FileDataSource("output.pdf"));
var optimizer = new Optimizer();
var result = optimizer.Process(optimizeOptions);
Console.WriteLine(result.ResultCollection.Count > 0 ? "Optimize succeeded" : "Optimize failed");
```

### TextExtractor
```csharp
var textOptions = new TextExtractorOptions();
textOptions.AddInput(new FileDataSource("input.pdf"));
// No AddOutput() — result in ResultCollection
var extractor = new TextExtractor();
var result = extractor.Process(textOptions);
if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)
    Console.WriteLine($"Extracted: {sr.Text}");
```

---

## Evaluation Mode Notes

- All PDFs created without a license are in evaluation mode
- Evaluation adds watermark text: `"Evaluation Only. Created with Aspose.PDF. Copyright 2002-2026"`
- TextExtractor captures this text in addition to the known text
- Validation must use `Contains()` not `Equals()` for text matching
- For licensed mode, evaluation watermark will not appear
