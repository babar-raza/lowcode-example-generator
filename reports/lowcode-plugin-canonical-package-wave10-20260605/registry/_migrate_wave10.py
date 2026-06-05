"""
Lane B — Wave 10 Registry Migration
Sprint: lowcode-plugin-canonical-package-wave10-20260605

Migrates 10 SLUG_ALIAS_REQUIRED entries to CANONICAL_IDENTITY_VERIFIED.
Special cases:
- zip/create-archive + zip/compress-folder → both become legacy aliases of universal-compressor
- psd/psd-image-converter → already-exists animation-maker gets psd-image-converter as alias
"""
import yaml
import json
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-package-wave10-20260605"
ROOT = Path(__file__).parents[3]
REGISTRY_DIR = ROOT / "pipeline/plugin-code-registry/family"
REPORT = Path(__file__).parent

DISPLAY_NAMES = {
    "ocr/scanned-image-to-text": "Scanned Image to Text Converter for .NET",
    "ocr/scanned-pdf-to-text": "Scanned PDF to Text Converter for .NET",
    "page/xps-converter": "XPS Converter for .NET",
    "page/eps-to-pdf": "EPS to PDF Converter for .NET",
    "page/ps-converter": "PS Converter for .NET",
    "psd/psd-to-pdf": "PSD to PDF Converter for .NET",
    "tasks/mpp-to-html": "MPP to HTML Converter for .NET",
    "tasks/mpp-to-png": "MPP to PNG Converter for .NET",
    "zip/universal-extractor": "ZIP Universal Extractor for .NET",
    "zip/universal-compressor": "ZIP Universal Compressor for .NET",
}

# Migrations: (family, old_slug, new_slug, canonical_url, display_name, nuget_package)
MIGRATIONS = [
    ("ocr", "recognize-text", "scanned-image-to-text",
     "https://products.aspose.net/ocr/scanned-image-to-text/",
     "Scanned Image to Text Converter for .NET", "Aspose.OCR"),
    ("ocr", "extract-text", "scanned-pdf-to-text",
     "https://products.aspose.net/ocr/scanned-pdf-to-text/",
     "Scanned PDF to Text Converter for .NET", "Aspose.OCR"),
    ("page", "convert-xps-to-pdf", "xps-converter",
     "https://products.aspose.net/page/xps-converter/",
     "XPS Converter for .NET", "Aspose.Page"),
    ("page", "convert-eps-to-pdf", "eps-to-pdf",
     "https://products.aspose.net/page/eps-to-pdf/",
     "EPS to PDF Converter for .NET", "Aspose.Page"),
    ("page", "convert-ps-to-pdf", "ps-converter",
     "https://products.aspose.net/page/ps-converter/",
     "PS Converter for .NET", "Aspose.Page"),
    ("psd", "convert-psd-to-pdf", "psd-to-pdf",
     "https://products.aspose.net/psd/psd-to-pdf/",
     "PSD to PDF Converter for .NET", "Aspose.PSD"),
    ("tasks", "convert-mpp-to-html", "mpp-to-html",
     "https://products.aspose.net/tasks/mpp-to-html/",
     "MPP to HTML Converter for .NET", "Aspose.Tasks"),
    ("tasks", "convert-mpp-to-image", "mpp-to-png",
     "https://products.aspose.net/tasks/mpp-to-png/",
     "MPP to PNG Converter for .NET", "Aspose.Tasks"),
    ("zip", "extract-files", "universal-extractor",
     "https://products.aspose.net/zip/universal-extractor/",
     "ZIP Universal Extractor for .NET", "Aspose.ZIP"),
    # universal-compressor: merge create-archive + compress-folder
    ("zip", "create-archive", "universal-compressor",
     "https://products.aspose.net/zip/universal-compressor/",
     "ZIP Universal Compressor for .NET", "Aspose.ZIP"),
]

# Special: compress-folder is a second legacy alias of universal-compressor (handled after main loop)
EXTRA_ALIASES = {
    "zip/universal-compressor": ["compress-folder"],
    # psd/psd-image-converter should become a legacy alias of animation-maker (already CANONICAL_IDENTITY_VERIFIED)
    "psd/animation-maker": ["psd-image-converter"],
}

before_counts = {}
after_counts = {}
migration_log = []

