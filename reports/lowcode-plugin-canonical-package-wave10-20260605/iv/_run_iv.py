"""
Lane H: Independent Verification
Sprint: lowcode-plugin-canonical-package-wave10-20260605
"""
import json
import yaml
import hashlib
from pathlib import Path

ROOT = Path(__file__).parents[3]
SPRINT = "lowcode-plugin-canonical-package-wave10-20260605"
WAVE9_SPRINT = "lowcode-plugin-canonical-package-wave9-20260605"
REPORT = ROOT / f"reports/{SPRINT}"
WAVE9_REPORT = ROOT / f"reports/{WAVE9_SPRINT}"
REGISTRY_DIR = ROOT / "pipeline/plugin-code-registry/family"
W10_BASE = REPORT / "dryrun/examples"
W9_BASE = WAVE9_REPORT / "dryrun/examples"
WAVE8_SPRINT = "lowcode-plugin-canonical-primary-wave8-20260605"
W8_BASE = ROOT / f"reports/{WAVE8_SPRINT}/wave8/dryrun/examples"

checks = []
errors = []

W10_SLUGS = {
    "barcode/1d-barcode-writer": "barcode",
    "barcode/1d-barcode-reader": "barcode",
    "barcode/2d-barcode-writer": "barcode",
    "barcode/2d-barcode-reader": "barcode",
    "drawing/convert-drawing": "drawing",
    "drawing/create-drawing": "drawing",
    "finance/convert-xbrl": "finance",
    "ocr/scan-document": "ocr",
    "ocr/image-text-finder": "ocr",
    "ocr/invoice-to-text": "ocr",
    "ocr/photo-to-text": "ocr",
    "ocr/table-to-text": "ocr",
    "psd/animation-maker": "psd",
    "psd/photo-processor": "psd",
    "svg/svg-to-image-converter": "svg",
    "tex/latex-figure-renderer": "tex",
    "zip/compress-files": "zip",
}

W9_SLUGS = {
    "imaging/image-compressor": "imaging",
    "imaging/image-cropper": "imaging",
    "imaging/image-filters": "imaging",
    "imaging/image-merger": "imaging",
    "imaging/add-watermark": "imaging",
    "imaging/image-rotator": "imaging",
    "tasks/project-to-pdf-converter": "tasks",
    "tasks/mpp-to-excel": "tasks",
    "html/html-to-docx-converter": "html",
    "html/html-to-image-converter": "html",
    "note/convert-onenote-to-word": "note",
    "note/convert-onenote-to-image": "note",
}

W8_SLUGS = {
    "html/html-to-pdf-converter": "html",
    "imaging/image-converter": "imaging",
    "imaging/image-resizer": "imaging",
    "note/convert-onenote-to-pdf": "note",
}

PROTECTED = {
    "pipeline/configs/families/cells.yml": "28c51b79f8dac9e7",
    "pipeline/configs/families/words.yml": "ef21e9e514386a7e",
    "pipeline/configs/families/pdf.yml": "de889ed24b3bc3a0",
    "pipeline/configs/families/slides.yml": "4eec3d74e7c9cca5",
    "pipeline/configs/families/email.yml": "3e872e96519168ba",
    "pipeline/configs/families/diagram.yml": "306c16e4acdf4802",
    "pipeline/format-authority/manifest.json": "3e96754355d7124f",
}


def check(name, passed, detail="", severity="ERROR"):
    status = "PASS" if passed else ("FAIL" if severity == "ERROR" else "WARN")
    checks.append({"check": name, "status": status, "detail": detail, "severity": severity})
    if not passed and severity == "ERROR":
        errors.append(f"FAIL: {name} — {detail}")
    return passed


# IV-01: Wave 9 state imported correctly
w9_imported = REPORT / "wave9-closeout/wave9-imported-state.json"
if w9_imported.exists():
    w9 = json.loads(w9_imported.read_text())
    verdict_val = w9.get("wave9_closeout_verdict") or w9.get("verdict")
    check("IV-01: Wave9 imported state verdict is WAVE9_CLOSED",
          verdict_val == "WAVE9_CLOSED", f"verdict={verdict_val}")
else:
    check("IV-01: Wave9 imported state exists", False, "wave9-imported-state.json not found")

