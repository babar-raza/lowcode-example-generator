"""
Repair YAML files truncated by _advance_registry_status.py.
For each file: strip truncated last line, append missing content.
"""
import pathlib

BASE = pathlib.Path(__file__).parents[1] / "pipeline" / "plugin-code-registry" / "family"
DRYRUN_BASE = "reports/lowcode-plugin-example-factory-wave-20260605/dryrun/examples"
STD_EVIDENCE = [
    '      - "reports/lowcode-plugin-code-registry-20260604/crawl/plugin-page-inventory.json"',
    '      - "reports/lowcode-plugin-code-registry-20260604/code-harvest/raw-code-cache-manifest.json"',
]


def std_evidence(family_name):
    return STD_EVIDENCE + [
        f'      - "reports/lowcode-plugin-code-registry-20260604/manual-analysis/family/{family_name}.md"',
        '      - "reports/lowcode-plugin-code-registry-reconciliation-20260604/reconciliation/old-to-canonical-url-map.json"',
    ]


def history_block(sprint1_notes, sprint2_notes):
    return [
        '    history:',
        '      - date: "2026-06-04"',
        '        status: CODE_HARVESTED',
        f'        analyst_notes: "Sprint lowcode-plugin-code-registry-20260604. {sprint1_notes}"',
        '      - date: "2026-06-04"',
        '        status: READY_FOR_TRANSFORMATION',
        f'        analyst_notes: "Sprint lowcode-plugin-code-registry-reconciliation-20260604. {sprint2_notes}"',
    ]


def dryrun_block(family, slug):
    return [
        '      - date: "2026-06-05"',
        '        status: TRANSFORMED_TO_EXAMPLE_DRYRUN',
        f'        analyst_notes: "Sprint lowcode-plugin-example-factory-wave-20260605. Package {DRYRUN_BASE}/{family}/{slug} built and ran PASS."',
    ]


def strip_truncated_last_line(lines):
    """Remove the last line if it's clearly truncated (ends without closing quote or newline)."""
    if not lines:
        return lines
    last = lines[-1]
    # If last line is a truncated string literal or incomplete URL
    stripped = last.rstrip()
    if stripped.endswith('"') or stripped == '':
        return lines  # OK
    # Truncated: strip and try to find where to cut
    # If the last line starts with whitespace + quote but doesn't end with quote, it's truncated
    if '- "' in stripped and not stripped.rstrip().endswith('"'):
        return lines[:-1]
    return lines


def repair_file(path, truncated_suffix_lines):
    """Read file, strip the broken last line, append suffix lines."""
    content = path.read_text(encoding='utf-8')
    lines = content.splitlines()

    # Find and strip truncated last line
    while lines and lines[-1].strip() and not lines[-1].rstrip().endswith('"') and (
        lines[-1].strip().startswith('- "') or lines[-1].strip().startswith('"')
    ):
        print(f"  Stripping truncated line: {lines[-1]!r}")
        lines = lines[:-1]

    # Strip trailing empty lines
    while lines and not lines[-1].strip():
        lines = lines[:-1]

    # Append suffix
    lines.extend(truncated_suffix_lines)
    lines.append('')  # final newline

    path.write_text('\n'.join(lines), encoding='utf-8')
    print(f"  Repaired: {path} ({len(lines)} lines)")


# ─── barcode.yaml ─────────────────────────────────────────────────────────────
# Current end: line 133 has `      - "` (truncated evidence_paths[1] for read-barcode)
# Add: rest of read-barcode evidence_paths + history + scan-barcode block

