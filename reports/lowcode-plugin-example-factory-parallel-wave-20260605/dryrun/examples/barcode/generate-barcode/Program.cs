// barcode/generate-barcode
// Canonical: https://products.aspose.net/barcode/1d-barcode-writer/
// Package: Aspose.BarCode 24.12.0
// Pattern: new BarcodeGenerator(EncodeTypes.Code128, data) -> Save(path, PNG)
using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "barcode.png");

using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "ASPOSE-BARCODE-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Parameters.Barcode.BarHeight.Pixels = 100;
    gen.Save(outputPath, BarCodeImageFormat.Png);
}
Console.WriteLine($"1D barcode generated: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
