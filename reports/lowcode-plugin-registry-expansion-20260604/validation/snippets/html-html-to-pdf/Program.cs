// Snippet validation: html/html-to-pdf-converter
// Source: https://products.aspose.net/html/html-to-pdf-converter/
// Official code: HTMLtoPDFExample.cs (aspose-html/Aspose.HTML-for-.NET)
// Pattern: Converter.ConvertHTML(htmlString, baseUri, saveOptions, outputPath)

using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);
string outputPath = Path.Combine(outputDir, "output.pdf");

// Single-line form (no fixture file required)
Converter.ConvertHTML("<h1>Hello from Aspose.HTML</h1><p>HTML to PDF conversion validated.</p>", ".", new PdfSaveOptions(), outputPath);

bool exists = File.Exists(outputPath);
long size = exists ? new FileInfo(outputPath).Length : 0;
Console.WriteLine($"OUTPUT_FILE={outputPath}");
Console.WriteLine($"FILE_EXISTS={exists}");
Console.WriteLine($"FILE_SIZE_BYTES={size}");
Console.WriteLine(exists && size > 100 ? "VALIDATION=PASS" : "VALIDATION=FAIL");
