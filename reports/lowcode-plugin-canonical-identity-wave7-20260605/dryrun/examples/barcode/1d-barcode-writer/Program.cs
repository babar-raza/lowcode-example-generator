// barcode/1d-barcode-writer
// Canonical: https://products.aspose.net/barcode/1d-barcode-writer/
// Package: Aspose.BarCode 24.12.0
// Generates a 1D barcode (Code128) and saves as PNG.
using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "barcode-1d.png");

using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "ASPOSE-1D-BARCODE-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Parameters.Barcode.BarHeight.Pixels = 100;
    gen.Save(outputPath, BarCodeImageFormat.Png);
}
Console.WriteLine($"1D barcode written: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
