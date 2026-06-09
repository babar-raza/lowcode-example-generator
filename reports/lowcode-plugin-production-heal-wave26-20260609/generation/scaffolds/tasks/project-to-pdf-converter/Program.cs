using Aspose.Tasks;
using Aspose.Tasks.Saving;

Console.WriteLine("Aspose.Tasks - Project to PDF Converter");
var project = new Project();
project.Set(Prj.Name, "Test Project");
var task = project.RootTask.Children.Add("Task 1");
task.Set(Tsk.Duration, project.GetDuration(1));
project.Save("output.pdf", SaveFileFormat.Pdf);
Console.WriteLine("Project converted to PDF: output.pdf");
