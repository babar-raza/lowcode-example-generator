// Source: https://raw.githubusercontent.com/aspose-html/Aspose.HTML-for-.NET/master/Examples/CSharp/Converting-Between-Formats/HTML-Converter/HTMLtoPDFExample.cs
// Fetched: 2026-06-04 | Sprint: lowcode-plugin-registry-expansion-20260604
using Aspose.Html;
using Aspose.Html.Converters;
using Aspose.Html.Drawing;
using Aspose.Html.Rendering.Pdf.Encryption;
using Aspose.Html.Saving;
using System.IO;

// CORE PATTERN (simplest form):
// Converter.ConvertHTML("<h1>text</h1>", ".", new PdfSaveOptions(), outputPath);
//
// OR with HTMLDocument:
// using HTMLDocument document = new HTMLDocument(documentPath);
// PdfSaveOptions options = new PdfSaveOptions();
// Converter.ConvertHTML(document, options, savePath);

// See full example below (from official repo):
public class HTMLtoPDFExample {
    public void ConvertHtmlToPdfWithSingleLine() {
        Converter.ConvertHTML(@"<h1>Convert HTML to PDF!</h1>", ".", new PdfSaveOptions(), "output.pdf");
    }
    public void ConvertHtmlToPdfFromFile() {
        using HTMLDocument document = new HTMLDocument("input.html");
        PdfSaveOptions options = new PdfSaveOptions();
        Converter.ConvertHTML(document, options, "output.pdf");
    }
}
