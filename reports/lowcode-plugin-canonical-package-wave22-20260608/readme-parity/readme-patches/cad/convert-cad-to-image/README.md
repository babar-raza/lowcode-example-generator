# cad/convert-cad-to-image

## Purpose

Converts a CAD drawing (DXF format) to a raster image (PNG/JPG).

**Canonical URL**: [https://products.aspose.net/cad/convert-cad-to-image/](https://products.aspose.net/cad/convert-cad-to-image/)

## NuGet Package

`Aspose.CAD` (version managed centrally in `Directory.Packages.props`; version 24.12.0 proven)

## Prerequisites

- .NET 8.0 SDK or later
- NuGet package `Aspose.CAD` (restored automatically by `dotnet restore`)

## Input

fixtures/minimal.dxf — minimal DXF CAD drawing file

## Input Fixture

fixtures/minimal.dxf included in this directory.

## Build & Run

```bash
dotnet restore
dotnet build
dotnet run
```

## Expected Output

raster image file

Output kind: `image`

## Contract Files

| File | Description |
|------|-------------|
| `Program.cs` | Runnable example |
| `cad-convert-cad-to-image.csproj` | Project file (central package management) |
| `example.manifest.json` | Public contract: inputs, outputs, canonical URL |
| `expected-output.json` | Public contract: expected stdout and output file |
| Fixture file(s) | Input data files documented in example.manifest.json |

## Troubleshooting

- **Restore fails**: ensure .NET 8.0 SDK is installed and internet access is available.
- **Build fails**: check that `Directory.Packages.props` in repo root defines `Aspose.CAD` version.
- **Output missing**: verify the example writes to the current directory.
