// tasks/convert-mpp-to-image
// Canonical: https://products.aspose.net/tasks/mpp-to-png/
// Package: Aspose.Tasks 24.12.0
// Pattern: new Project() + project.Save(path, new ImageSaveOptions(SaveFileFormat.Png))
using Aspose.Tasks;
using Aspose.Tasks.Saving;
using System;
using System.IO;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "project.png");

var project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 6, 30));

var task1 = project.RootTask.Children.Add("Sprint 1");
task1.Set(Tsk.Start, new DateTime(2026, 1, 1));
task1.Set(Tsk.Duration, project.GetDuration(14, TimeUnitType.Day));

var task2 = project.RootTask.Children.Add("Sprint 2");
task2.Set(Tsk.Start, new DateTime(2026, 1, 19));
task2.Set(Tsk.Duration, project.GetDuration(14, TimeUnitType.Day));

var options = new ImageSaveOptions(SaveFileFormat.Png);
project.Save(outputPath, options);
Console.WriteLine($"Project saved to Image: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
