using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;

Console.WriteLine("Aspose.HTML - HTML to DOCX Converter");
using var doc = new HTMLDocument("<html><body><h1>Hello World</h1></body></html>", ".");
Converter.ConvertHTML(doc, new DocSaveOptions(), "output.docx");
Console.WriteLine("HTML converted to DOCX successfully: output.docx");
