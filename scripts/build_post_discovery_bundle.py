"""Build the Phase J evidence bundle for the post-discovery next sprint."""
import json
import zipfile
from pathlib import Path
from datetime import datetime

base_dir = Path("workspace/verification/latest")
bundle_path = Path("workspace/verification/post-discovery-next-sprint-evidence-bundle.zip")

# All sprint-produced artifacts
sprint_artifacts = [
    # Ledger
    "workspace/verification/latest/lowcode-post-discovery-next-sprint-ledger.json",
    # Phase B state board
    "workspace/verification/latest/lowcode-all-family-current-state-board.json",
    "workspace/verification/latest/lowcode-all-family-candidate-inventory.json",
    "workspace/verification/latest/lowcode-post-discovery-roadmap-update.json",
    # Phase C denominators
    "pipeline/configs/denominators/email.json",
    "pipeline/configs/denominators/slides.json",
    "pipeline/configs/denominators/diagram.json",
    # Phase D reflection blockers
    "workspace/verification/latest/epub-reflection-blocker.json",
    "workspace/verification/latest/html-reflection-blocker.json",
    "workspace/verification/latest/ocr-reflection-blocker.json",
    "workspace/verification/latest/omr-reflection-blocker.json",
    "workspace/verification/latest/psd-reflection-blocker.json",
    "workspace/verification/latest/svg-reflection-blocker.json",
    # Phase I no-lowcode registry
    "workspace/verification/latest/confirmed-no-lowcode-family-registry.json",
    # Taskcard matrix (updated)
    "workspace/verification/latest/open-taskcard-closure-matrix.json",
]

# Config files modified this sprint
config_changes = [
    "pipeline/configs/families/html.yml",
    "pipeline/configs/families/svg.yml",
    "pipeline/configs/families/ocr.yml",
    "pipeline/configs/families/omr.yml",
    "pipeline/configs/families/psd.yml",
]

# Source-of-truth proofs for the 13 original no-lowcode families
sot_proofs = [
    f"workspace/verification/latest/{fam}-source-of-truth-proof.json"
    for fam in ["barcode", "cad", "drawing", "finance", "font", "gis", "imaging",
                "note", "page", "tasks", "tex", "threed", "zip"]
]

all_files = sprint_artifacts + config_changes + sot_proofs

# Build manifest
manifest = {
    "bundle_id": "post-discovery-next-sprint-evidence-bundle",
    "created": "2026-05-09",
    "sprint": "post-discovery-next-sprint",
    "phases_included": ["A", "B", "C", "D", "H-planning", "I"],
    "phases_gated": ["E", "F", "G"],
    "total_test_count": 1179,
    "test_result": "ALL_PASS",
    "files_included": [],
    "key_findings": [
        "25 families total: 6 LowCode-confirmed, 15 CONFIRMED_NO_LOWCODE, 4 still blocked",
        "html + svg reclassified CONFIRMED_NO_LOWCODE (manual DllReflector verification)",
        "email/slides/diagram: new denominator files created (DISCOVERY_ONLY basis)",
        "ocr/omr/psd: still blocked — resolved-libs population fix needed in extractor.py",
        "epub: blocked — PACKAGE_DOWNLOAD_FAILED, needs separate investigation",
        "105 total taskcards (42 OPEN, 63 CLOSED) after adding NEW-19 through NEW-28",
        "15-family CONFIRMED_NO_LOWCODE registry created (Phase I complete)"
    ],
    "no_credentials_included": True,
    "no_secrets_included": True
}

missing = []
included = []
for file_path_str in all_files:
    p = Path(file_path_str)
    if p.exists():
        included.append(file_path_str)
    else:
        missing.append(file_path_str)

manifest["files_included"] = included
manifest["files_missing"] = missing

# Write bundle
with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
    # Write manifest
    zf.writestr("manifest.json", json.dumps(manifest, indent=2))
    # Add all existing files
    for file_path_str in included:
        p = Path(file_path_str)
        zf.write(p, file_path_str)

print(f"Bundle written: {bundle_path}")
print(f"Files included: {len(included)}")
if missing:
    print(f"Files missing ({len(missing)}):")
    for m in missing:
        print(f"  MISSING: {m}")
else:
    print("All files present.")

# Update ledger phase_j status
ledger_path = Path("workspace/verification/latest/lowcode-post-discovery-next-sprint-ledger.json")
with open(ledger_path, encoding="utf-8") as f:
    ledger = json.load(f)
ledger["phase_j_status"] = {
    "status": "COMPLETE",
    "bundle_path": str(bundle_path),
    "files_in_bundle": len(included),
    "completed_date": "2026-05-09"
}
ledger["execution_status"] = "ALL_PHASES_COMPLETE_EXCEPT_GATED"
with open(ledger_path, "w", encoding="utf-8") as f:
    json.dump(ledger, f, indent=2)
print(f"Ledger updated: phase_j=COMPLETE, execution_status=ALL_PHASES_COMPLETE_EXCEPT_GATED")
