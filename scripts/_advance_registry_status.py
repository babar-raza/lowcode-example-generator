"""
Lane F: Advance registry_status to TRANSFORMED_TO_EXAMPLE_DRYRUN for Wave A packages.
Adds dryrun_package_path and dryrun_validation_status fields.
Preserves YAML formatting via targeted text replacement.
"""
import re
import sys
from pathlib import Path

REGISTRY_DIR = Path(__file__).parents[1] / "pipeline" / "plugin-code-registry" / "family"

# Wave A packages validated at 12/12 PASS
WAVE_A = {
    "barcode": ["generate-qr-code", "scan-barcode"],
    "svg": ["svg-to-pdf-converter"],
    "tex": ["latex-figure-renderer"],
    "zip": ["create-archive", "compress-folder"],
    "imaging": ["resize-image", "crop-image", "filter-image", "merge-images", "watermark-image", "rotate-image"],
}

DRYRUN_BASE = "reports/lowcode-plugin-example-factory-wave-20260605/dryrun/examples"
SPRINT = "lowcode-plugin-example-factory-wave-20260605"


def advance_entry(yaml_text: str, slug: str, family: str) -> str:
    """Find the plugin block for slug and advance its status."""
    dryrun_path = f"{DRYRUN_BASE}/{family}/{slug}"

    # Find the slug marker
    slug_pattern = rf'(  - plugin_slug: {re.escape(slug)}\n)'
    slug_match = re.search(slug_pattern, yaml_text)
    if not slug_match:
        print(f"  WARN: slug '{slug}' not found in YAML")
        return yaml_text

    # Find the registry_status line after the slug (within next 100 lines)
    slug_pos = slug_match.end()
    # Look for registry_status in the next chunk (up to 3000 chars)
    chunk = yaml_text[slug_pos:slug_pos + 3000]

    # Replace registry_status
    new_chunk = re.sub(
        r'(    registry_status: )READY_FOR_TRANSFORMATION',
        r'\1TRANSFORMED_TO_EXAMPLE_DRYRUN',
        chunk,
        count=1
    )

    if new_chunk == chunk:
        print(f"  WARN: registry_status not replaced for '{slug}'")
        return yaml_text

    # Also replace next_action
    new_chunk = re.sub(
        r'(    next_action: )"Transform to dry-run example package[^"]*"',
        r'\1"Example package validated DRYRUN_PASS; advance to PUBLICATION_CANDIDATE_LOCAL"',
        new_chunk,
        count=1
    )

    # Add dryrun fields after the registry_status line
    new_chunk = re.sub(
        r'(    registry_status: TRANSFORMED_TO_EXAMPLE_DRYRUN\n)',
        (
            r'\1'
            f'    dryrun_package_path: "{dryrun_path}"\n'
            f'    dryrun_validation_status: DRYRUN_PASS\n'
            f'    dryrun_validated_at: "2026-06-05"\n'
        ),
        new_chunk,
        count=1
    )

    return yaml_text[:slug_pos] + new_chunk


def process_family(family: str, slugs: list) -> None:
    yaml_path = REGISTRY_DIR / f"{family}.yaml"
    if not yaml_path.exists():
        print(f"SKIP: {yaml_path} not found")
        return

    text = yaml_path.read_text(encoding="utf-8")
    original = text

    for slug in slugs:
        print(f"  Advancing: {family}/{slug}")
        text = advance_entry(text, slug, family)

    if text != original:
        yaml_path.write_text(text, encoding="utf-8")
        print(f"  Saved: {yaml_path}")
    else:
        print(f"  No changes needed for {family}")


def main():
    print(f"Lane F: Advancing {sum(len(v) for v in WAVE_A.values())} entries to TRANSFORMED_TO_EXAMPLE_DRYRUN")
    for family, slugs in WAVE_A.items():
        print(f"\n{family}:")
        process_family(family, slugs)

    print("\nDone.")


if __name__ == "__main__":
    main()
