# I/O Format Authority Matrix — Sprint 57

**Source:** `pipeline/format-authority/contracts/*.json` (api_verified)
**Generated:** 2026-05-21
**Total types:** 42

| Family | Type | Input Format | Output Format | Output Kind | Cardinality | Validation Method |
|--------|------|-------------|---------------|-------------|-------------|------------------|
| cells | SpreadsheetConverter | .xlsx | .csv | file | single | file_exists |
| cells | JsonConverter | .xlsx | .json | file | single | file_exists |
| cells | HtmlConverter | .xlsx | .html | file | single | file_exists |
| cells | TextConverter | .xlsx | .txt | file | single | file_exists |
| cells | ImageConverter | .xlsx | .png | file | single | file_exists |
| cells | PdfConverter | .xlsx | .pdf | file | single | file_exists |
| cells | SpreadsheetMerger | .xlsx (multi) | .xlsx | file | single | file_exists |
| cells | SpreadsheetSplitter | .xlsx | .xlsx | file | multi | result_collection_count |
| cells | SpreadsheetLocker | .xlsx | .xlsx | file | single | file_exists |
| diagram | DiagramConverter | .vsdx | .vdx | file | single | file_exists |
| diagram | PdfConverter | .vsdx | .pdf | file | single | file_exists |
| email | Converter | .eml | directory | directory | — | directory_exists |
| pdf | DocConverter | .pdf | .docx | file | single | file_exists |
| pdf | XlsConverter | .pdf | .xlsx | file | single | file_exists |
| pdf | Html | .html | .pdf | file | single | file_exists |
| pdf | Jpeg | .pdf | .jpg | file | multi | result_collection_count |
| pdf | Png | .pdf | .png | file | multi | result_collection_count |
| pdf | Tiff | .pdf | .tiff | file | multi | result_collection_count |
| pdf | TextExtractor | .pdf | stdout | stdout | — | string_result_check |
| pdf | Merger | .pdf (multi) | .pdf | file | single | file_exists |
| pdf | Splitter | .pdf | .pdf | file | multi | result_collection_count |
| pdf | Optimizer | .pdf | .pdf | file | single | file_exists |
| pdf | PdfAConverter | .pdf | .pdf | file | single | file_exists |
| pdf | TocGenerator | .pdf | .pdf | file | single | file_exists |
| pdf | TableGenerator | .pdf | .pdf | file | single | file_exists |
| pdf | ImageExtractor | .pdf | .png | file | multi | result_collection_count |
| pdf | Security | .pdf | .pdf | file | single | file_exists |
| pdf | FormFlattener | .pdf | .pdf | file | single | file_exists |
| pdf | FormEditor | .pdf | .pdf | file | single | file_exists |
| pdf | FormExporter | .pdf | .json | file | single | file_exists |
| pdf | Signature | .pdf | .pdf | file | single | file_exists |
| slides | Convert | .pptx | .pdf | file | single | file_exists |
| slides | Merger | .pptx (multi) | .pptx | file | single | file_exists |
| slides | Compress | .pptx | .pptx | file | single | file_exists |
| words | Converter | .docx | .pdf | file | single | file_exists |
| words | Merger | .docx (multi) | .docx | file | single | file_exists |
| words | Splitter | .docx | .docx | file | multi | result_collection_count |
| words | Comparer | .docx (pair) | .docx | file | single | file_exists |
| words | MailMerger | .docx | .docx | file | single | file_exists |
| words | ReportBuilder | .docx | .docx | file | single | file_exists |
| words | Watermarker | .docx | .docx | file | single | file_exists |
| words | Replacer | .docx | .docx | file | single | file_exists |

## Special Output Kinds

### stdout/string-result
- **pdf/TextExtractor**: No `AddOutput()`. Results accessed via `result.ResultCollection[0]` as `StringResult`. Read text via `((StringResult)r).Text`. Must use `Contains()` not `Equals()` for unlicensed PDF (evaluation watermark included).

### directory
- **email/Converter**: Output via `FolderOutputHandler`. Produces a directory containing multiple HTML/attachment files. Validate via `Directory.Exists(outputDir)`.

### multi-file output
- **cells/SpreadsheetSplitter**: Produces multiple .xlsx files. Validate `result.ResultCollection.Count > 0`.
- **pdf/Jpeg, Png, Tiff**: Produces per-page image files. Validate `result.ResultCollection.Count > 0`.
- **pdf/ImageExtractor**: Produces embedded image files as .png. Validate `result.ResultCollection.Count > 0`.

## Evidence Authority

All entries: `evidence_confidence = "api_verified"` — sourced from DllReflector API catalog + pipeline contracts enrichment.

Evidence reference: `workspace/verification/lowcode-api-format-authority-20260519-153439/reports/api-backed-format-contracts.json`
