# FormImporter.Process() throws NullReferenceException — Aspose.PDF 26.5.0

**Title:** `Aspose.Pdf.LowCode.FormImporter.Process()` throws `NullReferenceException` on all inputs

## Environment

| Property | Value |
|----------|-------|
| Package | `Aspose.PDF` `26.5.0` |
| OS | Windows 11 Pro 10.0.26200 |
| .NET SDK | 10.0.204 (targeting net8.0) |
| Date confirmed | 2026-05-17 |

## Minimal Reproduction

```csharp
using Aspose.Pdf;
using Aspose.Pdf.Forms;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

// Step 1: Create minimal AcroForm PDF
var doc = new Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new TextFragment("Minimal form"));
var field = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));
field.PartialName = "F1";
field.Value = "original";
doc.Form.Add(field, 1);
doc.Save("minimal-form.pdf");

// Step 2: Export JSON using FormExporter (WORKS correctly)
var expOpt = new FormExporterToJsonOptions();
expOpt.AddInput(new FileDataSource("minimal-form.pdf"));
expOpt.AddOutput(new FileDataSource("form-data.json"));
new FormExporter().Process(expOpt); // OK

// Step 3: Import JSON using FormImporter — THROWS NullReferenceException
var impOpt = new FormImporterJsonOptions();
impOpt.AddInput(new FileDataSource("minimal-form.pdf"), new FileDataSource("form-data.json"));
impOpt.AddOutput(new FileDataSource("output.pdf"));
new FormImporter().Process(impOpt); // THROWS
```

## Project File

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Aspose.PDF" Version="26.5.0" />
  </ItemGroup>
</Project>
```

## Exception

```
System.NullReferenceException: Object reference not set to an instance of an object.
   at Aspose.Pdf.Forms.Form.#=zZQILclhNTKUB(String #=zEpsE$a4=, String& #=zE$vmhTE=, String& #=zi7RY1Vo=)
```

## Observations

1. `FormExporter.Process(FormExporterToJsonOptions)` works correctly and produces valid JSON.
2. The exported JSON is passed directly back to `FormImporter` — same crash on every attempt.
3. Tested with: round-trip FormExporter JSON, manually modified JSON, different PDF sources.
4. The `FormImporterJsonOptions.AddInput(IDataSource pdfSource, IDataSource jsonSource)` takes 2 arguments — this is the correct API call.
5. The crash occurs in obfuscated internal method `#=zZQILclhNTKUB` on `Aspose.Pdf.Forms.Form`, suggesting a null guard is missing during field name resolution.

## Exported JSON Sample

```json
[{"FieldType":1,"PageIndex":0,"Rectangle":"100,700,300,730","PageRef":true,"Flags":4,
  "Appearance":{...},"Characteristics":{},"PartialName":"F1","Value":"original"}]
```

## Expected Behavior

`FormImporter.Process()` should populate the output PDF with form field values from the JSON and produce a valid PDF file.

## Actual Behavior

`NullReferenceException` is thrown before any output is produced. No output file is written.

## Workaround

**None found.** All JSON sources and PDF origins trigger the same crash at the same internal frame.

## Attachment

Minimal repro ZIP: `formimporter-nullref-repro.zip` (Program.cs + .csproj, reproduces in `dotnet run`)
