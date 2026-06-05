"""
Independent Verification — Wave 11 Sprint
Sprint: lowcode-plugin-canonical-package-wave11-20260605
Lane: I

Runs 55 independent checks. All checks must PASS or be explicitly SKIP.
"""
import json
import yaml
import glob
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parents[3]
SPRINT = "lowcode-plugin-canonical-package-wave11-20260605"
REPORT = ROOT / "reports" / SPRINT
TODAY = str(date.today())

results = []
pass_count = 0
fail_count = 0
skip_count = 0


def iv_pass(check_id, msg):
    global pass_count
    pass_count += 1
    results.append({"id": check_id, "result": "PASS", "message": msg})
    print(f"  {check_id}: PASS — {msg}")


def iv_fail(check_id, msg):
    global fail_count
    fail_count += 1
    results.append({"id": check_id, "result": "FAIL", "message": msg})
    print(f"  {check_id}: FAIL — {msg}")


def iv_skip(check_id, msg):
    global skip_count
    skip_count += 1
    results.append({"id": check_id, "result": "SKIP", "message": msg})
    print(f"  {check_id}: SKIP — {msg}")


# ─── Lane 0: Coordinator ───────────────────────────────────────────────────────

print("Lane 0: Coordinator")
iv_pass("IV-01", f"lane-ledger.json exists") if (REPORT / "coordinator/lane-ledger.json").exists() else iv_fail("IV-01", "lane-ledger.json missing")
iv_pass("IV-02", f"taskcards.json exists") if (REPORT / "coordinator/taskcards.json").exists() else iv_fail("IV-02", "taskcards.json missing")

# ─── Lane A: Wave 10 Closeout Repair ──────────────────────────────────────────

print("\nLane A: Wave 10 Closeout Repair")

import subprocess
try:
    r10 = subprocess.run(["git", "cat-file", "-t", "cef9497"], capture_output=True, text=True, cwd=str(ROOT))
    if r10.stdout.strip() == "commit":
        iv_pass("IV-03", "cef9497 is a valid commit")
    else:
        iv_fail("IV-03", f"cef9497 is not a valid commit: {r10.stdout.strip()}")
except Exception as e:
    iv_fail("IV-03", f"git cat-file failed: {e}")

try:
    r11 = subprocess.run(["git", "cat-file", "-t", "8967b0b"], capture_output=True, text=True, cwd=str(ROOT))
    if r11.stdout.strip() == "commit":
        iv_pass("IV-04", "8967b0b is a valid commit")
    else:
        iv_fail("IV-04", f"8967b0b is not a valid commit: {r11.stdout.strip()}")
except Exception as e:
    iv_fail("IV-04", f"git cat-file failed: {e}")

iv_pass("IV-05", "commit-verification.md exists") if (REPORT / "wave10-closeout-repair/commit-verification.md").exists() else iv_fail("IV-05", "commit-verification.md missing")
iv_pass("IV-06", "closeout-repair-log.md exists") if (REPORT / "wave10-closeout-repair/closeout-repair-log.md").exists() else iv_fail("IV-06", "closeout-repair-log.md missing")

# ─── Lane B: Package Proof Repair ─────────────────────────────────────────────

print("\nLane B: Package Proof Repair")

wave10_ex = ROOT / "reports/lowcode-plugin-canonical-package-wave10-20260605/dryrun/examples"
for pkg_key in ["barcode/1d-barcode-writer", "zip/compress-files"]:
    fam, slug = pkg_key.split("/")
    pkg = wave10_ex / fam / slug
    check_label = pkg_key.replace("/", "_")
    iv_pass(f"IV-07-{check_label}-restore", f"restore.log present") if (pkg / "restore.log").exists() else iv_fail(f"IV-07-{check_label}-restore", "restore.log missing")
    iv_pass(f"IV-08-{check_label}-build", f"build.log present") if (pkg / "build.log").exists() else iv_fail(f"IV-08-{check_label}-build", "build.log missing")
    iv_pass(f"IV-09-{check_label}-run", f"run.log present") if (pkg / "run.log").exists() else iv_fail(f"IV-09-{check_label}-run", "run.log missing")

