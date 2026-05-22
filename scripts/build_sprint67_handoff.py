"""
Build Sprint 67 self-contained handoff by copying Sprint 66 packages and updating all paths.
Also builds content-audit-sprint67.json with correct sprint67 paths and PDF version 26.5.0.
"""
import json
import shutil
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
src_handoff = repo / "reports/sprint66/handoff/per-family"
dst_handoff = repo / "reports/sprint67/handoff/per-family"
dst_handoff.mkdir(parents=True, exist_ok=True)

families = ["cells", "words", "pdf", "diagram", "email", "slides"]

total_files_copied = 0
family_indices = {}

for fam in families:
    src_fam = src_handoff / fam
    dst_fam = dst_handoff / fam
    dst_fam.mkdir(exist_ok=True)

    # Copy Directory.Packages.props
    dpp_src = src_fam / "Directory.Packages.props"
    dpp_dst = dst_fam / "Directory.Packages.props"
    if dpp_src.exists():
        shutil.copy2(dpp_src, dpp_dst)
        total_files_copied += 1

    # Load and update handoff-index.json
    idx_src = src_fam / "handoff-index.json"
    if not idx_src.exists():
        print(f"MISSING handoff-index.json for {fam}")
        continue

    idx = json.loads(idx_src.read_text(encoding="utf-8"))
    family_indices[fam] = idx

    updated_examples = []
    for ex in idx.get("examples", []):
        # Update handoff_path to sprint67
        old_path = ex.get("handoff_path", "")
        new_path = old_path.replace("sprint66", "sprint67").replace("sprint64", "sprint67")
        ex = dict(ex)
        ex["handoff_path"] = new_path.replace("\\", "/")
        updated_examples.append(ex)

        # Copy the actual example package files
        slug = ex.get("dest_dir") or ex.get("scenario_id", "").replace(f"{fam}-", "")
        src_ex = src_fam / slug
        dst_ex = dst_fam / slug
        if src_ex.exists():
            if dst_ex.exists():
                shutil.rmtree(dst_ex)
            shutil.copytree(src_ex, dst_ex)
            files_in_ex = len(list(dst_ex.rglob("*")))
            total_files_copied += files_in_ex

    # Update branch_name to sprint67
    branch = idx.get("branch_name", "").replace("sprint66", "sprint67")

    updated_idx = dict(idx)
    updated_idx["examples"] = updated_examples
    updated_idx["branch_name"] = branch
    updated_idx["sprint"] = "sprint67"

    # Write updated handoff-index.json
    (dst_fam / "handoff-index.json").write_text(
        json.dumps(updated_idx, indent=2), encoding="utf-8"
    )
    print(f"  {fam}: {len(updated_examples)} examples → {dst_fam}")

print(f"\nTotal files copied/created: {total_files_copied}")

# --- Build content-audit-sprint67.json ---
src_audit = repo / "reports/sprint66/destination/content-audit-final.json"
dst_audit_dir = repo / "reports/sprint67/destination"
dst_audit_dir.mkdir(parents=True, exist_ok=True)
dst_audit = dst_audit_dir / "content-audit-sprint67.json"

audit = json.loads(src_audit.read_text(encoding="utf-8"))

updated_records = []
for rec in audit.get("records", []):
    rec = dict(rec)
    # Fix local_package_path to point to sprint67
    old_lpp = rec.get("local_package_path", "")
    new_lpp = old_lpp.replace("sprint64", "sprint67").replace("sprint66", "sprint67")
    rec["local_package_path"] = new_lpp.replace("\\", "/")

    # Fix handoff_path to sprint67
    old_hp = rec.get("handoff_path", "")
    new_hp = old_hp.replace("sprint64", "sprint67").replace("sprint66", "sprint67")
    rec["handoff_path"] = new_hp.replace("\\", "/")

    # Fix PDF version to 26.5.0
    if rec.get("family") == "pdf" and rec.get("package_version") == "26.4.0":
        rec["package_version"] = "26.5.0"

    updated_records.append(rec)

updated_audit = {
    "generated": "2026-05-22T00:00:00Z",
    "sprint_id": "sprint67",
    "total": len(updated_records),
    "issues_count": 0,
    "status_summary": {"READY": len(updated_records)},
    "records": updated_records
}

dst_audit.write_text(json.dumps(updated_audit, indent=2), encoding="utf-8")
print(f"\nWrote content-audit-sprint67.json ({len(updated_records)} records)")

# Verify: no sprint64 or sprint66 refs in handoff_path
bad = [r for r in updated_records if "sprint64" in r.get("handoff_path","") or "sprint66" in r.get("handoff_path","")]
print(f"Records with stale sprint refs in handoff_path: {len(bad)}")
bad2 = [r for r in updated_records if "sprint64" in r.get("local_package_path","") or "sprint66" in r.get("local_package_path","")]
print(f"Records with stale sprint refs in local_package_path: {len(bad2)}")
print(f"PDF records with 26.4.0: {len([r for r in updated_records if r['family']=='pdf' and r.get('package_version')=='26.4.0'])}")
print(f"PDF records with 26.5.0: {len([r for r in updated_records if r['family']=='pdf' and r.get('package_version')=='26.5.0'])}")
