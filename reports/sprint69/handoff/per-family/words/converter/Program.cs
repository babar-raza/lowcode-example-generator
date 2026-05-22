using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

string inputPath = Path.Combine(Path.GetTempPath(), "input.docx");
string outputPath = Path.Combine(Path.GetTempPath(), "output.pdf");

// Create a simple DOCX file
var document = new Document();
var builder = new DocumentBuilder(document);
builder.Writeln("Hello, Aspose.Words!");
document.Save(inputPath);

// Validate the input file exists and is non‑empty
if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
{
    throw new InvalidOperationException("Failed to create the input DOCX file.");
}

// Convert DOCX to PDF using the simplest overload
Converter.Convert(inputPath, outputPath);

// Validate the output file exists and is non‑empty
if (!File.Exists(outputPath) || new FileInfo(outputPath).Length == 0)
{
    throw new InvalidOperationException("Conversion failed; output PDF was not created.");
}

// Deterministic success message
Console.WriteLine($"Conversion succeeded: {outputPath}");
