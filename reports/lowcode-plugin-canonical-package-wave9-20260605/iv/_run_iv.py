"""
Lane J: Independent Verification
Sprint: lowcode-plugin-canonical-package-wave9-20260605
"""
import json
import yaml
import hashlib
from pathlib import Path

ROOT = Path(__file__).parents[3]
SPRINT = "lowcode-plugin-canonical-package-wave9-20260605"
REPORT = ROOT / f"reports/{SPRINT}"
WAVE8_REPORT = ROOT / "reports/lowcode-plugin-canonical-primary-wave8-20260605"
WAVE8_BASE = WAVE8_REPORT / "wave8/dryrun/examples"
WAVE9_BASE = REPORT / "dryrun/examples"
REGISTRY_DIR = ROOT / "pipeline/plugin-code-registry/family"

checks = []
errors = []

W9_SLUGS = [
    "image-compressor", "image-cropper", "image-filters", "image-merger",
    "add-watermark", "image-rotator",
    "project-to-pdf-converter", "mpp-to-excel",
    "html-to-docx-converter", "html-to-image-converter",
    "convert-onenote-to-word", "convert-onenote-to-image",
]
W9_FAMILIES = {
    "image-compressor": "imaging", "image-cropper": "imaging",
    "image-filters": "imaging", "image-merger": "imaging",
    "add-watermark": "imaging", "image-rotator": "imaging",
    "project-to-pdf-converter": "tasks", "mpp-to-excel": "tasks",
    "html-to-docx-converter": "html", "html-to-image-converter": "html",
    "convert-onenote-to-word": "note", "convert-onenote-to-image": "note",
}
W8_KEYS = [
    "imaging/image-converter", "imaging/image-resizer",
    "html/html-to-pdf-converter", "note/convert-onenote-to-pdf",
]


def check(name, passed, detail="", severity="ERROR"):
    status = "PASS" if passed else ("FAIL" if severity == "ERROR" else "WARN")
    checks.append({"check": name, "status": status, "detail": detail, "severity": severity})
    if not passed and severity == "ERROR":
        errors.append(f"FAIL: {name} — {detail}")
    return passed


# IV-01: Wave 8 lane-ledger all lanes COMPLETE
ll8 = json.loads((WAVE8_REPORT / "coordinator/lane-ledger.json").read_text())
pending8 = [l for l in ll8.get("lanes", []) if l.get("status") not in ("COMPLETE",)]
check("IV-01: Wave8 lane-ledger all lanes COMPLETE", len(pending8) == 0,
      f"pending={[l['lane'] for l in pending8]}")

# IV-02: Wave 8 taskcards all COMPLETE
tc8_path = WAVE8_REPORT / "taskcards/taskcards.json"
if tc8_path.exists():
    tc8 = json.loads(tc8_path.read_text())
    pending_tc8 = [t for t in tc8.get("taskcards", []) if t.get("status") not in ("COMPLETE",)]
    check("IV-02: Wave8 taskcards all COMPLETE", len(pending_tc8) == 0,
          f"pending={[t['id'] for t in pending_tc8]}")
else:
    check("IV-02: Wave8 taskcards all COMPLETE", False, "taskcards.json not found")

# IV-03: Wave 8 sprint-closeout evidence_bundle not PENDING
sc8 = json.loads((WAVE8_REPORT / "sprint-closeout.json").read_text())
bundle = sc8.get("evidence_bundle", {})
bundle_obj = bundle.get("objective", "") if isinstance(bundle, dict) else str(bundle)
check("IV-03: Wave8 evidence_bundle not PENDING",
      "PENDING" not in bundle_obj.upper() or "COMPLETE" in bundle_obj.upper(),
      f"bundle_objective={bundle_obj[:80]}")

# IV-04: Wave 8 packages all have package-manifest.json
missing_pm = []
for k in W8_KEYS:
    family, slug = k.split("/")
    if not (WAVE8_BASE / family / slug / "package-manifest.json").exists():
        missing_pm.append(k)
check("IV-04: Wave8 packages have package-manifest.json", len(missing_pm) == 0, f"missing={missing_pm}")

# IV-05: Wave 8 packages output-validation PASS
w8_fail = []
for k in W8_KEYS:
    family, slug = k.split("/")
    ov_path = WAVE8_BASE / family / slug / "output-validation.json"
    if ov_path.exists():
        ov = json.loads(ov_path.read_text())
        if ov.get("verdict") != "PASS":
            w8_fail.append(k)
    else:
        w8_fail.append(k)
check("IV-05: Wave8 packages output-validation PASS", len(w8_fail) == 0, f"fail={w8_fail}")

# IV-06: canonical_primary_entries = 33
total_canonical = 0
for yaml_file in sorted(REGISTRY_DIR.glob("*.yaml")):
    try:
        content = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        for entry in content.get("plugins", []):
            if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
                total_canonical += 1
    except Exception:
        pass
check("IV-06: canonical_primary_entries = 33", total_canonical == 33, f"actual={total_canonical}")

