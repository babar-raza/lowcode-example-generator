# PDF LowCode Type Role Classification

**Date:** 2026-05-04
**Sprint:** PDF Role Classification + Options-Aware Review Sprint
**Taskcard:** `followup-pdf-role-classification-review`
**Package:** Aspose.PDF 26.4.0
**Namespace:** Aspose.Pdf.LowCode
**Total Types:** 101
**Verdict:** `PDF_ROLE_CLASSIFICATION_COMPLETE`

> **IMPORTANT:** This classification does NOT enable PDF generation. Generation remains blocked until all 4 PDF taskcards are closed, `pdf.yml` status changes to `active`, and human approval is given.

---

## Role Summary

| Role | Count | Description |
|---|---|---|
| WORKFLOW_ROOT | 25 | Directly executable IPlugin types with Process() method |
| OPTIONS | 51 | Parameter bags passed to WORKFLOW_ROOT.Process() |
| PROVIDER_CALLBACK | 5 | Interfaces (IPlugin, IDataSource, ISaveTarget, etc.) |
| RESULT | 6 | Output containers from Process() |
| DATA_SOURCE | 3 | Concrete IDataSource implementations |
| SAVE_TARGET | 2 | Concrete ISaveTarget implementations |
| BUILDER | 4 | Builder-pattern types for TableGenerator |
| ENUM | 4 | Enumeration value types |

---

## Key Architectural Finding

Aspose.PDF LowCode uses the **instance-method IPlugin pattern**, not the static-method pattern used by Aspose.Cells/Words LowCode:

```csharp
// PDF LowCode pattern (instance-method):
var options = new MergeOptions();
options.AddInput(new FileDataSource("input1.pdf"));
options.AddInput(new FileDataSource("input2.pdf"));
options.AddOutput(new FileSaveTarget("output.pdf"));
var plugin = new Merger();
plugin.Process(options);

// Words/Cells LowCode pattern (static method):
Converter.Convert("input.docx", "output.pdf");
```

This explains why `workflow_root_candidate_count=0` in `family-generation-readiness-rank.json` — the auto-classifier uses a static-method heuristic. After this classification, the count updates to **25**.

---

## WORKFLOW_ROOT Types (25)

All 25 types confirmed as WORKFLOW_ROOT. All implement `IPlugin` and accept specific `XxxOptions` types.

### Pilot-Eligible (4)

| Type | Paired Options | Priority | Confidence | Rationale |
|---|---|---|---|---|
| **Merger** | MergeOptions | 1 | 0.98 | Simple: 2 PDFs → 1 merged PDF. Programmatic input straightforward. |
| **Splitter** | SplitOptions | 2 | 0.98 | Simple: 1 multi-page PDF → split pages. |
| **Optimizer** | OptimizeOptions | 3 | 0.98 | Simple: 1 PDF → optimized PDF. |
| **TextExtractor** | TextExtractorOptions | 4 | 0.95 | Input: PDF with known text. Output: StringResult for validation. |

### Deferred to Later Pilot (21)

| Type | Paired Options | Deferred Reason |
|---|---|---|
| DocConverter | PdfConverterOptions | Format-specific DOC output validation |
| FormEditor | FormEditorOptions | Requires PDF with existing form fields |
| FormExporter | FormExporterOptions | Requires PDF with form fields |
| FormFlattener | FormFlattenerOptions | Requires PDF with interactive form fields |
| FormImporter | FormImporterJsonOptions | Requires PDF with form fields + JSON data |
| Html | HtmlToPdfOptions | May require license; format differs |
| ImageExtractor | ImageExtractorOptions | Image output format inspection |
| Jpeg | JpegOptions | Image conversion; deferred to later pilot |
| Ofd | OfdToPdfOptions | Niche OFD format; requires OFD fixtures |
| PdfAConverter | PdfAConvertOptions | PDF/A conformance validation tooling required |
| PdfExtractor | PdfExtractorOptions | Content parsing for validation |
| PdfToImage | PdfToImageOptions | Image output format inspection |
| Png | PngOptions | Image output; same reason as PdfToImage |
| Security | EncryptionOptions / DecryptionOptions | Password management; encrypted PDF fixture |
| SelectField | FormFieldOptions | Requires PDF with interactive form fields |
| Signature | SignOptions | PKCS12 certificate fixture required |
| TableGenerator | PdfGeneratorOptions | Complex TableBuilder pattern |
| Tiff | TiffOptions | TIFF output; image conversion deferred |
| Timestamp | TimestampOptions | Timestamp server or local cert fixture |
| TocGenerator | TocOptions | Requires PDF with headings for meaningful TOC |
| XlsConverter | PdfToXlsOptions | Format-specific XLS output validation |

---

## OPTIONS Types (51)