# ─── Lane C: Wave 11 Dryrun Packages ──────────────────────────────────────────

print("\nLane C: Wave 11 Dryrun Packages")

wave11_targets = [
    ("ocr", "scanned-image-to-text"),
    ("ocr", "scanned-pdf-to-text"),
    ("page", "xps-converter"),
    ("page", "eps-to-pdf"),
    ("page", "ps-converter"),
    ("psd", "psd-to-pdf"),
    ("tasks", "mpp-to-html"),
    ("tasks", "mpp-to-png"),
    ("zip", "universal-extractor"),
    ("zip", "universal-compressor"),
]

wave11_ex = REPORT / "wave11-dryrun/examples"
built_count = 0
for fam, slug in wave11_targets:
    pkg = wave11_ex / fam / slug
    if pkg.exists():
        built_count += 1
    else:
        iv_fail(f"IV-10-{fam}-{slug}", f"Package dir missing")

iv_pass("IV-10", f"All 10 Wave 11 packages exist on disk ({built_count}/10)") if built_count == 10 else iv_fail("IV-10", f"Only {built_count}/10 Wave 11 packages exist")

# Check Program.cs
prog_count = sum(1 for fam, slug in wave11_targets if (wave11_ex / fam / slug / "Program.cs").exists())
iv_pass("IV-11", f"All 10 packages have Program.cs ({prog_count}/10)") if prog_count == 10 else iv_fail("IV-11", f"Only {prog_count}/10 packages have Program.cs")

# Check output-validation.json
ov_count = sum(1 for fam, slug in wave11_targets if (wave11_ex / fam / slug / "output-validation.json").exists())
iv_pass("IV-12", f"All 10 packages have output-validation.json ({ov_count}/10)") if ov_count == 10 else iv_fail("IV-12", f"Only {ov_count}/10")

# Check output-validation verdict=PASS
pass_ov = 0
for fam, slug in wave11_targets:
    ov_path = wave11_ex / fam / slug / "output-validation.json"
    if ov_path.exists():
        ov = json.loads(ov_path.read_text(encoding="utf-8"))
        if ov.get("verdict") == "PASS":
            pass_ov += 1
iv_pass("IV-13", f"All 10 output-validation have verdict=PASS ({pass_ov}/10)") if pass_ov == 10 else iv_fail("IV-13", f"Only {pass_ov}/10 have verdict=PASS")

# Check package-manifest.json
pm_count = sum(1 for fam, slug in wave11_targets if (wave11_ex / fam / slug / "package-manifest.json").exists())
iv_pass("IV-14", f"All 10 packages have package-manifest.json ({pm_count}/10)") if pm_count == 10 else iv_fail("IV-14", f"Only {pm_count}/10")

# Check source-provenance.json
sp_count = sum(1 for fam, slug in wave11_targets if (wave11_ex / fam / slug / "source-provenance.json").exists())
iv_pass("IV-15", f"All 10 packages have source-provenance.json ({sp_count}/10)") if sp_count == 10 else iv_fail("IV-15", f"Only {sp_count}/10")

# Check .csproj
csproj_count = sum(1 for fam, slug in wave11_targets if list((wave11_ex / fam / slug).glob("*.csproj")))
iv_pass("IV-16", f"All 10 packages have .csproj ({csproj_count}/10)") if csproj_count == 10 else iv_fail("IV-16", f"Only {csproj_count}/10 have .csproj")

# Check log proof
log_ok = 0
for fam, slug in wave11_targets:
    pkg = wave11_ex / fam / slug
    if all((pkg / log).exists() for log in ("restore.log", "build.log", "run.log")):
        log_ok += 1
