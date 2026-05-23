using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

namespace SplitterExample
{
    internal class Program
    {
        private static void Main()
        {
            const string inputPath = "input.pdf";
            const string outputPath = "output.pdf";

            // Create a simple PDF document programmatically
            var document = new Document();
            var page = document.Pages.Add();
            page.Paragraphs.Add(new TextFragment("Sample PDF for Splitter plugin."));
            document.Save(inputPath);

            // Validate input file exists
            if (!File.Exists(inputPath))
                throw new FileNotFoundException("Input PDF was not created correctly.", inputPath);

            // Prepare split options with input and output data sources
            var options = new SplitOptions();
            options.AddInput(new FileDataSource(inputPath));
            options.AddOutput(new FileDataSource(outputPath));

            // Execute the Splitter plugin
            var result = new Splitter().Process(options);

            // Verify the plugin reported results and output file exists
            bool success = result?.ResultCollection?.Count > 0 &&
                           File.Exists(outputPath) &&
                           new FileInfo(outputPath).Length > 0;

            Console.WriteLine(success ? "Splitter operation completed successfully." : "Splitter operation failed.");
        }
    }
}
