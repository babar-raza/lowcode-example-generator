// cad/convert-cad-to-pdf — W18 canonical package proof
// Canonical URL: https://products.aspose.net/cad/convert-cad-to-pdf/
// NuGet: Aspose.CAD
// Pattern: Image.Load(cadFile) -> CadRasterizationOptions -> PdfOptions -> image.Save(pdf)
using System;
using System.IO;
using Aspose.CAD;
using Aspose.CAD.ImageOptions;

Directory.CreateDirectory("output");
string cadPath = Path.Combine("fixtures", "minimal.dxf");
using (var image = Image.Load(cadPath))
{
    var raster = new CadRasterizationOptions { PageWidth = 1200, PageHeight = 900 };
    var pdfOpts = new PdfOptions { VectorRasterizationOptions = raster };
    string pdfPath = "output/cad-output.pdf";
    image.Save(pdfPath, pdfOpts);
    long size = new FileInfo(pdfPath).Length;
    Console.WriteLine($"CAD-to-PDF: {pdfPath} ({size} bytes)");
    File.WriteAllText("output/result.txt", $"Status: PASS\nPDF size: {size} bytes");
}
