// html/convert-html-to-markdown
// Canonical: https://products.aspose.net/html/convert-html-to-markdown/
// Package: Aspose.HTML 24.12.0
// Pattern: Converter.ConvertHTML(htmlContent, baseUri, MarkdownSaveOptions, outputPath)
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.md");

string htmlContent = @"<!DOCTYPE html>
<html>
<head><title>Sample Document</title></head>
<body>
  <h1>Hello from Aspose.HTML</h1>
  <h2>Introduction</h2>
  <p>This document demonstrates HTML to Markdown conversion using Aspose.HTML for .NET.</p>
  <h2>Features</h2>
  <ul>
    <li>Convert HTML to Markdown format</li>
    <li>Preserve headings and lists</li>
    <li>Handle paragraphs and inline text</li>
  </ul>
  <p>Use <strong>Aspose.HTML</strong> to process HTML documents programmatically.</p>
</body>
</html>";

var options = new MarkdownSaveOptions();
Converter.ConvertHTML(htmlContent, ".", options, outputPath);

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"HTML converted to Markdown: {outputPath} ({size} bytes)");
