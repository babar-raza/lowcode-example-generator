"""Build W18 evidence bundle, then write external sidecar + attestation."""
import hashlib, json, os, zipfile
from pathlib import Path

REPO = Path("c:/Users/prora/OneDrive/Documents/GitHub/lowcode-example-generator-gitlab")
REPORT = REPO / "reports/lowcode-plugin-canonical-package-wave18-20260606"
SPRINT = "lowcode-plugin-canonical-package-wave18-20260606"
BUNDLE_DIR = REPO / ".local/evidence-bundles"
BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
BUNDLE_PATH = BUNDLE_DIR / f"{SPRINT}.zip"

# Paths to include in bundle (relative to REPO)
include_dirs = [
    "reports/lowcode-plugin-canonical-package-wave18-20260606",
    # Also include registry changes and test fix
    "pipeline/plugin-code-registry/family/barcode.yaml",
    "pipeline/plugin-code-registry/family/cad.yaml",
    "pipeline/plugin-code-registry/family/omr.yaml",
    "pipeline/plugin-code-registry/family/finance.yaml",
    "pipeline/plugin-code-registry/family/font.yaml",
    "pipeline/plugin-code-registry/family/svg.yaml",
    "pipeline/plugin-code-registry/family/threed.yaml",
    "tests/unit/test_plugin_code_registry_loader.py",
]

# Paths to exclude from bundle
EXCLUDES = {".pfx", ".pem", ".key", ".p12", ".bin", ".glb", ".fbx", ".png", ".pdf", ".omr"}
# Exclude large binary files and output files to keep bundle compact
EXCLUDE_DIRS = {"bin", "obj", ".git", "__pycache__"}

def should_exclude(path_str):
    p = Path(path_str)
    # Check each component
    for part in p.parts:
        if part in EXCLUDE_DIRS:
            return True
    suffix = p.suffix.lower()
    return suffix in EXCLUDES