# IV-02: Wave 9 git proof exists
check("IV-02: Wave9 git proof file exists", (REPORT / "wave9-closeout/wave9-git-proof.md").exists())

# IV-03: Registry inventory total = 70
inv_path = REPORT / "registry/full-registry-inventory.json"
inv = json.loads(inv_path.read_text(encoding="utf-8"))
check("IV-03: Registry inventory total = 70", inv.get("total_entries") == 70,
      f"actual={inv.get('total_entries')}")

# IV-04: Registry CANONICAL_IDENTITY_VERIFIED = 43
civ_count = inv["by_status"].get("CANONICAL_IDENTITY_VERIFIED", 0)
check("IV-04: CANONICAL_IDENTITY_VERIFIED = 43", civ_count == 43, f"actual={civ_count}")

# IV-05: Registry SLUG_ALIAS_REQUIRED = 5
sar_count = inv["by_status"].get("SLUG_ALIAS_REQUIRED", 0)
check("IV-05: SLUG_ALIAS_REQUIRED = 5", sar_count == 5, f"actual={sar_count}")

# IV-06: Registry MISSING_CANONICAL_URL = 22
mcu_count = inv["by_status"].get("MISSING_CANONICAL_URL", 0)
check("IV-06: MISSING_CANONICAL_URL = 22", mcu_count == 22, f"actual={mcu_count}")

# IV-07: Actual YAML canonical count = 43
actual_canonical = 0
for yf in sorted(REGISTRY_DIR.glob("*.yaml")):
    try:
        content = yaml.safe_load(yf.read_text(encoding="utf-8"))
        for entry in content.get("plugins", []):
            if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
                actual_canonical += 1
    except Exception:
        pass
check("IV-07: Actual YAML canonical count = 43", actual_canonical == 43, f"actual={actual_canonical}")

# IV-08: Wave 10 build-results all 17 BUILT
br_path = REPORT / "dryrun/wave10-build-results.json"
br = json.loads(br_path.read_text())
not_built = [r["key"] for r in br["results"] if r["status"] not in ("BUILT", "BUILT_WITH_WARNINGS")]
check("IV-08: Wave10 build-results all 17 BUILT", len(not_built) == 0, f"not_built={not_built}")

# IV-09: All Wave 10 packages exist on disk
w10_missing = [k for k, fam in W10_SLUGS.items()
               if not (W10_BASE / fam / k.split("/")[1]).exists()]
check("IV-09: All 17 Wave10 packages exist on disk", len(w10_missing) == 0,
      f"missing={w10_missing}")

# IV-10: All Wave 10 packages have Program.cs
w10_no_cs = [k for k, fam in W10_SLUGS.items()
             if (W10_BASE / fam / k.split("/")[1]).exists()
             and not (W10_BASE / fam / k.split("/")[1] / "Program.cs").exists()]
check("IV-10: All Wave10 packages have Program.cs", len(w10_no_cs) == 0, f"missing={w10_no_cs}")

# IV-11: All Wave 10 packages have output-validation.json PASS
w10_not_pass = []
for k, fam in W10_SLUGS.items():
    slug = k.split("/")[1]
    ov_path = W10_BASE / fam / slug / "output-validation.json"
    if ov_path.exists():
        ov = json.loads(ov_path.read_text())
        if ov.get("verdict") != "PASS":
            w10_not_pass.append(f"{k} (verdict={ov.get('verdict')})")
    else:
        w10_not_pass.append(f"{k} (no ov)")
check("IV-11: All Wave10 packages output-validation PASS", len(w10_not_pass) == 0,
      f"not_pass={w10_not_pass}")

# IV-12: All Wave 10 packages have source-provenance.json
w10_no_sp = [k for k, fam in W10_SLUGS.items()
             if (W10_BASE / fam / k.split("/")[1]).exists()
             and not (W10_BASE / fam / k.split("/")[1] / "source-provenance.json").exists()]
check("IV-12: All Wave10 packages have source-provenance.json", len(w10_no_sp) == 0,
      f"missing={w10_no_sp}")

# IV-13: All Wave 10 packages have package-manifest.json
w10_no_pm = [k for k, fam in W10_SLUGS.items()
             if (W10_BASE / fam / k.split("/")[1]).exists()
             and not (W10_BASE / fam / k.split("/")[1] / "package-manifest.json").exists()]
