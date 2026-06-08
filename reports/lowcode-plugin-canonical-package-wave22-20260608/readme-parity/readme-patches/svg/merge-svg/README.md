# svg/merge-svg

## Purpose

Merges multiple SVG documents into a single SVG output.

**Canonical URL**: [https://products.aspose.net/svg/merge-svg/](https://products.aspose.net/svg/merge-svg/)

## NuGet Package

`Aspose.SVG` (version managed centrally in `Directory.Packages.props`; version 24.12.0 proven)

## Prerequisites

- .NET 8.0 SDK or later
- NuGet package `Aspose.SVG` (restored automatically by `dotnet restore`)

## Input

two SVG string documents (inline in example)

## Input Fixture

None — SVG content is inline in the example.

## Build & Run

```bash
dotnet restore
dotnet build
dotnet run
```

## Expected Output

merged SVG document (stdout)

Output kind: `text/svg`

## Contract Files

| File | Description |
|------|-------------|
| `Program.cs` | Runnable example |
| `svg-merge-svg.csproj` | Project file (central package management) |
| `example.manifest.json` | Public contract: inputs, outputs, canonical URL |
| `expected-output.json` | Public contract: expected stdout and output file |
| Fixture file(s) | Input data files documented in example.manifest.json |

## Troubleshooting

- **Restore fails**: ensure .NET 8.0 SDK is installed and internet access is available.
- **Build fails**: check that `Directory.Packages.props` in repo root defines `Aspose.SVG` version.
- **Output missing**: verify the example writes to the current directory.
