using System;
using System.IO;
using Aspose.Pdf;
using Aspose.Pdf.LowCode;
using Aspose.Pdf.Text;

namespace LowCodeXlsConverterDemo
{
    internal class Program
    {
        private static void Main()
        {
            // 1. Prepare working directory
            string workDir = Path.Combine(Path.GetTempPath(), "LowCodeXlsDemo");
            Directory.CreateDirectory(workDir);

            string inputPdfPath = Path.Combine(workDir, "input.pdf");
            string outputXlsPath = Path.Combine(workDir, "output.xlsx");

            // 2. Create a simple PDF document
            var pdfDoc = new Document();
            var page = pdfDoc.Pages.Add();
            var fragment = new TextFragment("Hello, PDF!");
            page.Paragraphs.Add(fragment);
            pdfDoc.Save(inputPdfPath);

            // 3. Validate input file
            if (!File.Exists(inputPdfPath) || new FileInfo(inputPdfPath).Length == 0)
                throw new InvalidOperationException("Input PDF was not created correctly.");

            // 4. Configure LowCode conversion options
            var options = new PdfToXlsOptions
            {
                Format = PdfToXlsOptions.ExcelFormat.XLSX
            };
            options.AddInput(new FileDataSource(inputPdfPath));
            options.AddOutput(new FileDataSource(outputXlsPath));

            // 5. Execute conversion using the primary method
            var converter = new XlsConverter();
            var result = converter.Process(options);

            // 6. Verify conversion result
            if (result?.ResultCollection == null || result.ResultCollection.Count == 0)
                throw new InvalidOperationException("Conversion did not produce any results.");

            // 7. Validate output file
            if (!File.Exists(outputXlsPath) || new FileInfo(outputXlsPath).Length == 0)
                throw new InvalidOperationException("Output XLSX was not created or is empty.");

            // 8. Deterministic success output
            Console.WriteLine($"Conversion succeeded, output size: {new FileInfo(outputXlsPath).Length} bytes");
        }
    }
}