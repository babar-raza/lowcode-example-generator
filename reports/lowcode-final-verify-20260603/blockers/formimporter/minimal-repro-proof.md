# FormImporter Minimal Repro

## Bug
`Aspose.Pdf.LowCode.FormImporter.Process()` throws `NullReferenceException`
in `Form.ImportJson(Stream)` for all 3 JSON fixture formats:
1. Flat key-value: `{"field1": "value1"}`
2. Array format: `[{"field": "field1", "value": "value1"}]`
3. Nested format: `{"form": {"fields": [{"name": "field1", "value": "value1"}]}}`

## Environment
- Aspose.PDF 26.5.0
- .NET 8.0
- Windows 11

## Stack trace
```
System.NullReferenceException: Object reference not set to an instance of an object.
   at Aspose.Pdf.Forms.Form.ImportJson(Stream inputStream)
   ...
   at Aspose.Pdf.LowCode.FormImporter.Process(FormImporterOptions options)
```

## Classification
UPSTREAM_BUG — internal SDK defect, not fixable in examples
