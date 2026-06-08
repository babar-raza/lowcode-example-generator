# Generate Barcode from Text — Aspose.BarCode for .NET

This example demonstrates generating a Code128 barcode from a text string using
`BarcodeGenerator.Save()` from the Aspose.BarCode library.

## Usage

```bash
dotnet run -- output.png
```

## Requirements

- .NET 8.0 SDK
- Aspose.BarCode 26.5.0 (installed via NuGet)

## How it Works

1. Creates a `BarcodeGenerator` with `EncodeTypes.Code128` and the source text
2. Configures barcode dimensions
3. Saves the barcode image to the specified output path as PNG

## API Reference

- Type: `Aspose.BarCode.Generation.BarcodeGenerator`
- Method: `Save(string, BarCodeImageFormat)`
- Namespace: `Aspose.BarCode.Generation`
- Package: `Aspose.BarCode` 26.5.0

## Probe Evidence

- Probe status: `PROBE_CONFIRMED`
- Output: `barcode-output.png` (12,104 bytes)
- Registry: `pipeline/plugin-capability-registry/barcode.yaml`
