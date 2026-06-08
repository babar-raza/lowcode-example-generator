# Blocked Family Reassessment
**Sprint**: lowcode-plugin-example-factory-parallel-wave-20260605
**Date**: 2026-06-05

## Summary

7 previously "blocked" families reassessed. None should be classified as DEFER_INDEFINITELY without specific evidence. Classifications updated below.

## Family-by-Family Analysis

### omr — PLUGIN_PAGE_BLOCKED_RETRY_LATER
- 2 plugins: recognize-omr, generate-omr-template
- Both NEEDS_MANUAL_MAPPING
- Aspose.OMR canonical pages exist but require specific OMR template files as fixtures
- Cannot generate OMR fixture programmatically
- Classification: **PLUGIN_PAGE_BLOCKED_RETRY_LATER** — retry when fixture generation tooling is available
- Next action: Create OMR template fixture generator (template is XML/JSON-based, feasible)

### gis — MANUAL_MAPPING_REQUIRED
- 2 plugins: convert-gis-data (NEEDS_MANUAL_MAPPING), read-gis-data (CODE_HARVESTED)
- Aspose.GIS processes geospatial data; requires .shp or GeoJSON fixture
- GeoJSON can be created programmatically (small inline string)
- Classification: **MANUAL_MAPPING_REQUIRED** for convert-gis-data; read-gis-data → **READY_FOR_REGISTRY_ENTRY** with GeoJSON fixture
- Next action: Create GeoJSON fixture inline; attempt read-gis-data dry-run package

### note — READY_FOR_REGISTRY_ENTRY
- 3 plugins: convert-one-to-pdf, convert-one-to-word, convert-one-to-image (all CODE_HARVESTED)
- Aspose.Note (.one files); requires .one fixture
- OneNote .one files cannot be created programmatically without Aspose.Note itself
- But: Aspose.Note can create a Document() programmatically and save → convert
- Classification: **READY_FOR_REGISTRY_ENTRY** — all 3 can use programmatic Document fixture
- Next action: Add canonical URL lookup; advance to READY_FOR_TRANSFORMATION

### drawing — READY_FOR_REGISTRY_ENTRY
- 2 plugins: convert-drawing (CODE_HARVESTED), create-drawing (CODE_HARVESTED)
- Aspose.Drawing (System.Drawing replacement); pure programmatic — no fixture needed
- Can create Graphics objects in code
- Classification: **READY_FOR_REGISTRY_ENTRY** — programmatic fixture, no file input
- Next action: Add canonical URLs, advance to READY_FOR_TRANSFORMATION, add to next wave

### font — MANUAL_MAPPING_REQUIRED (partial)
- convert-font: NEEDS_MANUAL_MAPPING — font conversion requires .ttf/.otf fixture
- render-text-with-font: CODE_HARVESTED — may work with system fonts
- Classification: convert-font → **MANUAL_MAPPING_REQUIRED**; render-text-with-font → **SOURCE_REPO_ONLY_CANDIDATE**
- Next action: Determine if system fonts are available; attempt render-text-with-font

### finance — SOURCE_REPO_ONLY_CANDIDATE
- convert-xbrl (CODE_HARVESTED): XBRL is structured XML; can create inline fixture
- parse-xbrl (NEEDS_MANUAL_MAPPING): XBRL parsing similarly feasible
- Classification: Both → **SOURCE_REPO_ONLY_CANDIDATE** with inline XML fixture
- Next action: Verify canonical pages; create XBRL XML fixture inline

### threed — PLUGIN_PAGE_BLOCKED_RETRY_LATER
- 2 plugins: convert-3d-model, compress-3d-scene (both NEEDS_MANUAL_MAPPING)
- Aspose.3D requires .fbx/.obj/.glb fixtures — cannot generate programmatically
- Classification: **PLUGIN_PAGE_BLOCKED_RETRY_LATER** — retry when 3D fixture generation is feasible
- Note: .obj format is text-based and CAN be generated inline (simple cube definition)
- Next action: Attempt .obj inline fixture for convert-3d-model

## Recommendations for Next Wave

Priority additions from this reassessment:
1. **drawing/convert-drawing** — fully programmatic, no fixture
2. **drawing/create-drawing** — fully programmatic, no fixture
3. **note/convert-one-to-pdf** — programmatic Document()
4. **gis/read-gis-data** — GeoJSON inline fixture
5. **threed/convert-3d-model** — inline .obj fixture (cube)

These 5 could form Wave 5 candidates.
