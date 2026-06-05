// barcode/1d-barcode-reader
// Canonical: https://products.aspose.net/barcode/1d-barcode-reader/
// Package: Aspose.BarCode 24.12.0
// Generates a 1D Code128 fixture then reads it back.
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

string fixturePath = "fixture_barcode.png";
using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "1D-READER-TEST-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Save(fixturePath, BarCodeImageFormat.Png);
}

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
string outPath = Path.Combine("output", "1d-recognition.txt");
File.WriteAllText(outPath, sb.ToString());
Console.WriteLine($"1D barcode read: {outPath} ({new FileInfo(outPath).Length} bytes)");