# IV-07: 12 Wave 9 entries are CANONICAL_IDENTITY_VERIFIED
not_verified = []
for slug in W9_SLUGS:
    family = W9_FAMILIES[slug]
    yaml_path = REGISTRY_DIR / f"{family}.yaml"
    content = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    entry = next((e for e in content.get("plugins", []) if e.get("plugin_slug") == slug), None)
    if not entry or entry.get("identity_status") != "CANONICAL_IDENTITY_VERIFIED":
        not_verified.append(f"{family}/{slug}")
check("IV-07: 12 Wave9 entries are CANONICAL_IDENTITY_VERIFIED", len(not_verified) == 0,
      f"not_verified={not_verified}")

# IV-08: Wave 9 dryrun packages all exist
w9_missing = [f"{W9_FAMILIES[s]}/{s}" for s in W9_SLUGS if not (WAVE9_BASE / W9_FAMILIES[s] / s).exists()]
check("IV-08: Wave9 dryrun packages all exist", len(w9_missing) == 0, f"missing={w9_missing}")

# IV-09: Wave 9 packages have Program.cs
w9_no_cs = [f"{W9_FAMILIES[s]}/{s}" for s in W9_SLUGS
            if (WAVE9_BASE / W9_FAMILIES[s] / s).exists()
            and not (WAVE9_BASE / W9_FAMILIES[s] / s / "Program.cs").exists()]
check("IV-09: Wave9 packages have Program.cs", len(w9_no_cs) == 0, f"missing_cs={w9_no_cs}")

# IV-10: Wave 9 packages output-validation PASS
w9_not_pass = []
for slug in W9_SLUGS:
    family = W9_FAMILIES[slug]
    ov_path = WAVE9_BASE / family / slug / "output-validation.json"
    if ov_path.exists():
        ov = json.loads(ov_path.read_text())
        if ov.get("verdict") != "PASS":
            w9_not_pass.append(f"{family}/{slug}")
    else:
        w9_not_pass.append(f"{family}/{slug} (no ov)")
check("IV-10: Wave9 packages output-validation PASS", len(w9_not_pass) == 0, f"not_pass={w9_not_pass}")

# IV-11: display_plugin_name for all CANONICAL_IDENTITY_VERIFIED (WARNING)
missing_dn = []
for yaml_file in sorted(REGISTRY_DIR.glob("*.yaml")):
    try:
        content = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        family = content.get("family", yaml_file.stem)
        for entry in content.get("plugins", []):
            if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
                if not entry.get("display_plugin_name"):
                    missing_dn.append(f"{family}/{entry.get('plugin_slug', '?')}")
    except Exception:
        pass
check("IV-11: All CANONICAL_IDENTITY_VERIFIED have display_plugin_name", len(missing_dn) == 0,
      f"missing={missing_dn}", "WARNING")

# IV-12: FPP validator module exists
check("IV-12: FPP validator module exists",
      (ROOT / "src/plugin_examples/fixture_factory/full_package_proof_validator.py").exists())

# IV-13: CCV validator module exists
check("IV-13: CCV validator module exists",
      (ROOT / "src/plugin_examples/fixture_factory/closeout_consistency_validators.py").exists())

# IV-14: FPP test file exists
check("IV-14: FPP test file exists",
      (ROOT / "tests/unit/test_full_package_proof_validator.py").exists())

# IV-15: CCV test file exists
check("IV-15: CCV test file exists",
      (ROOT / "tests/unit/test_closeout_consistency_validators.py").exists())

# IV-16: Publication matrix v2 exists
matrix_path = REPORT / "publication-readiness/unified-publication-matrix-v2.json"
check("IV-16: Publication matrix v2 exists", matrix_path.exists())

# IV-17: Publication matrix has 16 PUBLICATION_READY entries
if matrix_path.exists():
    matrix = json.loads(matrix_path.read_text())
    pub_count = matrix.get("publication_ready_count", 0)
    check("IV-17: Publication matrix has 16 PUBLICATION_READY", pub_count == 16, f"actual={pub_count}")

# IV-18: Protected files unchanged
protected = {
    "pipeline/configs/families/cells.yml": "28c51b79f8dac9e7",
    "pipeline/configs/families/words.yml": "ef21e9e514386a7e",
    "pipeline/configs/families/pdf.yml": "de889ed24b3bc3a0",
    "pipeline/configs/families/slides.yml": "4eec3d74e7c9cca5",
    "pipeline/configs/families/email.yml": "3e872e96519168ba",
    "pipeline/configs/families/diagram.yml": "306c16e4acdf4802",
    "pipeline/format-authority/manifest.json": "3e96754355d7124f",
}
changed = []
for fpath, expected_hash in protected.items():
    actual = hashlib.sha256((ROOT / fpath).read_bytes()).hexdigest()[:16]
    if actual != expected_hash:
        changed.append(f"{fpath}: expected={expected_hash} actual={actual}")
check("IV-18: Protected files unchanged", len(changed) == 0, f"changed={changed}")

