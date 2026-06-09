using Aspose.Zip;

Console.WriteLine("Aspose.ZIP - File Compressor");
File.WriteAllText("sample.txt", "Hello World - test content for compression");
using var archive = new Archive();
archive.CreateEntry("sample.txt", "sample.txt");
archive.Save("output.zip");
Console.WriteLine("Files compressed successfully: output.zip");
