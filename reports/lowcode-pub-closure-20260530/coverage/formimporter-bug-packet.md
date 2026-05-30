# FormImporter Bug Packet — lowcode-pub-closure-20260530

## Bug: NullReferenceException in Aspose.PDF.LowCode.FormImporter

### Repro
```csharp
var options = new FormImporterJsonOptions { DataFilePath = "data.json" };
FormImporter.Process(inputPdf, outputPdf, options);
```
Results in NullReferenceException at Aspose.PDF.LowCode.FormImporter.Process.

### Classification: EXTERNAL_BUG_BLOCKER
- Aspose.PDF bug — not a test/fixture issue
- Retry condition: Fixed in a future Aspose.PDF version
- Report: Bug should be filed with Aspose support team