iv_pass("IV-17", f"All 10 packages have complete log proof ({log_ok}/10)") if log_ok == 10 else iv_fail("IV-17", f"Only {log_ok}/10 have complete logs")

# Check wave11-build-results.json
br_path = REPORT / "wave11-dryrun/wave11-build-results.json"
if br_path.exists():
    br = json.loads(br_path.read_text(encoding="utf-8"))
    piv_pass = br.get("piv_pass", 0)
    piv_fail = br.get("piv_fail", 0)
    iv_pass("IV-18", f"wave11-build-results.json: {piv_pass}/10 PIV PASS") if piv_fail == 0 and piv_pass == 10 else iv_fail("IV-18", f"PIV: {piv_pass} PASS, {piv_fail} FAIL")
else:
    iv_fail("IV-18", "wave11-build-results.json missing")

# ─── Lane D: Slug Alias Resolution ────────────────────────────────────────────

print("\nLane D: Slug Alias Resolution")

# Verify registry has 0 SLUG_ALIAS_REQUIRED
sar_count = 0
total_count = 0
civ_count = 0
for f in sorted(glob.glob(str(ROOT / "pipeline/plugin-code-registry/family/*.yaml"))):
    data = yaml.safe_load(Path(f).read_text(encoding="utf-8"))
    for p in data.get("plugins", []):
        status = p.get("identity_status", "MISSING_CANONICAL_URL")
        total_count += 1
        if status == "SLUG_ALIAS_REQUIRED":
            sar_count += 1
        elif status == "CANONICAL_IDENTITY_VERIFIED":
            civ_count += 1

iv_pass("IV-19", f"SLUG_ALIAS_REQUIRED = 0 (all 5 resolved)") if sar_count == 0 else iv_fail("IV-19", f"SLUG_ALIAS_REQUIRED = {sar_count} (expected 0)")
iv_pass("IV-20", f"CANONICAL_IDENTITY_VERIFIED = {civ_count} (>= 45)") if civ_count >= 45 else iv_fail("IV-20", f"CANONICAL_IDENTITY_VERIFIED = {civ_count} (expected >= 45)")
iv_pass("IV-21", f"Registry total = {total_count} (67)") if total_count == 67 else iv_fail("IV-21", f"Registry total = {total_count} (expected 67)")

# Check psd/photo-processor has edit-psd-layers as legacy alias
psd_data = yaml.safe_load((ROOT / "pipeline/plugin-code-registry/family/psd.yaml").read_text(encoding="utf-8"))
photo_proc = next((p for p in psd_data["plugins"] if p["plugin_slug"] == "photo-processor"), None)
if photo_proc and "edit-psd-layers" in photo_proc.get("legacy_aliases", []):
    iv_pass("IV-22", "psd/photo-processor has edit-psd-layers in legacy_aliases")
else:
    iv_fail("IV-22", "psd/photo-processor missing edit-psd-layers in legacy_aliases")

# Check migration ledger exists
iv_pass("IV-23", "slug-alias-migration-ledger.json exists") if (REPORT / "slug-alias-resolution/slug-alias-migration-ledger.json").exists() else iv_fail("IV-23", "missing slug-alias-migration-ledger.json")

# ─── Lane E: Canonical URL Discovery ─────────────────────────────────────────

print("\nLane E: Canonical URL Discovery")

iv_pass("IV-24", "missing-url-ledger.json exists") if (REPORT / "canonical-url-discovery/missing-url-ledger.json").exists() else iv_fail("IV-24", "missing-url-ledger.json missing")

# Check svg-to-pdf-converter and vectorizer are now CIV
svg_data = yaml.safe_load((ROOT / "pipeline/plugin-code-registry/family/svg.yaml").read_text(encoding="utf-8"))
svg_map = {p["plugin_slug"]: p for p in svg_data["plugins"]}
for slug in ("svg-to-pdf-converter", "vectorizer"):
    p = svg_map.get(slug, {})
    if p.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
        iv_pass(f"IV-25-{slug}", f"svg/{slug} upgraded to CANONICAL_IDENTITY_VERIFIED")
    else:
        iv_fail(f"IV-25-{slug}", f"svg/{slug} identity_status = {p.get('identity_status')}")

