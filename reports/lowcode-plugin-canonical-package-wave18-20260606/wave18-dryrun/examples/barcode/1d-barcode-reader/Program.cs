// barcode/1d-barcode-reader — W18 canonical package proof
// Canonical URL: https://products.aspose.net/barcode/1d-barcode-reader/
// NuGet: Aspose.BarCode
// Pattern: BarcodeGenerator(Code128) -> Save PNG -> BarCodeReader -> ReadBarCodes
using Aspose.BarCode.Generation;
using Aspose.BarCode.BarCodeRecognition;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

// Step 1: Generate a Code128 fixture barcode image programmatically
string fixturePath = "output/fixture_barcode.png";
using (var gen = new BarcodeGenerator(EncodeTypes.Code128, "WAVE18-1D-READER-2026"))
{
    gen.Parameters.Barcode.XDimension.Pixels = 3;
    gen.Save(fixturePath, BarCodeImageFormat.Png);
}
Console.WriteLine($"Fixture barcode generated: {fixturePath}");

// Step 2: Read (recognize) the 1D barcode from the fixture image
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

// Step 3: Save recognition results
string resultPath = "output/result.txt";
File.WriteAllText(resultPath, sb.ToString());
Console.WriteLine($"Recognition complete. Result saved to {resultPath} ({new FileInfo(resultPath).Length} bytes)");
