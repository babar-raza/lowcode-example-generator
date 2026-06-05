// note/convert-one-to-pdf
// Canonical: https://products.aspose.net/note/convert-onenote-to-pdf/
// Package: Aspose.Note 24.12.0
// Pattern: new Document() -> new Page() -> AppendChildLast -> Save PDF
// Note: RichText requires ParagraphStyle set for PDF rendering
using Aspose.Note;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.pdf");

var doc = new Document();
var page = new Page();
var outline = new Outline();
var element = new OutlineElement();
var richText = new RichText()
{
    Text = "This note was generated programmatically by the Aspose.Note fixture factory.\n" +
           "It demonstrates converting a OneNote document to PDF format.\n" +
           "The document contains structured content with outline elements.",
    ParagraphStyle = ParagraphStyle.Default
};

element.AppendChildLast(richText);
outline.AppendChildLast(element);
page.AppendChildLast(outline);
doc.AppendChildLast(page);

doc.Save(outputPath, SaveFormat.Pdf);
long size = new FileInfo(outputPath).Length;
Console.WriteLine($"Note converted to PDF: {outputPath} ({size} bytes)");
