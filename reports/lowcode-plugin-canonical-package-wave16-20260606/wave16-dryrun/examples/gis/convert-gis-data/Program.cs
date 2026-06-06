// gis/convert-gis-data
// Canonical: https://products.aspose.net/gis/convert-gis-data/
// Package: Aspose.GIS 24.12.0
// Pattern: Write GeoJSON fixture -> VectorLayer.Convert(GeoJSON -> KML)
using Aspose.Gis;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");

string inputPath = Path.Combine("output", "input.geojson");
string outputPath = Path.Combine("output", "output.kml");

// Create a GeoJSON fixture programmatically
string geoJson = @"{
  ""type"": ""FeatureCollection"",
  ""features"": [
    {
      ""type"": ""Feature"",
      ""geometry"": {""type"": ""Point"", ""coordinates"": [13.4050, 52.5200]},
      ""properties"": {""name"": ""Berlin"", ""population"": 3645000}
    },
    {
      ""type"": ""Feature"",
      ""geometry"": {""type"": ""Point"", ""coordinates"": [2.3522, 48.8566]},
      ""properties"": {""name"": ""Paris"", ""population"": 2161000}
    },
    {
      ""type"": ""Feature"",
      ""geometry"": {
        ""type"": ""LineString"",
        ""coordinates"": [[13.4050, 52.5200], [2.3522, 48.8566]]
      },
      ""properties"": {""name"": ""Berlin-Paris Route""}
    }
  ]
}";

File.WriteAllText(inputPath, geoJson, Encoding.UTF8);

// Convert GeoJSON to KML
VectorLayer.Convert(inputPath, Drivers.GeoJson, outputPath, Drivers.Kml);

long size = new FileInfo(outputPath).Length;
Console.WriteLine($"GIS data converted: {inputPath} -> {outputPath} ({size} bytes)");