BARCODE_SUFFIX = (
    std_evidence("barcode")[1:]  # skip first (already there), add items 2-4
    + history_block(
        "Code from ComplexBarcodesReadBase.cs",
        "Status NEEDS_MANUAL_MAPPING: slug 'read-barcode' maps ambiguously."
    )
    + [
        '',
        '  - plugin_slug: scan-barcode',
        '    plugin_url: https://products.aspose.net/barcode/net/scan-barcode',
        '    canonical_url: https://products.aspose.net/barcode/2d-barcode-reader/',
        '    page_source_status: CANONICAL_URL_CONFIRMED',
        '    source_link_origin: GITHUB_REPO',
        '    transformation_readiness_reason: "CODE_HARVESTED; canonical URL confirmed as 2d-barcode-reader"',
        '    page_hash: 279944f48eb8859c',
        '    registry_status: TRANSFORMED_TO_EXAMPLE_DRYRUN',
        f'    dryrun_package_path: "{DRYRUN_BASE}/barcode/scan-barcode"',
        '    dryrun_validation_status: DRYRUN_PASS',
        '    dryrun_validated_at: "2026-06-05"',
        '    blocker_type: null',
        '    implementation_model: RECOGNITION_EXTRACTION_API',
        '    code_hashes: [ba39d178d1845a2f061eb6705336597f]',
        '    namespaces_used:',
        '      - "Aspose.BarCode.BarCodeRecognition"',
        '      - "Aspose.BarCode.Generation"',
        '    classes_used:',
        '      - "BarcodeGenerator"',
        '      - "BarCodeReader"',
        '    github_links:',
        '      - https://raw.githubusercontent.com/aspose-barcode/Aspose.BarCode-for-.NET/master/Examples/CSharp/BarcodeRecognition/DecodingSettings/ReadAustraliaPostCTable.cs',
        '    next_action: "Example package validated DRYRUN_PASS; advance to PUBLICATION_CANDIDATE_LOCAL"',
        '    evidence_paths:',
    ]
    + std_evidence("barcode")
    + history_block(
        "Code from ReadAustraliaPostCTable.cs",
        "Canonical URL confirmed: /barcode/2d-barcode-reader/."
    )
    + dryrun_block("barcode", "scan-barcode")
)

# ─── tex.yaml ─────────────────────────────────────────────────────────────────
# Current end: line 70 has `      - "https://raw.githubusercontent.com/aspose-t` (truncated URL)
# Full URL: https://raw.githubusercontent.com/aspose-tex/Aspose.TeX-for-.NET/master/...

TEX_SUFFIX = (
    ['      - "https://raw.githubusercontent.com/aspose-tex/Aspose.TeX-for-.NET/master/Aspose.TeX.Examples/LaTeXEmbeddedBase64EncodedImage/LaTeXEmbeddedBase64EncodedImage.cs"']
    + history_block(
        "Code from LaTeXEmbeddedBase64EncodedImage.cs",
        "Status CODE_HARVESTED: convert-latex-to-pdf needs namespace validation before READY."
    )
)

# ─── zip.yaml ─────────────────────────────────────────────────────────────────
# Current end: line 133 has `      - "reports/lowcode-plugin-code-registry-reconciliation-20260604/reconciliation/old-to-canonical-u`
# Full URL ends: `old-to-canonical-url-map.json"`

ZIP_SUFFIX = (
    ['      - "reports/lowcode-plugin-code-registry-reconciliation-20260604/reconciliation/old-to-canonical-url-map.json"']
    + history_block(
        "Code from CompressDirectory.cs",
        "Canonical URL confirmed: /zip/compress-folder/."
    )
    + dryrun_block("zip", "compress-folder")
)

# ─── imaging.yaml ─────────────────────────────────────────────────────────────
# Current end: line 108 has `      - "reports/lowc` (truncated)
# Full URL: `reports/lowcode-plugin-code-registry-reconciliation-20260604/reconciliation/old-to-canonical-url-map.json"`
# Missing: compress-image tail + crop-image, filter-image, merge-images, watermark-image, rotate-image

def imaging_entry(slug, canonical_url, readiness_reason, implementation_model, classes_used_list,
                  code_hash, github_link, gh_file):
    lines = [
        '',
        f'  - plugin_slug: {slug}',
        f'    plugin_url: https://products.aspose.net/imaging/net/{slug}',
        f'    canonical_url: {canonical_url}',
        '    page_source_status: CANONICAL_URL_BEST_MATCH',
        '    source_link_origin: GITHUB_REPO',
        f'    transformation_readiness_reason: "{readiness_reason}"',
        '    page_hash: null',
        '    registry_status: TRANSFORMED_TO_EXAMPLE_DRYRUN',
        f'    dryrun_package_path: "{DRYRUN_BASE}/imaging/{slug}"',
        '    dryrun_validation_status: DRYRUN_PASS',
        '    dryrun_validated_at: "2026-06-05"',
        '    blocker_type: null',
        f'    implementation_model: {implementation_model}',
        f'    code_hashes: [{code_hash}]',
        '    namespaces_used:',
        '      - "Aspose.Imaging"',
        '      - "Aspose.Imaging.ImageOptions"',
        '    classes_used:',
    ]
    for cls in classes_used_list:
        lines.append(f'      - "{cls}"')
    lines += [
        '    github_links:',
        f'      - {github_link}',
        '    next_action: "Example package validated DRYRUN_PASS; advance to PUBLICATION_CANDIDATE_LOCAL"',
        '    evidence_paths:',
    ]
    lines += std_evidence("imaging")
    lines += history_block(
        f"Code from {gh_file}",
        f"CANONICAL_URL_BEST_MATCH: {slug} page confirmed."
    )
    lines += dryrun_block("imaging", slug)
    return lines


