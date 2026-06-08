// Snippet validation: tasks/project-to-pdf-converter
// Source: https://products.aspose.net/tasks/project-to-pdf-converter/
// Official code: AsposeTasksConversion.cs (aspose-tasks/Aspose.Tasks-for-.NET)
// Pattern: new Project() → project.Save(outPath, (SaveOptions)new PdfSaveOptions())
// Note: Using programmatic Project() creation (no .mpp fixture needed)

using Aspose.Tasks;
using Aspose.Tasks.Saving;
using System;
using System.IO;

string outputDir = "output";
Directory.CreateDirectory(outputDir);
string outputPath = Path.Combine(outputDir, "output.pdf");

// Create project programmatically (no .mpp fixture required)
Project project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 12, 31));

var task = project.RootTask.Children.Add("Validate Aspose.Tasks PDF export");
task.Set(Tsk.Start, new DateTime(2026, 1, 1));
task.Set(Tsk.Duration, project.GetDuration(5, TimeUnitType.Day));

PdfSaveOptions pdfSaveOptions = new PdfSaveOptions();
project.Save(outputPath, (SaveOptions)pdfSaveOptions);

bool exists = File.Exists(outputPath);
long size = exists ? new FileInfo(outputPath).Length : 0;
Console.WriteLine($"OUTPUT_FILE={outputPath}");
Console.WriteLine($"FILE_EXISTS={exists}");
Console.WriteLine($"FILE_SIZE_BYTES={size}");
Console.WriteLine(exists && size > 100 ? "VALIDATION=PASS" : "VALIDATION=FAIL");
