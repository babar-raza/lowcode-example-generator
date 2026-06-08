# Family Manual Analysis: gis

## Date: 2026-06-04
## Evidence: GitHub repo aspose-gis/Aspose.GIS-for-.NET, code: LimitPrecisionWhenReadingGeometries.cs
## Prior sprint: PROBE_BLOCKED_API (geospatial datasets required)

---

## 1. LowCode Namespace? No.
## 2. Plugins Namespace? No.
## 3. Regular Product APIs? Yes. VectorLayer class with open/convert operations.
## 4. Dedicated Plugin-Like Classes?
Yes:
- `VectorLayer` — primary class for GIS vector data (SHP, GeoJSON, KML, GPX etc.)
- `Drivers` — static factory: Drivers.Shapefile, Drivers.GeoJson, etc.

## 5. Static Converter Classes? No.
## 6. Load/Save with Format Options? Yes. `VectorLayer.Convert(sourcePath, sourceDriver, destPath, destDriver)`.
## 7. Document Object Model Workflow? Yes. VectorLayer has Features, Geometry, Attributes.
## 8. Recognition/Extraction APIs? No.
## 9. Rendering/Export APIs? Yes. Map rendering to image possible.

## 10. Fixtures Needed?
Yes. GIS plugins need geospatial data files (SHP, GeoJSON, KML etc.).

## 11. License-Sensitive?
Trial mode: limited features. Prior sprint: PROBE_BLOCKED_API.

## 12. Official Snippets?
- `LimitPrecisionWhenReadingGeometries.cs` — VectorLayer.Open + feature enumeration

## 13. Classes/Methods?
- `VectorLayer.Convert(sourcePath, Drivers.Shapefile, destPath, Drivers.GeoJson);`
- `using (VectorLayer layer = VectorLayer.Open(filePath, Drivers.GeoJson))`
- `foreach (Feature feature in layer)` — enumerate features
- `feature.Geometry` — access geometry

## 14. Plugins Sharing API Pattern?
convert-gis-data: VectorLayer.Convert() — single static call
read-gis-data: VectorLayer.Open() + feature enumeration

## 15. Plugins Needing Unique Mapping?
read-gis-data: Output is data objects, not a file conversion.

## 16. Plugins with No Code?
convert-gis-data matched App.xaml.cs (wrong file). NEEDS_MANUAL_MAPPING.

## 17. Can Be Transformed Next Sprint?
- convert-gis-data: NEEDS_MANUAL_MAPPING (wrong code fetched, but pattern clear)
- read-gis-data: YES with GeoJSON fixture

## 18. Blockers?
GIS fixture data files needed. convert-gis-data fetched wrong file.

## 19. Registry Strategy?
1 NEEDS_MANUAL_MAPPING; 1 READY_FOR_TRANSFORMATION with fixture.

## 20. First Transformation Candidates?
1. read-gis-data (simpler)

## Implementation Model
`LOAD_SAVE_OPTIONS` for convert-gis-data (VectorLayer.Convert).
`DOCUMENT_OBJECT_MODEL_WORKFLOW` for read-gis-data.
