# barcode/1d-barcode-writer

## Purpose

Generates a 1D barcode (Code128) PNG image from a text value.

**Canonical URL**: [https://products.aspose.net/barcode/1d-barcode-writer/](https://products.aspose.net/barcode/1d-barcode-writer/)

## NuGet Package

`Aspose.BarCode` (version managed centrally in `Directory.Packages.props`; version 24.12.0 proven)

## Prerequisites

- .NET 8.0 SDK or later
- NuGet package `Aspose.BarCode` (restored automatically by `dotnet restore`)

## Input

text string (hardcoded in example)

## Build & Run

```bash
dotnet restore
dotnet build
dotnet run
```

## Expected Output

PNG image file containing the barcode

Output kind: `image/png`

## Contract Files

| File | Description |
|------|-------------|
| `Program.cs` | Runnable example |
| `barcode-1d-barcode-writer.csproj` | Project file (central package management) |
| `example.manifest.json` | Public contract: inputs, outputs, canonical URL |
| `expected-output.json` | Public contract: expected stdout and output file |

## Troubleshooting

- **Restore fails**: ensure .NET 8.0 SDK is installed and internet access is available.
- **Build fails**: check that `Directory.Packages.props` in repo root defines `Aspose.BarCode` version.
- **Output missing**: verify the example writes to the current directory.
