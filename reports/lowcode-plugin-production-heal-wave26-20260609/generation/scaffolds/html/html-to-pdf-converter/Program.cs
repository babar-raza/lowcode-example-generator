using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Saving;

Console.WriteLine("Aspose.HTML - HTML to PDF Converter");
using var doc = new HTMLDocument("<html><body><h1>Hello World</h1></body></html>", ".");
Converter.ConvertHTML(doc, new PdfSaveOptions(), "output.pdf");
Console.WriteLine("HTML converted to PDF successfully: output.pdf");
