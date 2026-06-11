"""Phase 4: Build full destination audit for Sprint 66 with all 25 required fields."""
import json
import hashlib
from pathlib import Path
from datetime import datetime

BASE = Path(".")

# Load sprint65 content audit as base
with open("reports/sprint65/destination/content-audit-final.json", encoding="utf-8") as f:
    s65_records = json.load(f)["records"]

# Load remote inventory
with open("reports/sprint66/remote/remote-example-inventory.json", encoding="utf-8") as f:
    remote_inv = {r["scenario_id"]: r for r in json.load(f)["records"]}

# Load remote README I/O audit
with open("reports/sprint66/remote/remote-readme-io-audit.json", encoding="utf-8") as f:
    remote_io = {r["scenario_id"]: r for r in json.load(f)["records"]}

# Load publication state matrix
with open("reports/sprint66/publication/publication-truth-matrix-final.json", encoding="utf-8") as f:
    pub_matrix = {r["scenario_id"]: r for r in json.load(f)["records"]}

# Load handoff hashes
with open("reports/sprint66/handoff/package-artifact-hashes.json", encoding="utf-8") as f:
    handoff_hashes = {r["scenario_id"]: r for r in json.load(f)["records"]}

# Correct output_kind values for missing fields
OUTPUT_KIND_OVERRIDES = {
    "pdf-html-converter": "converter",
    "pdf-pdfa-converter": "converter",
    "pdf-text-extractor": "extractor",
}

# Remote path overrides (for cases where dir name differs from scenario_id)
REMOTE_PATH_OVERRIDES = {
    "pdf-html-converter": "examples/pdf/lowcode/html",
}

records = []
for rec in s65_records:
    sid = rec["scenario_id"]
    family = rec["family"]
    remote = remote_inv.get(sid, {})
    io_info = remote_io.get(sid, {})
    pub = pub_matrix.get(sid, {})
    handoff = handoff_hashes.get(sid, {})

    # Determine remote_path
    if sid in REMOTE_PATH_OVERRIDES:
        remote_path = REMOTE_PATH_OVERRIDES[sid]
    elif remote.get("remote_path"):
        remote_path = remote["remote_path"]
    else:
        remote_path = rec.get("destination_path", "")

    # Fix output_kind
    output_kind = rec.get("output_kind") or OUTPUT_KIND_OVERRIDES.get(sid, "")

    # Determine remote_status
    if remote.get("readme_sha"):
        if io_info.get("has_io_section"):
            remote_status = "REMOTE_CURRENT"
        else:
            remote_status = "REMOTE_STALE_README"
    else:
        remote_status = "REMOTE_MISSING"

    # local_package_status
    if handoff.get("status") == "OK":
        local_pkg_status = "READY"
    elif handoff.get("status") == "PARTIAL":
        local_pkg_status = "PARTIAL"
    else:
        local_pkg_status = "MISSING"

    # readme_io_status
    if handoff.get("readme_has_io"):
        readme_io_status = "IO_DOC_LOCAL_READY"
    else:
        readme_io_status = "IO_DOC_MISSING_LOCAL"

    new_rec = {
        "scenario_id": sid,
        "family": family,
        "destination_repo": rec.get("destination_repo", ""),
        "destination_path": remote_path,
        "local_package_path": str(Path(rec.get("publication_package_path", "")).as_posix()) if rec.get("publication_package_path") else "",
        "handoff_path": handoff.get("handoff_path", ""),
        "remote_path": remote_path,
        "programcs_path": f"{remote_path}/Program.cs",
        "programcs_hash": handoff.get("programcs_hash_local", rec.get("programcs_hash", "")),
        "readme_path": f"{remote_path}/README.md",
        "readme_hash": handoff.get("readme_hash_local", rec.get("readme_hash", "")),
        "package_version": rec.get("package_version", ""),
        "input_format": rec.get("input_format", ""),
        "input_kind": rec.get("input_kind", ""),
        "output_format": rec.get("output_format", ""),
        "output_kind": output_kind,
        "api_type": rec.get("api_type", ""),
        "full_type_name": rec.get("full_type_name", ""),
        "operation_kind": rec.get("operation_kind", ""),
        "authority_source": rec.get("authority_source", ""),
        "remote_status": remote_status,
        "local_package_status": local_pkg_status,
        "readme_io_status": readme_io_status,
        "root_readme_status": rec.get("root_readme_status", ""),
        "version_status": rec.get("package_version_status", ""),
        "final_status": "READY" if local_pkg_status == "READY" and output_kind else "PARTIAL",
        "remote_readme_sha": remote.get("readme_sha", ""),
        "remote_programcs_sha": remote.get("programcs_sha", ""),
        "remote_readme_has_io": io_info.get("has_io_section", False),
        "publication_status": pub.get("publication_status", ""),
        "dry_run_package_ready": pub.get("dry_run_package_ready", False),
        "approval_blocked": pub.get("approval_blocked", True),
    }
    records.append(new_rec)

# Validate all required fields
REQUIRED_FIELDS = [
    "scenario_id", "family", "destination_repo", "destination_path",
    "local_package_path", "remote_path", "programcs_path", "programcs_hash",
    "readme_path", "readme_hash", "package_version", "input_format", "input_kind",
    "output_format", "output_kind", "api_type", "full_type_name", "operation_kind",
    "authority_source", "remote_status", "local_package_status", "readme_io_status",
    "root_readme_status", "version_status", "final_status",
]

issues = []
for rec in records:
    for field in REQUIRED_FIELDS:
        val = rec.get(field)
        if val is None or val == "":
            issues.append(f"{rec['scenario_id']}: {field} is blank")

if issues:
    print(f"VALIDATION ISSUES ({len(issues)}):")
    for iss in issues[:20]:
        print(f"  {iss}")
else:
    print("All required fields present for all 42 records!")

# Status summary
status_counts = {}
for r in records:
    s = r.get("final_status", "?")
    status_counts[s] = status_counts.get(s, 0) + 1

output_kind_blank = [r["scenario_id"] for r in records if not r.get("output_kind")]
print(f"\noutput_kind blank: {len(output_kind_blank)} {output_kind_blank}")
print(f"final_status distribution: {status_counts}")

with open("reports/sprint66/destination/content-audit-final.json", "w", encoding="utf-8") as f:
    json.dump({
        "generated": datetime.now().isoformat() + "Z",
        "total": len(records),
        "issues_count": len(issues),
        "status_summary": status_counts,
        "records": records,
    }, f, indent=2)

print(f"\nSaved: destination/content-audit-final.json ({len(records)} records)")
