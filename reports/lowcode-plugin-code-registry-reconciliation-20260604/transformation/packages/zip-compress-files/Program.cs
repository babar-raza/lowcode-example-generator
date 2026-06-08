// Aspose.ZIP — Compress files/folder into a ZIP archive
// Canonical product page: https://products.aspose.net/zip/universal-compressor/
// Source authority: https://github.com/aspose-zip/Aspose.ZIP-for-.NET
// Source file: Examples/CSharp/CompressingAndDecompressingFolders/CompressDirectory.cs
//
// Pattern: LOAD_SAVE_OPTIONS
//   new Archive() → archive.CreateEntries(directoryInfo) → archive.Save(stream)

using Aspose.Zip;

string outputDir = Path.Combine(Directory.GetCurrentDirectory(), "output");
Directory.CreateDirectory(outputDir);

// Create test files to compress
string inputDir = Path.Combine(outputDir, "files_to_compress");
Directory.CreateDirectory(inputDir);
File.WriteAllText(Path.Combine(inputDir, "file1.txt"), "Hello from Aspose.ZIP example - file 1");
File.WriteAllText(Path.Combine(inputDir, "file2.txt"), "Hello from Aspose.ZIP example - file 2");

string archivePath = Path.Combine(outputDir, "compressed_output.zip");

using (FileStream zipFile = File.Open(archivePath, FileMode.Create))
{
    using (Archive archive = new Archive())
    {
        // Add all files from the directory
        DirectoryInfo dirInfo = new DirectoryInfo(inputDir);
        archive.CreateEntries(dirInfo);
        archive.Save(zipFile);
    }
}

Console.WriteLine($"Archive saved to: {archivePath}");
Console.WriteLine($"File exists: {File.Exists(archivePath)}");
Console.WriteLine($"Archive size: {new FileInfo(archivePath).Length} bytes");
Console.WriteLine("SNIPPET_RUN: PASS");
