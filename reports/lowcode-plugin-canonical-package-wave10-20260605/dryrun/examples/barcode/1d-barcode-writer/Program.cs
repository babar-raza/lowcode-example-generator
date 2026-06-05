// Aspose.BarCode — Generate 1D Barcode (Code128) and save as PNG
// Canonical product page: https://products.aspose.net/barcode/1d-barcode-writer/
// Source authority: https://github.com/aspose-barcode/Aspose.BarCode-for-.NET
// Source file: Examples/CSharp/BarcodeGeneration/BarcodeOutput/StoreBarcodeOutputAsBitmap.cs
//
// Pattern: STATIC_CONVERTER_CLASS
//   BarcodeGenerator(encodeType, codeText) → GenerateBarCodeImage() → save PNG

using Aspose.BarCode.Generation;

string outputDir = Path.Combine(Directory.GetCurrentDirectory(), "output");
Directory.CreateDirectory(outputDir);

string outputPath = Path.Combine(outputDir, "barcode_code128.png");

// Create a Code128 barcode generator with value "12345678"
BarcodeGenerator gen = new BarcodeGenerator(EncodeTypes.Code128, "12345678");

// Set dimensions for readable output
gen.Parameters.Barcode.XDimension.Pixels = 2;
gen.Parameters.Barcode.BarHeight.Pixels = 48;

// Save the barcode image as PNG
gen.Save(outputPath, BarCodeImageFormat.Png);

Console.WriteLine($"Barcode saved to: {outputPath}");
Console.WriteLine($"File exists: {File.Exists(outputPath)}");
Console.WriteLine($"File size: {new FileInfo(outputPath).Length} bytes");
Console.WriteLine("SNIPPET_RUN: PASS");
