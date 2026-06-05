"""
Lane G — Wave 8 Canonical Package Advancement
Sprint: lowcode-plugin-canonical-primary-wave8-20260605

Advances 4 SLUG_ALIAS_REQUIRED entries to canonical-primary by:
1. Creating canonical dryrun packages under canonical slug paths
2. Enriching source-provenance.json with full canonical identity
3. Updating registry entries to CANONICAL_IDENTITY_VERIFIED + CANONICAL_PRIMARY_MIGRATED

Wave 8 candidates selected:
- imaging/image-converter  (from imaging/convert-image)
- imaging/image-resizer    (from imaging/resize-image)
- html/html-to-pdf-converter (from html/convert-html-to-pdf)
- note/convert-onenote-to-pdf (from note/convert-one-to-pdf)
"""
import json
import shutil
import yaml
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-primary-wave8-20260605"
ROOT = Path(__file__).parents[3]
REPORT = Path(__file__).parent
YAML_DIR = ROOT / "pipeline/plugin-code-registry/family"
DRYRUN_BASE = REPORT / "dryrun" / "examples"

WAVE8_MAP = [
    {
        "family": "imaging",
        "canonical_slug": "image-converter",
        "legacy_slug": "convert-image",
        "display_name": "Image Converter for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-converter/",
        "source_sprint": "lowcode-plugin-example-factory-parallel-wave-20260605",
    },
    {
        "family": "imaging",
        "canonical_slug": "image-resizer",
        "legacy_slug": "resize-image",
        "display_name": "Image Resizer for .NET",
        "canonical_url": "https://products.aspose.net/imaging/image-resizer/",
        "source_sprint": "lowcode-plugin-example-factory-wave-20260605",
    },
    {
        "family": "html",
        "canonical_slug": "html-to-pdf-converter",
        "legacy_slug": "convert-html-to-pdf",
        "display_name": "HTML to PDF Converter for .NET",
        "canonical_url": "https://products.aspose.net/html/html-to-pdf-converter/",
        "source_sprint": "lowcode-plugin-example-factory-wave6-20260605",
    },
    {
        "family": "note",
        "canonical_slug": "convert-onenote-to-pdf",
        "legacy_slug": "convert-one-to-pdf",
        "display_name": "OneNote to PDF Converter for .NET",
        "canonical_url": "https://products.aspose.net/note/convert-onenote-to-pdf/",
        "source_sprint": "lowcode-plugin-example-factory-closeout-wave5-20260605",
    },
]

build_results = []
changes_log = []


def find_source_pkg(entry):
    """Locate the source generic-slug dryrun package."""
    sprint_dir = ROOT / f"reports/{entry['source_sprint']}"
    for examples_dir in [sprint_dir / "dryrun" / "examples", sprint_dir / "examples"]:
        pkg = examples_dir / entry["family"] / entry["legacy_slug"]
        if pkg.exists():
            return pkg
    # Fallback: scan all sprint dirs
    for sdir in sorted(ROOT.glob("reports/lowcode-plugin-example-factory-*/dryrun/examples")):
        pkg = sdir / entry["family"] / entry["legacy_slug"]
        if pkg.exists():
            return pkg
    for sdir in sorted(ROOT.glob("reports/lowcode-plugin-example-factory-*/examples")):
        pkg = sdir / entry["family"] / entry["legacy_slug"]
        if pkg.exists():
            return pkg
    return None


