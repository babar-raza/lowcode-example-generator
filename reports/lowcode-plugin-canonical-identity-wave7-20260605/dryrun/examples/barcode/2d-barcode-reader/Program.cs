// barcode/2d-barcode-reader
// Canonical: https://products.aspose.net/barcode/2d-barcode-reader/
// Package: Aspose.BarCode 24.12.0
// Generates a 2D QR fixture then reads it back.
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

string fixturePath = "fixture_2d.png";
using (var gen = new BarcodeGenerator(EncodeTypes.QR, "2D-READER-TEST-ASPOSE-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 6;
    gen.Parameters.Barcode.QR.QrErrorLevel = QRErrorLevel.LevelH;
    gen.Save(fixturePath, BarCodeImageFormat.Png);
}

var sb = new StringBuilder();
using (var reader = new BarCodeReader(fixturePath, DecodeType.QR))
{
    foreach (var result in reader.ReadBarCodes())
    {
        string line = $"Type={result.CodeType}, Value={result.CodeText}";
        Console.WriteLine(line);
        sb.AppendLine(line);
    }
}
string outPath = Path.Combine("output", "2d-recognition.txt");
File.WriteAllText(outPath, sb.ToString());
Console.WriteLine($"2D barcode read: {outPath} ({new FileInfo(outPath).Length} bytes)");
