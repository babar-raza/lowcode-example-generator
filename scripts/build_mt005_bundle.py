"""Build the MT005 final evidence bundle."""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "lowcode-ai-publication-readiness-mega-train-20260520-064955"
EDIR = REPO_ROOT / "workspace" / "verification" / RUN_ID
BUNDLE_DIR = EDIR / "bundles"
BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
ZP = BUNDLE_DIR / f"{RUN_ID}.zip"

# Collect all files (excluding bundles subdirectory)
files_to_add: list[tuple[str, bytes]] = []
for f in sorted(EDIR.rglob("*")):
    if f.is_file() and "bundles" not in str(f.relative_to(EDIR)):
        arcname = str(f.relative_to(EDIR)).replace("\\", "/")
        files_to_add.append((arcname, f.read_bytes()))

# Build sha256 manifest
manifest_lines: list[str] = []
for arcname, content in files_to_add:
    h = hashlib.sha256(content).hexdigest()
    manifest_lines.append(f"{h}  {arcname}")
manifest_lines.append("SELF  sha256-manifest.txt")
manifest_content = "\n".join(manifest_lines) + "\n"
files_to_add.append(("sha256-manifest.txt", manifest_content.encode("utf-8")))

# Write ZIP
with zipfile.ZipFile(ZP, "w", zipfile.ZIP_DEFLATED) as zf:
    for arcname, content in files_to_add:
        zf.writestr(arcname, content)

entry_count = len(files_to_add)

# Sprint-scoped contract for MT005
MT005_CATEGORIES = {
    "run_metadata": ["run-metadata.json"],
    "preflight": ["preflight-baseline-verification.md"],
    "dirty_state": ["dirty-state-classification.json"],
    "evidence_hygiene": ["evidence-hygiene-repair-report.md"],
    "manifest_consistency": ["manifest-validation-consistency-report.json"],
    "blocked_action_labels": ["planner-blocked-action-labels-report.json"],
    "publication_readiness": ["active-family-publication-readiness-matrix.json"],
    "pdf_merge_readiness": ["pdf-pr-merge-readiness-packet.md"],
    "action_board": ["portfolio-action-board.json"],
    "planner_executed": ["planner-executed-actions-report.md"],
    "planner_blocked": ["planner-blocked-actions-report.json"],
    "ai_matrix_regression": ["cross-family-ai-pipeline-matrix-regression.json"],
    "ai_regression_diff": ["ai-matrix-regression-diff.md"],
    "blocker_retest": ["blocker-retest-report.json"],
    "master_plan_sync": ["master-plan-taskcard-sync-report.md"],
    "taskcard_ledger": ["taskcard-ledger.json"],
    "approval_gates": ["approval-gate-classification.json"],
    "lane_ownership": ["lane-file-ownership-matrix.json"],
    "changed_files": ["changed-files-report.json"],
    "commit_log": ["commit-log-proof.txt"],
    "git_state_initial": ["git-state-initial.txt"],
    "git_state_final": ["git-state-final.txt"],
    "final_verdict": ["final-verdict.md"],
    "sha256_manifest": ["sha256-manifest.txt"],
    "publication_summary": ["publication-readiness-proof-summary.json"],
}

# Validate
with zipfile.ZipFile(ZP) as zf:
    names = zf.namelist()
    basenames = {Path(n).name for n in names}
    found = []
    missing = []
    for cat, patterns in MT005_CATEGORIES.items():
        if any(p in basenames for p in patterns):
            found.append(cat)
        else:
            missing.append(cat)

passed = len(missing) == 0
sha256 = hashlib.sha256(ZP.read_bytes()).hexdigest()

validation = {
    "contract": "MT005_PUBLICATION_READINESS_SPRINT_CONTRACT",
    "contract_version": "mt005-v1",
    "validated_bundle": str(ZP.resolve()),
    "validated_bundle_sha256": sha256,
    "validated_bundle_size_bytes": ZP.stat().st_size,
    "validation_timestamp": datetime.now(timezone.utc).isoformat(),
    "result": {
        "passed": passed,
        "verdict": "MT005_BUNDLE_CONTRACT_PASSED" if passed else "MT005_BUNDLE_CONTRACT_FAILED",
        "entry_count": entry_count,
        "categories_found": found,
        "categories_found_count": len(found),
        "categories_missing": missing,
        "categories_missing_count": len(missing),
    },
    "manifest_self_exclusion_note": (
        "sha256-manifest.txt lists itself as SELF (cannot self-hash). "
        "evidence-contract-validation.json is a companion file outside the ZIP."
    ),
}

companion = BUNDLE_DIR / "evidence-contract-validation.json"
companion.write_text(json.dumps(validation, indent=2), encoding="utf-8")

print(f"ZIP: {ZP.resolve()}")
print(f"Entries: {entry_count}")
print(f"SHA256: {sha256}")
print(f"Validation: {'PASS' if passed else 'FAIL'}")
print(f"Categories: {len(found)}/{len(MT005_CATEGORIES)}")
if missing:
    print(f"Missing: {missing}")
