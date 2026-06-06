// cad/convert-cad-to-image — W18 canonical package proof
// Canonical URL: https://products.aspose.net/cad/convert-cad-to-image/
// NuGet: Aspose.CAD
// Pattern: Image.Load(cadFile) -> CadRasterizationOptions -> PngOptions -> image.Save(png)
using System;
using System.IO;
using Aspose.CAD;
using Aspose.CAD.ImageOptions;

Directory.CreateDirectory("output");
string cadPath = Path.Combine("fixtures", "minimal.dxf");
using (var image = Image.Load(cadPath))
{
    var raster = new CadRasterizationOptions { PageWidth = 800, PageHeight = 600 };
    var pngOpts = new PngOptions { VectorRasterizationOptions = raster };
    string pngPath = "output/cad-output.png";
    image.Save(pngPath, pngOpts);
    long size = new FileInfo(pngPath).Length;
    Console.WriteLine($"CAD-to-Image (PNG): {pngPath} ({size} bytes)");
    File.WriteAllText("output/result.txt", $"Status: PASS\nPNG size: {size} bytes");
}
