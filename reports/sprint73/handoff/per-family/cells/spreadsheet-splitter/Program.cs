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
            throw new FileNotFoundException("Input fixture not found", inputPath);

        // Define output path
        string outputPath = Path.Combine(AppContext.BaseDirectory, "output.xlsx");
        if (File.Exists(outputPath))
            File.Delete(outputPath);

        // Call the plugin API (simplest string-path overload)
        SpreadsheetSplitter.Process(inputPath, outputPath);

        // Validate output
        if (File.Exists(outputPath))
        {
            long size = new FileInfo(outputPath).Length;
            Console.WriteLine($"Done. Output: {outputPath} ({size} bytes)");
        }
        else
        {
            throw new InvalidOperationException("Output file was not created");
        }
    }
}