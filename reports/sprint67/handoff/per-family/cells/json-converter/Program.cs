using System;
using System.IO;
using Aspose.Cells.LowCode;

namespace JsonConverterDemo
{
    internal class Program
    {
        private static void Main(string[] args)
        {
            // Locate input Excel file
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
            if (!File.Exists(inputPath))
                throw new FileNotFoundException("Input file not found.", inputPath);

            // Define output JSON file
            string outputPath = Path.Combine(AppContext.BaseDirectory, "output.json");

            // Perform conversion using the simplest overload
            JsonConverter.Process(inputPath, outputPath);

            // Validate output
            if (!File.Exists(outputPath))
                throw new InvalidOperationException("Output file was not created.");

            // Deterministic success output
            FileInfo info = new FileInfo(outputPath);
            Console.WriteLine($"Conversion succeeded. Output: {outputPath} ({info.Length} bytes)");
        }
    }
}