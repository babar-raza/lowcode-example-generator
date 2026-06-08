// Source: https://raw.githubusercontent.com/aspose-ocr/Aspose.OCR-for-.NET/master/Examples/Aspose.OCR.Examples.CSharp/PerformingandManagingOCR/RecognizeImageFromStream.cs
// Fetched: 2026-06-04 | Sprint: lowcode-plugin-registry-expansion-20260604

// CORE PATTERN:
// AsposeOcr api = new AsposeOcr();
// OcrInput input = new OcrInput(InputType.SingleImage);
// input.Add(stream);
// List<RecognitionResult> result = api.Recognize(input);
// Console.WriteLine(result[0].RecognitionText);

using System;
using System.Collections.Generic;
using System.IO;
using Aspose.OCR;

public class RecognizeImageFromStream {
    public static void Run() {
        string dataDir = "data/";
        AsposeOcr api = new AsposeOcr();
        using MemoryStream ms = new MemoryStream();
        using FileStream file = new FileStream(dataDir + "sample.png", FileMode.Open, FileAccess.Read);
        file.CopyTo(ms);
        OcrInput input = new OcrInput(InputType.SingleImage);
        input.Add(ms);
        List<RecognitionResult> result = api.Recognize(input);
        Console.WriteLine(result[0].RecognitionText);
    }
}
