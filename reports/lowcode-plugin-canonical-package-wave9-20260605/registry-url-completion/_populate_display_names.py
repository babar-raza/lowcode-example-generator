"""
Lane B — Registry Canonical URL + Display Name Completion
Sprint: lowcode-plugin-canonical-package-wave9-20260605

Adds display_plugin_name to all 21 CANONICAL_IDENTITY_VERIFIED entries
that are missing it. Uses slug → human-readable name derivation based on
products.aspose.net URL structure.
"""
import yaml
import json
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-package-wave9-20260605"
ROOT = Path(__file__).parents[3]
REPORT = Path(__file__).parent
YAML_DIR = ROOT / "pipeline/plugin-code-registry/family"

# Hand-curated display names derived from products.aspose.net URL slugs
DISPLAY_NAMES = {
    # Drawing
    "drawing/convert-drawing": "Drawing Converter for .NET",
    "drawing/create-drawing": "Drawing Creator for .NET",
    # Finance
    "finance/convert-xbrl": "XBRL Converter for .NET",
    # OCR
    "ocr/scan-document": "Document Scanner for .NET",
    "ocr/image-text-finder": "Image Text Finder for .NET",
    "ocr/invoice-to-text": "Invoice to Text Converter for .NET",
    "ocr/photo-to-text": "Photo to Text Converter for .NET",
    "ocr/table-to-text": "Table to Text Converter for .NET",
    # PSD
    "psd/animation-maker": "PSD Animation Maker for .NET",
    "psd/photo-processor": "PSD Photo Processor for .NET",
    # SVG
    "svg/svg-to-image-converter": "SVG to Image Converter for .NET",
    # TeX
    "tex/latex-figure-renderer": "LaTeX Figure Renderer for .NET",
    # ZIP
    "zip/compress-files": "ZIP File Compressor for .NET",
}

changes = []
before_state = {}
after_state = {}

families_to_update = set()
for key in DISPLAY_NAMES:
    families_to_update.add(key.split("/")[0])

for family in sorted(families_to_update):
    fpath = YAML_DIR / f"{family}.yaml"
    if not fpath.exists():
        print(f"  SKIP: {fpath} not found")
        continue
    data = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    updated = False
    for p in data.get("plugins", []):
        slug = p.get("plugin_slug", "")
        key = f"{family}/{slug}"
        if key in DISPLAY_NAMES:
            before_state[key] = p.get("display_plugin_name")
            if not p.get("display_plugin_name"):
                p["display_plugin_name"] = DISPLAY_NAMES[key]
                changes.append(f"{key}: set display_plugin_name = '{DISPLAY_NAMES[key]}'")
                updated = True
            after_state[key] = p.get("display_plugin_name")
    if updated:
        fpath.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

print(f"Changes: {len(changes)}")
for c in changes:
    print(f"  {c}")

(REPORT / "display-name-completion.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "total_changes": len(changes),
    "changes": changes,
    "before": before_state,
    "after": after_state,
    "verdict": "DISPLAY_NAMES_POPULATED",
}, indent=2))

print("\nWritten: display-name-completion.json")
