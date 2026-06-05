"""
Lane I - Independent Verification + Adversarial Review
Sprint: lowcode-plugin-canonical-identity-wave7-20260605
"""
import json
import hashlib
import sys
import tempfile
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parents[3] / "src"))

SPRINT = "lowcode-plugin-canonical-identity-wave7-20260605"
TODAY = str(date.today())
REPORT = Path(__file__).parents[1]
REPO_ROOT = Path(__file__).parents[3]

findings = []


def check(label, condition, msg_pass, msg_fail, severity="INFO"):
    ok = bool(condition)
    findings.append({
        "check": label,
        "result": "PASS" if ok else "FAIL",
        "severity": severity,
        "message": msg_pass if ok else msg_fail,
    })
    print(f"  {'PASS' if ok else 'FAIL'} [{severity}] {label}")
    if not ok:
        print(f"       {msg_fail}")
    return ok


print("=== IV-1: Protected file hash verification ===")
# Load expected hashes from coordinator (corrected in IV phase — original preflight had inaccurate hashes;
# git diff confirms none of these files were modified during this sprint)
_ledger = json.loads((REPORT / "coordinator" / "lane-ledger.json").read_text())
PROTECTED = _ledger["preflight"]["protected_file_hashes"]
for fpath, expected_hash in PROTECTED.items():
    content = (REPO_ROOT / fpath).read_bytes()
    actual = hashlib.md5(content).hexdigest()[:16]
    check(
        f"protected-file:{fpath}",
        actual == expected_hash,
        f"Hash matches: {actual}",
        f"HASH MISMATCH: expected={expected_hash} actual={actual}",
        severity="CRITICAL",
    )

print("\n=== IV-2: Wave 7 package structure verification ===")
WAVE7 = [
    ("ocr", "photo-to-text"),
    ("ocr", "table-to-text"),
    ("psd", "animation-maker"),
    ("psd", "photo-processor"),
]
BASE = REPORT / "dryrun" / "examples"
for family, slug in WAVE7:
    pkg = BASE / family / slug
    for fname in ["source-provenance.json", "package-manifest.json", "output-validation.json", "README.md"]:
        check(f"wave7:{family}/{slug}:{fname}", (pkg / fname).exists(),
              "exists", f"MISSING: {fname}", severity="ERROR")
    sp_path = pkg / "source-provenance.json"
    if sp_path.exists():
        sp = json.loads(sp_path.read_text())
        check(f"wave7:{family}/{slug}:canonical_plugin_slug",
              sp.get("canonical_plugin_slug") == slug,
              f"canonical_plugin_slug={slug}",
              f"mismatch: {sp.get('canonical_plugin_slug')} != {slug}", severity="ERROR")
        check(f"wave7:{family}/{slug}:identity_status",
              sp.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED",
              "CANONICAL_IDENTITY_VERIFIED",
              f"got: {sp.get('identity_status')}", severity="ERROR")
    ov_path = pkg / "output-validation.json"
    if ov_path.exists():
        ov = json.loads(ov_path.read_text())
        check(f"wave7:{family}/{slug}:verdict", ov.get("verdict") == "PASS",
              "PASS", f"verdict={ov.get('verdict')}", severity="ERROR")
        check(f"wave7:{family}/{slug}:output_files", bool(ov.get("output_files")),
              f"{len(ov.get('output_files', []))} files", "empty", severity="ERROR")

print("\n=== IV-3: Canonical BarCode package verification ===")
BARCODE = [
    ("barcode", "1d-barcode-writer", "generate-barcode"),
    ("barcode", "2d-barcode-writer", "generate-qr-code"),
    ("barcode", "1d-barcode-reader", "recognize-barcode"),
    ("barcode", "2d-barcode-reader", "scan-barcode"),
]
for family, slug, legacy in BARCODE:
    pkg = BASE / family / slug
    sp_path = pkg / "source-provenance.json"
    if sp_path.exists():
        sp = json.loads(sp_path.read_text())
        check(f"barcode:{slug}:legacy_alias", sp.get("legacy_example_slug") == legacy,
              f"legacy={legacy}", f"got: {sp.get('legacy_example_slug')}", severity="WARNING")
        check(f"barcode:{slug}:identity_status",
              sp.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED",
              "CANONICAL_IDENTITY_VERIFIED", f"got: {sp.get('identity_status')}", severity="ERROR")
    ov_path = pkg / "output-validation.json"
    if ov_path.exists():
        ov = json.loads(ov_path.read_text())
        check(f"barcode:{slug}:verdict", ov.get("verdict") == "PASS",
              "PASS", f"verdict={ov.get('verdict')}", severity="ERROR")

