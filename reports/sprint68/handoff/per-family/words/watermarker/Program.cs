using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

class Program
{
    static void Main()
    {
        // Define temporary file paths
        string inputPath = Path.Combine(Path.GetTempPath(), "input.docx");
        string outputPath = Path.Combine(Path.GetTempPath(), "output.docx");

        // Clean up any previous runs
        if (File.Exists(inputPath)) File.Delete(inputPath);
        if (File.Exists(outputPath)) File.Delete(outputPath);

        // Create a simple Word document programmatically
        var doc = new Document();
        var builder = new DocumentBuilder(doc);
        builder.Writeln("Sample document for Watermarker SetText demonstration.");
        doc.Save(inputPath);

        // Verify the input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
        {
            Console.WriteLine("Failed to create the input document.");
            return;
        }

        // Apply a text watermark using the simplest overload of Watermarker.SetText
        Watermarker.SetText(inputPath, outputPath, "CONFIDENTIAL");

        // Verify the output file exists and is non‑empty
        if (File.Exists(outputPath) && new FileInfo(outputPath).Length > 0)
        {
            Console.WriteLine("Watermark applied successfully.");
        }
        else
        {
            Console.WriteLine("Watermark application failed.");
        }
    }
}