All 51 OPTIONS types confirmed. Each is a parameter bag with primarily properties. No `Process()` method. Instantiated by user and passed to `WORKFLOW_ROOT.Process()` via `AddInput()` / `AddOutput()` calls.

Key groupings:
- **Form field operations** (17 types): FormCheckBoxField*, FormComboBoxField*, FormEditorAdd/Remove/Set*, FormField*, FormFlattener*, FormImporter*, FormTextBoxField*, FormOptions, FormRemoveAll/Selected*
- **Merger/Splitter** (2 types): MergeOptions, SplitOptions
- **Image output** (5 types): JpegOptions, PngOptions, TiffOptions, PdfToImageOptions, ImageExtractorOptions
- **PDF/A** (3 types): PdfAConvertOptions, PdfAOptionsBase, PdfAValidateOptions
- **Optimizer/Transform** (3 types): OptimizeOptions, CompressOptions, ResizeOptions, RotateOptions
- **Conversion** (4 types): PdfConverterOptions, PdfToDocOptions, PdfToHtmlOptions, PdfToXlsOptions, HtmlToPdfOptions, OfdToPdfOptions

---

## PROVIDER_CALLBACK Types (5)

Interfaces only. Pipeline does not generate stubs for these.

| Interface | Description |
|---|---|
| IPlugin | Root plugin interface. All WORKFLOW_ROOT types implement this. |
| IPluginOptions | Root options interface. All OPTIONS types implement this. |
| IDataSource | Input data interface. Implemented by FileDataSource, StreamDataSource. |
| ISaveTarget | Output capture interface. Implemented by FileSaveTarget, StreamSaveTarget. |
| IOperationResult | Result interface. Implemented by ResultContainer. |

---

## RESULT Types (6)

Output containers returned by `Process()`. Used for validation only.

| Type | Use |
|---|---|
| ResultContainer | Top-level container; has `IsSuccess` property. |
| StringResult | Text content (used by TextExtractor). |
| FileResult | File path of result. |
| StreamResult | Stream output. |
| ObjectResult | Arbitrary object result. |
| PdfAValidationResult | PDF/A conformance result. |

---

## DATA_SOURCE Types (3)

| Type | Constructor | Use |
|---|---|---|
| FileDataSource | `new FileDataSource(string filePath)` | Standard input factory. Used in `options.AddInput()`. |
| StreamDataSource | `new StreamDataSource(Stream stream)` | Stream-based input. |
| FormJsonImportSource | `new FormJsonImportSource(string jsonPath)` | JSON source for FormImporter. |

---

## SAVE_TARGET Types (2)

| Type | Constructor | Use |
|---|---|---|
| FileSaveTarget | `new FileSaveTarget(string filePath)` | Standard output factory. Used in `options.AddOutput()`. |
| StreamSaveTarget | `new StreamSaveTarget(Stream stream)` | Stream-based output. |

---

## BUILDER Types (4)

Used with `TableGenerator` to construct structured table data.

| Type | Method | Use |
|---|---|---|
| TableBuilder | `AddRow(TableRowBuilder)` | Top-level table structure builder. |
| TableRowBuilder | `AddCell(TableCellBuilder)` | Row builder. |
| TableCellBuilder | `AddParagraph()`, `SetBackgroundColor()` | Cell builder. |
| TableOptions | — | Container holding TableBuilder; passed to TableGenerator. |

---

## ENUM Types (4)

| Type | Values |
|---|---|
| ConversionMode | EnhancedFlow, Pure (PDF-to-document conversion quality mode) |
| DataType | Form data type classifier |
| PdfAStandardVersion | PDF_A_1A, PDF_A_1B, PDF_A_2A, PDF_A_2B, PDF_A_3A, PDF_A_3B |
| SaveFormat | Doc, DocX (output format for DocConverter) |

---

## Updated Generation Readiness Fields

After classification, `family-generation-readiness-rank.json` for PDF is updated:

| Field | Before | After |
|---|---|---|
| `workflow_root_candidate_count` | 0 | 25 |
| `options_type_count` | 41 | 51 |
| `expected_output_validation_supported` | false | true |
| `generation_risk` | high | medium |
| `recommended_next_action` | needs_type_role_rules | close_followup_pdf_options_aware_review |
| `generation_ready` | false | **false (unchanged)** |

**Generation remains blocked.** Classification only updates the informational fields.

---

## Standard PDF LowCode Code Pattern

```csharp
// Step 1: Create options and add inputs/outputs
var options = new MergeOptions();  // Replace with specific XxxOptions
options.AddInput(new FileDataSource("input1.pdf"));
options.AddInput(new FileDataSource("input2.pdf"));
options.AddOutput(new FileSaveTarget("output.pdf"));

// Step 2: Create plugin instance and execute
var plugin = new Merger();  // Replace with specific WORKFLOW_ROOT
var result = plugin.Process(options);

// Step 3: Validate result
if (!result.IsSuccess) { /* handle error */ }
```