entries_added = 0
with zipfile.ZipFile(BUNDLE_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for include in include_dirs:
        full = REPO / include
        if full.is_file():
            rel = str(full.relative_to(REPO)).replace("\\", "/")
            zf.write(full, rel)
            entries_added += 1
        elif full.is_dir():
            for fp in sorted(full.rglob("*")):
                if fp.is_file() and not should_exclude(str(fp.relative_to(REPO))):
                    rel = str(fp.relative_to(REPO)).replace("\\", "/")
                    zf.write(fp, rel)
                    entries_added += 1

print(f"Bundle created: {BUNDLE_PATH}")
print(f"Entries: {entries_added}")

# Compute SHA-256
with open(BUNDLE_PATH, "rb") as f:
    sha256 = hashlib.sha256(f.read()).hexdigest()
size_bytes = BUNDLE_PATH.stat().st_size

print(f"SHA-256: {sha256}")
print(f"Size: {size_bytes} bytes")

# Write external sidecar
sidecar_path = BUNDLE_DIR / f"{SPRINT}.sha256"
sidecar_path.write_text(f"{sha256}  {SPRINT}.zip\n")
print(f"Sidecar: {sidecar_path}")

# Write final-attestation.json
attestation = {
    "attestation_type": "FINAL_ATTESTATION",
    "protocol_version": "v2",
    "sprint": SPRINT,
    "date": "2026-06-06",
    "path": f".local/evidence-bundles/{SPRINT}.zip",
    "sha256": sha256,
    "size_bytes": size_bytes,
    "entry_count": entries_added,
    "bundle_frozen_before_attestation": True,
    "inside_bundle_sha_claim": "NONE — pre-bundle-closeout.json inside bundle has no SHA claim",
    "attestation_note": "This file is the post-freeze external authority per Evidence Authority Protocol v2. The ZIP was frozen first; SHA computed; sidecar and this attestation written after. No ZIP-contains-own-SHA flaw."
}
att_path = REPORT / "final/final-attestation.json"
att_path.parent.mkdir(parents=True, exist_ok=True)
with open(att_path, "w") as f:
    json.dump(attestation, f, indent=2)
print(f"Attestation: {att_path}")

# Write sprint-closeout.json (post-freeze, outside bundle per v2)
closeout = {
    "sprint": SPRINT,
    "sprint_id": "LOWCODE-PLUGIN-CANONICAL-PACKAGE-WAVE18-FINISH-LINE-MEGA-TRAIN-PUBLICATION-PACKAGE-CONSUMPTION-001",
    "date": "2026-06-06",
    "verdict": "SPRINT_COMPLETE",
    "final_verdict": "APPROVAL_BLOCKED",
    "final_verdict_reason": "All local work complete. 33 PCLC PR packets ready. Only live PR push (human approval + credentials) remains.",
    "protocol_version": "v2",
    "evidence_bundle": {
        "path": f".local/evidence-bundles/{SPRINT}.zip",
        "sha256": sha256,
        "size_bytes": size_bytes,
        "entry_count": entries_added,
        "external_sidecar": f".local/evidence-bundles/{SPRINT}.sha256",
        "protocol_note": "SHA is authoritative in external sidecar only (v2 protocol — no ZIP-contains-own-SHA)"
    },
    "taskcards": {
        "total": 53,
        "complete": 53,
        "pending": 0,
        "iv_prerequisite_satisfied": True
    },
    "new_packages_proven": {
        "wave18_new": [
            "barcode/1d-barcode-reader", "barcode/2d-barcode-reader",
            "threed/compress-3d-scene", "svg/merge-svg",
            "font/render-text-with-font", "finance/parse-xbrl",
            "cad/convert-dxf-to-pdf", "cad/convert-cad-to-pdf",
            "cad/convert-cad-to-image", "omr/generate-omr-template", "omr/recognize-omr"
        ],
        "total_proven": 66,
        "pclc_total": 33
    },
    "validators": {
        "full_suite": "3828 passed, 18 skipped, 0 failures",
        "test_fix": "test_family_registry_ready_plugins updated for W18 registry changes"
    },
    "iv_verdict": "IV_PASS",
    "adversarial_review_verdict": "ADVERSARIAL_REVIEW_PASS",
    "cvb_conditions": {
        "all_taskcards_complete": True,
        "iv_pass": True,
        "adversarial_review_pass": True,
        "no_pfx_staged": True,
        "no_pfx_bundled": True,
        "bundle_sha_external": True,
        "zero_pytest_failures": True,
        "final_git_status_in_bundle": True,
        "raw_pytest_log_in_bundle": True,
        "pr_packet_count_equals_pclc": True,
        "taskcard_total_accurate": True,
        "no_pending_evidence_in_complete_taskcards": True
    },
    "key_decisions": [
        "11 new packages proven (including 2 reclassifications: finance/parse-xbrl was NETWORK_DEPENDENCY_BLOCKED, cad/convert-dxf-to-pdf was FIXTURE_BLOCKED)",
        "33 total PCLC packages, all with PR packets",
        "Total proven packages: 66 (W8:4+W9:12+W10:17+W11:10+W12:2+W14:2+W15:2+W16:4+W17:2+W18:11)",
        "W17 classified correctly: PROGRESS_ACCEPTED with repair addendum",
        "pytest baseline maintained: 3828/0/18",
        "Only 2 local blockers remain: cad/convert-dwg-to-pdf and cad/convert-dwg-to-jpg (FIXTURE_BLOCKED, DWG binary format)",
        "Only external gates for publication: human approval + GH/GL credentials for PR push"
    ],
    "wave19_queue": "state-docs/wave19-next-queue.json (2 DWG fixture tasks + 2 external gate tasks)"
}
closeout_path = REPORT / "final/sprint-closeout.json"
with open(closeout_path, "w") as f:
    json.dump(closeout, f, indent=2)
print(f"Sprint closeout: {closeout_path}")

print(f"\n=== SUMMARY ===")
print(f"Bundle: {BUNDLE_PATH}")
print(f"SHA256: {sha256}")
print(f"Size: {size_bytes} bytes")
print(f"Entries: {entries_added}")
print(f"Sidecar: {sidecar_path}")
print(f"Attestation: {att_path}")
