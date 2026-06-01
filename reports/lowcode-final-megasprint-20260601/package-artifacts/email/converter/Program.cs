using System;
using System.IO;
using System.Threading.Tasks;
using Aspose.Email.LowCode;

namespace PluginExample
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("Example: email-converter");

            string inputPath = "input.eml";
            File.WriteAllText(inputPath,
                "From: sender@example.com\r\n" +
                "To: recipient@example.com\r\n" +
                "Subject: LowCode Converter Test\r\n" +
                "MIME-Version: 1.0\r\n" +
                "Content-Type: text/plain\r\n\r\n" +
                "Hello, this is a test email for LowCode conversion.");

            string outputDir = "output_html";
            Directory.CreateDirectory(outputDir);

            using var stream = new MemoryStream(File.ReadAllBytes(inputPath));
            string fileName = Path.GetFileName(inputPath);
            var outputHandler = new FolderOutputHandler(outputDir);
            await Converter.ConvertToHtml(stream, fileName, outputHandler);

            Console.WriteLine(Directory.Exists(outputDir) && Directory.GetFiles(outputDir).Length > 0
                ? $"Conversion succeeded: {outputDir}"
                : "Conversion failed: no output files found.");
        }
    }
}
