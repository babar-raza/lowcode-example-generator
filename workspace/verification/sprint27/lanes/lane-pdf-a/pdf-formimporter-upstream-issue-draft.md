# FormImporter NullReferenceException — Aspose.PDF 26.5.0

## Summary

`Aspose.Pdf.LowCode.FormImporter.Process()` throws `NullReferenceException` on every call with `FormImporterJsonOptions`.

## Package

`Aspose.PDF` version `26.5.0`

## Minimal Reproduction

```csharp
using Aspose.Pdf;
using Aspose.Pdf.Forms;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

// Step 1: Create AcroForm PDF
var doc = new Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new TextFragment("Minimal form"));
var field = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));
field.PartialName = "F1";
field.Value = "original";
doc.Form.Add(field, 1);
doc.Save("minimal-form.pdf");

// Step 2: Export JSON using FormExporter (works fine)
var expOpt = new FormExporterToJsonOptions();
expOpt.AddInput(new FileDataSource("minimal-form.pdf"));
expOpt.AddOutput(new FileDataSource("form-data.json"));
new FormExporter().Process(expOpt); // OK

// Step 3: Import JSON using FormImporter — THROWS
var impOpt = new FormImporterJsonOptions();
impOpt.AddInput(new FileDataSource("minimal-form.pdf"), new FileDataSource("form-data.json"));
impOpt.AddOutput(new FileDataSource("output.pdf"));
new FormImporter().Process(impOpt); // NullReferenceException
```

## Exception

```
System.NullReferenceException: Object reference not set to an instance of an object.
   at Aspose.Pdf.Forms.Form.#=zZQILclhNTKUB(String #=zEpsE$a4=, String& #=zE$vmhTE=, String& #=zi7RY1Vo=)
```

## Observations

- The exception occurs in an obfuscated internal method `#=zZQILclhNTKUB` on `Aspose.Pdf.Forms.Form`
- Reproduced with: round-trip FormExporter JSON, manually-modified JSON, different PDF sources
- `FormExporter` works correctly and produces valid JSON
- The JSON produced by `FormExporter` is passed directly back to `FormImporter` — same crash
- `FormImporterJsonOptions.AddInput` requires 2 arguments: `(IDataSource pdfSource, IDataSource jsonSource)`

## Expected Behavior

`FormImporter.Process()` should import the JSON field data into the PDF and produce a valid output PDF.

## Actual Behavior

`NullReferenceException` is thrown before any output is produced.

## Workaround

None found. All JSON sources and PDF origins trigger the same crash.

## Suggested Fix

The internal `#=zZQILclhNTKUB` method appears to be performing field name resolution and dereferencing a null reference. Please check for null guards when resolving field names from the imported JSON against the PDF form fields.