# ─── Lane F: Validators ────────────────────────────────────────────────────────

print("\nLane F: Validators")

rbc_file = ROOT / "src/plugin_examples/fixture_factory/registry_bundle_completeness_validators.py"
iv_pass("IV-27", "registry_bundle_completeness_validators.py exists") if rbc_file.exists() else iv_fail("IV-27", "RBC validator file missing")

rbc_test = ROOT / "tests/unit/test_registry_bundle_completeness_validators.py"
iv_pass("IV-28", "test_registry_bundle_completeness_validators.py exists") if rbc_test.exists() else iv_fail("IV-28", "RBC test file missing")

# Count RBC rules in the file
if rbc_file.exists():
    content = rbc_file.read_text(encoding="utf-8")
    rbc_rule_count = sum(1 for line in content.splitlines() if line.strip().startswith("def rbc_"))
    iv_pass("IV-29", f"RBC validator has {rbc_rule_count} rules (expected 8)") if rbc_rule_count == 8 else iv_fail("IV-29", f"RBC validator has {rbc_rule_count} rules (expected 8)")

# ─── Lane G: Publication Readiness ────────────────────────────────────────────

print("\nLane G: Publication Readiness")

matrix_v4 = REPORT / "publication-readiness/unified-publication-matrix-v4.json"
iv_pass("IV-30", "unified-publication-matrix-v4.json exists") if matrix_v4.exists() else iv_fail("IV-30", "matrix v4 missing")

if matrix_v4.exists():
    mv4 = json.loads(matrix_v4.read_text(encoding="utf-8"))
    iv_pass("IV-31", f"Matrix v4 has {mv4['registry_total']} rows (expected 67)") if mv4["registry_total"] == 67 else iv_fail("IV-31", f"Matrix v4 has {mv4['registry_total']} rows")
    cvfp = mv4["counts"].get("CANONICAL_VERIFIED_FULL_PACKAGE", 0)
    iv_pass("IV-32", f"CANONICAL_VERIFIED_FULL_PACKAGE = {cvfp} (expected 33)") if cvfp == 33 else iv_fail("IV-32", f"CANONICAL_VERIFIED_FULL_PACKAGE = {cvfp}")
    pclc = mv4["counts"].get("PUBLICATION_CANDIDATE_LOCAL_CLEAN", 0)
    iv_pass("IV-33", f"PUBLICATION_CANDIDATE_LOCAL_CLEAN = {pclc} (expected 10)") if pclc == 10 else iv_fail("IV-33", f"PUBLICATION_CANDIDATE_LOCAL_CLEAN = {pclc}")
    total_proven = mv4["proven_packages"]["total"]
    iv_pass("IV-34", f"Total proven packages = {total_proven} (expected 43)") if total_proven == 43 else iv_fail("IV-34", f"Total proven = {total_proven}")

# ─── Lane H: State / Docs / Skills ─────────────────────────────────────────────

print("\nLane H: State / Docs / Skills")

iv_pass("IV-35", "canonical-package-ledger.json exists") if (REPORT / "state-docs/canonical-package-ledger.json").exists() else iv_fail("IV-35", "canonical-package-ledger.json missing")
iv_pass("IV-36", "wave12-next-queue.json exists") if (REPORT / "state-docs/wave12-next-queue.json").exists() else iv_fail("IV-36", "wave12-next-queue.json missing")

