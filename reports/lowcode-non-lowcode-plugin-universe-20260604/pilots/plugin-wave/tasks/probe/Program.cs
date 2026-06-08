// Aspose.Tasks probe — convert-mpp-to-pdf
// Pilot: TRAIN F - tasks family, Plugin 1
// PR-01: Aspose.Tasks.Project confirmed by DllReflector (367 types)
// PR-02: Project.Save(string, SaveFileFormat) confirmed
// PR-03: Project has public constructor Project(string)
// PR-04: SaveFileFormat.Pdf enum confirmed in DllReflector output
using Aspose.Tasks;
using Aspose.Tasks.Saving;

var outputPath = args.Length > 0 ? args[0] : "output.pdf";

// Create a minimal project (no MPP file needed — create in-memory)
var project = new Project();
project.Set(Prj.StartDate, new DateTime(2026, 1, 1));
project.Set(Prj.FinishDate, new DateTime(2026, 12, 31));

// Add a simple task
var task = project.RootTask.Children.Add("Sample Task");
task.Set(Tsk.Start, new DateTime(2026, 1, 1));
task.Set(Tsk.Duration, project.GetDuration(5, TimeUnitType.Day));

// Save as PDF
project.Save(outputPath, SaveFileFormat.Pdf);
Console.WriteLine($"Saved project to: {outputPath}");
