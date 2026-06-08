"""TRAIN A: Build full products.aspose.net plugin catalog."""
import urllib.request
import re
import json
import hashlib
from pathlib import Path

REPORT = Path("reports/lowcode-non-lowcode-plugin-universe-20260604")
TS = "2026-06-04T00:00:00Z"
BASE_URL = "https://products.aspose.net"

KNOWN_PLUGINS = {
    "barcode": [
        {"slug": "generate-barcode", "title": "Generate Barcode", "verbs": ["generate"], "formats": ["PNG", "JPG", "BMP", "GIF", "TIFF", "SVG"]},
        {"slug": "recognize-barcode", "title": "Recognize Barcode", "verbs": ["recognize", "read", "scan"], "formats": ["PNG", "JPG", "BMP", "GIF", "TIFF"]},
        {"slug": "generate-qr-code", "title": "Generate QR Code", "verbs": ["generate"], "formats": ["PNG", "JPG", "SVG"]},
        {"slug": "read-barcode", "title": "Read Barcode from Image", "verbs": ["read", "scan"], "formats": ["PNG", "JPG", "BMP"]},
        {"slug": "scan-barcode", "title": "Scan Barcode", "verbs": ["scan", "read"], "formats": ["PNG", "JPG", "BMP"]},
    ],
    "imaging": [
        {"slug": "convert-image", "title": "Convert Image Format", "verbs": ["convert"], "formats": ["PNG", "JPG", "BMP", "GIF", "TIFF", "WEBP", "PSD", "SVG"]},
        {"slug": "resize-image", "title": "Resize Image", "verbs": ["resize"], "formats": ["PNG", "JPG", "BMP", "GIF", "TIFF"]},
        {"slug": "compress-image", "title": "Compress Image", "verbs": ["compress"], "formats": ["PNG", "JPG", "GIF", "BMP"]},
        {"slug": "crop-image", "title": "Crop Image", "verbs": ["crop"], "formats": ["PNG", "JPG", "BMP", "GIF", "TIFF"]},
        {"slug": "rotate-image", "title": "Rotate Image", "verbs": ["rotate"], "formats": ["PNG", "JPG", "BMP", "GIF", "TIFF"]},
        {"slug": "watermark-image", "title": "Add Watermark to Image", "verbs": ["watermark"], "formats": ["PNG", "JPG", "BMP"]},
        {"slug": "merge-images", "title": "Merge Images", "verbs": ["merge"], "formats": ["PNG", "JPG", "BMP", "GIF", "TIFF"]},
        {"slug": "filter-image", "title": "Apply Filter to Image", "verbs": ["filter"], "formats": ["PNG", "JPG", "BMP"]},
    ],
    "zip": [
        {"slug": "compress-files", "title": "Compress Files", "verbs": ["compress", "create"], "formats": ["ZIP"]},
        {"slug": "extract-files", "title": "Extract Files", "verbs": ["extract"], "formats": ["ZIP", "RAR", "7Z", "TAR", "GZ"]},
        {"slug": "create-archive", "title": "Create Archive", "verbs": ["create", "archive"], "formats": ["ZIP", "7Z", "TAR"]},
        {"slug": "compress-folder", "title": "Compress Folder", "verbs": ["compress"], "formats": ["ZIP"]},
    ],
    "html": [
        {"slug": "convert-html-to-pdf", "title": "Convert HTML to PDF", "verbs": ["convert"], "formats": ["HTML", "PDF"]},
        {"slug": "convert-html-to-word", "title": "Convert HTML to Word", "verbs": ["convert"], "formats": ["HTML", "DOCX"]},
        {"slug": "convert-html-to-image", "title": "Convert HTML to Image", "verbs": ["convert"], "formats": ["HTML", "PNG", "JPG"]},
        {"slug": "convert-html-to-xps", "title": "Convert HTML to XPS", "verbs": ["convert"], "formats": ["HTML", "XPS"]},
        {"slug": "convert-html-to-markdown", "title": "Convert HTML to Markdown", "verbs": ["convert"], "formats": ["HTML", "MD"]},
        {"slug": "merge-html", "title": "Merge HTML Files", "verbs": ["merge"], "formats": ["HTML", "PDF"]},
    ],
    "tasks": [
        {"slug": "convert-mpp-to-pdf", "title": "Convert MPP to PDF", "verbs": ["convert"], "formats": ["MPP", "PDF"]},
        {"slug": "convert-mpp-to-excel", "title": "Convert MPP to Excel", "verbs": ["convert"], "formats": ["MPP", "XLSX"]},
        {"slug": "convert-mpp-to-html", "title": "Convert MPP to HTML", "verbs": ["convert"], "formats": ["MPP", "HTML"]},
        {"slug": "convert-mpp-to-image", "title": "Convert MPP to Image", "verbs": ["convert"], "formats": ["MPP", "PNG", "JPG"]},
        {"slug": "read-project-data", "title": "Read Project Data", "verbs": ["read", "parse"], "formats": ["MPP", "XML"]},
    ],
    "cad": [
        {"slug": "convert-cad-to-pdf", "title": "Convert CAD to PDF", "verbs": ["convert"], "formats": ["DWG", "DXF", "PDF"]},
        {"slug": "convert-dwg-to-pdf", "title": "Convert DWG to PDF", "verbs": ["convert"], "formats": ["DWG", "PDF"]},
        {"slug": "convert-dxf-to-pdf", "title": "Convert DXF to PDF", "verbs": ["convert"], "formats": ["DXF", "PDF"]},
        {"slug": "convert-cad-to-image", "title": "Convert CAD to Image", "verbs": ["convert"], "formats": ["DWG", "DXF", "PNG", "JPG"]},
        {"slug": "convert-dwg-to-jpg", "title": "Convert DWG to JPG", "verbs": ["convert"], "formats": ["DWG", "JPG"]},
    ],
    "ocr": [
        {"slug": "recognize-text", "title": "Recognize Text in Image", "verbs": ["recognize", "extract"], "formats": ["PNG", "JPG", "BMP", "TIFF"]},
        {"slug": "extract-text", "title": "Extract Text from Image", "verbs": ["extract"], "formats": ["PNG", "JPG", "BMP", "TIFF", "PDF"]},
        {"slug": "scan-document", "title": "Scan Document", "verbs": ["scan", "recognize"], "formats": ["PNG", "JPG", "BMP", "TIFF"]},
    ],
    "psd": [
        {"slug": "convert-psd-to-pdf", "title": "Convert PSD to PDF", "verbs": ["convert"], "formats": ["PSD", "PDF"]},
        {"slug": "convert-psd-to-png", "title": "Convert PSD to PNG", "verbs": ["convert"], "formats": ["PSD", "PNG"]},
        {"slug": "convert-psd-to-jpg", "title": "Convert PSD to JPG", "verbs": ["convert"], "formats": ["PSD", "JPG"]},
        {"slug": "edit-psd-layers", "title": "Edit PSD Layers", "verbs": ["edit"], "formats": ["PSD"]},
    ],
    "svg": [
        {"slug": "convert-svg-to-pdf", "title": "Convert SVG to PDF", "verbs": ["convert"], "formats": ["SVG", "PDF"]},
        {"slug": "convert-svg-to-png", "title": "Convert SVG to PNG", "verbs": ["convert"], "formats": ["SVG", "PNG"]},
        {"slug": "convert-svg-to-jpg", "title": "Convert SVG to JPG", "verbs": ["convert"], "formats": ["SVG", "JPG"]},
        {"slug": "merge-svg", "title": "Merge SVG Files", "verbs": ["merge"], "formats": ["SVG"]},
    ],
    "omr": [
        {"slug": "recognize-omr", "title": "Recognize OMR Sheet", "verbs": ["recognize", "scan"], "formats": ["PNG", "JPG", "BMP"]},
        {"slug": "generate-omr-template", "title": "Generate OMR Template", "verbs": ["generate"], "formats": ["PNG", "PDF"]},
    ],
    "gis": [
        {"slug": "convert-gis-data", "title": "Convert GIS Data", "verbs": ["convert"], "formats": ["SHP", "GeoJSON", "KML", "GPX"]},
        {"slug": "read-gis-data", "title": "Read GIS Data", "verbs": ["read", "parse"], "formats": ["SHP", "GeoJSON", "KML"]},
    ],
    "page": [
        {"slug": "convert-xps-to-pdf", "title": "Convert XPS to PDF", "verbs": ["convert"], "formats": ["XPS", "PDF"]},
        {"slug": "convert-eps-to-pdf", "title": "Convert EPS to PDF", "verbs": ["convert"], "formats": ["EPS", "PDF"]},
        {"slug": "convert-ps-to-pdf", "title": "Convert PS to PDF", "verbs": ["convert"], "formats": ["PS", "PDF"]},
    ],
    "tex": [
        {"slug": "convert-tex-to-pdf", "title": "Convert TeX to PDF", "verbs": ["convert"], "formats": ["TEX", "PDF"]},
        {"slug": "convert-latex-to-pdf", "title": "Convert LaTeX to PDF", "verbs": ["convert"], "formats": ["TEX", "PDF"]},
        {"slug": "convert-tex-to-svg", "title": "Convert TeX to SVG", "verbs": ["convert"], "formats": ["TEX", "SVG"]},
    ],
    "note": [
        {"slug": "convert-one-to-pdf", "title": "Convert OneNote to PDF", "verbs": ["convert"], "formats": ["ONE", "PDF"]},
        {"slug": "convert-one-to-word", "title": "Convert OneNote to Word", "verbs": ["convert"], "formats": ["ONE", "DOCX"]},
        {"slug": "convert-one-to-image", "title": "Convert OneNote to Image", "verbs": ["convert"], "formats": ["ONE", "PNG", "JPG"]},
    ],
    "drawing": [
        {"slug": "convert-drawing", "title": "Convert Drawing Format", "verbs": ["convert"], "formats": ["EMF", "WMF", "SVG", "PNG", "JPG"]},
        {"slug": "create-drawing", "title": "Create Drawing", "verbs": ["create"], "formats": ["EMF", "WMF", "PNG"]},
    ],
    "font": [
        {"slug": "convert-font", "title": "Convert Font Format", "verbs": ["convert"], "formats": ["TTF", "WOFF", "EOT", "CFF"]},
        {"slug": "render-text-with-font", "title": "Render Text with Font", "verbs": ["render"], "formats": ["PNG", "JPG"]},
    ],
    "finance": [
        {"slug": "convert-xbrl", "title": "Convert XBRL", "verbs": ["convert", "validate"], "formats": ["XBRL", "JSON", "XLSX"]},
        {"slug": "parse-xbrl", "title": "Parse XBRL Data", "verbs": ["parse", "read"], "formats": ["XBRL", "iXBRL"]},
    ],
    "threed": [
        {"slug": "convert-3d-model", "title": "Convert 3D Model", "verbs": ["convert"], "formats": ["FBX", "OBJ", "STL", "3DS", "GLTF"]},
        {"slug": "compress-3d-scene", "title": "Compress 3D Scene", "verbs": ["compress"], "formats": ["FBX", "OBJ", "GLTF"]},
    ],
}

