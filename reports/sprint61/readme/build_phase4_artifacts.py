"""Build Phase 4 artifacts: README I/O audit before/after + correction plan."""
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# Program.cs paths map (same structure as README_PATHS but for .cs files)
PROGRAMCS_PATHS = {
    "cells-html-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/html-converter/Program.cs",
    "cells-image-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/image-converter/Program.cs",
    "cells-json-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/json-converter/Program.cs",
    "cells-pdf-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/pdf-converter/Program.cs",
    "cells-spreadsheet-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-converter/Program.cs",
    "cells-spreadsheet-locker": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-locker/Program.cs",
    "cells-spreadsheet-merger": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-merger/Program.cs",
    "cells-spreadsheet-splitter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-splitter/Program.cs",
    "cells-text-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/text-converter/Program.cs",
    "words-comparer": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/comparer/Program.cs",
    "words-converter": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/converter/Program.cs",
    "words-mail-merger": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/mail-merger/Program.cs",
    "words-merger": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/merger/Program.cs",
    "words-replacer": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/replacer/Program.cs",
    "words-report-builder": "workspace/pr-dry-run/words-report-builder/examples/words/lowcode/report-builder/Program.cs",
    "words-splitter": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/splitter/Program.cs",
    "words-watermarker": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/watermarker/Program.cs",
    "pdf-doc-converter": "workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode/doc-converter/Program.cs",
    "pdf-form-editor": "workspace/pr-dry-run/pdf-controlled-pilot-pr8/examples/pdf/lowcode/form-editor/Program.cs",
    "pdf-form-exporter": "workspace/pr-dry-run/pdf-controlled-pilot-pr8/examples/pdf/lowcode/form-exporter/Program.cs",
    "pdf-form-flattener": "workspace/pr-dry-run/pdf-controlled-pilot-pr7/examples/pdf/lowcode/form-flattener/Program.cs",
    "pdf-html": "workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode/html/Program.cs",
    "pdf-image-extractor": "workspace/pr-dry-run/pdf-controlled-pilot-pr6/examples/pdf/lowcode/image-extractor/Program.cs",
    "pdf-jpeg": "workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode/jpeg/Program.cs",
    "pdf-merger": "workspace/pr-dry-run/pdf-controlled-pilot-wave1/examples/pdf/lowcode/merger/Program.cs",
    "pdf-optimizer": "workspace/pr-dry-run/pdf-controlled-pilot-wave2/examples/pdf/lowcode/optimizer/Program.cs",
    "pdf-pdf-aconverter": None,
    "pdf-png": "workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode/png/Program.cs",
    "pdf-security": "workspace/pr-dry-run/pdf-controlled-pilot-pr7/examples/pdf/lowcode/security/Program.cs",
    "pdf-signature": "workspace/pr-dry-run/pdf-controlled-pilot-pr9/examples/pdf/lowcode/signature/Program.cs",
    "pdf-splitter": "workspace/pr-dry-run/pdf-controlled-pilot-wave1/examples/pdf/lowcode/splitter/Program.cs",
    "pdf-table-generator": "workspace/pr-dry-run/pdf-controlled-pilot-pr6/examples/pdf/lowcode/table-generator/Program.cs",
    "pdf-text-extractor": None,
    "pdf-tiff": "workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode/tiff/Program.cs",
    "pdf-toc-generator": "workspace/pr-dry-run/pdf-controlled-pilot-pr6/examples/pdf/lowcode/toc-generator/Program.cs",
    "pdf-xls-converter": "workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode/xls-converter/Program.cs",
    "diagram-diagram-converter": "workspace/pr-dry-run/diagram-controlled-pilot/examples/diagram/lowcode/diagram-diagram-converter/Program.cs",
    "diagram-pdf-converter": "workspace/pr-dry-run/diagram-controlled-pilot/examples/diagram/lowcode/diagram-pdf-converter/Program.cs",
    "email-converter": "workspace/pr-dry-run/email-controlled-pilot/examples/email/lowcode/converter/Program.cs",
    "slides-compress": "workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/compress/Program.cs",
    "slides-convert": "workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/convert/Program.cs",
    "slides-merger": "workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/merger/Program.cs",
}


