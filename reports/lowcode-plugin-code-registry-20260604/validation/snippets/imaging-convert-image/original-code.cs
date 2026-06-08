// GIST-ID: 7850a7dd21684c1c466565d85085340c
// Source: https://raw.githubusercontent.com/aspose-imaging/Aspose.Imaging-for-.NET/master/Examples/CSharp/ModifyingAndConvertingImages/ConvertImageWithGrayscale.cs
using System;
using Aspose.Imaging;
using Aspose.Imaging.ImageOptions;
using Aspose.Imaging.FileFormats.Jpeg;

namespace CSharp.ModifyingAndConvertingImages
{
    class ConvertImageWithGrayscale
    {
        public static void Run()
        {
            string dataDir = RunExamples.GetDataDir_ModifyingAndConvertingImages();
            // Core pattern: Image.Load() + configure options + Save()
            using (Image image = Image.Load(dataDir + "aspose-logo.jpg"))
            {
                JpegOptions jpegOptions = new JpegOptions();
                jpegOptions.ColorType = JpegCompressionColorMode.Grayscale;
                image.Save(dataDir + "output_grayscale.jpg", jpegOptions);
            }
        }
    }
}
