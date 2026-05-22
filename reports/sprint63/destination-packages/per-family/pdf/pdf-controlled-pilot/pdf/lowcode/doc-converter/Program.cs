using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

class Program
{
    static void Main()
    {
        // 1. Create input PDF fixture
        string inputPath = Path.Combine(Path.GetTempPath(), "input.pdf");
        var doc = new Document();
        doc.Pages.Add().Paragraphs.Add(new TextFragment("Hello, Aspose PDF LowCode!"));
        doc.Save(inputPath);

        // Validate input file
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
        {
            Console.Error.WriteLine("Input PDF was not created correctly.");
            return;
        }

        // 2. Perform LowCode conversion (PDF to DOCX)
        var converter = new DocConverter();

        var options = new PdfToDocOptions
        {
            SaveFormat = Aspose.Pdf.LowCode.SaveFormat.DocX
        };
        options.AddInput(new FileDataSource(inputPath));

        string outputPath = Path.Combine(Path.GetTempPath(), "output.docx");
        options.AddOutput(new FileDataSource(outputPath));

        var result = converter.Process(options);

        // Verify processing result
        if (result?.ResultCollection == null || result.ResultCollection.Count == 0)
        {
            Console.Error.WriteLine("LowCode processing did not produce any results.");
            return;
        }

        // 3. Validate output file
        if (File.Exists(outputPath) && new FileInfo(outputPath).Length > 0)
        {
            Console.WriteLine($"Conversion succeeded, output file size: {new FileInfo(outputPath).Length} bytes");
        }
        else
        {
            Console.Error.WriteLine("Output file was not created.");
        }
    }
}