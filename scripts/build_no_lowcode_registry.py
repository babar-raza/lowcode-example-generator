"""Build the confirmed-no-lowcode-family-registry.json for Phase I."""
import json
from pathlib import Path

base = Path("workspace/verification/latest")
out_path = base / "confirmed-no-lowcode-family-registry.json"

# 13 original confirmed-no-lowcode families with source-of-truth proofs
families_13 = [
    ("barcode",  "Aspose.BarCode"),
    ("cad",      "Aspose.CAD"),
    ("drawing",  "Aspose.Drawing"),
    ("finance",  "Aspose.Finance"),
    ("font",     "Aspose.Font"),
    ("gis",      "Aspose.GIS"),
    ("imaging",  "Aspose.Imaging"),
    ("note",     "Aspose.Note"),
    ("page",     "Aspose.Page"),
    ("tasks",    "Aspose.Tasks"),
    ("tex",      "Aspose.TeX"),
    ("threed",   "Aspose.3D"),
    ("zip",      "Aspose.ZIP"),
]

entries = []

for fam, pkg_id in families_13:
    proof_path = base / f"{fam}-source-of-truth-proof.json"
    with open(proof_path, encoding="utf-8") as f:
        proof = json.load(f)

    entries.append({
        "family": fam,
        "package_id": proof["package_id"],
        "resolved_version": proof["resolved_version"],
        "nupkg_sha256": proof["nupkg_sha256"],
        "selected_target_framework": proof["selected_target_framework"],
        "namespace_count": proof["namespace_count"],
        "lowcode_namespace_found": False,
        "matched_plugin_namespaces": proof["matched_plugin_namespaces"],
        "public_plugin_type_count": proof["public_plugin_type_count"],
        "public_plugin_method_count": proof["public_plugin_method_count"],
        "eligibility_status": proof["eligibility_status"],
        "eligibility_reason": proof["eligibility_reason"],
        "discovery_method": "dll_reflection_via_dllreflector",
        "yaml_status": "disabled",
        "yaml_enabled": False,
        "verified_date": "2026-05-09",
        "evidence_file": f"{fam}-source-of-truth-proof.json",
        "reclassified_this_sprint": False,
        "notes": None,
    })

# html - reclassified from BLOCKED to CONFIRMED_NO_LOWCODE this sprint
with open(base / "html-reflection-blocker.json", encoding="utf-8") as f:
    html_blocker = json.load(f)

entries.append({
    "family": "html",
    "package_id": "Aspose.HTML",
    "resolved_version": html_blocker.get("package_version", "26.4.0"),
    "nupkg_sha256": html_blocker.get("package_sha256", "unknown"),
    "selected_target_framework": "netstandard2.0",
    "namespace_count": html_blocker.get("namespaces_found_count", 49),
    "lowcode_namespace_found": False,
    "matched_plugin_namespaces": [],
    "public_plugin_type_count": 0,
    "public_plugin_method_count": 0,
    "eligibility_status": "not_eligible",
    "eligibility_reason": "DllReflector run with explicit dep (Microsoft.Extensions.Logging.Abstractions) found 49 namespaces, none LowCode",
    "discovery_method": "manual_dll_reflection_with_explicit_dep",
    "yaml_status": "disabled",
    "yaml_enabled": False,
    "verified_date": "2026-05-09",
    "evidence_file": "html-reflection-blocker.json",
    "reclassified_this_sprint": True,
    "notes": "Previously BLOCKED due to missing Microsoft.Extensions.Logging.Abstractions transitive dep. Manually ran DllReflector with explicit dep path — 49 namespaces found, none LowCode. Reclassified CONFIRMED_NO_LOWCODE 2026-05-09.",
})

# svg - reclassified from BLOCKED to CONFIRMED_NO_LOWCODE this sprint
with open(base / "svg-reflection-blocker.json", encoding="utf-8") as f:
    svg_blocker = json.load(f)

entries.append({
    "family": "svg",
    "package_id": "Aspose.SVG",
    "resolved_version": svg_blocker.get("package_version", "24.2.0"),
    "nupkg_sha256": svg_blocker.get("package_sha256", "unknown"),
    "selected_target_framework": "netstandard2.0",
    "namespace_count": svg_blocker.get("namespaces_found_count", 36),
    "lowcode_namespace_found": False,
    "matched_plugin_namespaces": [],
    "public_plugin_type_count": 0,
    "public_plugin_method_count": 0,
    "eligibility_status": "not_eligible",
    "eligibility_reason": "DllReflector run with explicit dep (Microsoft.Extensions.Logging.Abstractions) found 36 namespaces, none LowCode",
    "discovery_method": "manual_dll_reflection_with_explicit_dep",
    "yaml_status": "disabled",
    "yaml_enabled": False,
    "verified_date": "2026-05-09",
    "evidence_file": "svg-reflection-blocker.json",
    "reclassified_this_sprint": True,
    "notes": "Previously BLOCKED due to missing Microsoft.Extensions.Logging.Abstractions transitive dep. Manually ran DllReflector with explicit dep path — 36 namespaces found, none LowCode. Reclassified CONFIRMED_NO_LOWCODE 2026-05-09.",
})

registry = {
    "artifact_id": "confirmed-no-lowcode-family-registry",
    "created": "2026-05-09",
    "sprint": "Post-Discovery Next Sprint Phase I",
    "total_families": len(entries),
    "families_with_source_of_truth_proof": 13,
    "families_reclassified_this_sprint": 2,
    "reclassified_families": ["html", "svg"],
    "verdict_for_all": "CONFIRMED_NO_LOWCODE — no LowCode namespace found after successful DLL reflection",
    "pipeline_action": "YAMLs set to status=disabled, enabled=false. Excluded from generation pipeline.",
    "taskcard": "NEW-28-followup-confirmed-no-lowcode-documentation",
    "entries": entries,
}

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(registry, f, indent=2)

print(f"Wrote {out_path}")
print(f"Total families: {len(entries)}")
for e in entries:
    flag = " [RECLASSIFIED THIS SPRINT]" if e["reclassified_this_sprint"] else ""
    print(f"  {e['family']}: {e['package_id']} v{e['resolved_version']}, ns={e['namespace_count']}{flag}")
