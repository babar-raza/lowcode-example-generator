# Upstream Bug Packet — Aspose.PDF FormImporter LowCode API

## Summary
`Aspose.Pdf.LowCode.FormImporter.Process(FormImporterJsonOptions)` throws `NullReferenceException` for all tested JSON input formats when importing form data into a PDF with AcroForm fields.

## Package
- Aspose.PDF 26.5.0
- Target: net8.0
- OS: Windows 11 Pro 10.0.26200

## Minimal Reproduction
```csharp
var doc = new Document();
var page = doc.Pages.Add();
var field = new TextBoxField(page, new Rectangle(100, 700, 300, 720));
field.PartialName = "name";
doc.Form.Add(field);
doc.Save("form.pdf");

var options = new FormImporterJsonOptions();
options.AddInput(new FileDataSource("form.pdf"), new FileDataSource("data.json"));
options.AddOutput(new FileDataSource("output.pdf"));
new FormImporter().Process(options); // NullReferenceException
```

## Stack Trace
```
System.NullReferenceException: Object reference not set to an instance of an object.
   at Aspose.Pdf.Forms.Form.[obfuscated]
   at Aspose.Pdf.Facades.Form.ImportJson(Stream)
   at Aspose.Pdf.LowCode.FormImporter.[obfuscated](FormImporterJsonOptions)
   at Aspose.Pdf.LowCode.FormImporter.Process(IPluginOptions options)
```

## Source Files
- `workspace/probes/pdf-form-importer/FormImporterProbe.cs`
- `workspace/probes/pdf-form-importer/FormImporterProbe.csproj`
