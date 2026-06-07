# Recommended Example Package Standard

## Directory Structure
```
examples/{family}/{slug}/
  Program.cs              — top-level statements, clear variable names
  {family}-{slug}.csproj  — net8.0, single PackageReference
  README.md               — canonical URL + nuget + build command
  output-validation.json  — machine-readable proof record
  fixtures/               — input files (only when needed)
  output/                 — .gitignored output directory
```

## README Template
```markdown
# {family}/{slug}
Canonical URL: https://products.aspose.net/{family}/{slug}/
NuGet: Aspose.{Product} {version}
Proven: Wave N (YYYY-MM-DD)

## Build & Run
dotnet restore && dotnet build && dotnet run
```

## Program.cs Pattern
- Top-level statements (C# 9+)
- Directory.CreateDirectory("output") at start
- Console.WriteLine with output path and file size
- No interactive input
