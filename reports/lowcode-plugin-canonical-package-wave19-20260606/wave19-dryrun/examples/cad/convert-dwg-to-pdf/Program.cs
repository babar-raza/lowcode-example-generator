using Aspose.CAD;
using Aspose.CAD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");

string dwgPath = "fixtures/Drawing11.dwg";
string pdfPath = "output/output.pdf";

using (var image = Image.Load(dwgPath))
{
    var rasterOpts = new CadRasterizationOptions
    {
        PageWidth = 1200,
        PageHeight = 900
    };
    var pdfOpts = new PdfOptions
    {
        VectorRasterizationOptions = rasterOpts
    };
    image.Save(pdfPath, pdfOpts);
}

long pdfSize = new FileInfo(pdfPath).Length;
string result = $"DWG: {dwgPath}, PDF: {pdfPath}, Size: {pdfSize} bytes";
Console.WriteLine(result);
File.WriteAllText("output/conversion-result.txt", result + Environment.NewLine);
