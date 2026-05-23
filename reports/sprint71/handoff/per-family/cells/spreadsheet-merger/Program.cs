using System;
using System.IO;
using Aspose.Cells;
using Aspose.Cells.LowCode;

class Program
{
    static void Main()
    {
        // Prepare a simple input workbook if it does not already exist
        string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
        if (!File.Exists(inputPath))
        {
            var workbook = new Workbook();
            workbook.Worksheets[0].Name = "Sheet1";
            workbook.Save(inputPath);
        }

        // Validate input file exists
        if (!File.Exists(inputPath))
            throw new FileNotFoundException("Input file not found.", inputPath);

        // Define output file path
        string outputPath = Path.Combine(AppContext.BaseDirectory, "output.xlsx");

        // Use the overload of SpreadsheetMerger.Process that accepts an array of template files
        SpreadsheetMerger.Process(new[] { inputPath }, outputPath);

        // Validate output file was created
        if (!File.Exists(outputPath))
            throw new InvalidOperationException("Output file was not created by SpreadsheetMerger.Process.");

        // Deterministic success output
        Console.WriteLine($"SpreadsheetMerger.Process succeeded: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
    }
}