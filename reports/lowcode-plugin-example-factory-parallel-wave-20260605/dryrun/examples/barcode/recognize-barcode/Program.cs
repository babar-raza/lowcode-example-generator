// barcode/recognize-barcode
// Canonical: https://products.aspose.net/barcode/1d-barcode-reader/
// Package: Aspose.BarCode 24.12.0
// Pattern: BarcodeGenerator(Code128) -> Save PNG -> BarCodeReader(PNG, Code128) -> ReadBarCodes
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

// Generate fixture barcode image
string fixturePath = "fixture_barcode.png";
using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "RECOGNITION-TEST-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Save(fixturePath, BarCodeImageFormat.Png);
}

// Recognize the barcode
var sb = new StringBuilder();
using (var reader = new BarCodeReader(fixturePath, DecodeType.Code128))
{
    foreach (var result in reader.ReadBarCodes())
    {
        string line = $"Type={result.CodeType}, Value={result.CodeText}";
        Console.WriteLine(line);
        sb.AppendLine(line);
    }
}
File.WriteAllText("output/result.txt", sb.ToString());
Console.WriteLine($"Recognition complete. Output/result.txt: {new FileInfo("output/result.txt").Length} bytes");
