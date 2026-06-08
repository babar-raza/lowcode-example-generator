// Dry-run example: tasks/project-to-pdf-converter
// Canonical URL: https://products.aspose.net/tasks/project-to-pdf-converter/
// Package: Aspose.Tasks 24.12.0
// Pattern: new Project() → project.Save(outPath, (SaveOptions)new PdfSaveOptions())

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

var task = project.RootTask.Children.Add("Sample Task");
task.Set(Tsk.Start, new DateTime(2026, 1, 1));
task.Set(Tsk.Duration, project.GetDuration(5, TimeUnitType.Day));

project.Save(outputPath, (SaveOptions)new PdfSaveOptions());

Console.WriteLine($"Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
