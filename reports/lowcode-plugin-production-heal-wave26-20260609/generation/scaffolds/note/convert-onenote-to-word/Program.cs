using Aspose.Note;
using Aspose.Note.Saving;

Console.WriteLine("Aspose.Note - OneNote to Word Converter");
var doc = new Document();
var page = new Page(doc);
var outline = new Outline(doc);
var outlineElement = new OutlineElement(doc);
var text = new RichText(doc) { Text = "Hello World" };
outlineElement.AppendChildLast(text);
outline.AppendChildLast(outlineElement);
page.AppendChildLast(outline);
doc.AppendChildLast(page);
doc.Save("output.docx");
Console.WriteLine("OneNote converted to Word successfully: output.docx");
