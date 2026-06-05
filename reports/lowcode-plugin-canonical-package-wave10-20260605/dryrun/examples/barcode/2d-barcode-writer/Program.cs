// barcode/generate-qr-code
// Canonical: https://products.aspose.net/barcode/qr-code-generator/
// Package: Aspose.BarCode 24.12.0
// Pattern: BarcodeGenerator(EncodeTypes.QR, text) -> Save PNG
using Aspose.BarCode.Generation;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "qr-code.png");

var generator = new BarcodeGenerator(EncodeTypes.QR, "https://www.aspose.com");
generator.Parameters.Barcode.XDimension.Pixels = 6;
generator.Parameters.Barcode.QR.QrErrorLevel = QRErrorLevel.LevelH;
generator.Save(outputPath, BarCodeImageFormat.Png);

Console.WriteLine($"QR code saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
