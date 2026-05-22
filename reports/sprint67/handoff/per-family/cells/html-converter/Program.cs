using System;
using System.IO;
using Aspose.Cells.LowCode;

string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
if (!File.Exists(inputPath))
    throw new FileNotFoundException("Input file not found", inputPath);

string outputPath = Path.Combine(AppContext.BaseDirectory, "output.html");

// Convert Excel to HTML using the simplest overload
HtmlConverter.Process(inputPath, outputPath);

// Validate output
if (File.Exists(outputPath))
{
    var info = new FileInfo(outputPath);
    Console.WriteLine($"Conversion succeeded. Output: {outputPath} ({info.Length} bytes)");
}
else
{
    throw new InvalidOperationException("Output file was not created");
}