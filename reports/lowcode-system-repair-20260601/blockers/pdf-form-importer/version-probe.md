# PDF FormImporter Investigation — lowcode-system-repair-20260601

## API Discovery
- Class: `Aspose.Pdf.LowCode.FormImporter`
- Namespace: `Aspose.Pdf.LowCode` (VALID — same as all other PDF LowCode classes)
- Package: Aspose.PDF 26.5.0
- Previous claim "invalid namespace" was INCORRECT — Aspose.Pdf.LowCode exists in 26.5.0

## Reflection Evidence
```
FormImporter: EXISTS
  BaseType: System.Object
  Constructor: () — public default
  Method: ResultContainer Process(IPluginOptions options)

FormImporterJsonOptions: EXISTS
  Property: IReadOnlyList<IDataSource> Inputs
  Property: List<IDataSource> Outputs
  Method: void AddInput(IDataSource pdfSource, IDataSource jsonSource)
  Method: void AddOutput(IDataSource saveDataSource)

FormJsonImportSource: EXISTS
  Constructor: (IDataSource pdfSource, IDataSource jsonSource)
  Property: IDataSource PdfSource
  Property: IDataSource JsonSource
```

## Functional Probe Results
All three JSON input formats tested. All crash with same error:

```
NullReferenceException at Aspose.Pdf.Forms.Form (internal obfuscated methods)
  → Aspose.Pdf.Facades.Form.ImportJson(Stream)
  → Aspose.Pdf.LowCode.FormImporter.Process(IPluginOptions)
```

### JSON Format 1: Flat object
```json
{"name": "Test User"}
```
Result: NullReferenceException

### JSON Format 2: Array of field entries
```json
[{"fieldName": "name", "fieldValue": "Test User"}]
```
Result: NullReferenceException

### JSON Format 3: Nested with Fields key
```json
{"Fields": [{"Name": "name", "Value": "Test User"}]}
```
Result: NullReferenceException

## Classification
**UPSTREAM_BUG** — API exists, compiles, has correct namespace, but Process() throws NullReferenceException on all tested JSON formats in Aspose.PDF 26.5.0.

## Retry Condition
Re-test when Aspose.PDF > 26.5.0 is released with fix for Form.ImportJson internal NullReferenceException.

## Note
Previous sprint incorrectly classified this as "invalid namespace (Aspose.Pdf.LowCode)".
The namespace is valid — this is a runtime bug, not a compile error.
