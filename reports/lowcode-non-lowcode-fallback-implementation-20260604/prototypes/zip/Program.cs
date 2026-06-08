using System;
using System.IO;
using Aspose.Zip;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length < 1)
        {
            Console.Error.WriteLine("Usage: probe <output-path>");
            Environment.Exit(1);
        }
        string outputPath = args[0];

        // PR-01: Archive is in Aspose.Zip (confirmed by DllReflector)
        // PR-02: Save(string) method confirmed
        // PR-03: Archive has public constructor
        using var archive = new Archive();

        // Add a text entry to the archive
        byte[] content = System.Text.Encoding.UTF8.GetBytes("Aspose.ZIP probe entry — 2026-06-04");
        archive.CreateEntry("probe-content.txt", new MemoryStream(content));

        // PR-05: output path passed as CLI arg
        archive.Save(outputPath);

        Console.WriteLine($"Archive saved: {outputPath}");
        Console.WriteLine($"Size: {new FileInfo(outputPath).Length} bytes");
    }
}