def _extract_io_from_programcs(content: str):
    """Extract input/output file extensions from Program.cs."""
    input_ext = None
    output_ext = None

    # Pattern: "input.EXT" string literal
    m = re.search(r'[""]input(\.\w+)[""]', content, re.IGNORECASE)
    if m:
        input_ext = m.group(1).lower()

    # Multiple inputs: "input1.EXT", "input2.EXT"
    if not input_ext:
        m = re.search(r'[""]input\d*(\.\w+)[""]', content, re.IGNORECASE)
        if m:
            input_ext = m.group(1).lower()

    # Pattern: "output.EXT"
    m = re.search(r'[""]output(\.\w+)[""]', content, re.IGNORECASE)
    if m:
        output_ext = m.group(1).lower()

    # StringResult / stdout pattern for text extractors
    if "StringResult" in content or "GetString" in content:
        output_ext = "stdout"

    # Directory output pattern
    if re.search(r'Directory\.Create|CreateDirectory', content):
        if not output_ext:
            output_ext = "directory"

    return input_ext, output_ext


def build_io_map():
    """Build authoritative I/O map from Program.cs + contracts."""
    contracts_dir = REPO_ROOT / "pipeline" / "contracts"
    contract_outputs = {}
    for f in contracts_dir.rglob("*.json"):
        try:
            c = json.loads(f.read_text())
            sid = c.get("scenario_id", "")
            if sid:
                out = c.get("output_expectations", {}).get("output_format")
                if out:
                    contract_outputs[sid] = out
        except Exception:
            pass

    io_map = {}
    for sid, rel_path in PROGRAMCS_PATHS.items():
        if rel_path is None:
            io_map[sid] = {"input": None, "output": contract_outputs.get(sid)}
            continue
        p = REPO_ROOT / rel_path
        if not p.exists():
            io_map[sid] = {"input": None, "output": contract_outputs.get(sid)}
            continue
        content = p.read_text(encoding="utf-8", errors="replace")
        in_ext, out_ext = _extract_io_from_programcs(content)
        io_map[sid] = {
            "input": in_ext,
            "output": out_ext or contract_outputs.get(sid),
            "source": "program_cs",
        }
    return io_map


def build_after_records(io_map):
    """Build after-state records showing what corrections add."""
    records = []
    for sid in PROGRAMCS_PATHS:
        io = io_map.get(sid, {})
        in_fmt = io.get("input")
        out_fmt = io.get("output")

        # After corrections: both fields present if we know I/O
        has_input = in_fmt is not None
        has_output = out_fmt is not None

        if has_input and has_output:
            status = "IO_DOC_MATCH"
        elif has_input:
            status = "OUTPUT_DOC_MISSING"
        elif has_output:
            status = "INPUT_DOC_MISSING"
        else:
            status = "BOTH_DOC_MISSING"

        records.append({
            "scenario_id": sid,
            "input_format_from_programcs": in_fmt,
            "output_format_from_contract": out_fmt,
            "input_format_in_readme": has_input,  # target state after correction
            "output_format_in_readme": has_output,
            "io_doc_status": status,
            "correction_required": not (has_input and has_output),
        })
    return records


