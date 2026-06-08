# svg/vectorizer

## Purpose

Converts a raster PNG image to an SVG vector graphic.

**Canonical URL**: [https://products.aspose.net/svg/vectorizer/](https://products.aspose.net/svg/vectorizer/)

## NuGet Package

`Aspose.SVG` (version managed centrally in `Directory.Packages.props`; version 24.12.0 proven)

## Prerequisites

- .NET 8.0 SDK or later
- NuGet package `Aspose.SVG` (restored automatically by `dotnet restore`)

## Input

fixture.png — small raster PNG image

## Input Fixture

fixture.png included in this directory.

## Build & Run

```bash
dotnet restore
dotnet build
dotnet run
```

## Expected Output

SVG vector file

Output kind: `image/svg+xml`

## Contract Files

| File | Description |
|------|-------------|
| `Program.cs` | Runnable example |
| `svg-vectorizer.csproj` | Project file (central package management) |
| `example.manifest.json` | Public contract: inputs, outputs, canonical URL |
| `expected-output.json` | Public contract: expected stdout and output file |
| Fixture file(s) | Input data files documented in example.manifest.json |

## Troubleshooting

- **Restore fails**: ensure .NET 8.0 SDK is installed and internet access is available.
- **Build fails**: check that `Directory.Packages.props` in repo root defines `Aspose.SVG` version.
- **Output missing**: verify the example writes to the current directory.
