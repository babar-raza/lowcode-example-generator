// barcode/2d-barcode-reader — W18 canonical package proof
// Canonical URL: https://products.aspose.net/barcode/2d-barcode-reader/
// NuGet: Aspose.BarCode
// Pattern: BarcodeGenerator(QR) -> Save PNG -> BarCodeReader -> ReadBarCodes
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;

Directory.CreateDirectory("output");

// Step 1: Generate a QR Code fixture image programmatically
string fixturePath = "output/fixture_qr.png";
using (var gen = new BarcodeGenerator(EncodeTypes.QR, "WAVE18-2D-READER-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 4;
    gen.Save(fixturePath, BarCodeImageFormat.Png);
}
Console.WriteLine($"Fixture QR code generated: {fixturePath}");

// Step 2: Read (recognize) the 2D barcode from the fixture image
using var reader = new BarCodeReader(fixturePath, DecodeType.QR);
var results = reader.ReadBarCodes();

string resultText = results.Length > 0
    ? $"Type: {results[0].CodeTypeName}, Value: {results[0].CodeText}"
    : "No barcode recognized";

// Step 3: Save recognition results
string resultPath = "output/result.txt";
File.WriteAllText(resultPath, resultText);
Console.WriteLine($"Recognition result: {resultText}");
Console.WriteLine($"Result saved: {resultPath}");
