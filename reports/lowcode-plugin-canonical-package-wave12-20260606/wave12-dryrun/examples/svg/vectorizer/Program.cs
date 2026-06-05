// svg/vectorizer
// Canonical: https://products.aspose.net/svg/vectorizer/
// Package: Aspose.SVG 24.12.0
// Pattern: ImageVectorizer.Vectorize(imagePath) -> SVGDocument.Save()
using Aspose.Svg;
using Aspose.Svg.ImageVectorization;
using System;
using System.IO;

Directory.CreateDirectory("output");
string fixturePath = Path.GetFullPath("fixture.png");
string outputPath = Path.Combine("output", "output.svg");

// Minimal 1x1 white PNG (valid base64, 96 chars)
byte[] pngBytes = Convert.FromBase64String(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVQI12Ng" +
    "AAAAAgAB4iG8MwAAAABJRU5ErkJggg==");
File.WriteAllBytes(fixturePath, pngBytes);

var vectorizer = new ImageVectorizer
{
    Configuration = new ImageVectorizerConfiguration
    {
        ColorsLimit = 4,
        LineWidth = 1.0f
    }
};
using var document = vectorizer.Vectorize(fixturePath);
document.Save(outputPath);
Console.WriteLine($"Image vectorized to SVG: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
