// Source: https://raw.githubusercontent.com/aspose-psd/Aspose.PSD-for-.NET/master/Examples/CSharp/Aspose/ModifyingAndConvertingImages/PSD/ConvertPsdToJpg.cs
// Fetched: 2026-06-04 | Sprint: lowcode-plugin-registry-expansion-20260604

// CORE PATTERN:
// using (var psdImage = (PsdImage)Image.Load(inputFile))
// {
//     psdImage.Save(outputFile, new JpegOptions() { Quality = 80 });
// }

using Aspose.PSD.FileFormats.Psd;
using Aspose.PSD.ImageOptions;

public class ConvertPsdToJpg {
    public static void Run() {
        string inputFile = "PsdConvertToExample.psd";
        using (var psdImage = (PsdImage)Image.Load(inputFile)) {
            psdImage.Save("PsdConvertedToJpg.jpg", new JpegOptions() { Quality = 80, JpegLsAllowedLossyError = 10 });
        }
    }
}
