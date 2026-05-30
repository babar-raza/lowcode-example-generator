using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

namespace PluginExample
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Example: words-mail-merger");

            string templatePath = "template.docx";
            var doc = new Document();
            var builder = new DocumentBuilder(doc);
            builder.Write("Hello, ");
            builder.InsertField("MERGEFIELD FirstName");
            builder.Write(" ");
            builder.InsertField("MERGEFIELD LastName");
            builder.Writeln("! Welcome to the LowCode example.");
            doc.Save(templatePath);

            string outputPath = "output.docx";
            string[] fieldNames = { "FirstName", "LastName" };
            string[] fieldValues = { "John", "Doe" };
            MailMerger.Execute(templatePath, outputPath, fieldNames, fieldValues);

            Console.WriteLine(File.Exists(outputPath)
                ? $"Mail merge succeeded: {outputPath}"
                : "Mail merge failed: output not found.");
        }
    }
}
