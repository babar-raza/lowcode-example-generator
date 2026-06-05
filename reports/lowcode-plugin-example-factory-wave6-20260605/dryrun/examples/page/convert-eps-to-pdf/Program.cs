// page/convert-eps-to-pdf
// Canonical: https://products.aspose.net/page/eps-to-pdf/
// Package: Aspose.Page 24.12.0
// Pattern: PsDocument(epsStream) -> SaveAsPdf(pdfStream, PdfSaveOptions)
using Aspose.Page.EPS;
using Aspose.Page.EPS.Device;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "output.pdf");

// Minimal valid EPS fixture
string[] epsLines = {
    "%!PS-Adobe-3.0 EPSF-3.0",
    "%%BoundingBox: 0 0 200 200",
    "%%Title: Aspose.Page EPS Demo",
    "%%Creator: lowcode-example-factory",
    "%%EndComments",
    "% Draw border rectangle",
    "0.5 setlinewidth",
    "10 10 moveto",
    "190 10 lineto",
    "190 190 lineto",
    "10 190 lineto",
    "closepath stroke",
    "% Title text",
    "/Helvetica findfont 14 scalefont setfont",
    "20 160 moveto",
    "(Aspose.Page EPS to PDF Demo) show",
    "20 130 moveto",
    "(Generated 2026-06-05) show",
    "%%EOF"
};
byte[] epsBytes = Encoding.ASCII.GetBytes(string.Join("\n", epsLines) + "\n");

using var epsStream = new MemoryStream(epsBytes);
using var pdfStream = File.Open(outputPath, FileMode.Create);
var doc = new PsDocument(epsStream);
var options = new PdfSaveOptions();
doc.SaveAsPdf(pdfStream, options);
Console.WriteLine($"EPS converted to PDF: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