for family_yaml in sorted(REGISTRY_DIR.glob("*.yaml")):
    content = yaml.safe_load(family_yaml.read_text(encoding="utf-8"))
    family = content.get("family", family_yaml.stem)
    plugins = content.get("plugins", [])
    before_counts[family] = sum(1 for p in plugins if p.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED")

    modified = False
    slugs_to_remove = set()

    for mig in MIGRATIONS:
        m_family, old_slug, new_slug, canonical_url, display_name, nuget_pkg = mig
        if m_family != family:
            continue

        # Find the old entry
        old_entry = next((p for p in plugins if p.get("plugin_slug") == old_slug), None)
        if old_entry is None:
            continue

        # Check if canonical slug already exists (e.g. universal-compressor already created by create-archive migration)
        existing_canonical = next((p for p in plugins if p.get("plugin_slug") == new_slug), None)

        if existing_canonical:
            # Just add old_slug as a legacy alias to existing canonical
            existing_aliases = existing_canonical.get("legacy_aliases", [])
            if old_slug not in existing_aliases:
                existing_aliases.append(old_slug)
                existing_canonical["legacy_aliases"] = existing_aliases
                migration_log.append(f"{family}/{old_slug} → added as legacy alias of {new_slug}")
            slugs_to_remove.add(old_slug)
            modified = True
        else:
            # Transform old entry into canonical entry
            old_aliases = old_entry.get("legacy_aliases", [])
            if old_slug not in old_aliases:
                old_aliases = [old_slug] + old_aliases

            new_entry = {
                "plugin_slug": new_slug,
                "canonical_plugin_slug": new_slug,
                "canonical_url": canonical_url,
                "display_plugin_name": display_name,
                "identity_status": "CANONICAL_IDENTITY_VERIFIED",
                "migration_status": "CANONICAL_PRIMARY_MIGRATED",
                "migrated_from": old_slug,
                "legacy_aliases": old_aliases,
                "sprint": SPRINT,
            }
            # Preserve nuget fields if present
            for k in ("nuget_package", "nuget_version", "class_name", "namespace"):
                if k in old_entry:
                    new_entry[k] = old_entry[k]

            # Replace old entry with new
            idx = next(i for i, p in enumerate(plugins) if p.get("plugin_slug") == old_slug)
            plugins[idx] = new_entry
            migration_log.append(f"{family}/{old_slug} → {new_slug} (CANONICAL_IDENTITY_VERIFIED)")
            modified = True

    # Remove entries that became aliases (slugs_to_remove)
    plugins = [p for p in plugins if p.get("plugin_slug") not in slugs_to_remove]
    content["plugins"] = plugins

    # Handle extra aliases
    for key, extra_aliases in EXTRA_ALIASES.items():
        key_family, key_slug = key.split("/")
        if key_family != family:
            continue
        canon = next((p for p in plugins if p.get("plugin_slug") == key_slug), None)
        if canon:
            existing = canon.get("legacy_aliases", [])
            for alias in extra_aliases:
                # Also remove standalone entry if it exists
                plugins = [p for p in plugins if p.get("plugin_slug") != alias]
                if alias not in existing:
                    existing.append(alias)
            canon["legacy_aliases"] = existing
            content["plugins"] = plugins
            for alias in extra_aliases:
                migration_log.append(f"{family}/{alias} → added as extra alias of {key_slug}")
            modified = True

    if modified:
        family_yaml.write_text(yaml.dump(content, default_flow_style=False, allow_unicode=True, sort_keys=False))
        after_counts[family] = sum(1 for p in content.get("plugins", []) if p.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED")

# Final counts
total_before = 0
total_after = 0
final_counts = {}
for family_yaml in sorted(REGISTRY_DIR.glob("*.yaml")):
    content = yaml.safe_load(family_yaml.read_text(encoding="utf-8"))
    family = content.get("family", family_yaml.stem)
    c = sum(1 for p in content.get("plugins", []) if p.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED")
    total_after += c
    final_counts[family] = c

import sys
out = sys.stdout
out.reconfigure(encoding='utf-8') if hasattr(out, 'reconfigure') else None
print(f"Migrations: {len(migration_log)}")
for m in migration_log:
    print(f"  {m}")
print(f"\nCanonical entries before: 33  after: {total_after}")

ledger = {
    "sprint": SPRINT,
    "date": TODAY,
    "canonical_primary_before": 33,
    "canonical_primary_after": total_after,
    "migrations_applied": len(migration_log),
    "migration_log": migration_log,
    "per_family": final_counts,
}
(REPORT / "wave10-migration-ledger.json").write_text(json.dumps(ledger, indent=2))
print("\nWritten: wave10-migration-ledger.json")
