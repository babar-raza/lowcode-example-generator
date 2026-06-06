// cad/convert-dxf-to-pdf — W18 canonical package proof
// Canonical URL: https://products.aspose.net/cad/convert-dxf-to-pdf/
// NuGet: Aspose.CAD
// Pattern: Image.Load(dxfPath) -> CadRasterizationOptions -> PdfOptions -> image.Save(pdfPath)
using System;
using System.IO;
using Aspose.CAD;
using Aspose.CAD.FileFormats.Cad;
using Aspose.CAD.ImageOptions;

Directory.CreateDirectory("output");

string dxfPath = Path.Combine("fixtures", "minimal.dxf");
if (!File.Exists(dxfPath))
    throw new FileNotFoundException($"DXF fixture not found: {dxfPath}");

Console.WriteLine($"Loading DXF: {dxfPath}");

using (var image = Image.Load(dxfPath))
{
    Console.WriteLine($"DXF loaded. Type: {image.GetType().Name}");

    var rasterOpts = new CadRasterizationOptions
    {
        PageWidth = 800,
        PageHeight = 600
    };

    var pdfOpts = new PdfOptions
    {
        VectorRasterizationOptions = rasterOpts
    };

    string pdfPath = "output/output.pdf";
    image.Save(pdfPath, pdfOpts);
    long size = new FileInfo(pdfPath).Length;
    Console.WriteLine($"PDF saved: {pdfPath} ({size} bytes)");

    File.WriteAllText("output/conversion-result.txt", $"DXF loaded successfully\nPDF output: {size} bytes\nStatus: PASS");
}
