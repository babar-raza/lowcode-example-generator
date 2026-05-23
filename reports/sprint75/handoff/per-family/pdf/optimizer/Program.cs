using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;

class Program
{
    static void Main()
    {
        const string inputPath = "input.pdf";
        const string outputPath = "output.pdf";

        // Create a simple PDF document programmatically
        var doc = new Document();
        doc.Pages.Add();
        doc.Save(inputPath);

        // Validate input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
            throw new FileNotFoundException("Input PDF was not created.", inputPath);

        // Prepare optimizer options with input and output data sources
        var options = new OptimizeOptions();
        options.AddInput(new FileDataSource(inputPath));
        options.AddOutput(new FileDataSource(outputPath));

        // Run the Optimizer plugin
        var result = new Optimizer().Process(options);

        // Verify processing succeeded and output file was created
        if (result?.ResultCollection?.Count > 0 && File.Exists(outputPath))
        {
            Console.WriteLine($"Optimization succeeded: {outputPath}");
        }
        else
        {
            throw new InvalidOperationException("Optimization failed or output not created.");
        }
    }
}