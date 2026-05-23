using System;
using System.IO;
using Aspose.Cells.LowCode;

class Program
{
    static void Main()
    {
        // Locate input file from project output directory
        string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
        if (!File.Exists(inputPath))
            throw new FileNotFoundException("Input file not found", inputPath);

        // Define output path
        string outputPath = Path.Combine(AppContext.BaseDirectory, "output.png");

        // Convert the workbook to an image
        ImageConverter.Process(inputPath, outputPath);

        // Validate output
        if (File.Exists(outputPath))
            Console.WriteLine($"Done. Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
        else
            throw new InvalidOperationException("Output file was not created");
    }
}