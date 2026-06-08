using System;
using System.IO;
using Aspose.BarCode.Generation;

// Example: Generate a barcode from text using Aspose.BarCode for .NET
// Aspose.BarCode — BarcodeGenerator.Save

class Program
{
    static void Main(string[] args)
    {
        string outputPath = args.Length > 0 ? args[0] : "barcode-output.png";

        // Create a BarcodeGenerator for Code128 encoding
        var generator = new BarcodeGenerator(EncodeTypes.Code128, "Hello, Aspose.BarCode!");

        // Configure barcode appearance
        generator.Parameters.Barcode.XDimension.Pixels = 2;
        generator.Parameters.Barcode.BarHeight.Pixels = 40;

        // Save the barcode image to the output path
        generator.Save(outputPath, BarCodeImageFormat.Png);

        Console.WriteLine($"Barcode saved to: {outputPath}");
        Console.WriteLine($"Size: {new FileInfo(outputPath).Length} bytes");
    }
}