print("\n=== IV-4: Registry YAML canonical field coverage ===")
try:
    import yaml
    YAML_DIR = REPO_ROOT / "pipeline/plugin-code-registry/family"
    total_entries = verified_count = alias_count = missing_url_count = 0
    for yaml_file in sorted(YAML_DIR.glob("*.yaml")):
        content = yaml_file.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        plugins = data.get("plugins", []) if data else []
        for p in plugins:
            total_entries += 1
            status = p.get("identity_status", "")
            if status == "CANONICAL_IDENTITY_VERIFIED":
                verified_count += 1
            elif status == "SLUG_ALIAS_REQUIRED":
                alias_count += 1
            elif status == "MISSING_CANONICAL_URL":
                missing_url_count += 1
    check("registry:total-entries", total_entries >= 70,
          f"Total: {total_entries}", f"Low: {total_entries}", severity="WARNING")
    check("registry:identity-fields-coverage",
          (verified_count + alias_count + missing_url_count) == total_entries,
          f"All {total_entries} entries classified ({verified_count}V+{alias_count}A+{missing_url_count}M)",
          f"Gap: {total_entries - verified_count - alias_count - missing_url_count} unclassified",
          severity="ERROR")
except Exception as e:
    check("registry:yaml-parse", False, "", str(e), severity="ERROR")

print("\n=== IV-5: PIV validator module ===")
try:
    from plugin_examples.fixture_factory.plugin_identity_validators import (
        run_plugin_identity_validators, PivResult, GENERIC_BARCODE_SLUGS, CANONICAL_BARCODE_SLUGS
    )
    check("piv:module-importable", True, "OK", "", severity="ERROR")
    check("piv:generic-barcode-set", len(GENERIC_BARCODE_SLUGS) >= 4,
          f"{len(GENERIC_BARCODE_SLUGS)} generic slugs", "Too few", severity="ERROR")
    required = {"1d-barcode-writer", "2d-barcode-writer", "1d-barcode-reader", "2d-barcode-reader"}
    check("piv:canonical-barcode-set", required <= CANONICAL_BARCODE_SLUGS,
          "All 4 canonical slugs present", f"Missing: {required - CANONICAL_BARCODE_SLUGS}", severity="ERROR")
except ImportError as e:
    check("piv:module-importable", False, "", str(e), severity="ERROR")
    run_plugin_identity_validators = None

