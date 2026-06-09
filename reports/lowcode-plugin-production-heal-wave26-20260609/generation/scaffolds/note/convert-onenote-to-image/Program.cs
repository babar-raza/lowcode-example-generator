using Aspose.Note;
using Aspose.Note.Saving;

Console.WriteLine("Aspose.Note - OneNote to Image Converter");
var doc = new Document();
var page = new Page(doc);
var outline = new Outline(doc);
var outlineElement = new OutlineElement(doc);
var text = new RichText(doc) { Text = "Hello World" };
outlineElement.AppendChildLast(text);
outline.AppendChildLast(outlineElement);
page.AppendChildLast(outline);
doc.AppendChildLast(page);
doc.Save("output.png", new ImageSaveOptions(SaveFormat.Png));
Console.WriteLine("OneNote converted to image successfully: output.png");
