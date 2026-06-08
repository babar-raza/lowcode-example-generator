# FormImporter Upstream Bug — Retry Taskcard

## Example: pdf/form-importer

## Classification
EXTERNAL_UPSTREAM_BUG — NullReferenceException in Aspose.PDF 26.5.0 `Form.ImportJson()`

## Bug Summary
FormImporter.Process() calls Form.ImportJson() which throws NullReferenceException regardless of JSON format used (FormExport, DataExchange, FDF-style). The bug is in Aspose.PDF internals, not in the generated example code.

## Min-Repro
Available at: `workspace/probes/pdf-form-importer/FormImporterProbe.cs`
- Creates AcroForm PDF with text fields
- Creates valid JSON data
- Calls FormImporter.Process(FormImporterJsonOptions)
- All 3 JSON formats crash with same NullReferenceException

## Stack Trace
```
System.NullReferenceException: Object reference not set to an instance of an object.
   at Aspose.Pdf.Forms.Form.ImportJson(...)
```

## Retry Condition
Retry when Aspose.PDF releases a version where FormImporter.Process() no longer throws NullReferenceException. Check release notes for "FormImporter" or "ImportJson" fix.

## Publication Decision
EXTERNAL_UPSTREAM_BUG — excluded from publication until upstream fix available.
