// html/merge-html
// Canonical: https://products.aspose.net/html/merge-html/
// Package: Aspose.HTML 24.12.0
// Pattern: Load multiple HTMLDocument objects, merge body content, Converter.ConvertHTML -> PDF
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "merged.pdf");

// First HTML document
string html1 = @"<!DOCTYPE html>
<html><body>
  <h1>Document 1</h1>
  <p>Content from the first HTML document.</p>
</body></html>";

// Second HTML document
string html2 = @"<!DOCTYPE html>
<html><body>
  <h1>Document 2</h1>
  <p>Content from the second HTML document.</p>
</body></html>";

// Merge: combine both HTML bodies into a single document
string mergedHtml = $@"<!DOCTYPE html>
<html>
<head><title>Merged Document</title></head>
<body>
  <div class='doc1'>
    <h1>Document 1</h1>
    <p>Content from the first HTML document.</p>
  </div>
  <hr/>
  <div class='doc2'>
    <h1>Document 2</h1>
    <p>Content from the second HTML document.</p>
  </div>
</body>
</html>";

// Convert merged HTML to PDF
var options = new PdfSaveOptions();
Converter.ConvertHTML(mergedHtml, ".", options, outputPath);

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"Merged HTML documents to PDF: {outputPath} ({size} bytes)");