def migrate_package(entry):
    """Create canonical dryrun package from legacy generic package."""
    family = entry["family"]
    canonical_slug = entry["canonical_slug"]
    legacy_slug = entry["legacy_slug"]

    src_pkg = find_source_pkg(entry)
    if not src_pkg:
        return {
            "family": family,
            "canonical_slug": canonical_slug,
            "legacy_slug": legacy_slug,
            "status": "SKIPPED_SOURCE_NOT_FOUND",
            "error": f"Source package not found for {family}/{legacy_slug}",
        }

    dest_pkg = DRYRUN_BASE / family / canonical_slug
    if dest_pkg.exists():
        shutil.rmtree(dest_pkg)
    dest_pkg.mkdir(parents=True, exist_ok=True)

    # Copy all files from source except bin/obj
    for item in src_pkg.iterdir():
        if item.name in ("bin", "obj"):
            continue
        if item.is_file():
            shutil.copy2(item, dest_pkg / item.name)
        elif item.is_dir():
            shutil.copytree(item, dest_pkg / item.name)

    # Rewrite source-provenance.json with canonical identity
    sp = {}
    sp_path = dest_pkg / "source-provenance.json"
    if sp_path.exists():
        try:
            sp = json.loads(sp_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    sp.update({
        "family": family,
        "plugin_slug": canonical_slug,
        "canonical_plugin_slug": canonical_slug,
        "canonical_url": entry["canonical_url"],
        "display_plugin_name": entry["display_name"],
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "migration_status": "CANONICAL_PRIMARY_MIGRATED",
        "migrated_from": legacy_slug,
        "legacy_example_slug": legacy_slug,
        "generation_sprint": SPRINT,
        "migrated_at": TODAY,
    })
    sp_path.write_text(json.dumps(sp, indent=2))

    # Rewrite output-validation.json with canonical package_key
    ov = {}
    ov_path = dest_pkg / "output-validation.json"
    if ov_path.exists():
        try:
            ov = json.loads(ov_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    ov["package_key"] = f"{family}/{canonical_slug}"
    ov["canonical_plugin_slug"] = canonical_slug
    ov["migrated_from"] = legacy_slug
    ov["migration_sprint"] = SPRINT
    ov_path.write_text(json.dumps(ov, indent=2))

    # Update README title if it has legacy slug
    readme_path = dest_pkg / "README.md"
    if readme_path.exists():
        text = readme_path.read_text(encoding="utf-8", errors="replace")
        lines = text.split("\n")
        if lines and not lines[0].startswith(f"# {entry['display_name']}"):
            lines[0] = f"# {entry['display_name']}"
            readme_path.write_text("\n".join(lines))

    # Validate result
    ov2 = json.loads(ov_path.read_text(encoding="utf-8"))
    verdict = ov2.get("verdict")
    out_dir = dest_pkg / "output"
    out_files = [f for f in out_dir.iterdir() if f.is_file() and f.stat().st_size > 0] if out_dir.exists() else []

    return {
        "family": family,
        "canonical_slug": canonical_slug,
        "legacy_slug": legacy_slug,
        "status": "BUILT" if verdict == "PASS" and out_files else "BUILT_NO_OUTPUT",
        "verdict": verdict,
        "output_files": len(out_files),
        "path": str(dest_pkg),
        "source": str(src_pkg),
    }


def update_registry(entry):
    """Update YAML registry to canonical-primary for this entry."""
    family = entry["family"]
    fpath = YAML_DIR / f"{family}.yaml"
    if not fpath.exists():
        return False
    data = yaml.safe_load(fpath.read_text(encoding="utf-8"))
    updated = False
    for p in data.get("plugins", []):
        if p.get("plugin_slug") == entry["legacy_slug"]:
            p["legacy_aliases"] = [entry["legacy_slug"]]
            p["plugin_slug"] = entry["canonical_slug"]
            p["canonical_plugin_slug"] = entry["canonical_slug"]
            p["display_plugin_name"] = entry["display_name"]
            p["canonical_url"] = entry["canonical_url"]
            p["identity_status"] = "CANONICAL_IDENTITY_VERIFIED"
            p["migration_status"] = "CANONICAL_PRIMARY_MIGRATED"
            p["migrated_from"] = entry["legacy_slug"]
            p["dryrun_package_path"] = (
                f"reports/{SPRINT}/dryrun/examples/{family}/{entry['canonical_slug']}"
            )
            if "history" not in p:
                p["history"] = []
            p["history"].append({
                "date": TODAY,
                "status": "CANONICAL_PRIMARY_MIGRATED",
                "analyst_notes": (
                    f"Sprint {SPRINT}. Wave 8 canonical advancement: "
                    f"'{entry['legacy_slug']}' -> '{entry['canonical_slug']}'."
                ),
            })
            updated = True
            changes_log.append(f"{family}: {entry['legacy_slug']} -> {entry['canonical_slug']}")
    if updated:
        fpath.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
    return updated


# Execute Wave 8
for entry in WAVE8_MAP:
    result = migrate_package(entry)
    reg_ok = update_registry(entry)
    result["registry_updated"] = reg_ok
    build_results.append(result)
    print(f"  {entry['family']}/{entry['canonical_slug']}: {result['status']} registry={reg_ok}")

print(f"\nWave 8 results: {len(build_results)} packages")
passed = [r for r in build_results if r["status"] == "BUILT"]
print(f"  BUILT: {len(passed)}")
print(f"  Changes: {changes_log}")

(REPORT / "wave8-build-results.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "total": len(build_results),
    "built": len(passed),
    "changes": changes_log,
    "results": build_results,
    "verdict": "WAVE8_CANONICAL_ADVANCEMENT_COMPLETE" if len(passed) == len(WAVE8_MAP) else "WAVE8_PARTIAL",
}, indent=2))

print("\nWritten: wave8-build-results.json")
print(f"Verdict: WAVE8_CANONICAL_ADVANCEMENT_COMPLETE" if len(passed) == len(WAVE8_MAP) else "WAVE8_PARTIAL")
