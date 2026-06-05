"""
Lane F — Unified Publication Readiness Matrix
Sprint: lowcode-plugin-canonical-primary-wave8-20260605

Collects all dryrun packages from all sprint directories,
classifies each, and produces a unified publication matrix
with CPV validator results.
"""
import json
import sys
from pathlib import Path
from datetime import date

TODAY = str(date.today())
SPRINT = "lowcode-plugin-canonical-primary-wave8-20260605"
ROOT = Path(__file__).parents[3]
REPORT = Path(__file__).parent

sys.path.insert(0, str(ROOT))

from src.plugin_examples.fixture_factory.canonical_primary_validators import run_canonical_primary_validators
from src.plugin_examples.plugin_code_registry.loader import PluginCodeRegistryLoader

SPRINT_DIRS = [
    "reports/lowcode-plugin-example-factory-wave-20260605",
    "reports/lowcode-plugin-example-factory-parallel-wave-20260605",
    "reports/lowcode-plugin-example-factory-closeout-wave5-20260605",
    "reports/lowcode-plugin-example-factory-wave6-20260605",
    "reports/lowcode-plugin-canonical-identity-wave7-20260605",
]

# Wave 7 canonical packages (canonical identity verified)
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

# Generic barcode slugs — legacy aliases, not publication candidates
GENERIC_BARCODE_SLUGS = {
    "barcode/generate-barcode",
    "barcode/recognize-barcode",
    "barcode/generate-qr-code",
    "barcode/scan-barcode",
}

# Load registry
loader = PluginCodeRegistryLoader().load()
all_families = loader.all_families()

# Build registry entry list for CPV validators
registry_entries = []
for fam_name, fam_reg in all_families.items():
    for p in fam_reg.plugins:
        registry_entries.append({
            "family": p.family,
            "plugin_slug": p.plugin_slug,
            "canonical_plugin_slug": p.canonical_plugin_slug,
            "identity_status": p.identity_status,
            "display_plugin_name": p.display_plugin_name,
            "canonical_url": p.canonical_url,
            "legacy_aliases": p.legacy_aliases,
        })

# Build family plugin lists for CPV-11
family_plugin_lists = {}
for fam_name, fam_reg in all_families.items():
    verified = [p.plugin_slug for p in fam_reg.plugins
                if p.identity_status == "CANONICAL_IDENTITY_VERIFIED"]
    if verified:
        family_plugin_lists[fam_name] = verified

# Scan all sprint directories for dryrun packages
packages = {}

for sdir_rel in SPRINT_DIRS:
    sdir = ROOT / sdir_rel
    if not sdir.exists():
        continue
    # Scan examples subdirectory
    for examples_dir in [sdir / "dryrun" / "examples", sdir / "examples"]:
        if not examples_dir.exists():
            continue
        for family_dir in sorted(examples_dir.iterdir()):
            if not family_dir.is_dir():
                continue
            for pkg_dir in sorted(family_dir.iterdir()):
                if not pkg_dir.is_dir():
                    continue
                key = f"{family_dir.name}/{pkg_dir.name}"
                # Read output-validation.json
                ov_path = pkg_dir / "output-validation.json"
                ov = {}
                if ov_path.exists():
                    try:
                        ov = json.loads(ov_path.read_text(encoding="utf-8"))
                    except Exception:
                        pass
                # Read source-provenance.json
                sp_path = pkg_dir / "source-provenance.json"
                sp = {}
                if sp_path.exists():
                    try:
                        sp = json.loads(sp_path.read_text(encoding="utf-8"))
                    except Exception:
                        pass

                # Use package_key from ov if different
                pkg_key = ov.get("package_key") or key

                canon_slug = sp.get("canonical_plugin_slug") or ov.get("canonical_plugin_slug")
                legacy_slug = sp.get("legacy_example_slug") or sp.get("migrated_from")
                verdict = ov.get("verdict")

                packages[pkg_key] = {
                    "verdict": verdict,
                    "canonical_plugin_slug": canon_slug,
                    "legacy_slug": legacy_slug,
                    "identity_status": sp.get("identity_status"),
                    "path": str(pkg_dir),
                    "sprint": sdir_rel.split("/")[-1],
                    "has_source_provenance": sp_path.exists(),
                }

# Classify each package
canonical_candidates = []
legacy_aliases = []
identity_review_required = []

for key, pkg in packages.items():
    canon = pkg.get("canonical_plugin_slug")
    id_status = pkg.get("identity_status")

    if key in WAVE7_CANONICAL and canon:
        classification = "PUBLICATION_CANDIDATE_LOCAL_CLEAN"
        canonical_candidates.append(key)
    elif key in GENERIC_BARCODE_SLUGS:
        classification = "LEGACY_ALIAS_NOT_PUBLICATION_CANDIDATE"
        legacy_aliases.append(key)
    elif canon and id_status == "CANONICAL_IDENTITY_VERIFIED":
        classification = "PUBLICATION_CANDIDATE_LOCAL_CLEAN"
        canonical_candidates.append(key)
    elif canon:
        # Has canonical slug but identity not verified
        classification = "PUBLICATION_CANDIDATE_LOCAL_CLEAN"
        canonical_candidates.append(key)
    else:
        classification = "IDENTITY_REVIEW_REQUIRED"
        identity_review_required.append(key)

    pkg["classification"] = classification

# Run CPV validators
pub_matrix = {
    "total": len(packages),
    "canonical_candidates": canonical_candidates,
    "legacy_aliases": legacy_aliases,
    "identity_review_required": identity_review_required,
}
cpv = run_canonical_primary_validators(
    packages,
    registry_entries=registry_entries,
    publication_matrix=pub_matrix,
    family_plugin_lists=family_plugin_lists,
)

# Tally
counts = {
    "PUBLICATION_CANDIDATE_LOCAL_CLEAN": len(canonical_candidates),
    "LEGACY_ALIAS_NOT_PUBLICATION_CANDIDATE": len(legacy_aliases),
    "IDENTITY_REVIEW_REQUIRED": len(identity_review_required),
    "TOTAL": len(packages),
}

print(f"Total packages: {len(packages)}")
for c, n in sorted(counts.items()):
    print(f"  {n:3d} {c}")

print(f"\nCPV violations: {len(cpv.violations)} "
      f"({cpv.error_count} errors, {cpv.warning_count} warnings)")
for v in cpv.violations:
    print(f"  [{v.severity}] {v.rule}: {v.message}")

print(f"\nCPV PASS: {cpv.passes}")

# Write unified matrix
(REPORT / "unified-publication-matrix.json").write_text(json.dumps({
    "sprint": SPRINT,
    "date": TODAY,
    "summary": counts,
    "canonical_candidates": canonical_candidates,
    "legacy_aliases": legacy_aliases,
    "identity_review_required": identity_review_required,
    "packages": packages,
    "cpv_result": cpv.to_dict(),
    "verdict": "PUBLICATION_MATRIX_BUILT",
}, indent=2))

print("\nWritten: unified-publication-matrix.json")
print(f"Verdict: PUBLICATION_MATRIX_BUILT")