check("IV-13: All Wave10 packages have package-manifest.json", len(w10_no_pm) == 0,
      f"missing={w10_no_pm}")

# IV-14: Publication matrix v3 exists
matrix_path = REPORT / "publication-readiness/unified-publication-matrix-v3.json"
check("IV-14: Publication matrix v3 exists", matrix_path.exists())

# IV-15: Matrix v3 covers 70 entries
if matrix_path.exists():
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    row_count = len(matrix.get("rows", []))
    check("IV-15: Matrix v3 covers 70 entries", row_count == 70, f"actual={row_count}")

# IV-16: Matrix v3 PUBLICATION_READY = 16
if matrix_path.exists():
    pub_ready = matrix.get("publication_ready_count", 0)
    check("IV-16: Matrix v3 PUBLICATION_READY = 16", pub_ready == 16, f"actual={pub_ready}")

# IV-17: Matrix v3 PUBLICATION_CANDIDATE_LOCAL_CLEAN = 17
if matrix_path.exists():
    pub_candidate = matrix.get("publication_candidate_local_clean_count", 0)
    check("IV-17: Matrix v3 PUBLICATION_CANDIDATE_LOCAL_CLEAN = 17",
          pub_candidate == 17, f"actual={pub_candidate}")

# IV-18: Protected files unchanged
changed = []
for fpath, expected in PROTECTED.items():
    actual = hashlib.sha256((ROOT / fpath).read_bytes()).hexdigest()[:16]
    if actual != expected:
        changed.append(f"{fpath}: expected={expected} actual={actual}")
check("IV-18: Protected files unchanged", len(changed) == 0, f"changed={changed}")

# IV-19: CCV validator has 18 rules
ccv_path = ROOT / "src/plugin_examples/fixture_factory/closeout_consistency_validators.py"
ccv_text = ccv_path.read_text(encoding="utf-8")
ccv_rules = [f"CCV-{i:02d}" for i in range(1, 19)]
missing_rules = [r for r in ccv_rules if r not in ccv_text]
check("IV-19: CCV validator has all 18 rules", len(missing_rules) == 0,
      f"missing={missing_rules}")

# IV-20: CCV test file has 64 tests
ccv_test_path = ROOT / "tests/unit/test_closeout_consistency_validators.py"
ccv_test_text = ccv_test_path.read_text(encoding="utf-8")
ccv_test_count = ccv_test_text.count("def test_")
check("IV-20: CCV test file has 64 tests", ccv_test_count == 64, f"actual={ccv_test_count}")

# IV-21: CCV validator results file exists
check("IV-21: CCV validator results file exists",
      (REPORT / "validators/wave10-validator-results.json").exists())

# IV-22: CCV test log exists
check("IV-22: CCV test log exists", (REPORT / "validators/ccv-test-log.txt").exists())

# IV-23: FPP validator exists
check("IV-23: FPP validator module exists",
      (ROOT / "src/plugin_examples/fixture_factory/full_package_proof_validator.py").exists())

# IV-24: Package-proof ledger exists with 16 PASS entries
proof_path = REPORT / "package-proof/full-publication-ready-proof-ledger.json"
if proof_path.exists():
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    # check total proven
    total_entries = len(proof.get("results", []))
    check("IV-24: Package-proof ledger covers 16 entries", total_entries == 16,
          f"actual={total_entries}")
else:
    check("IV-24: Package-proof ledger exists", False, "file not found")

# IV-25: Wave 9 packages still intact on disk (spot check 3)
w9_spot = ["imaging/image-compressor", "tasks/mpp-to-excel", "html/html-to-image-converter"]
w9_missing = []
for k in w9_spot:
    fam, slug = k.split("/")
    if not (W9_BASE / fam / slug / "Program.cs").exists():
        w9_missing.append(k)
check("IV-25: Wave9 packages spot-check intact", len(w9_missing) == 0, f"missing={w9_missing}")

# IV-26: Wave 8 packages still intact (spot check 2)
w8_spot = ["html/html-to-pdf-converter", "imaging/image-converter"]
w8_missing = []
for k in w8_spot:
    fam, slug = k.split("/")
    if not (W8_BASE / fam / slug / "Program.cs").exists():
        w8_missing.append(k)