# IV-19: Wave 9 lanes 0-I all COMPLETE
ll9 = json.loads((REPORT / "coordinator/lane-ledger.json").read_text())
not_complete_9 = [l for l in ll9.get("lanes", [])
                  if l["lane"] not in ("J", "K") and l.get("status") != "COMPLETE"]
check("IV-19: Wave9 lanes 0-I all COMPLETE", len(not_complete_9) == 0,
      f"not_complete={[l['lane'] for l in not_complete_9]}")

# IV-20: Wave 9 taskcards TC-00..TC-0I all COMPLETE
tc9 = json.loads((REPORT / "taskcards/taskcards.json").read_text())
not_complete_tc9 = [t for t in tc9.get("taskcards", [])
                    if t["id"] not in ("TC-0J", "TC-0K") and t.get("status") != "COMPLETE"]
check("IV-20: Wave9 taskcards TC-00..TC-0I all COMPLETE", len(not_complete_tc9) == 0,
      f"not_complete={[t['id'] for t in not_complete_tc9]}")

# IV-21: FPP test log exists
check("IV-21: FPP test log exists", (REPORT / "tooling/fpp-test-log.txt").exists())

# IV-22: CCV test log exists
check("IV-22: CCV test log exists", (REPORT / "validators/ccv-test-log.txt").exists())

# IV-23: Wave 9 build-results 12 BUILT
w9_br_path = REPORT / "dryrun/wave9-build-results.json"
if w9_br_path.exists():
    w9_br = json.loads(w9_br_path.read_text())
    total_built = w9_br.get("built", w9_br.get("total_built", 0))
    check("IV-23: Wave9 build-results 12 BUILT", total_built == 12, f"actual={total_built}")
else:
    check("IV-23: Wave9 build-results 12 BUILT", False, "file not found")

# IV-24: Wave 8 state verification doc exists
check("IV-24: Wave8 state verification doc exists",
      (REPORT / "wave8-closeout/wave8-state-verification.md").exists())

# IV-25: canonical-package-ledger.json exists
check("IV-25: canonical-package-ledger.json exists",
      (REPORT / "state/canonical-package-ledger.json").exists())

# IV-26: wave10-next-queue.json exists
check("IV-26: wave10-next-queue.json exists",
      (REPORT / "state/wave10-next-queue.json").exists())

# IV-27: Wave 9 packages have source-provenance.json
w9_no_sp = [f"{W9_FAMILIES[s]}/{s}" for s in W9_SLUGS
            if (WAVE9_BASE / W9_FAMILIES[s] / s).exists()
            and not (WAVE9_BASE / W9_FAMILIES[s] / s / "source-provenance.json").exists()]
check("IV-27: Wave9 packages have source-provenance.json", len(w9_no_sp) == 0, f"missing={w9_no_sp}")

# IV-28: Wave 9 packages have package-manifest.json
w9_no_pm = [f"{W9_FAMILIES[s]}/{s}" for s in W9_SLUGS
            if (WAVE9_BASE / W9_FAMILIES[s] / s).exists()
            and not (WAVE9_BASE / W9_FAMILIES[s] / s / "package-manifest.json").exists()]
check("IV-28: Wave9 packages have package-manifest.json", len(w9_no_pm) == 0, f"missing={w9_no_pm}")

# IV-29: No legacy aliases appear as publication-ready in matrix
if matrix_path.exists():
    matrix = json.loads(matrix_path.read_text())
    all_legacy = set()
    for yaml_file in sorted(REGISTRY_DIR.glob("*.yaml")):
        try:
            content = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
            family = content.get("family", yaml_file.stem)
            for entry in content.get("plugins", []):
                for alias in entry.get("legacy_aliases", []):
                    all_legacy.add(f"{family}/{alias}")
        except Exception:
            pass
    legacy_in_ready = [r["package_key"] for r in matrix.get("rows", [])
                       if r.get("publication_status") == "PUBLICATION_READY"
                       and r["package_key"] in all_legacy]
    check("IV-29: No legacy aliases in PUBLICATION_READY matrix", len(legacy_in_ready) == 0,
          f"found={legacy_in_ready}")

# Summary
pass_count = sum(1 for c in checks if c["status"] == "PASS")
fail_count = sum(1 for c in checks if c["status"] == "FAIL")
warn_count = sum(1 for c in checks if c["status"] == "WARN")
print(f"IV Results: {pass_count} PASS / {fail_count} FAIL / {warn_count} WARN / {len(checks)} total")
for e in errors:
    print(f"  {e}")

iv_verdict = "IV_PASS" if fail_count == 0 else "IV_FAIL"
result = {
    "sprint": SPRINT,
    "date": "2026-06-05",
    "checks_total": len(checks),
    "checks_pass": pass_count,
    "checks_fail": fail_count,
    "checks_warn": warn_count,
    "verdict": iv_verdict,
    "errors": errors,
    "checks": checks,
}
(REPORT / "iv/iv-results.json").write_text(json.dumps(result, indent=2))
print(f"Written: iv/iv-results.json  verdict={iv_verdict}")
