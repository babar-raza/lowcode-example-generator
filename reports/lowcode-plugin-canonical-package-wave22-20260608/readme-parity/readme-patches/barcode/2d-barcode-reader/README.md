# barcode/2d-barcode-reader

## Purpose

Reads and decodes 2D barcodes (QR Code, DataMatrix) from an input image.

**Canonical URL**: [https://products.aspose.net/barcode/2d-barcode-reader/](https://products.aspose.net/barcode/2d-barcode-reader/)

## NuGet Package

`Aspose.BarCode` (version managed centrally in `Directory.Packages.props`; version 24.12.0 proven)

## Prerequisites

- .NET 8.0 SDK or later
- NuGet package `Aspose.BarCode` (restored automatically by `dotnet restore`)

## Input

QR code PNG image

## Input Fixture

None — example generates an inline test image programmatically.

## Build & Run

```bash
dotnet restore
dotnet build
dotnet run
```

## Expected Output

decoded QR code text (stdout)

Output kind: `text`

## Contract Files

| File | Description |
|------|-------------|
| `Program.cs` | Runnable example |
| `barcode-2d-barcode-reader.csproj` | Project file (central package management) |
| `example.manifest.json` | Public contract: inputs, outputs, canonical URL |
| `expected-output.json` | Public contract: expected stdout and output file |
| Fixture file(s) | Input data files documented in example.manifest.json |

## Troubleshooting

- **Restore fails**: ensure .NET 8.0 SDK is installed and internet access is available.
- **Build fails**: check that `Directory.Packages.props` in repo root defines `Aspose.BarCode` version.
- **Output missing**: verify the example writes to the current directory.
