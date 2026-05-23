using System;
using System.IO;
using Aspose.Cells.LowCode;

class Program
{
    static void Main()
    {
        // Locate input file from project output directory
        string inputPath = Path.Combine(AppContext.BaseDirectory, "input.csv");
        if (!File.Exists(inputPath))
            throw new FileNotFoundException("Input file not found", inputPath);

        // Define output path
        string outputPath = Path.Combine(AppContext.BaseDirectory, "output.txt");

        // Call the plugin API (string-path overload)
        TextConverter.Process(inputPath, outputPath);

        // Validate output
        if (File.Exists(outputPath))
        {
            var info = new FileInfo(outputPath);
            Console.WriteLine($"Done. Output: {outputPath} ({info.Length} bytes)");
        }
        else
        {
            throw new InvalidOperationException("Output file was not created");
        }
    }
}