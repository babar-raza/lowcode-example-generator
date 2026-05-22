using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

class Program
{
    static void Main()
    {
        // Prepare temporary folder
        string tempDir = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        Directory.CreateDirectory(tempDir);

        // Define file paths
        string inputPath = Path.Combine(tempDir, "input.docx");
        string outputPath = Path.Combine(tempDir, "output.docx");

        // Create a simple Word document programmatically
        var doc = new Document();
        var builder = new DocumentBuilder(doc);
        builder.Writeln("This is a sample document with a placeholder token.");
        doc.Save(inputPath);

        // Validate input file exists and is non‑empty
        if (!File.Exists(inputPath) || new FileInfo(inputPath).Length == 0)
        {
            Console.WriteLine("Failed to create input file.");
            return;
        }

        // Perform replace operation using the simplest string‑path overload
        string pattern = "placeholder";
        string replacement = "world";
        int result = Replacer.Replace(inputPath, outputPath, pattern, replacement);

        // Validate the operation succeeded (non‑negative return) and output file exists
        if (result < 0 || !File.Exists(outputPath) || new FileInfo(outputPath).Length == 0)
        {
            Console.WriteLine("Replace operation failed.");
            return;
        }

        Console.WriteLine($"Replace succeeded (result={result}). Output file created at: {outputPath}");
    }
}
