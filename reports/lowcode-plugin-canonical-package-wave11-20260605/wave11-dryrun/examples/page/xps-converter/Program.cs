// page/xps-converter
// Canonical: https://products.aspose.net/page/xps-converter/
// Package: Aspose.Page 24.12.0
// Pattern: new XpsDocument() -> AddPath -> Save XPS -> Load XPS -> SaveAsPdf(path, PdfSaveOptions)
using Aspose.Page.XPS;
using Aspose.Page.XPS.XpsModel;
using Aspose.Page.XPS.Presentation.Pdf;
using System;
using System.IO;

Directory.CreateDirectory("output");
string xpsPath = "fixture.xps";
string outputPath = Path.Combine("output", "output.pdf");

// Step 1: Create a minimal XPS document programmatically
using (var xpsDoc = new XpsDocument())
{
    XpsPath path1 = xpsDoc.AddPath(xpsDoc.CreatePathGeometry("M 30,20 L 300,20 L 300,100 L 30,100 Z"));
    path1.Fill = xpsDoc.CreateSolidColorBrush(xpsDoc.CreateColor(0.2f, 0.5f, 0.8f));

    XpsPath path2 = xpsDoc.AddPath(xpsDoc.CreatePathGeometry("M 50,130 L 280,130 L 280,180 L 50,180 Z"));
    path2.Fill = xpsDoc.CreateSolidColorBrush(xpsDoc.CreateColor(0.8f, 0.3f, 0.2f));

    xpsDoc.Save(xpsPath);
    Console.WriteLine($"XPS fixture created: {xpsPath}");
}

// Step 2: Load XPS and convert to PDF using SaveAsPdf
using (var xps = new XpsDocument(xpsPath, new XpsLoadOptions()))
{
    var pdfOptions = new PdfSaveOptions();
    xps.SaveAsPdf(outputPath, pdfOptions);
}
Console.WriteLine($"PDF saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
