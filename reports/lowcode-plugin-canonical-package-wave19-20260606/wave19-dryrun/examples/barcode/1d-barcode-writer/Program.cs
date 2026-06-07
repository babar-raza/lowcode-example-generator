using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = "output/barcode-1d.png";

using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "WAVE19-1D-WRITER-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Parameters.Barcode.BarHeight.Pixels = 80;
    gen.Save(outputPath, BarCodeImageFormat.Png);
}

long size = new FileInfo(outputPath).Length;
string result = $"1D barcode generated: {outputPath} ({size} bytes)";
Console.WriteLine(result);
File.WriteAllText("output/result.txt", result + Environment.NewLine);
