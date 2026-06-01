# FormImporter Retry Plan

## Current Status
pdf/form-importer is EXTERNAL_UPSTREAM_BUG — FormImporter.Process() throws NullReferenceException.

## Retry Conditions
- Aspose.PDF releases a version with FormImporter fix
- Update NuGet reference in form-importer.csproj
- Run: dotnet restore && dotnet build && dotnet run
- If passes: reclassify as PUBLISH_MAIN_CLASS_EXAMPLE
- Add to publication matrix