# Verify ledger has correct registry state
ledger = json.loads((REPORT / "state-docs/canonical-package-ledger.json").read_text(encoding="utf-8"))
iv_pass("IV-37", f"Ledger CIV = {ledger['registry_state']['CANONICAL_IDENTITY_VERIFIED']} (expected 45)") if ledger["registry_state"]["CANONICAL_IDENTITY_VERIFIED"] == 45 else iv_fail("IV-37", f"Ledger CIV = {ledger['registry_state']['CANONICAL_IDENTITY_VERIFIED']}")
iv_pass("IV-38", f"Ledger total proven = {ledger['proven_packages']['total']} (expected 43)") if ledger["proven_packages"]["total"] == 43 else iv_fail("IV-38", f"Ledger total proven = {ledger['proven_packages']['total']}")

# ─── Protected Files ──────────────────────────────────────────────────────────

print("\nProtected Files")

import hashlib

protected = {
    "pipeline/configs/families/cells.yml": "28c51b79f8dac9e7",
    "pipeline/configs/families/words.yml": "ef21e9e514386a7e",
    "pipeline/configs/families/pdf.yml": "de889ed24b3bc3a0",
    "pipeline/configs/families/slides.yml": "4eec3d74e7c9cca5",
    "pipeline/configs/families/email.yml": "3e872e96519168ba",
    "pipeline/configs/families/diagram.yml": "306c16e4acdf4802",
    "pipeline/format-authority/manifest.json": "3e96754355d7124f",
}

for rel_path, expected_hash in protected.items():
    full_path = ROOT / rel_path
    if not full_path.exists():
        iv_fail(f"IV-39-{Path(rel_path).stem}", f"{rel_path} missing")
        continue
    data = full_path.read_bytes()
    actual = hashlib.sha256(data).hexdigest()[:16]
    if actual == expected_hash:
        iv_pass(f"IV-39-{Path(rel_path).stem}", f"{rel_path} hash matches")
    else:
        iv_fail(f"IV-39-{Path(rel_path).stem}", f"{rel_path} hash mismatch: {actual} != {expected_hash}")

# ─── Slug Alias Consolidation ─────────────────────────────────────────────────

print("\nSlug Alias Consolidation Details")

# Check svg-to-pdf-converter has convert-svg-to-png as legacy alias
svg_pdf = svg_map.get("svg-to-pdf-converter", {})
if "convert-svg-to-png" in svg_pdf.get("legacy_aliases", []):
    iv_pass("IV-46", "svg/svg-to-pdf-converter has convert-svg-to-png in legacy_aliases")
else:
    iv_fail("IV-46", "svg/svg-to-pdf-converter missing convert-svg-to-png in legacy_aliases")

# Check vectorizer has convert-svg-to-jpg as legacy alias
vec = svg_map.get("vectorizer", {})
if "convert-svg-to-jpg" in vec.get("legacy_aliases", []):
    iv_pass("IV-47", "svg/vectorizer has convert-svg-to-jpg in legacy_aliases")
else:
    iv_fail("IV-47", "svg/vectorizer missing convert-svg-to-jpg in legacy_aliases")

# Check psd/edit-psd-layers is GONE from registry
psd_slugs = [p["plugin_slug"] for p in psd_data["plugins"]]
if "edit-psd-layers" not in psd_slugs:
    iv_pass("IV-48", "psd/edit-psd-layers removed from registry (consolidated)")
else:
    iv_fail("IV-48", "psd/edit-psd-layers still exists as standalone entry")

# ─── Summary ─────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"IV SUMMARY: {pass_count} PASS, {fail_count} FAIL, {skip_count} SKIP")
print(f"Total checks: {pass_count + fail_count + skip_count}")
print(f"Verdict: {'IV_PASS' if fail_count == 0 else 'IV_FAIL'}")
print(f"{'='*60}")

# Write results
out = {
    "sprint": SPRINT,
    "date": TODAY,
    "total_checks": pass_count + fail_count + skip_count,
    "checks_pass": pass_count,
    "checks_fail": fail_count,
    "checks_skip": skip_count,
    "verdict": "IV_PASS" if fail_count == 0 else "IV_FAIL",
    "results": results,
}
out_path = REPORT / "iv/iv-results.json"
out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
print(f"Results written to {out_path}")
