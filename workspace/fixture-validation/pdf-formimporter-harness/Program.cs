using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.Forms;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

Console.WriteLine("=== FormImporter API Probe Harness ===");

// Step 1: Create AcroForm PDF with a text field
Console.WriteLine("Creating AcroForm PDF fixture...");
var doc = new Document();
var page = doc.Pages.Add();
page.Paragraphs.Add(new TextFragment("Form with importable fields"));
var textBox = new TextBoxField(page, new Aspose.Pdf.Rectangle(100, 700, 300, 730));
textBox.PartialName = "TextField1";
textBox.Value = "OriginalValue";
doc.Form.Add(textBox, 1);
doc.Save("acroform-input.pdf");
Console.WriteLine("AcroForm PDF created: acroform-input.pdf");

// Step 2: Export form data to JSON using FormExporter (to get the correct JSON format)
Console.WriteLine("Exporting form fields to JSON via FormExporter...");
try
{
    var exportOptions = new FormExporterToJsonOptions();
    exportOptions.AddInput(new FileDataSource("acroform-input.pdf"));
    exportOptions.AddOutput(new FileDataSource("form-data.json"));
    new FormExporter().Process(exportOptions);
    Console.WriteLine($"Exported JSON exists: {File.Exists("form-data.json")}");
    if (File.Exists("form-data.json"))
    {
        var exported = File.ReadAllText("form-data.json");
        Console.WriteLine($"Exported JSON (first 200 chars): {exported[..Math.Min(200, exported.Length)]}");
    }
}
catch (Exception ex)
{
    Console.WriteLine($"EXPORT_FAIL: {ex.GetType().Name}: {ex.Message}");
}

// Step 3: Modify exported JSON to have updated values, then import back
if (File.Exists("form-data.json"))
{
    var originalJson = File.ReadAllText("form-data.json");
    var modifiedJson = originalJson.Replace("OriginalValue", "ImportedValue");
    File.WriteAllText("form-data-modified.json", modifiedJson, new System.Text.UTF8Encoding(false));
    Console.WriteLine("Modified JSON created for import.");

    // Test 1: Import unmodified FormExporter JSON (round-trip)
    Console.WriteLine("Test 1: Round-trip with FormExporter JSON...");
    try
    {
        var opt1 = new FormImporterJsonOptions();
        opt1.AddInput(new FileDataSource("acroform-input.pdf"), new FileDataSource("form-data.json"));
        opt1.AddOutput(new FileDataSource("output-roundtrip.pdf"));
        var r1 = new FormImporter().Process(opt1);
        Console.WriteLine($"Test 1: {r1.ResultCollection.Count} items, output={File.Exists("output-roundtrip.pdf")}");
        Console.WriteLine("FORMIMPORTER_ROUNDTRIP_PASS");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"FORMIMPORTER_ROUNDTRIP_FAIL: {ex.GetType().Name}: {ex.Message}");
        Console.WriteLine($"Stack: {ex.StackTrace?.Split('\n')[0]}");
        if (ex.InnerException != null) Console.WriteLine($"Inner: {ex.InnerException.Message}");
    }

    // Test 2: Add FullName to exported JSON (PartialName alone may be insufficient)
    Console.WriteLine("Test 2: Exported JSON with FullName added...");
    var exportedWithFull = File.ReadAllText("form-data.json")
        .Replace("\"PartialName\":\"TextField1\"", "\"PartialName\":\"TextField1\",\"FullName\":\"TextField1\"");
    File.WriteAllText("form-data-fullname.json", exportedWithFull, new System.Text.UTF8Encoding(false));
    try
    {
        var opt2 = new FormImporterJsonOptions();
        opt2.AddInput(new FileDataSource("acroform-input.pdf"), new FileDataSource("form-data-fullname.json"));
        opt2.AddOutput(new FileDataSource("output-fullname.pdf"));
        var r2 = new FormImporter().Process(opt2);
        Console.WriteLine($"Test 2: {r2.ResultCollection.Count} items, output={File.Exists("output-fullname.pdf")}");
        Console.WriteLine("FORMIMPORTER_FULLNAME_PASS");
    }
    catch (Exception ex)
    {
        Console.WriteLine($"FORMIMPORTER_FULLNAME_FAIL: {ex.GetType().Name}: {ex.Message}");
        Console.WriteLine($"Stack: {ex.StackTrace?.Split('\n')[0]}");
    }

    // Test 3: Try with known-good AcroForm from PR#8 form-exporter (copied as form-exporter-input.pdf)
    if (File.Exists("form-exporter-input.pdf"))
    {
        Console.WriteLine("Test 3: FormImporter with known PR#8 AcroForm PDF...");
        // First export to JSON from the known PDF
        try
        {
            var expOpt = new FormExporterToJsonOptions();
            expOpt.AddInput(new FileDataSource("form-exporter-input.pdf"));
            expOpt.AddOutput(new FileDataSource("known-form-data.json"));
            new FormExporter().Process(expOpt);
            Console.WriteLine($"Test 3 export: {File.Exists("known-form-data.json")}");
        }
        catch (Exception ex) { Console.WriteLine($"Test 3 export fail: {ex.Message}"); }

        if (File.Exists("known-form-data.json"))
        {
            try
            {
                var opt3 = new FormImporterJsonOptions();
                opt3.AddInput(new FileDataSource("form-exporter-input.pdf"), new FileDataSource("known-form-data.json"));
                opt3.AddOutput(new FileDataSource("output-known.pdf"));
                var r3 = new FormImporter().Process(opt3);
                Console.WriteLine($"Test 3 import: {r3.ResultCollection.Count} items, output={File.Exists("output-known.pdf")}");
                Console.WriteLine("FORMIMPORTER_KNOWN_PASS");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"FORMIMPORTER_KNOWN_FAIL: {ex.GetType().Name}: {ex.Message}");
                Console.WriteLine($"Stack: {ex.StackTrace?.Split('\n')[0]}");
            }
        }
    }
}
