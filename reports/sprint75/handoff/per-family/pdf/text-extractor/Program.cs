using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

class Program
{
    static void Main()
    {
        // Create input PDF fixture
        string inputPath = Path.Combine(Path.GetTempPath(), "input.pdf");
        var document = new Document();
        var page = document.Pages.Add();
        page.Paragraphs.Add(new TextFragment("Sample text for extraction."));
        document.Save(inputPath);

        // Validate input file existence
        if (!File.Exists(inputPath))
            throw new FileNotFoundException("Input PDF was not created.", inputPath);

        // Configure LowCode TextExtractor options
        var options = new TextExtractorOptions();
        options.AddInput(new FileDataSource(inputPath));

        // Execute extraction using the primary Process method
        var result = new TextExtractor().Process(options);

        // Validate and display extracted text
        if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)
            Console.WriteLine("Extracted text: " + sr.Text);
        else
            Console.WriteLine("No text extracted.");
    }
}