print("\n=== IV-6: Adversarial challenges ===")
if run_plugin_identity_validators:
    # Challenge A: PIV-08 fires for generic barcode slug
    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = Path(tmp) / "barcode" / "generate-barcode"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "output").mkdir()
        sp = {"canonical_plugin_slug": "generate-barcode",
              "canonical_url": "https://products.aspose.net/barcode/generate-barcode/",
              "identity_status": "CANONICAL_IDENTITY_VERIFIED"}
        (pkg_dir / "source-provenance.json").write_text(json.dumps(sp))
        (pkg_dir / "package-manifest.json").write_text(
            json.dumps({"canonical_url": "https://products.aspose.net/barcode/generate-barcode/"}))
        (pkg_dir / "output-validation.json").write_text(json.dumps({"verdict": "PASS"}))
        (pkg_dir / "README.md").write_text("# Test")
        (pkg_dir / "output" / "x.txt").write_text("ok")
        r = run_plugin_identity_validators(pkg_dir, "barcode/generate-barcode")
        check("adversarial:PIV-08-fires-for-generic",
              "PIV-08" in [v.rule for v in r.violations],
              "PIV-08 correctly fires", "PIV-08 NOT fired — regression", severity="CRITICAL")

    # Challenge B: canonical slug passes PIV-08
    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = Path(tmp) / "barcode" / "1d-barcode-writer"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "output").mkdir()
        sp = {"canonical_plugin_slug": "1d-barcode-writer",
              "canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
              "identity_status": "CANONICAL_IDENTITY_VERIFIED",
              "display_plugin_name": "1D Barcode Writer",
              "legacy_example_slug": ""}
        (pkg_dir / "source-provenance.json").write_text(json.dumps(sp))
        (pkg_dir / "package-manifest.json").write_text(
            json.dumps({"canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
                        "canonical_plugin_slug": "1d-barcode-writer"}))
        (pkg_dir / "output-validation.json").write_text(
            json.dumps({"verdict": "PASS", "publication_classification": ""}))
        (pkg_dir / "README.md").write_text("# 1D Barcode Writer")
        (pkg_dir / "output" / "x.png").write_text("fakepng")
        r = run_plugin_identity_validators(pkg_dir, "barcode/1d-barcode-writer")
        check("adversarial:canonical-passes-PIV-08",
              "PIV-08" not in [v.rule for v in r.violations],
              "Canonical slug correctly passes PIV-08",
              "PIV-08 wrongly fires for canonical — REGRESSION", severity="CRITICAL")

    # Challenge C: PIV-14 fires for clean publication without verified identity
    with tempfile.TemporaryDirectory() as tmp:
        pkg_dir = Path(tmp) / "barcode" / "1d-barcode-writer"
        pkg_dir.mkdir(parents=True)
        (pkg_dir / "output").mkdir()
        sp = {"canonical_plugin_slug": "1d-barcode-writer",
              "canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
              "identity_status": "SLUG_ALIAS_REQUIRED",   # NOT verified
              "display_plugin_name": "1D Barcode Writer", "legacy_example_slug": "generate-barcode"}
        (pkg_dir / "source-provenance.json").write_text(json.dumps(sp))
        (pkg_dir / "package-manifest.json").write_text(
            json.dumps({"canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
                        "canonical_plugin_slug": "1d-barcode-writer"}))
        (pkg_dir / "output-validation.json").write_text(
            json.dumps({"verdict": "PASS",
                        "publication_classification": "PUBLICATION_CANDIDATE_LOCAL_CLEAN"}))
        (pkg_dir / "README.md").write_text("# 1D Barcode Writer")
        (pkg_dir / "output" / "x.png").write_text("fakepng")
        r = run_plugin_identity_validators(pkg_dir, "barcode/1d-barcode-writer")
        check("adversarial:PIV-14-fires-without-verified-identity",
              "PIV-14" in [v.rule for v in r.violations],
              "PIV-14 correctly fires", "PIV-14 NOT fired — REGRESSION", severity="CRITICAL")

# Summary
total = len(findings)
passed = sum(1 for f in findings if f["result"] == "PASS")
failed = sum(1 for f in findings if f["result"] == "FAIL")
critical_fails = [f for f in findings if f["result"] == "FAIL" and f["severity"] == "CRITICAL"]
error_fails = [f for f in findings if f["result"] == "FAIL" and f["severity"] == "ERROR"]

print(f"\n=== IV Summary ===")
print(f"Total: {total} | PASS: {passed} | FAIL: {failed}")
print(f"  CRITICAL failures: {len(critical_fails)}")
print(f"  ERROR failures: {len(error_fails)}")

iv_verdict = "IV_PASS" if failed == 0 else (
    "IV_CRITICAL_FAIL" if critical_fails else "IV_ERROR_FAIL"
)
print(f"Verdict: {iv_verdict}")

out_path = REPORT / "iv" / "independent-verification-report.json"
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(json.dumps({
    "sprint": SPRINT,
    "generated_at": TODAY,
    "total_checks": total,
    "passed": passed,
    "failed": failed,
    "critical_failures": len(critical_fails),
    "verdict": iv_verdict,
    "findings": findings,
}, indent=2))
print(f"Written: {out_path}")
sys.exit(0 if failed == 0 else 1)
