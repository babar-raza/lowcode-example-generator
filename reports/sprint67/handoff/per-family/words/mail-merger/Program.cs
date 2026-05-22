using System;
using System.IO;
using Aspose.Words;
using Aspose.Words.LowCode;

class Program
{
    static void Main()
    {
        // Paths for the template and the result document
        string templatePath = Path.Combine(AppContext.BaseDirectory, "template.docx");
        string resultPath = Path.Combine(AppContext.BaseDirectory, "result.docx");

        // Ensure any previous files are removed
        if (File.Exists(templatePath)) File.Delete(templatePath);
        if (File.Exists(resultPath)) File.Delete(resultPath);

        // Create a simple template with MERGEFIELD fields
        Document templateDoc = new Document();
        DocumentBuilder builder = new DocumentBuilder(templateDoc);
        builder.Writeln("Dear ");
        builder.InsertField("MERGEFIELD FirstName");
        builder.Write(" ");
        builder.InsertField("MERGEFIELD LastName");
        builder.Writeln(",");
        builder.Writeln("This is a test merge.");
        templateDoc.Save(templatePath);

        // Validate that the template was created
        if (!File.Exists(templatePath))
            throw new FileNotFoundException("Template file was not created.", templatePath);

        // Define merge field names and values
        string[] fieldNames = { "FirstName", "LastName" };
        string[] fieldValues = { "John", "Doe" };

        // Perform the mail merge using the LowCode static method
        MailMerger.Execute(templatePath, resultPath, fieldNames, fieldValues);

        // Verify that the result file was created
        if (!File.Exists(resultPath))
            throw new InvalidOperationException("Result file was not created.");

        // Deterministic success output
        Console.WriteLine($"Merge completed successfully. Output: {resultPath} ({new FileInfo(resultPath).Length} bytes)");
    }
}