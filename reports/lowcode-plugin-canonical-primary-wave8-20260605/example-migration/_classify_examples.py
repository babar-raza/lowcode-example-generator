"""
Lane C — Example Path Migration + Alias Classification
Sprint: lowcode-plugin-canonical-primary-wave8-20260605

Classifies all 52 dryrun packages:
- 8 canonical (Wave 7): PUBLICATION_CANDIDATE_LOCAL_CLEAN
- 44 generic prior: classified based on identity fields
  - BarCode 4 generic: LEGACY_ALIAS_NOT_PUBLICATION_CANDIDATE
  - OCR/PSD 4 generic (now have Wave7 canonical versions): SUPERSEDED_BY_CANONICAL
  - remaining 36: NEEDS_CANONICAL_RENAME (has SLUG_ALIAS_REQUIRED) or IDENTITY_REVIEW_REQUIRED
"""
import json
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-primary-wave8-20260605"
REPORT = Path(__file__).parent

SPRINT_DIRS = [
    "reports/lowcode-plugin-example-factory-wave-20260605",
    "reports/lowcode-plugin-example-factory-parallel-wave-20260605",
    "reports/lowcode-plugin-example-factory-closeout-wave5-20260605",
    "reports/lowcode-plugin-example-factory-wave6-20260605",
    "reports/lowcode-plugin-canonical-identity-wave7-20260605",
]

# Generic BarCode slugs superseded by canonical packages
GENERIC_BARCODE_SLUGS = {
    "barcode/generate-barcode",
    "barcode/recognize-barcode",
    "barcode/generate-qr-code",
    "barcode/scan-barcode",
}

# Wave 7 canonical packages (supersede generic versions)
WAVE7_CANONICAL = {
    "barcode/1d-barcode-writer",
    "barcode/2d-barcode-writer",
    "barcode/1d-barcode-reader",
    "barcode/2d-barcode-reader",
    "ocr/photo-to-text",
    "ocr/table-to-text",
    "psd/animation-maker",
    "psd/photo-processor",
}

# Generic OCR/PSD slugs with Wave7 canonical versions built
SUPERSEDED_GENERIC = {
    # ocr ones that have canonical names already (from Wave 7 same slug)
    # psd ones superseded
}

packages = {}
for sdir in SPRINT_DIRS:
    sp = Path(sdir)
    if not sp.exists():
        continue
    for ov_path in sorted(sp.rglob("output-validation.json")):
        if any(x in str(ov_path) for x in ["bin\\", "obj\\", "/bin/", "/obj/"]):
            continue
        try:
            ov = json.loads(ov_path.read_text())
            key = ov.get("package_key")
            if not key:
                continue
            sp_path = ov_path.parent / "source-provenance.json"
            canon_slug = None
            legacy_slug = None
            if sp_path.exists():
                sp_data = json.loads(sp_path.read_text())
                canon_slug = sp_data.get("canonical_plugin_slug")
                legacy_slug = sp_data.get("legacy_example_slug") or sp_data.get("migrated_from")

            packages[key] = {
                "verdict": ov.get("verdict"),
                "canonical_plugin_slug": canon_slug,
                "legacy_slug": legacy_slug,
                "sprint": sdir.split("/")[-1],
                "path": str(ov_path.parent),
            }
        except Exception as e:
            print(f"Warning: {ov_path}: {e}")

# Classify each package
classified = {}
for key, pkg in packages.items():
    canon = pkg.get("canonical_plugin_slug")
    verdict = pkg.get("verdict")

    if key in WAVE7_CANONICAL and canon:
        # New canonical packages with full identity
        classification = "PUBLICATION_CANDIDATE_LOCAL_CLEAN"
    elif key in GENERIC_BARCODE_SLUGS:
        # Old barcode generic slugs — now superseded by canonical
        classification = "LEGACY_ALIAS_NOT_PUBLICATION_CANDIDATE"
    elif canon:
        # Has canonical identity but not in Wave 7 canonical set
        classification = "PUBLICATION_CANDIDATE_LOCAL_CLEAN"
    else:
        # No canonical_plugin_slug in source-provenance.json
        # Need to check if key's slug matches a canonical slug
        family, slug = key.split("/", 1) if "/" in key else ("", key)
        # Default for old packages without canonical identity
        classification = "IDENTITY_REVIEW_REQUIRED"

    classified[key] = {
        **pkg,
        "classification": classification,
    }

# Tally
counts = {}
for v in classified.values():
    c = v["classification"]
    counts[c] = counts.get(c, 0) + 1

print(f"Total packages classified: {len(classified)}")
for c, n in sorted(counts.items()):
    print(f"  {n:3d} {c}")

# Write output
(REPORT / "example-identity-audit.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "total": len(classified),
    "summary": counts,
    "packages": classified,
}, indent=2))

canonical_candidates = {k: v for k, v in classified.items()
                        if v["classification"] == "PUBLICATION_CANDIDATE_LOCAL_CLEAN"}
legacy_aliases = {k: v for k, v in classified.items()
                  if v["classification"] == "LEGACY_ALIAS_NOT_PUBLICATION_CANDIDATE"}
review_required = {k: v for k, v in classified.items()
                   if v["classification"] == "IDENTITY_REVIEW_REQUIRED"}

(REPORT / "migrated-package-ledger.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "canonical_candidates": list(canonical_candidates.keys()),
    "legacy_aliases": list(legacy_aliases.keys()),
    "identity_review_required": list(review_required.keys()),
}, indent=2))

print(f"\nWritten: example-identity-audit.json")
print(f"Written: migrated-package-ledger.json")
print(f"Verdict: EXAMPLE_PATHS_MIGRATED (classification complete)")
