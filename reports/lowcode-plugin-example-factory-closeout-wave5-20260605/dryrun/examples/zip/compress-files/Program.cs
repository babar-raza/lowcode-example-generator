// zip/compress-files
// Canonical: https://products.aspose.net/zip/compress-files/
// Package: Aspose.ZIP 24.12.0
// Pattern: Create individual file entries -> new Archive() -> CreateEntry per file -> Save
using Aspose.Zip;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "compressed.zip");

// Create in-memory file contents to compress
var files = new (string name, byte[] content)[]
{
    ("document.txt", Encoding.UTF8.GetBytes("Sample document for compression.\nLine 2.\nLine 3.")),
    ("data.csv",     Encoding.UTF8.GetBytes("id,name,value\n1,alpha,100\n2,beta,200\n3,gamma,300")),
    ("notes.md",     Encoding.UTF8.GetBytes("# Notes\n\n- Item 1\n- Item 2\n- Item 3\n")),
};

using (var archive = new Archive())
{
    foreach (var (name, content) in files)
    {
        using var ms = new MemoryStream(content);
        archive.CreateEntry(name, ms);
    }
    archive.Save(outputPath);
}

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"Compressed {files.Length} files into: {outputPath} ({size} bytes)");
