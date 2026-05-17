using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.Forms;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

// Minimal repro for FormImporter NullReferenceException — Aspose.PDF 26.5.0
// Bug: FormImporter.Process() throws NullReferenceException in Forms.Form.#=zZQILclhNTKUB
// regardless of JSON format or PDF origin.

Console.WriteLine("=== FormImporter NullRef Minimal Repro ===");
Console.WriteLine("Aspose.PDF version: 26.5.0");

// Create a minimal AcroForm PDF
var doc = new Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new TextFragment("Minimal form"));
var field = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));
field.PartialName = "F1";
field.Value = "original";
doc.Form.Add(field, 1);
doc.Save("minimal-form.pdf");
Console.WriteLine("Fixture: minimal-form.pdf created");

// Export JSON via FormExporter (known-good LowCode API)
var expOpt = new FormExporterToJsonOptions();
expOpt.AddInput(new FileDataSource("minimal-form.pdf"));
expOpt.AddOutput(new FileDataSource("minimal-form-data.json"));
new FormExporter().Process(expOpt);
Console.WriteLine($"FormExporter JSON created: {File.Exists("minimal-form-data.json")}");
Console.WriteLine($"JSON content: {File.ReadAllText("minimal-form-data.json")}");

// Attempt import — this triggers the NullReferenceException
Console.WriteLine("Attempting FormImporter.Process...");
try
{
    var impOpt = new FormImporterJsonOptions();
    impOpt.AddInput(new FileDataSource("minimal-form.pdf"), new FileDataSource("minimal-form-data.json"));
    impOpt.AddOutput(new FileDataSource("minimal-form-output.pdf"));
    var result = new FormImporter().Process(impOpt);
    Console.WriteLine($"PASS: {result.ResultCollection.Count} items");
}
catch (NullReferenceException nre)
{
    Console.WriteLine($"NULLREF_CONFIRMED: {nre.Message}");
    Console.WriteLine($"Stack[0]: {nre.StackTrace?.Split('\n')[0]}");
    Console.WriteLine("DEFECT_REPRODUCED: Aspose.PDF 26.5.0 FormImporter NullReferenceException in Forms.Form");
}
catch (Exception ex)
{
    Console.WriteLine($"OTHER_EXCEPTION: {ex.GetType().Name}: {ex.Message}");
}
