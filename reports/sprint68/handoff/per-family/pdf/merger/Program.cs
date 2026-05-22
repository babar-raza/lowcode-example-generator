using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

class Program
{
    static void Main()
    {
        // Prepare temporary file paths
        string tempDir = Path.GetTempPath();
        string inputPath = Path.Combine(tempDir, "input.pdf");
        string outputPath = Path.Combine(tempDir, "output.pdf");

        // Create a simple PDF document programmatically
        var doc = new Document();
        var page = doc.Pages.Add();
        page.Paragraphs.Add(new TextFragment("Hello, Aspose PDF LowCode Merger!"));
        doc.Save(inputPath);

        // Validate input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
        {
            Console.WriteLine("Input PDF was not created correctly.");
            return;
        }

        // Configure merge options with AddInput and AddOutput
        var options = new MergeOptions();
        options.AddInput(new FileDataSource(inputPath));
        options.AddOutput(new FileDataSource(outputPath));

        // Execute the merge operation
        var result = new Merger().Process(options);

        // Validate that the merger produced at least one result and output file exists
        if (result?.ResultCollection?.Count > 0 && File.Exists(outputPath) && new FileInfo(outputPath).Length > 0)
        {
            Console.WriteLine($"Merge succeeded: {outputPath}");
        }
        else
        {
            Console.WriteLine("Merge failed or produced no output.");
        }
    }
}
