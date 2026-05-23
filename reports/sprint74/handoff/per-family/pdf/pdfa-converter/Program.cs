using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.Text;
using Aspose.Pdf.LowCode;

class Program
{
    static void Main()
    {
        const string inputPath = "input.pdf";
        const string outputPath = "output.pdf";

        // Create input PDF programmatically
        var doc = new Document();
        var page = doc.Pages.Add();
        page.Paragraphs.Add(new TextFragment("Hello PDF"));
        doc.Save(inputPath);

        // Validate input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
            throw new InvalidOperationException("Input PDF was not created correctly.");

        // Configure LowCode options
        var options = new PdfAConvertOptions();
        options.AddInput(new FileDataSource(inputPath));
        options.AddOutput(new FileDataSource(outputPath));

        // Execute conversion using PdfAConverter
        var converter = new PdfAConverter();
        var result = converter.Process(options);

        // Verify that the operation produced results
        if (result == null || result.ResultCollection == null || result.ResultCollection.Count == 0)
            throw new InvalidOperationException("PdfAConverter did not produce any results.");

        // Validate output file exists and is non‑empty
        if (!File.Exists(outputPath) || new FileInfo(outputPath).Length == 0)
            throw new InvalidOperationException("Output PDF was not created correctly.");

        Console.WriteLine($"Success: output file size {new FileInfo(outputPath).Length} bytes.");
    }
}