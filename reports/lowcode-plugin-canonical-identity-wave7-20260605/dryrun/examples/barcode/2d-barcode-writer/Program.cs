// barcode/2d-barcode-writer
// Canonical: https://products.aspose.net/barcode/2d-barcode-writer/
// Package: Aspose.BarCode 24.12.0
// Generates a 2D QR barcode and saves as PNG.
using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "barcode-2d.png");

using (var gen = new BarcodeGenerator(EncodeTypes.QR, "https://www.aspose.com/barcode-2d"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 6;
    gen.Parameters.Barcode.QR.QrErrorLevel = QRErrorLevel.LevelH;
    gen.Save(outputPath, BarCodeImageFormat.Png);
}
Console.WriteLine($"2D QR barcode written: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
