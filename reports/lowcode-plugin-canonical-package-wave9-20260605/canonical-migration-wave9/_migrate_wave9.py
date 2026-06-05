"""
Lane D — Canonical Migration Wave 9
Sprint: lowcode-plugin-canonical-package-wave9-20260605

Migrates 12 SLUG_ALIAS_REQUIRED entries to CANONICAL_IDENTITY_VERIFIED + canonical-primary.
All entries have confirmed canonical_url and canonical_plugin_slug.
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

WAVE9_MIGRATION_MAP = [
    # Imaging (6)
    {
        "family": "imaging",
        "legacy_slug": "compress-image",
        "canonical_slug": "image-compressor",
        "display_name": "Image Compressor for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-compressor/",
    },
    {
        "family": "imaging",
        "legacy_slug": "crop-image",
        "canonical_slug": "image-cropper",
        "display_name": "Image Cropper for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-cropper/",
    },
    {
        "family": "imaging",
        "legacy_slug": "filter-image",
        "canonical_slug": "image-filters",
        "display_name": "Image Filters for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-filters/",
    },
    {
        "family": "imaging",
        "legacy_slug": "merge-images",
        "canonical_slug": "image-merger",
        "display_name": "Image Merger for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-merger/",
    },
    {
        "family": "imaging",
        "legacy_slug": "watermark-image",
        "canonical_slug": "add-watermark",
        "display_name": "Add Watermark to Image for .NET",
        "canonical_url": "https://products.aspose.net/imaging/add-watermark/",
    },
    {
        "family": "imaging",
        "legacy_slug": "rotate-image",
        "canonical_slug": "image-rotator",
        "display_name": "Image Rotator for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-rotator/",
    },
    # Tasks (2)
    {
        "family": "tasks",
        "legacy_slug": "convert-mpp-to-pdf",
        "canonical_slug": "project-to-pdf-converter",
        "display_name": "Project to PDF Converter for .NET",
        "canonical_url": "https://products.aspose.net/tasks/project-to-pdf-converter/",
    },
    {
        "family": "tasks",
        "legacy_slug": "convert-mpp-to-excel",
        "canonical_slug": "mpp-to-excel",
        "display_name": "MPP to Excel Converter for .NET",
        "canonical_url": "https://products.aspose.net/tasks/mpp-to-excel/",
    },
    # HTML (2)
    {
        "family": "html",
        "legacy_slug": "convert-html-to-word",
        "canonical_slug": "html-to-docx-converter",
        "display_name": "HTML to DOCX Converter for .NET",
        "canonical_url": "https://products.aspose.net/html/html-to-docx-converter/",
    },
    {
        "family": "html",
        "legacy_slug": "convert-html-to-image",
        "canonical_slug": "html-to-image-converter",
        "display_name": "HTML to Image Converter for .NET",
        "canonical_url": "https://products.aspose.net/html/html-to-image-converter/",
    },
    # Note (2)
    {
        "family": "note",
        "legacy_slug": "convert-one-to-word",
        "canonical_slug": "convert-onenote-to-word",
        "display_name": "OneNote to Word Converter for .NET",
        "canonical_url": "https://products.aspose.net/note/convert-onenote-to-word/",
    },
    {
        "family": "note",
        "legacy_slug": "convert-one-to-image",
        "canonical_slug": "convert-onenote-to-image",
        "display_name": "OneNote to Image Converter for .NET",
        "canonical_url": "https://products.aspose.net/note/convert-onenote-to-image/",
    },
]

changes_log = []
before_by_family = {}
after_by_family = {}


def process_family(family, entries):
    fpath = YAML_DIR / f"{family}.yaml"
    if not fpath.exists():
        return
    data = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    before_slugs = [p.get("plugin_slug") for p in data.get("plugins", [])]
    before_by_family[family] = before_slugs

    entry_map = {e["legacy_slug"]: e for e in entries}

    for p in data.get("plugins", []):
        slug = p.get("plugin_slug", "")
        if slug not in entry_map:
            continue
        entry = entry_map[slug]
        canon = entry["canonical_slug"]

        # Set canonical-primary fields
        p["legacy_aliases"] = p.get("legacy_aliases", [])
        if slug not in p["legacy_aliases"]:
            p["legacy_aliases"].append(slug)
        p["plugin_slug"] = canon
        p["canonical_plugin_slug"] = canon
        p["display_plugin_name"] = entry["display_name"]
        p["canonical_url"] = entry["canonical_url"]
        p["identity_status"] = "CANONICAL_IDENTITY_VERIFIED"
        p["migration_status"] = "CANONICAL_PRIMARY_MIGRATED"
        p["migrated_from"] = slug
        p["dryrun_package_path"] = (
            f"reports/{SPRINT}/dryrun/examples/{family}/{canon}"
        )

        if "history" not in p:
            p["history"] = []
        p["history"].append({
            "date": TODAY,
            "status": "CANONICAL_PRIMARY_MIGRATED",
            "analyst_notes": (
                f"Sprint {SPRINT}. Wave 9 canonical migration: "
                f"'{slug}' -> '{canon}'."
            ),
        })
        changes_log.append(f"{family}: {slug} -> {canon}")

    after_slugs = [p.get("plugin_slug") for p in data.get("plugins", [])]
    after_by_family[family] = after_slugs
    fpath.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


# Group entries by family
from collections import defaultdict
by_family = defaultdict(list)
for entry in WAVE9_MIGRATION_MAP:
    by_family[entry["family"]].append(entry)

for family, entries in sorted(by_family.items()):
    process_family(family, entries)

print(f"Changes ({len(changes_log)}):")
for c in changes_log:
    print(f"  {c}")

(REPORT / "migration-before-after.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "total_migrations": len(changes_log),
    "changes": changes_log,
    "before_by_family": before_by_family,
    "after_by_family": after_by_family,
    "verdict": "WAVE9_MIGRATION_DONE",
}, indent=2))

print("\nWritten: migration-before-after.json")
print(f"Verdict: WAVE9_MIGRATION_DONE")
