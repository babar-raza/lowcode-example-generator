using System;
using System.IO;
using Aspose.Pdf.LowCode;

namespace HtmlConversionExample
{
    class Program
    {
        static void Main()
        {
            // Create HTML input file
            string inputPath = Path.Combine(Path.GetTempPath(), "input.html");
            File.WriteAllText(inputPath, "<html><body><h1>Hello, Aspose PDF LowCode!</h1></body></html>");

            if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
                throw new InvalidOperationException("Failed to create the HTML input file.");

            // Define output PDF path
            string outputPath = Path.Combine(Path.GetTempPath(), "output.pdf");

            // Initialize Html plugin and options
            var plugin = new Html();
            var options = new HtmlToPdfOptions();
            options.AddInput(new FileDataSource(inputPath));
            options.AddOutput(new FileDataSource(outputPath));

            // Process conversion
            var result = plugin.Process(options);

            // Verify processing result
            if (result?.ResultCollection == null || result.ResultCollection.Count == 0)
                throw new InvalidOperationException("LowCode processing did not produce any results.");

            // Validate output file
            if (!File.Exists(outputPath) || new FileInfo(outputPath).Length == 0)
                throw new InvalidOperationException("Output PDF was not created or is empty.");

            Console.WriteLine("Success: output.pdf created.");

            // Clean up
            plugin.Dispose();
        }
    }
}