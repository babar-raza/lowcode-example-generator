// zip/universal-extractor
// Canonical: https://products.aspose.net/zip/universal-extractor/
// Package: Aspose.ZIP 24.12.0
// Pattern: new Archive() -> archive.CreateEntry(name, stream) -> archive.Save(outputPath)
using Aspose.Zip;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "archive.zip");

using (var archive = new Archive())
{
    // Add first entry from memory stream
    byte[] data1 = Encoding.UTF8.GetBytes("Hello from Aspose.ZIP — file1.txt");
    archive.CreateEntry("file1.txt", new MemoryStream(data1));

    // Add second entry
    byte[] data2 = Encoding.UTF8.GetBytes("Second document content for demonstration.");
    archive.CreateEntry("docs/file2.txt", new MemoryStream(data2));

    // Add a JSON entry
    byte[] data3 = Encoding.UTF8.GetBytes(@"{""generated"": ""2026-06-05"", ""sprint"": ""factory-wave""}");
    archive.CreateEntry("metadata.json", new MemoryStream(data3));

    archive.Save(outputPath);
}

Console.WriteLine($"Archive created: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
