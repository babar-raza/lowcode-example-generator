using System;
using System.IO;
using Aspose.Cells.LowCode;

class Program
{
    static void Main()
    {
        // Locate input file from the project output directory
        string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
        if (!File.Exists(inputPath))
            throw new FileNotFoundException("Input fixture not found", inputPath);

        // Define output path
        string outputPath = Path.Combine(AppContext.BaseDirectory, "output.xlsx");

        // Call the simplest overload of SpreadsheetLocker.Process
        SpreadsheetLocker.Process(inputPath, outputPath, "", "");

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