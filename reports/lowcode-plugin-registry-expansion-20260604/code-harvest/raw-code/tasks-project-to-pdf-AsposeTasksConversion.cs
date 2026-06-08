// Source: https://raw.githubusercontent.com/aspose-tasks/Aspose.Tasks-for-.NET/master/Demos/src/Aspose.Tasks.Live.Demos.UI/Models/AsposeTasksConversion.cs
// Fetched: 2026-06-04 | Sprint: lowcode-plugin-registry-expansion-20260604

// CORE PATTERN:
// Project project = new Project(inFilePath);
// PdfSaveOptions pdfSaveOptions = new PdfSaveOptions();
// project.Save(outPath, (SaveOptions)pdfSaveOptions);

using Aspose.Tasks;
using Aspose.Tasks.Saving;

public void ConvertProjectToPdf(string inFilePath, string outPath) {
    Project project = new Project(inFilePath);
    PdfSaveOptions pdfSaveOptions = new PdfSaveOptions();
    project.Save(outPath, (SaveOptions)pdfSaveOptions);
}
