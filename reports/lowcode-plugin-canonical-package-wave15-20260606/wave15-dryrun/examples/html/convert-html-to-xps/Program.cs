// html/convert-html-to-xps
// Canonical: https://products.aspose.net/html/convert-html-to-xps/
// Package: Aspose.HTML 24.12.0
// Pattern: Converter.ConvertHTML(htmlContent, baseUri, XpsSaveOptions, outputPath)
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.xps");

string htmlContent =
    "<!DOCTYPE html><html><head><title>HTML to XPS Demo</title></head><body>" +
    "<h1>HTML to XPS Conversion</h1>" +
    "<p>This document was converted from HTML to XPS format using Aspose.HTML for .NET.</p>" +
    "<h2>XPS Format Benefits</h2>" +
    "<ul><li>Fixed-layout document format</li>" +
    "<li>Print-ready output</li>" +
    "<li>Platform-independent rendering</li></ul>" +
    "<p>Generated on 2026-06-06 by the lowcode example factory.</p>" +
    "</body></html>";

var options = new XpsSaveOptions();
Converter.ConvertHTML(htmlContent, ".", options, outputPath);
Console.WriteLine($"HTML converted to XPS: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
