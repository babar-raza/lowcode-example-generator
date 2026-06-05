// html/convert-html-to-word
// Canonical: https://products.aspose.net/html/html-to-docx-converter/
// Package: Aspose.HTML 24.12.0
// Pattern: Converter.ConvertHTML(htmlContent, baseUri, DocSaveOptions, outputPath)
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.docx");

string htmlContent =
    "<!DOCTYPE html><html><head><title>HTML to Word Demo</title></head><body>" +
    "<h1>HTML to Word Conversion</h1>" +
    "<p>This document was converted from HTML to Word format using Aspose.HTML for .NET.</p>" +
    "<h2>Features</h2>" +
    "<ul><li>Preserve HTML structure</li>" +
    "<li>Convert headings and paragraphs</li>" +
    "<li>Support lists and tables</li></ul>" +
    "<p>Generated on 2026-06-05 by the lowcode example factory.</p>" +
    "</body></html>";

var options = new DocSaveOptions();
Converter.ConvertHTML(htmlContent, ".", options, outputPath);
Console.WriteLine($"HTML converted to Word: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
