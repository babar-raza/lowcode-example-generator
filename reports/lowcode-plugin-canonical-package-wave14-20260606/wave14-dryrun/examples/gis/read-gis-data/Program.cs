// gis/read-gis-data
// Canonical: https://products.aspose.net/gis/net/read-gis-data/
// Package: Aspose.GIS 24.12.0
// Pattern: Write GeoJSON fixture -> VectorLayer.Open(GeoJSON) -> iterate features
using Aspose.Gis;
using System;
using System.IO;
using System.Text;

Directory.CreateDirectory("output");
string outputPath = Path.Combine("output", "features.txt");

string geoJson = @"{
  ""type"": ""FeatureCollection"",
  ""features"": [
    {
      ""type"": ""Feature"",
      ""geometry"": {""type"": ""Point"", ""coordinates"": [13.4050, 52.5200]},
      ""properties"": {""name"": ""Berlin"", ""pop"": 3645000}
    },
    {
      ""type"": ""Feature"",
      ""geometry"": {
        ""type"": ""Polygon"",
        ""coordinates"": [[[0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0],[0.0,0.0]]]
      },
      ""properties"": {""name"": ""Unit Square"", ""area_km2"": 1.0}
    }
  ]
}";

string fixturePath = "fixture.geojson";
File.WriteAllText(fixturePath, geoJson, Encoding.UTF8);

var sb = new StringBuilder();
sb.AppendLine("GIS Features Read from GeoJSON:");
sb.AppendLine($"Source: {fixturePath}");
sb.AppendLine();

int featureCount = 0;
using (var layer = VectorLayer.Open(fixturePath, Drivers.GeoJson))
{
    featureCount = layer.Count;
    sb.AppendLine($"Feature count: {featureCount}");
    int i = 1;
    foreach (var feature in layer)
    {
        sb.AppendLine($"Feature {i++}:");
        sb.AppendLine($"  Geometry type: {feature.Geometry?.GeometryType}");
        if (feature.Geometry != null)
            sb.AppendLine($"  WKT: {feature.Geometry.AsText()}");
        foreach (var attr in layer.Attributes)
        {
            try
            {
                var val = feature.GetValue<object>(attr.Name);
                sb.AppendLine($"  {attr.Name}: {val}");
            }
            catch
            {
                sb.AppendLine($"  {attr.Name}: (not set)");
            }
        }
    }
}

File.WriteAllText(outputPath, sb.ToString());
Console.WriteLine($"GIS data read: {featureCount} features");
Console.WriteLine($"Saved: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
