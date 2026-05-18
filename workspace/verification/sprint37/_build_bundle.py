"""Build Sprint 37 evidence bundle (two-pass ZIP, V7 contract, 69 categories)."""
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
SPRINT37_DIR = Path(__file__).parent
STAGING = SPRINT37_DIR / "bundle-staging"

sys.path.insert(0, str(ROOT / "src"))

RUN_ID = "sprint37-all-lowcode-launch-execution-and-version-drift-20260518-195241"
BUNDLE_NAME = f"{RUN_ID}.zip"
BUNDLE_DIR = ROOT / "workspace/verification"
BUNDLE_PATH = BUNDLE_DIR / BUNDLE_NAME

# ── Use V7 if available, else V6 ───────────────────────────────────────────
try:
    from plugin_examples.evidence_contract import (
        COMBINED_CATEGORIES_V7,
        StrictEvidenceContractV7,
    )
    categories = COMBINED_CATEGORIES_V7
    contract_version = "7.0.0"
    validator = StrictEvidenceContractV7()
    print(f"Using V7 contract ({len(categories)} categories)")
except ImportError:
    from plugin_examples.evidence_contract import (
        COMBINED_CATEGORIES_V6,
        StrictEvidenceContractV6,
    )
    categories = COMBINED_CATEGORIES_V6
    contract_version = "6.0.0"
    validator = StrictEvidenceContractV6()
    print(f"Using V6 contract ({len(categories)} categories)")

# ── Re-populate staging (idempotent) ──────────────────────────────────────
print("\nRe-populating bundle-staging...")
result = subprocess.run(
    [sys.executable, str(SPRINT37_DIR / "_populate_bundle_staging.py")],
    capture_output=True, text=True, cwd=str(ROOT)
)
for line in result.stdout.strip().splitlines():
    print(f"  {line}")
if result.returncode != 0:
    print(f"  STDERR: {result.stderr[:500]}")

staged_files = sorted(f for f in STAGING.iterdir() if f.is_file())
print(f"\nStaged file count: {len(staged_files)}")


def build_zip(bundle_bytes_override: int = 0) -> int:
    """Build ZIP and return actual byte size."""
    # Update validation report with current size before zipping
    validation_path = STAGING / "bundle-contract-validation-report.json"
    bootstrap = json.loads(validation_path.read_text(encoding="utf-8"))
    bootstrap["bundle_file"] = BUNDLE_NAME
    bootstrap["bundle_bytes"] = bundle_bytes_override
    validation_path.write_text(json.dumps(bootstrap, indent=2), encoding="utf-8")

    with zipfile.ZipFile(BUNDLE_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(STAGING.iterdir()):
            if f.is_file():
                zf.write(f, f.name)
    return BUNDLE_PATH.stat().st_size


# ── Pass 1 ─────────────────────────────────────────────────────────────────
print("\nPass 1: building ZIP to measure size...")
size_pass1 = build_zip(bundle_bytes_override=0)
print(f"  Pass 1 size: {size_pass1} bytes")

# ── Pass 2 ─────────────────────────────────────────────────────────────────
print("Pass 2: rebuilding ZIP with correct size embedded...")
size_pass2 = build_zip(bundle_bytes_override=size_pass1)
print(f"  Pass 2 size: {size_pass2} bytes")

# ── Run actual V7 validator ────────────────────────────────────────────────
print("\nRunning StrictEvidenceContractV7 validator...")
contract_result = validator.validate_zip(BUNDLE_PATH)
found_count = len(contract_result.categories_found)
missing_cats = contract_result.categories_missing

print(f"  ZIP entries: {contract_result.file_count}")
print(f"  Categories found: {found_count}/{len(categories)}")
if missing_cats:
    print(f"  Missing ({len(missing_cats)}):")
    for m in missing_cats[:30]:
        print(f"    - {m}")
content_failures = [f for f in contract_result.failures if "Secret" not in f and "verdict" not in f.lower() and "category" not in f.lower()]
if content_failures:
    print(f"  Content failures:")
    for f in content_failures[:10]:
        print(f"    * {f}")

# ── Update validation report with real results ─────────────────────────────
validation_report = {
    "sprint": "sprint37",
    "run_id": RUN_ID,
    "contract_version": contract_version,
    "passed": contract_result.passed,
    "bundle_bytes": size_pass2,
    "bundle_file": BUNDLE_NAME,
    "categories_total": len(categories),
    "categories_found": found_count,
    "categories_missing": missing_cats,
    "zip_entries": contract_result.file_count,
    "failures": contract_result.failures[:50] if contract_result.failures else [],
    "note": "Two-pass build using StrictEvidenceContractV7.",
}
(STAGING / "bundle-contract-validation-report.json").write_text(
    json.dumps(validation_report, indent=2), encoding="utf-8"
)

# ── Pass 3: final rebuild with completed validation report ──────────────────
print("\nPass 3: final ZIP rebuild with completed validation report...")
size_final = build_zip(bundle_bytes_override=size_pass2)

with zipfile.ZipFile(BUNDLE_PATH, "r") as zf:
    final_entry_count = len(zf.namelist())
print(f"  Final size: {size_final} bytes")
print(f"  Final entries: {final_entry_count}")

# ── Print result ───────────────────────────────────────────────────────────
print("\n" + "=" * 70)
bundle_verdict = "BUNDLE_CONTRACT_PASSED" if contract_result.passed else f"BUNDLE_CONTRACT_FAILED ({len(missing_cats)} missing)"
print(f"Bundle verdict: {bundle_verdict}")
print(f"Contract: V{contract_version[0]} ({len(categories)} categories), {found_count} found")
print(f"ZIP entries: {final_entry_count}")
print(f"Size: {size_final} bytes")
print(f"\nAbsolute path: {BUNDLE_PATH.resolve()}")