check("IV-26: Wave8 packages spot-check intact", len(w8_missing) == 0, f"missing={w8_missing}")

# IV-27: Wave10 migration ledger exists
check("IV-27: Wave10 migration ledger exists",
      (REPORT / "registry/wave10-migration-ledger.json").exists())

# IV-28: Wave10 migration canonical_primary_after = 43
ml_path = REPORT / "registry/wave10-migration-ledger.json"
if ml_path.exists():
    ml = json.loads(ml_path.read_text(encoding="utf-8"))
    after = ml.get("canonical_primary_after", 0)
    check("IV-28: Migration ledger canonical_primary_after = 43", after == 43, f"actual={after}")

# IV-29: State ledger exists
check("IV-29: State canonical-package-ledger.json exists",
      (REPORT / "state/canonical-package-ledger.json").exists())

# IV-30: Wave11 queue exists
check("IV-30: Wave11 next queue exists",
      (REPORT / "state/wave11-next-queue.json").exists())

# IV-31: Wave11 queue has 10 candidates
q_path = REPORT / "state/wave11-next-queue.json"
if q_path.exists():
    q = json.loads(q_path.read_text(encoding="utf-8"))
    q_count = len(q.get("wave11_queue", {}).get("candidates", []))
    check("IV-31: Wave11 queue has 10 candidates", q_count == 10, f"actual={q_count}")

# IV-32: No legacy aliases appear as PUBLICATION_READY or PUBLICATION_CANDIDATE in matrix
if matrix_path.exists():
    all_legacy = set()
    for yf in sorted(REGISTRY_DIR.glob("*.yaml")):
        try:
            content = yaml.safe_load(yf.read_text(encoding="utf-8"))
            family = content.get("family", yf.stem)
            for entry in content.get("plugins", []):
                for alias in entry.get("legacy_aliases", []):
                    all_legacy.add(f"{family}/{alias}")
        except Exception:
            pass
    pub_statuses = {"PUBLICATION_READY", "PUBLICATION_CANDIDATE_LOCAL_CLEAN"}
    alias_in_pub = [r["package_key"] for r in matrix.get("rows", [])
                    if r.get("publication_status") in pub_statuses
                    and r["package_key"] in all_legacy]
    check("IV-32: No legacy aliases in publication matrix", len(alias_in_pub) == 0,
          f"found={alias_in_pub}")

# IV-33: All CANONICAL_IDENTITY_VERIFIED entries have display_plugin_name (WARNING)
missing_dn = []
for yf in sorted(REGISTRY_DIR.glob("*.yaml")):
    try:
        content = yaml.safe_load(yf.read_text(encoding="utf-8"))
        family = content.get("family", yf.stem)
        for entry in content.get("plugins", []):
            if entry.get("identity_status") == "CANONICAL_IDENTITY_VERIFIED":
                if not entry.get("display_plugin_name"):
                    missing_dn.append(f"{family}/{entry.get('plugin_slug','?')}")
    except Exception:
        pass
check("IV-33: All CANONICAL_IDENTITY_VERIFIED have display_plugin_name",
      len(missing_dn) == 0, f"missing={missing_dn}", "WARNING")

# IV-34: Approval packet exists
check("IV-34: Approval-gated publication plan exists",
      (REPORT / "publication-packet/approval-gated-publication-plan.md").exists())

# IV-35: Skills file updated with Wave 10 state
skill_text = (ROOT / "skills/canonical-plugin-identity-and-aliasing.md").read_text(encoding="utf-8")
check("IV-35: Skills file mentions Wave 10 registry state",
      "Wave 10" in skill_text and "43" in skill_text, "skill file should reference Wave 10")

# IV-36: Wave10 dryrun build results all verdict PASS
not_pass_br = [r["key"] for r in br["results"] if r.get("verdict") != "PASS"]
check("IV-36: All Wave10 build results verdict=PASS", len(not_pass_br) == 0,
      f"not_pass={not_pass_br}")

# IV-37: CCV-15 rule is in CCV validator
check("IV-37: CCV-15 rule exists in validator", "CCV-15" in ccv_text)

