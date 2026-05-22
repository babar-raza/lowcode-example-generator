using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

class Program
{
    static void Main()
    {
        // Prepare temporary file paths
        string tempDir = Path.Combine(Path.GetTempPath(), "AsposeWordsLowCodeDemo");
        Directory.CreateDirectory(tempDir);
        string inputPath = Path.Combine(tempDir, "input.docx");
        string outputPath = Path.Combine(tempDir, "output.docx");

        // Create a simple multi‑page Word document
        var doc = new Document();
        var builder = new DocumentBuilder(doc);
        builder.Writeln("First page content.");
        builder.InsertBreak(BreakType.PageBreak);
        builder.Writeln("Second page content.");
        doc.Save(inputPath);

        // Validate input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
            throw new InvalidOperationException("Input file was not created correctly.");

        // Extract the first page using the simplest overload of ExtractPages
        Splitter.ExtractPages(inputPath, outputPath, startPageIndex: 0, pageCount: 1);

        // Validate output file exists and is non‑empty
        if (!File.Exists(outputPath) || new FileInfo(outputPath).Length == 0)
            throw new InvalidOperationException("Output file was not created correctly.");

        Console.WriteLine($"ExtractPages succeeded: '{outputPath}'");
    }
}
