# Diff from Official Snippet: barcode/generate-barcode

## Official Source
File: `StoreBarcodeOutputAsFile.cs`
URL: https://raw.githubusercontent.com/aspose-barcode/Aspose.BarCode-for-.NET/master/Examples/CSharp/BarcodeGeneration/BarcodeOutput/StoreBarcodeOutputAsFile.cs

## Original Code (verbatim)
```csharp
using Aspose.BarCode.Generation;

internal class StoreBarcodeOutputAsFile : StoreBarcodeOutputBase
{
    public static void Run()
    {
        string path = GetFolder();
        BarcodeGenerator gen = new BarcodeGenerator(EncodeTypes.Code128, "12345678");
        gen.Save($"{path}StoreImageAsFile.png", BarCodeImageFormat.Png);
        // + 4 more Save calls for jpg, bmp, tif, gif
    }
}
```

## Adaptation Required for Standalone Example

To make this a standalone runnable example:

1. Remove inheritance from `StoreBarcodeOutputBase` — replace `GetFolder()` with `Environment.CurrentDirectory`
2. Wrap in `Program` class with `static void Main(string[] args)`
3. Select single output format (PNG) for simplicity
4. Add license setup call (trial-safe)

## Diff

```diff
- internal class StoreBarcodeOutputAsFile : StoreBarcodeOutputBase
+ internal class Program
  {
-     public static void Run()
+     public static void Main(string[] args)
      {
-         string path = GetFolder();
+         string path = args.Length > 0 ? args[0] : "";
          BarcodeGenerator gen = new BarcodeGenerator(EncodeTypes.Code128, "12345678");
-         gen.Save($"{path}StoreImageAsFile.png", BarCodeImageFormat.Png);
-         gen.Save($"{path}StoreImageAsFile.jpg", BarCodeImageFormat.Jpeg);
-         // ... 3 more formats
+         gen.Save("output-barcode.png", BarCodeImageFormat.Png);
      }
  }
```

## API Changes
- None. All classes, enums, and methods are identical to official snippet.
- Only structural adaptation (standalone Main vs example class hierarchy).

## Verdict
NO_API_CHANGE — official snippet maps directly to standalone example with structural wrap only.