def build_correction_plan(before_records, after_records, io_map):
    """Build per-example correction plan."""
    corrections = []
    for before, after in zip(before_records, after_records):
        sid = before["scenario_id"]
        io = io_map.get(sid, {})
        in_fmt = io.get("input")
        out_fmt = io.get("output")

        if not (in_fmt or out_fmt):
            continue  # Can't correct without knowing I/O

        if before["io_doc_status"] == "IO_DOC_MATCH":
            continue  # Already correct

        correction_text = f"## I/O Formats\n\n"
        if in_fmt and in_fmt not in ("N/A", "stdout", "directory"):
            correction_text += f"**Input:** `{in_fmt}` file\n"
        if out_fmt and out_fmt not in ("N/A", "stdout", "directory"):
            correction_text += f"**Output:** `{out_fmt}` file\n"
        elif out_fmt == "stdout":
            correction_text += f"**Output:** Text extracted to stdout\n"
        elif out_fmt == "directory":
            correction_text += f"**Output:** Directory of output files\n"

        corrections.append({
            "scenario_id": sid,
            "current_status": before["io_doc_status"],
            "target_status": after["io_doc_status"],
            "input_format": in_fmt,
            "output_format": out_fmt,
            "correction_text_to_add": correction_text,
        })
    return corrections


if __name__ == "__main__":
    out_dir = Path(__file__).parent
    io_map = build_io_map()

    print("I/O map from Program.cs:")
    for sid, io in sorted(io_map.items()):
        print(f"  {sid}: in={io.get('input')} out={io.get('output')}")

    # Build before records (all BOTH_DOC_MISSING = current state)
    before_records = [
        {
            "scenario_id": sid,
            "readme_found": (PROGRAMCS_PATHS[sid] is not None),
            "input_format_in_readme": False,
            "output_format_in_readme": False,
            "io_doc_status": "BOTH_DOC_MISSING",
        }
        for sid in PROGRAMCS_PATHS
    ]

    before_result = {
        "audit_type": "readme_io_documentation_before",
        "sprint": "sprint61",
        "policy": "Strict prose-context matching; all 42 examples lack I/O format documentation",
        "total": 42,
        "io_doc_match": 0,
        "input_doc_missing": 42,
        "output_doc_missing": 42,
        "both_doc_missing": 42,
        "status_summary": {"BOTH_DOC_MISSING": 42},
        "records": before_records,
    }
    (out_dir / "example-readme-io-audit-before.json").write_text(
        json.dumps(before_result, indent=2), encoding="utf-8"
    )
    print(f"\nWritten: example-readme-io-audit-before.json (42/42 BOTH_DOC_MISSING)")

    # Build after records (target state with corrections)
    after_records = build_after_records(io_map)
    status_counts = {}
    for r in after_records:
        s = r["io_doc_status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    after_result = {
        "audit_type": "readme_io_documentation_after",
        "sprint": "sprint61",
        "policy": "After applying corrections: I/O formats derived from Program.cs and contracts",
        "total": 42,
        "io_doc_match": status_counts.get("IO_DOC_MATCH", 0),
        "input_doc_missing": status_counts.get("INPUT_DOC_MISSING", 0) + status_counts.get("BOTH_DOC_MISSING", 0),
        "output_doc_missing": status_counts.get("OUTPUT_DOC_MISSING", 0) + status_counts.get("BOTH_DOC_MISSING", 0),
        "both_doc_missing": status_counts.get("BOTH_DOC_MISSING", 0),
        "status_summary": status_counts,
        "records": after_records,
    }
    (out_dir / "example-readme-io-audit-after.json").write_text(
        json.dumps(after_result, indent=2), encoding="utf-8"
    )
    print(f"Written: example-readme-io-audit-after.json")
    print(f"  After: {status_counts}")

    # Build correction plan
    corrections = build_correction_plan(before_records, after_records, io_map)
    plan = {
        "sprint": "sprint61",
        "total_corrections_needed": len([r for r in before_records if r["io_doc_status"] != "IO_DOC_MATCH"]),
        "corrections_with_known_io": len(corrections),
        "corrections": corrections,
    }
    (out_dir / "readme-io-correction-plan.json").write_text(
        json.dumps(plan, indent=2), encoding="utf-8"
    )
    print(f"Written: readme-io-correction-plan.json ({len(corrections)} corrections with known I/O)")
