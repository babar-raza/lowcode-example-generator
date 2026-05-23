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

        // Define output PDF path
        string outputPath = Path.Combine(AppContext.BaseDirectory, "output.pdf");

        // Convert the Excel file to PDF using the simplest overload
        PdfConverter.Process(inputPath, outputPath);

        // Verify that the output file was created
        if (File.Exists(outputPath))
            Console.WriteLine($"Done. Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
        else
            throw new InvalidOperationException("Output file was not created");
    }
}