using Aspose.Note;
using Aspose.Note.Saving;
using System;
using System.IO;

// Create a OneNote document with content
var doc = new Document();
var page = new Page();
var outline = new Outline();
var outlineElement = new OutlineElement();
var text = new RichText() { Text = "Hello from Aspose.Note plugin example" };

outlineElement.AppendChildLast(text);
outline.AppendChildLast(outlineElement);
page.AppendChildLast(outline);
doc.AppendChildLast(page);

// Save as PDF
string outputPath = "output.pdf";
doc.Save(outputPath, SaveFormat.Pdf);

var info = new FileInfo(outputPath);
Console.WriteLine($"PDF created: {info.Length} bytes");
File.WriteAllText("expected-output.json", "{\"status\": \"success\", \"format\": \"pdf\"}");
