"""Build Phase 7 artifacts: package authority depth matrix + API catalog snippets."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# I/O map from Phase 4/6 Program.cs parsing
PROGRAMCS_IO = {
    "cells-html-converter":        {"input": ".xlsx", "output": ".html"},
    "cells-image-converter":       {"input": ".xlsx", "output": ".png"},
    "cells-json-converter":        {"input": ".xlsx", "output": ".json"},
    "cells-pdf-converter":         {"input": ".xlsx", "output": ".pdf"},
    "cells-spreadsheet-converter": {"input": ".xlsx", "output": ".csv"},
    "cells-spreadsheet-locker":    {"input": ".xlsx", "output": ".xlsx"},
    "cells-spreadsheet-merger":    {"input": ".xlsx", "output": ".xlsx"},
    "cells-spreadsheet-splitter":  {"input": ".xlsx", "output": ".xlsx"},
    "cells-text-converter":        {"input": ".csv",  "output": ".txt"},
    "diagram-diagram-converter":   {"input": ".vsdx", "output": ".vdx"},
    "diagram-pdf-converter":       {"input": ".vsdx", "output": ".pdf"},
    "email-converter":             {"input": ".eml",  "output": "directory"},
    "pdf-doc-converter":           {"input": ".pdf",  "output": ".docx"},
    "pdf-form-editor":             {"input": ".pdf",  "output": ".pdf"},
    "pdf-form-exporter":           {"input": ".pdf",  "output": ".json"},
    "pdf-form-flattener":          {"input": ".pdf",  "output": ".pdf"},
    "pdf-html":                    {"input": ".html", "output": ".pdf"},
    "pdf-image-extractor":         {"input": ".pdf",  "output": ".png"},
    "pdf-jpeg":                    {"input": ".pdf",  "output": ".jpg"},
    "pdf-merger":                  {"input": ".pdf",  "output": ".pdf"},
    "pdf-optimizer":               {"input": ".pdf",  "output": ".pdf"},
    "pdf-pdf-aconverter":          {"input": None,    "output": None},
    "pdf-png":                     {"input": ".pdf",  "output": ".png"},
    "pdf-security":                {"input": ".pdf",  "output": ".pdf"},
    "pdf-signature":               {"input": ".pdf",  "output": ".pdf"},
    "pdf-splitter":                {"input": ".pdf",  "output": ".pdf"},
    "pdf-table-generator":         {"input": ".pdf",  "output": ".pdf"},
    "pdf-text-extractor":          {"input": None,    "output": "stdout"},
    "pdf-tiff":                    {"input": ".pdf",  "output": ".tiff"},
    "pdf-toc-generator":           {"input": ".pdf",  "output": ".pdf"},
    "pdf-xls-converter":           {"input": ".pdf",  "output": ".xlsx"},
    "slides-compress":             {"input": ".pptx", "output": ".pptx"},
    "slides-convert":              {"input": ".pptx", "output": ".pdf"},
    "slides-merger":               {"input": ".pptx", "output": ".pptx"},
    "words-comparer":              {"input": ".docx", "output": ".docx"},
    "words-converter":             {"input": ".docx", "output": ".pdf"},
    "words-mail-merger":           {"input": None,    "output": ".docx"},
    "words-merger":                {"input": ".docx", "output": ".docx"},
    "words-replacer":              {"input": ".docx", "output": ".docx"},
    "words-report-builder":        {"input": None,    "output": ".docx"},
    "words-splitter":              {"input": ".docx", "output": ".docx"},
    "words-watermarker":           {"input": ".docx", "output": ".docx"},
}


def load_contracts():
    """Load all format-authority contracts."""
    contracts_dir = REPO_ROOT / "pipeline" / "format-authority" / "contracts"
    contracts = {}
    for f in sorted(contracts_dir.glob("*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        family = data.get("family", f.stem)
        for t in data.get("types", []):
            type_name = t.get("type_name", "")
            in_fmts = [a.get("format") for a in t.get("input_artifacts", [])]
            out_fmt = t.get("canonical_output_format")
            variants = t.get("variants", [])
            api_verified = t.get("api_verified", False)
            package = data.get("package_id", "")
            contracts[f"{family}/{type_name}"] = {
                "family": family,
                "type_name": type_name,
                "package_id": package,
                "input_formats": in_fmts,
                "canonical_output_format": out_fmt,
                "variant_count": len(variants),
                "api_verified": api_verified,
                "full_type_name": t.get("full_type_name", ""),
            }
    return contracts


def build_depth_matrix(contracts):
    """Build per-scenario depth matrix combining contract + Program.cs sources."""
    rows = []
    for sid, pc_io in sorted(PROGRAMCS_IO.items()):
        # Map scenario_id to contract key
        family = sid.split("-")[0]
        scenario_suffix = "-".join(sid.split("-")[1:])
        # Find matching contract
        contract_key = None
        contract_entry = None
        for key, entry in contracts.items():
            if entry["family"] == family:
                # Match by type_name similarity
                type_lower = entry["type_name"].lower()
                suffix_lower = scenario_suffix.replace("-", "").lower()
                suffix_parts = [p.lower() for p in scenario_suffix.split("-")]
                if (suffix_lower in type_lower or
                        type_lower in suffix_lower or
                        any(p in type_lower for p in suffix_parts if len(p) > 3)):
                    contract_key = key
                    contract_entry = entry
                    break

        pc_in = pc_io["input"]
        pc_out = pc_io["output"]
        has_contract = contract_entry is not None
        has_program_cs = pc_in is not None or pc_out is not None

        sources = []
        if has_contract:
            sources.append("format_authority_contract")
        if has_program_cs:
            sources.append("program_cs")

        if has_contract and has_program_cs:
            authority_depth = "DUAL_SOURCE"
        elif has_contract:
            authority_depth = "CONTRACT_ONLY"
        elif has_program_cs:
            authority_depth = "PROGRAMCS_ONLY"
        else:
            authority_depth = "NO_AUTHORITY"

        row = {
            "scenario_id": sid,
            "family": family,
            "authority_depth": authority_depth,
            "sources": sources,
            "contract_key": contract_key,
            "contract_input_formats": contract_entry["input_formats"] if contract_entry else [],
            "contract_output_format": contract_entry["canonical_output_format"] if contract_entry else None,
            "contract_api_verified": contract_entry["api_verified"] if contract_entry else None,
            "contract_variant_count": contract_entry["variant_count"] if contract_entry else 0,
            "programcs_input_format": pc_in,
            "programcs_output_format": pc_out,
        }
        rows.append(row)
    return rows


def build_api_catalog_snippets(contracts, out_dir: Path):
    """Write per-family API catalog snippet JSON files."""
    by_family = {}
    for key, entry in contracts.items():
        fam = entry["family"]
        by_family.setdefault(fam, []).append(entry)

    snippets_dir = out_dir / "api-catalog-snippets"
    snippets_dir.mkdir(parents=True, exist_ok=True)

    for fam, entries in sorted(by_family.items()):
        snippet = {
            "family": fam,
            "package_id": entries[0]["package_id"] if entries else "",
            "total_types": len(entries),
            "types": [
                {
                    "type_name": e["type_name"],
                    "full_type_name": e["full_type_name"],
                    "canonical_input_formats": e["input_formats"],
                    "canonical_output_format": e["canonical_output_format"],
                    "variant_count": e["variant_count"],
                    "api_verified": e["api_verified"],
                }
                for e in entries
            ],
        }
        out_path = snippets_dir / f"{fam}-api-catalog-snippet.json"
        out_path.write_text(json.dumps(snippet, indent=2), encoding="utf-8")
        print(f"  Written: {out_path.name} ({len(entries)} types)")


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    contracts = load_contracts()
    print(f"Loaded {len(contracts)} type contracts from format-authority")

    # Build API catalog snippets
    print("\nBuilding API catalog snippets:")
    build_api_catalog_snippets(contracts, out_dir)

    # Build depth matrix
    rows = build_depth_matrix(contracts)
    depth_counts = {}
    for r in rows:
        k = r["authority_depth"]
        depth_counts[k] = depth_counts.get(k, 0) + 1

    api_verified_count = sum(
        1 for r in rows if r.get("contract_api_verified")
    )
    dual_source_count = depth_counts.get("DUAL_SOURCE", 0)

    matrix = {
        "audit_type": "package_authority_depth_matrix",
        "sprint": "sprint61",
        "total": len(rows),
        "dual_source": dual_source_count,
        "contract_only": depth_counts.get("CONTRACT_ONLY", 0),
        "programcs_only": depth_counts.get("PROGRAMCS_ONLY", 0),
        "no_authority": depth_counts.get("NO_AUTHORITY", 0),
        "api_verified_count": api_verified_count,
        "depth_summary": depth_counts,
        "rows": rows,
    }
    (out_dir / "authority-depth-matrix.json").write_text(
        json.dumps(matrix, indent=2), encoding="utf-8"
    )
    print(f"\nWritten: authority-depth-matrix.json")
    print(f"  Depth summary: {depth_counts}")
    print(f"  API-verified types: {api_verified_count}/{len(rows)}")

    # Build contract-derived-assumptions summary
    assumptions = []
    for r in rows:
        if r["contract_output_format"] and not r["contract_api_verified"]:
            assumptions.append({
                "scenario_id": r["scenario_id"],
                "assumed_output_format": r["contract_output_format"],
                "assumed_input_formats": r["contract_input_formats"],
                "assumption_source": "format_authority_contract (not api_verified)",
                "corroborated_by_programcs": r["programcs_input_format"] is not None or r["programcs_output_format"] is not None,
            })

    assumptions_doc = {
        "audit_type": "contract_derived_assumptions",
        "sprint": "sprint61",
        "description": "I/O format assumptions derived from format-authority contracts without API verification",
        "total_assumptions": len(assumptions),
        "corroborated_by_programcs": sum(1 for a in assumptions if a["corroborated_by_programcs"]),
        "assumptions": assumptions,
    }
    (out_dir / "contract-derived-assumptions.json").write_text(
        json.dumps(assumptions_doc, indent=2), encoding="utf-8"
    )
    print(f"\nWritten: contract-derived-assumptions.json ({len(assumptions)} assumptions)")
    print(f"  Corroborated by Program.cs: {assumptions_doc['corroborated_by_programcs']}/{len(assumptions)}")
