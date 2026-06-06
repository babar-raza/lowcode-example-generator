// omr/recognize-omr — W18 canonical package proof
// Canonical URL: https://products.aspose.net/omr/recognize-omr/
// NuGet: Aspose.OMR 24.12.0
// Pattern: OmrEngine().GetTemplateProcessor(template) -> Recognize(image) -> GetCsv() -> save
using System;
using System.IO;
using Aspose.OMR.Api;

Directory.CreateDirectory("output");

string templatePath = Path.Combine("fixtures", "template.omr");
string imagePath    = Path.Combine("fixtures", "template.png");

Console.WriteLine($"Loading OMR template: {templatePath}");
var api = new OmrEngine();
var processor = api.GetTemplateProcessor(templatePath);

Console.WriteLine($"Recognizing image: {imagePath}");
var result = processor.Recognize(imagePath);

// Get CSV content
string csvContent = result.GetCsv();
string csvPath = "output/recognition-result.csv";
File.WriteAllText(csvPath, csvContent);
long csvSize = new FileInfo(csvPath).Length;
Console.WriteLine($"Recognition complete. CSV saved: {csvPath} ({csvSize} bytes)");

// Get JSON too
string jsonContent = result.GetJson();
File.WriteAllText("output/recognition-result.json", jsonContent);

File.WriteAllText("output/result-summary.txt",
    $"Template: {templatePath}\nImage: {imagePath}\nCSV size: {csvSize} bytes\nStatus: PASS");
Console.WriteLine("Status: PASS");
