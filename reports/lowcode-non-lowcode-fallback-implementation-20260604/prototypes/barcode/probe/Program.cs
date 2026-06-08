// Probe: BarcodeGenerator.Save — TC-IMPL-007
// PR-01: BarcodeGenerator confirmed in DllReflector (Aspose.BarCode 26.5.0 / Aspose.BarCode.Generation)
// PR-02: Save method confirmed in DllReflector output
// PR-03: has_public_constructor=true; is_abstract=false; is_interface=false
// PR-05: output path passed as CLI arg
// PR-08: dotnet run stdout/stderr captured (see probe-restore.log, probe-build.log, probe-run.log)
using System;
using Aspose.BarCode.Generation;

var outputPath = args.Length > 0 ? args[0] : "probe-output.png";
Console.WriteLine("[PROBE] Initializing BarcodeGenerator...");
var gen = new BarcodeGenerator(EncodeTypes.Code128, "ProbeTest12345");
Console.WriteLine("[PROBE] Generating barcode image...");
gen.Save(outputPath, BarCodeImageFormat.Png);
Console.WriteLine("[PROBE] Barcode saved to: " + outputPath);