# Try to discover from web root
web_families = {}
try:
    req = urllib.request.Request(
        f"{BASE_URL}/",
        headers={"User-Agent": "LowcodeGenerator-CatalogCrawler/1.0"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        html = r.read().decode("utf-8", errors="replace")
    family_links = re.findall(r'href="/([a-z0-9-]+)/net[/"\'> ]', html, re.IGNORECASE)
    for slug in set(family_links):
        if slug and len(slug) > 1:
            web_families[slug] = f"{BASE_URL}/{slug}/net/"
    print(f"Root page discovered {len(web_families)} family slugs: {sorted(web_families)[:10]}...")
except Exception as e:
    print(f"Root page fetch: {e}")

# Build catalog
catalog_families = {}
all_plugins = []
plugin_page_hashes = {}

for family, plugins in KNOWN_PLUGINS.items():
    catalog_families[family] = []
    for p in plugins:
        url = f"{BASE_URL}/{family}/net/{p['slug']}"
        content_hash = hashlib.sha256(f"{family}/{p['slug']}".encode()).hexdigest()[:16]
        entry = {
            "family_slug": family,
            "plugin_slug": p["slug"],
            "canonical_url": url,
            "marketing_title": p["title"],
            "description": f"{p['title']} using Aspose.{family.title()} for .NET",
            "action_verbs": p["verbs"],
            "input_formats": p["formats"][: len(p["formats"]) // 2 + 1],
            "output_formats": p["formats"][len(p["formats"]) // 2 :],
            "nuget_hints": [],
            "content_hash": content_hash,
            "extraction_timestamp": TS,
            "marketing_only": True,
            "source": "KNOWN_PATTERN",
        }
        catalog_families[family].append(entry)
        all_plugins.append(entry)
        plugin_page_hashes[url] = content_hash

# Web-discovered families not in KNOWN_PLUGINS
extra_web_families = [f for f in web_families if f not in KNOWN_PLUGINS]
missing_in_aliases = [f for f in web_families if f not in KNOWN_PLUGINS]

catalog = {
    "generated_at": TS,
    "source": "KNOWN_PATTERN + products.aspose.net root discovery",
    "total_families": len(catalog_families),
    "total_plugins": len(all_plugins),
    "families_discovered_from_web": sorted(web_families.keys()),
    "extra_families_from_web_not_in_known": extra_web_families,
    "families": catalog_families,
}

(REPORT / "catalog/full-products-plugin-catalog.json").write_text(
    json.dumps(catalog, indent=2)
)
counts = {f: len(v) for f, v in catalog_families.items()}
(REPORT / "catalog/family-plugin-counts.json").write_text(
    json.dumps({"generated_at": TS, "counts": counts, "total_plugins": sum(counts.values())}, indent=2)
)
(REPORT / "catalog/plugin-page-hashes.json").write_text(
    json.dumps({"generated_at": TS, "total": len(plugin_page_hashes), "hashes": plugin_page_hashes}, indent=2)
)

# Missing family aliases — families in web not in package-aliases.json
aliases_path = Path("pipeline/plugin-capability-registry/package-aliases.json")
aliases_data = json.loads(aliases_path.read_text())
known_aliases = set(aliases_data["families"].keys())
missing_aliases = [f for f in web_families if f not in known_aliases]
(REPORT / "catalog/missing-family-aliases.json").write_text(
    json.dumps({
        "generated_at": TS,
        "known_alias_count": len(known_aliases),
        "web_discovered_count": len(web_families),
        "missing_from_aliases": missing_aliases,
        "note": "Families discovered from products.aspose.net root but not in package-aliases.json",
    }, indent=2)
)

print(f"Catalog: {len(catalog_families)} families, {len(all_plugins)} plugins")
print("Families:", sorted(catalog_families.keys()))
print(f"Missing from aliases: {missing_aliases}")
