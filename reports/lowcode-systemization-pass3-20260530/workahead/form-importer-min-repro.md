# FormImporter Minimum Repro — lowcode-systemization-pass3-20260530

## Status: EXTERNAL_BUG_BLOCKER (BLK-001)

The Aspose.Pdf.LowCode.FormImporter.ImportFromJson() method throws a
NullReferenceException when called with a valid PDF and JSON payload.

Minimum repro:
```csharp
using Aspose.Pdf.LowCode;
FormImporter.ImportFromJson("input.pdf", "data.json", "output.pdf");
// throws NullReferenceException
```

Expected: Successfully imports JSON form data into PDF
Actual: System.NullReferenceException in Aspose.Pdf.LowCode
