using System;
using System.IO;
using Aspose.Cells.LowCode;

class Program
{
    static void Main()
    {
        // Locate input file from the application base directory
        string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
        if (!File.Exists(inputPath))
            throw new FileNotFoundException("Input file not found", inputPath);

        // Define output file path (CSV is a supported format)
        string outputPath = Path.Combine(AppContext.BaseDirectory, "output.csv");

        // Convert the spreadsheet using the simplest overload
        SpreadsheetConverter.Process(inputPath, outputPath);

        // Verify that the output file was created and report success
        if (File.Exists(outputPath))
            Console.WriteLine($"Done. Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
        else
            throw new InvalidOperationException("Output file was not created");
    }
}