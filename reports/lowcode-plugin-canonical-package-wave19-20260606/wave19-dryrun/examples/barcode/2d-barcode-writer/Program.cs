using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = "output/barcode-2d.png";

using (var gen = new BarcodeGenerator(EncodeTypes.QR, "WAVE19-2D-WRITER-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 4;
    gen.Save(outputPath, BarCodeImageFormat.Png);
}

long size = new FileInfo(outputPath).Length;
string result = $"2D barcode generated: {outputPath} ({size} bytes)";
Console.WriteLine(result);
File.WriteAllText("output/result.txt", result + Environment.NewLine);
