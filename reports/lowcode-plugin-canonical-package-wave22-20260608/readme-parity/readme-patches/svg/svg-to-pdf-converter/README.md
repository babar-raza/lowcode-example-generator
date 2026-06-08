# svg/svg-to-pdf-converter

## Purpose

Converts an SVG document to a PDF file.

**Canonical URL**: [https://products.aspose.net/svg/svg-to-pdf-converter/](https://products.aspose.net/svg/svg-to-pdf-converter/)

## NuGet Package

`Aspose.SVG` (version managed centrally in `Directory.Packages.props`; version 24.12.0 proven)

## Prerequisites

- .NET 8.0 SDK or later
- NuGet package `Aspose.SVG` (restored automatically by `dotnet restore`)

## Input

SVG string document (inline in example)

## Input Fixture

None — SVG content is inline in the example.

## Build & Run

```bash
dotnet restore
dotnet build
dotnet run
```

## Expected Output

PDF file

Output kind: `application/pdf`

## Contract Files

| File | Description |
|------|-------------|
| `Program.cs` | Runnable example |
| `svg-svg-to-pdf-converter.csproj` | Project file (central package management) |
| `example.manifest.json` | Public contract: inputs, outputs, canonical URL |
| `expected-output.json` | Public contract: expected stdout and output file |
| Fixture file(s) | Input data files documented in example.manifest.json |

## Troubleshooting

- **Restore fails**: ensure .NET 8.0 SDK is installed and internet access is available.
- **Build fails**: check that `Directory.Packages.props` in repo root defines `Aspose.SVG` version.
- **Output missing**: verify the example writes to the current directory.
