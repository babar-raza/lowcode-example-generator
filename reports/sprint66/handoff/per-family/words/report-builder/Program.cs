using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

public class Person
{
    public string Name { get; set; }
}

class Program
{
    static void Main()
    {
        // Paths for the template and the generated report
        string templatePath = Path.Combine(AppContext.BaseDirectory, "template.docx");
        string outputPath = Path.Combine(AppContext.BaseDirectory, "report.docx");

        // Create a simple template with a LINQ placeholder if it does not exist
        if (!File.Exists(templatePath))
        {
            var doc = new Document();
            var builder = new DocumentBuilder(doc);
            builder.Writeln("Hello, <<[Name]>>!");
            doc.Save(templatePath);
        }

        // Validate that the template file exists
        if (!File.Exists(templatePath))
            throw new FileNotFoundException("Template file not found.", templatePath);

        // Prepare the data source
        var person = new Person { Name = "John Doe" };

        // Generate the report using the LowCode ReportBuilder static method
        ReportBuilder.BuildReport(templatePath, outputPath, person);

        // Validate that the report was created
        if (!File.Exists(outputPath))
            throw new InvalidOperationException("Report was not generated.");

        var info = new FileInfo(outputPath);
        Console.WriteLine($"Report generated successfully: {outputPath} ({info.Length} bytes)");
    }
}