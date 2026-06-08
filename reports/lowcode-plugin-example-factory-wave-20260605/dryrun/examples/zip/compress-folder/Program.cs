// zip/compress-folder
// Canonical: https://products.aspose.net/zip/compress-folder/
// Package: Aspose.ZIP 24.12.0
// Pattern: Create temp dir with files -> new Archive() -> CreateEntries(DirectoryInfo) -> Save
using Aspose.Zip;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "compressed-folder.zip");

// Create a temporary directory structure to compress
string tempDir = Path.Combine(Path.GetTempPath(), "aspose-zip-demo-" + Guid.NewGuid().ToString("N")[..8]);
Directory.CreateDirectory(Path.Combine(tempDir, "subdir"));

File.WriteAllText(Path.Combine(tempDir, "readme.txt"), "Folder compression demo via Aspose.ZIP");
File.WriteAllText(Path.Combine(tempDir, "data.csv"), "id,name,value\n1,alpha,100\n2,beta,200\n3,gamma,300");
File.WriteAllText(Path.Combine(tempDir, "subdir", "notes.txt"), "Notes in subdirectory");

try
{
    using (var archive = new Archive())
    {
        archive.CreateEntries(new DirectoryInfo(tempDir));
        archive.Save(outputPath);
    }
    Console.WriteLine($"Folder compressed: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
}
finally
{
    Directory.Delete(tempDir, true);
}