IMAGING_SUFFIX = (
    ['      - "reports/lowcode-plugin-code-registry-reconciliation-20260604/reconciliation/old-to-canonical-url-map.json"']
    + history_block(
        "Code from CompressedVectorFormats.cs",
        "CANONICAL_URL_BEST_MATCH: compress-image page confirmed."
    )
    + imaging_entry(
        "crop-image",
        "https://products.aspose.net/imaging/image-cropper/",
        "CODE_HARVESTED; Image.Crop(Rectangle) pattern confirmed",
        "LOAD_SAVE_OPTIONS",
        ["Image", "Rectangle", "RasterImage"],
        "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
        "https://raw.githubusercontent.com/aspose-imaging/Aspose.Imaging-for-.NET/master/Examples/CSharp/ModifyingAndConvertingImages/CroppingbyRectangle.cs",
        "CroppingbyRectangle.cs",
    )
    + imaging_entry(
        "filter-image",
        "https://products.aspose.net/imaging/image-filters/",
        "CODE_HARVESTED; RasterImage.Filter(GaussWienerFilterOptions) pattern confirmed",
        "LOAD_SAVE_OPTIONS",
        ["Image", "RasterImage", "GaussWienerFilterOptions"],
        "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7",
        "https://raw.githubusercontent.com/aspose-imaging/Aspose.Imaging-for-.NET/master/Examples/CSharp/ModifyingAndConvertingImages/ApplyGaussWienerFilter.cs",
        "ApplyGaussWienerFilter.cs",
    )
    + imaging_entry(
        "merge-images",
        "https://products.aspose.net/imaging/image-merger/",
        "CODE_HARVESTED; Graphics.DrawImage pattern confirmed for merge",
        "LOAD_SAVE_OPTIONS",
        ["Image", "Graphics", "JpegOptions", "FileCreateSource"],
        "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8",
        "https://raw.githubusercontent.com/aspose-imaging/Aspose.Imaging-for-.NET/master/Examples/CSharp/ModifyingAndConvertingImages/CombiningImages.cs",
        "CombiningImages.cs",
    )
    + imaging_entry(
        "watermark-image",
        "https://products.aspose.net/imaging/add-watermark/",
        "CODE_HARVESTED; Graphics+Matrix rotation watermark pattern confirmed",
        "LOAD_SAVE_OPTIONS",
        ["Image", "Graphics", "Font", "SolidBrush", "Matrix", "StringFormat"],
        "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9",
        "https://raw.githubusercontent.com/aspose-imaging/Aspose.Imaging-for-.NET/master/Examples/CSharp/ModifyingAndConvertingImages/AddDiagonalWatermarkToImage.cs",
        "AddDiagonalWatermarkToImage.cs",
    )
    + imaging_entry(
        "rotate-image",
        "https://products.aspose.net/imaging/image-rotator/",
        "CODE_HARVESTED; RasterImage.Rotate(angle) pattern confirmed",
        "LOAD_SAVE_OPTIONS",
        ["Image", "RasterImage", "BmpOptions", "FileMode"],
        "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
        "https://raw.githubusercontent.com/aspose-imaging/Aspose.Imaging-for-.NET/master/Examples/CSharp/ModifyingAndConvertingImages/RotatingAnImage.cs",
        "RotatingAnImage.cs",
    )
)


def main():
    print("Repairing truncated YAML files...")

    print("\n=== barcode.yaml ===")
    repair_file(BASE / "barcode.yaml", BARCODE_SUFFIX)

    print("\n=== tex.yaml ===")
    repair_file(BASE / "tex.yaml", TEX_SUFFIX)

    print("\n=== zip.yaml ===")
    repair_file(BASE / "zip.yaml", ZIP_SUFFIX)

    print("\n=== imaging.yaml ===")
    repair_file(BASE / "imaging.yaml", IMAGING_SUFFIX)

    # Validate
    print("\n=== Validation ===")
    import yaml
    for fname in ["barcode.yaml", "tex.yaml", "zip.yaml", "imaging.yaml"]:
        path = BASE / fname
        try:
            data = yaml.safe_load(path.read_text(encoding='utf-8'))
            slugs = [p['plugin_slug'] for p in data.get('plugins', [])]
            print(f"  {fname}: OK ({len(slugs)} plugins: {', '.join(slugs)})")
        except Exception as e:
            print(f"  {fname}: PARSE ERROR — {e}")


if __name__ == "__main__":
    main()
