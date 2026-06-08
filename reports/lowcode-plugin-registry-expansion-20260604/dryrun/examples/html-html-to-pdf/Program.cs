// Dry-run example: html/html-to-pdf-converter
// Canonical URL: https://products.aspose.net/html/html-to-pdf-converter/
// Package: Aspose.HTML 24.12.0
// Pattern: Converter.ConvertHTML(htmlString, baseUri, saveOptions, outputPath)

using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);
string outputPath = Path.Combine(outputDir, "output.pdf");

Converter.ConvertHTML(
    "<h1>Hello from Aspose.HTML</h1><p>HTML to PDF conversion example.</p>",
    ".",
    new PdfSaveOptions(),
    outputPath);

Console.WriteLine($"Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
