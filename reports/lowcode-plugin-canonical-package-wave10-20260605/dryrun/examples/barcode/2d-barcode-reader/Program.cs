// barcode/scan-barcode
// Canonical: https://products.aspose.net/barcode/barcode-scanner/
// Package: Aspose.BarCode 24.12.0
// Pattern: BarcodeGenerator -> Save -> BarCodeReader -> ReadBarCodes
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;

Directory.CreateDirectory("output");

// Step 1: Generate a Code128 barcode to use as input
string barcodePath = Path.Combine("output", "input-barcode.png");
var gen = new BarcodeGenerator(EncodeTypes.Code128, "SCAN-DEMO-20260605");
gen.Parameters.Barcode.XDimension.Pixels = 3;
gen.Save(barcodePath, BarCodeImageFormat.Png);

// Step 2: Scan (recognize) it
var reader = new BarCodeReader(barcodePath, DecodeType.AllSupportedTypes);
var results = reader.ReadBarCodes();

string resultText = results.Length > 0
    ? $"Type: {results[0].CodeTypeName}, Value: {results[0].CodeText}"
    : "No barcode recognized";

string resultPath = Path.Combine("output", "scan-result.txt");
File.WriteAllText(resultPath, resultText);
Console.WriteLine($"Scan result: {resultText}");
Console.WriteLine($"Result saved: {resultPath}");
