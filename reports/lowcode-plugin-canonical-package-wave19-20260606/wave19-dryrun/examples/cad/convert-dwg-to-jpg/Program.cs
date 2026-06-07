using Aspose.CAD;
using Aspose.CAD.ImageOptions;
using System;
using System.IO;

Directory.CreateDirectory("output");

string dwgPath = "fixtures/Drawing11.dwg";
string jpgPath = "output/output.jpg";

using (var image = Image.Load(dwgPath))
{
    var rasterOpts = new CadRasterizationOptions
    {
        PageWidth = 1200,
        PageHeight = 900
    };
    var jpegOpts = new JpegOptions
    {
        VectorRasterizationOptions = rasterOpts,
        Quality = 90
    };
    image.Save(jpgPath, jpegOpts);
}

long jpgSize = new FileInfo(jpgPath).Length;
string result = $"DWG: {dwgPath}, JPG: {jpgPath}, Size: {jpgSize} bytes";
Console.WriteLine(result);
File.WriteAllText("output/conversion-result.txt", result + Environment.NewLine);