# IV-38: CCV-16 rule is in CCV validator
check("IV-38: CCV-16 rule exists in validator", "CCV-16" in ccv_text)

# IV-39: CCV-17 rule is in CCV validator
check("IV-39: CCV-17 rule exists in validator", "CCV-17" in ccv_text)

# IV-40: CCV-40 rule is in CCV validator
check("IV-40: CCV-18 rule exists in validator", "CCV-18" in ccv_text)

# IV-41: registry inventory entries count = 70
inv_entry_count = len(inv.get("entries", []))
check("IV-41: Registry inventory entries count = 70", inv_entry_count == 70,
      f"actual={inv_entry_count}")

# IV-42: Wave10 dryrun packages have .csproj files
w10_no_csproj = []
for k, fam in W10_SLUGS.items():
    slug = k.split("/")[1]
    pkg_dir = W10_BASE / fam / slug
    if pkg_dir.exists():
        csproj_files = list(pkg_dir.glob("*.csproj"))
        if not csproj_files:
            w10_no_csproj.append(k)
check("IV-42: All Wave10 packages have .csproj file", len(w10_no_csproj) == 0,
      f"missing={w10_no_csproj}")

# IV-43: Lane A (Wave9 closeout) evidence complete
check("IV-43: Wave9 closeout dir has 3 evidence files",
      len(list((REPORT / "wave9-closeout").glob("*"))) >= 3,
      f"found={len(list((REPORT / 'wave9-closeout').glob('*')))}")

# IV-44: Lane B (registry) evidence exists
check("IV-44: Registry evidence dir complete",
      (REPORT / "registry/full-registry-inventory.json").exists() and
      (REPORT / "registry/wave10-migration-ledger.json").exists())

# IV-45: Lane C (package-proof) evidence exists
check("IV-45: Package-proof ledger evidence exists",
      (REPORT / "package-proof/full-publication-ready-proof-ledger.json").exists())

# IV-46: Lane D (dryrun) evidence exists
check("IV-46: Dryrun build results evidence exists",
      (REPORT / "dryrun/wave10-build-results.json").exists())

# IV-47: Lane E (validators) evidence exists
check("IV-47: Validator results evidence exists",
      (REPORT / "validators/wave10-validator-results.json").exists())

# IV-48: Lane F (publication) evidence exists
check("IV-48: Publication matrix v3 evidence exists",
      (REPORT / "publication-readiness/unified-publication-matrix-v3.json").exists() and
      (REPORT / "publication-packet/approval-gated-publication-plan.md").exists())

# IV-49: Lane G (state) evidence exists
check("IV-49: State ledger and wave11 queue evidence exists",
      (REPORT / "state/canonical-package-ledger.json").exists() and
      (REPORT / "state/wave11-next-queue.json").exists())

# IV-50: PIV validator module exists
check("IV-50: PIV validator module exists",
      (ROOT / "src/plugin_examples/fixture_factory/plugin_identity_validators.py").exists())

# IV-51: Source-provenance.json canonical_url matches registry for Wave10 spot check
spot_pkg = W10_BASE / "barcode" / "1d-barcode-writer"
if spot_pkg.exists() and (spot_pkg / "source-provenance.json").exists():
    sp = json.loads((spot_pkg / "source-provenance.json").read_text())
    expected_url = "https://products.aspose.net/barcode/1d-barcode-writer/"
    check("IV-51: barcode/1d-barcode-writer source-provenance canonical_url matches registry",
          sp.get("canonical_url") == expected_url,
          f"actual={sp.get('canonical_url')!r}")
else:
    check("IV-51: barcode/1d-barcode-writer source-provenance.json exists", False,
          "source-provenance.json not found")

# IV-52: package-manifest.json package_key matches expected for Wave10 spot check
spot_pm = spot_pkg / "package-manifest.json"
if spot_pm.exists():
    pm = json.loads(spot_pm.read_text())
    check("IV-52: barcode/1d-barcode-writer package-manifest package_key correct",
          pm.get("package_key") == "barcode/1d-barcode-writer",
          f"actual={pm.get('package_key')!r}")
else:
    check("IV-52: barcode/1d-barcode-writer package-manifest.json exists", False)

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
(REPORT / "iv/iv-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(f"Written: iv/iv-results.json  verdict={iv_verdict}")
