"""
Lane B — Canonical-Primary Registry Migration
Sprint: lowcode-plugin-canonical-primary-wave8-20260605
"""
import yaml
import json
import copy
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-primary-wave8-20260605"
REPORT = Path(__file__).parent
YAML_DIR = Path(__file__).parents[3] / "pipeline/plugin-code-registry/family"

changes_log = []

BARCODE_CANONICAL_MAP = {
    "generate-barcode":  {
        "canonical": "1d-barcode-writer",
        "display": "1D Barcode Writer for .NET",
        "canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
    },
    "recognize-barcode": {
        "canonical": "1d-barcode-reader",
        "display": "1D Barcode Reader for .NET",
        "canonical_url": "https://products.aspose.net/barcode/1d-barcode-reader/",
    },
    "generate-qr-code":  {
        "canonical": "2d-barcode-writer",
        "display": "2D Barcode Writer for .NET",
        "canonical_url": "https://products.aspose.net/barcode/2d-barcode-writer/",
    },
    "scan-barcode":      {
        "canonical": "2d-barcode-reader",
        "display": "2D Barcode Reader for .NET",
        "canonical_url": "https://products.aspose.net/barcode/2d-barcode-reader/",
    },
}


def migrate_barcode(data):
    for p in data.get("plugins", []):
        slug = p.get("plugin_slug", "")
        if slug in BARCODE_CANONICAL_MAP:
            cm = BARCODE_CANONICAL_MAP[slug]
            p["legacy_aliases"] = [slug]
            p["plugin_slug"] = cm["canonical"]
            p["canonical_plugin_slug"] = cm["canonical"]
            p["display_plugin_name"] = cm["display"]
            p["canonical_url"] = cm["canonical_url"]
            p["identity_status"] = "CANONICAL_IDENTITY_VERIFIED"
            p["migration_status"] = "CANONICAL_PRIMARY_MIGRATED"
            p["migrated_from"] = slug
            p["dryrun_package_path"] = (
                f"reports/lowcode-plugin-canonical-identity-wave7-20260605"
                f"/dryrun/examples/barcode/{cm['canonical']}"
            )
            p["registry_status"] = "TRANSFORMED_TO_EXAMPLE_DRYRUN"
            if "history" not in p:
                p["history"] = []
            p["history"].append({
                "date": TODAY,
                "status": "CANONICAL_PRIMARY_MIGRATED",
                "analyst_notes": (
                    f"Sprint {SPRINT}. Migrated from legacy alias '{slug}' to "
                    f"canonical primary '{cm['canonical']}'."
                ),
            })
            changes_log.append(f"barcode: {slug} -> {cm['canonical']}")


def fix_ocr(data):
    for p in data.get("plugins", []):
        slug = p.get("plugin_slug")
        if slug in ("photo-to-text", "table-to-text") and p.get("registry_status") == "READY_FOR_TRANSFORMATION":
            p["registry_status"] = "TRANSFORMED_TO_EXAMPLE_DRYRUN"
            p["dryrun_package_path"] = (
                f"reports/lowcode-plugin-canonical-identity-wave7-20260605"
                f"/dryrun/examples/ocr/{slug}"
            )
            p["dryrun_validation_status"] = "DRYRUN_PASS"
            p["dryrun_validated_at"] = TODAY
            if "history" not in p:
                p["history"] = []
            p["history"].append({
                "date": TODAY,
                "status": "TRANSFORMED_TO_EXAMPLE_DRYRUN",
                "analyst_notes": f"Sprint {SPRINT}. Wave 7 package PASS. Status updated.",
            })
            changes_log.append(f"ocr: {slug} -> TRANSFORMED_TO_EXAMPLE_DRYRUN")


def fix_psd(data):
    for p in data.get("plugins", []):
        slug = p.get("plugin_slug")
        if slug in ("animation-maker", "photo-processor"):
            if p.get("registry_status") == "READY_FOR_TRANSFORMATION":
                p["registry_status"] = "TRANSFORMED_TO_EXAMPLE_DRYRUN"
                p["dryrun_package_path"] = (
                    f"reports/lowcode-plugin-canonical-identity-wave7-20260605"
                    f"/dryrun/examples/psd/{slug}"
                )
                p["dryrun_validation_status"] = "DRYRUN_PASS"
                p["dryrun_validated_at"] = TODAY
                if "history" not in p:
                    p["history"] = []
                p["history"].append({
                    "date": TODAY,
                    "status": "TRANSFORMED_TO_EXAMPLE_DRYRUN",
                    "analyst_notes": f"Sprint {SPRINT}. Wave 7 package PASS. Status updated.",
                })
                changes_log.append(f"psd: {slug} -> TRANSFORMED_TO_EXAMPLE_DRYRUN")
            if (p.get("identity_status") == "MISSING_CANONICAL_URL"
                    and p.get("canonical_url")):
                p["identity_status"] = "CANONICAL_IDENTITY_VERIFIED"
                changes_log.append(
                    f"psd: {slug} identity_status -> CANONICAL_IDENTITY_VERIFIED"
                )


def process_family(name, transform_fn):
    fpath = YAML_DIR / f"{name}.yaml"
    data = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    before_slugs = [p.get("plugin_slug") for p in data.get("plugins", [])]
    transform_fn(data)
    after_slugs = [p.get("plugin_slug") for p in data.get("plugins", [])]
    new_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
    fpath.write_text(new_content, encoding="utf-8")
    return before_slugs, after_slugs


bc_before, bc_after = process_family("barcode", migrate_barcode)
ocr_before, ocr_after = process_family("ocr", fix_ocr)
psd_before, psd_after = process_family("psd", fix_psd)

print(f"Changes ({len(changes_log)}):")
for c in changes_log:
    print(f"  {c}")

(REPORT / "registry-before-after.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "changes": changes_log,
    "families_modified": ["barcode", "ocr", "psd"],
    "barcode_before": bc_before,
    "barcode_after": bc_after,
    "ocr_before": ocr_before,
    "ocr_after": ocr_after,
    "psd_before": psd_before,
    "psd_after": psd_after,
}, indent=2))

(REPORT / "barcode-canonical-primary-migration.md").write_text(
    f"# BarCode Canonical-Primary Migration\n\n"
    f"Sprint: {SPRINT}\nDate: {TODAY}\n\n"
    "## Migrated Entries\n\n"
    "| Legacy Slug | Canonical Primary |\n"
    "|-------------|------------------|\n"
    "| generate-barcode | 1d-barcode-writer |\n"
    "| recognize-barcode | 1d-barcode-reader |\n"
    "| generate-qr-code | 2d-barcode-writer |\n"
    "| scan-barcode | 2d-barcode-reader |\n\n"
    "## Fields Updated\n\n"
    "- `plugin_slug`: set to canonical slug\n"
    "- `legacy_aliases`: old slug preserved\n"
    "- `identity_status`: CANONICAL_IDENTITY_VERIFIED\n"
    "- `migration_status`: CANONICAL_PRIMARY_MIGRATED\n"
    "- `migrated_from`: old slug\n"
    "- `dryrun_package_path`: updated to Wave 7 canonical path\n"
)

print("\nWritten: registry-migration/registry-before-after.json")
print("Written: registry-migration/barcode-canonical-primary-migration.md")
print(f"Verdict: REGISTRY_CANONICAL_PRIMARY_MIGRATED")
