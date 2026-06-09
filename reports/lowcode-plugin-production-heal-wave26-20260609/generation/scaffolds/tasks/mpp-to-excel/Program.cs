using Aspose.Tasks;
using Aspose.Tasks.Saving;

Console.WriteLine("Aspose.Tasks - MPP to Excel Converter");
var project = new Project();
project.Set(Prj.Name, "Test Project");
var task = project.RootTask.Children.Add("Task 1");
task.Set(Tsk.Duration, project.GetDuration(1));
project.Save("output.xlsx", SaveFileFormat.Xlsx);
Console.WriteLine("Project converted to Excel: output.xlsx");
