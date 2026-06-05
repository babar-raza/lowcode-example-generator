# Factory Automation Design — Wave 6
**Sprint:** lowcode-plugin-example-factory-wave6-20260605
**Lane:** C — Factory Tooling
**Date:** 2026-06-05

## Objective
Automate the registry-to-dryrun generation pipeline with family template dispatch.
No external writes; all generation is local to the report directory.

## Template Dispatch Matrix

| Family | Implementation Model | Template Strategy | NuGet Package |
|--------|----------------------|-------------------|---------------|
| ocr | RECOGNITION_EXTRACTION_API | `ocr_template` — AsposeOcr + OcrInput + PNG fixture | Aspose.OCR |
| note | LOAD_SAVE_OPTIONS | `note_template` — Document + Page + RichText + SaveFormat | Aspose.Note |
| tasks | LOAD_SAVE_OPTIONS | `tasks_template` — Project + task creation + SaveOptions | Aspose.Tasks |
| html | STATIC_CONVERTER_CLASS | `html_template` — Converter.ConvertHTML + SaveOptions | Aspose.HTML |
| page | DEDICATED_PLUGIN_CLASS | `page_template` — PsDocument + SaveAsPdf | Aspose.Page |
| psd | LOAD_SAVE_OPTIONS | `psd_template` — PsdImage(w,h) + Clear + Save + reload | Aspose.PSD |
| svg | STATIC_CONVERTER_CLASS | `svg_template` — Converter.ConvertSVG or ImageVectorizer | Aspose.SVG |
| tex | STATIC_CONVERTER_CLASS | `tex_template` — FigureRendererPlugin or TeXJob | Aspose.TeX |
| drawing | LOAD_SAVE_OPTIONS | `drawing_template` — System.Drawing + Bitmap | System.Drawing |
| finance | LOAD_SAVE_OPTIONS | `finance_template` — XbrlDocument + Save(SaveOptions) | Aspose.Finance |
| gis | LOAD_SAVE_OPTIONS | `gis_template` — VectorLayer.Open + foreach feature | Aspose.GIS |
| zip | ARCHIVE_API | `zip_template` — Archive + CreateEntry + Save | Aspose.ZIP |

## Template Generation Plan

### Phase 1: Registry Scan
```python
def scan_registry_for_ready(registry_dir: Path) -> list[dict]:
    """Scan all family YAMLs for READY_FOR_TRANSFORMATION entries."""
    targets = []
    for yaml_file in registry_dir.glob("*.yaml"):
        family = yaml.safe_load(yaml_file.read_text())
        for plugin in family.get("plugins", []):
            if plugin["registry_status"] == "READY_FOR_TRANSFORMATION":
                targets.append({
                    "family": family["family"],
                    "slug": plugin["plugin_slug"],
                    "model": plugin.get("implementation_model", "UNKNOWN"),
                    "package_id": family["package_id"],
                })
    return targets
```

### Phase 2: Template Selection
```python
TEMPLATE_MAP = {
    "ocr": "ocr_template",
    "note": "note_template",
    "tasks": "tasks_template",
    "html": "html_template",
    "page": "page_template",
    "psd": "psd_template",
    "svg": "svg_template",
    "tex": "tex_template",
    # default: "generic_load_save_template"
}

def select_template(family: str, model: str) -> str:
    return TEMPLATE_MAP.get(family, "generic_load_save_template")
```

### Phase 3: Package Generation
```python
def generate_package(target: dict, output_root: Path) -> PackageGenerationResult:
    """Generate a dry-run package for a registry entry."""
    template = select_template(target["family"], target["model"])
    generator = TEMPLATE_REGISTRY[template]
    pkg_dir = output_root / target["family"] / target["slug"]
    return generator(pkg_dir, target)
```

### Phase 4: Build + Validate
```python
def build_validate_package(pkg_dir: Path, key: str) -> BuildResult:
    """Run dotnet restore/build/run and collect output-validation.json."""
    ...
```

## Anti-Overclaiming Design Principles

1. **No write outside report dir**: All generated packages live in `reports/<sprint>/dryrun/`
2. **Fixture provenance**: Every package must include `source-provenance.json` with `fixture_strategy`
3. **Output classification**: `output-validation.json` must classify outputs per `PASS/FAIL/ZERO_BYTE`
4. **No fabricated output**: If dotnet run fails, verdict is `FAIL`, not invented
5. **Registry atomic**: Registry YAML advances only after dryrun PASS confirmed

## Generation Preview

Running against current READY_FOR_TRANSFORMATION registry:

| Family/Slug | Template | Confidence | Wave Target |
|-------------|----------|------------|-------------|
| ocr/image-text-finder | ocr_template | HIGH | Wave 6 |
| ocr/invoice-to-text | ocr_template | HIGH | Wave 6 |
| ocr/photo-to-text | ocr_template | HIGH | Wave 7 |
| ocr/table-to-text | ocr_template | HIGH | Wave 7 |
| psd/psd-image-converter | psd_template | MEDIUM | Wave 6 |
| psd/animation-maker | psd_template | LOW | Wave 7 |
| psd/photo-processor | psd_template | MEDIUM | Wave 7 |
| svg/vectorizer | svg_template | MEDIUM | Wave 6 |

## Evidence
- Template dispatch matrix: above table
- No external write: all output is within `reports/<sprint>/dryrun/`
- Tests pass: see Lane J final test run
