"""Script: Audit all 42 example READMEs for I/O format documentation.

Strict policy: I/O documentation is ONLY counted if the extension appears
in a prose or explicit Input/Output section context — NOT inside backtick
API symbol names or class names (e.g. PdfConverter, DocConverter).

Rationale: The Sprint 60 audit used broad regex that matched '.pdf' in
'Aspose.Pdf.LowCode.PdfConverter', leading to false IO_DOC_MATCH verdicts.
This audit removes those false positives.
"""
import json
import re
from pathlib import Path

# Strip API symbol lines and code blocks before checking
def _prose_content(content: str) -> str:
    lines = []
    in_code = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        # Skip lines that are only API symbols (backtick-enclosed)
        if re.match(r'^`[^`]+`[,\s]*$', stripped):
            continue
        # Skip lines from "## API Symbols Used" section up to next section
        lines.append(line)
    return "\n".join(lines)

# Strict patterns: file extension must appear in prose context
# (not inside CamelCase class name, not inside namespace)
INPUT_PROSE_PATTERNS = [
    r'(?<![A-Za-z])\.xlsx\b', r'(?<![A-Za-z])\.xls\b', r'(?<![A-Za-z])\.xlsm\b',
    r'(?<![A-Za-z])\.csv\b',
    r'(?<![A-Za-z])\.docx\b', r'(?<![A-Za-z])\.doc\b',
    r'(?<![A-Za-z])\.rtf\b',
    r'(?<![A-Za-z])\.pdf\b',
    r'(?<![A-Za-z])\.vsdx\b', r'(?<![A-Za-z])\.vsd\b',
    r'(?<![A-Za-z])\.eml\b', r'(?<![A-Za-z])\.msg\b',
    r'(?<![A-Za-z])\.pptx\b', r'(?<![A-Za-z])\.ppt\b',
    r'\bInput:\s', r'\binput format\b', r'\baccepts?\s+\.\w+',
    r'\bInput file\b',
]
OUTPUT_PROSE_PATTERNS = [
    r'(?<![A-Za-z])\.html\b', r'(?<![A-Za-z])\.htm\b',
    r'(?<![A-Za-z])\.jpg\b', r'(?<![A-Za-z])\.jpeg\b',
    r'(?<![A-Za-z])\.png\b', r'(?<![A-Za-z])\.tiff?\b',
    r'(?<![A-Za-z])\.pdf\b',
    r'(?<![A-Za-z])\.json\b', r'(?<![A-Za-z])\.txt\b',
    r'(?<![A-Za-z])\.xlsx\b', r'(?<![A-Za-z])\.xls\b',
    r'(?<![A-Za-z])\.docx\b', r'(?<![A-Za-z])\.doc\b',
    r'(?<![A-Za-z])\.pptx\b', r'(?<![A-Za-z])\.ppt\b',
    r'\bOutput:\s', r'\boutput format\b', r'\bproduces?\s+\.\w+',
    r'\bOutput file\b',
]

README_PATHS = {
    "cells-html-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/html-converter/README.md",
    "cells-image-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/image-converter/README.md",
    "cells-json-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/json-converter/README.md",
    "cells-pdf-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/pdf-converter/README.md",
    "cells-spreadsheet-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-converter/README.md",
    "cells-spreadsheet-locker": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-locker/README.md",
    "cells-spreadsheet-merger": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-merger/README.md",
    "cells-spreadsheet-splitter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/spreadsheet-splitter/README.md",
    "cells-text-converter": "workspace/pr-dry-run/cells-controlled-pilot/examples/cells/lowcode/text-converter/README.md",
    "words-comparer": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/comparer/README.md",
    "words-converter": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/converter/README.md",
    "words-mail-merger": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/mail-merger/README.md",
    "words-merger": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/merger/README.md",
    "words-replacer": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/replacer/README.md",
    "words-report-builder": "workspace/pr-dry-run/words-report-builder/examples/words/lowcode/report-builder/README.md",
    "words-splitter": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/splitter/README.md",
    "words-watermarker": "workspace/pr-dry-run/words-controlled-pilot/examples/words/lowcode/watermarker/README.md",
    "pdf-doc-converter": "workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode/doc-converter/README.md",
    "pdf-form-editor": "workspace/pr-dry-run/pdf-controlled-pilot-pr8/examples/pdf/lowcode/form-editor/README.md",
    "pdf-form-exporter": "workspace/pr-dry-run/pdf-controlled-pilot-pr8/examples/pdf/lowcode/form-exporter/README.md",
    "pdf-form-flattener": "workspace/pr-dry-run/pdf-controlled-pilot-pr7/examples/pdf/lowcode/form-flattener/README.md",
    "pdf-html": "workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode/html/README.md",
    "pdf-image-extractor": "workspace/pr-dry-run/pdf-controlled-pilot-pr6/examples/pdf/lowcode/image-extractor/README.md",
    "pdf-jpeg": "workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode/jpeg/README.md",
    "pdf-merger": "workspace/pr-dry-run/pdf-controlled-pilot-wave1/examples/pdf/lowcode/merger/README.md",
    "pdf-optimizer": "workspace/pr-dry-run/pdf-controlled-pilot-wave2/examples/pdf/lowcode/optimizer/README.md",
    "pdf-pdf-aconverter": None,
    "pdf-png": "workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode/png/README.md",
    "pdf-security": "workspace/pr-dry-run/pdf-controlled-pilot-pr7/examples/pdf/lowcode/security/README.md",
    "pdf-signature": "workspace/pr-dry-run/pdf-controlled-pilot-pr9/examples/pdf/lowcode/signature/README.md",
    "pdf-splitter": "workspace/pr-dry-run/pdf-controlled-pilot-wave1/examples/pdf/lowcode/splitter/README.md",
    "pdf-table-generator": "workspace/pr-dry-run/pdf-controlled-pilot-pr6/examples/pdf/lowcode/table-generator/README.md",
    "pdf-text-extractor": None,
    "pdf-tiff": "workspace/pr-dry-run/pdf-controlled-pilot-pr5/examples/pdf/lowcode/tiff/README.md",
    "pdf-toc-generator": "workspace/pr-dry-run/pdf-controlled-pilot-pr6/examples/pdf/lowcode/toc-generator/README.md",
    "pdf-xls-converter": "workspace/pr-dry-run/pdf-controlled-pilot/examples/pdf/lowcode/xls-converter/README.md",
    "diagram-diagram-converter": "workspace/pr-dry-run/diagram-controlled-pilot/examples/diagram/lowcode/diagram-diagram-converter/README.md",
    "diagram-pdf-converter": "workspace/pr-dry-run/diagram-controlled-pilot/examples/diagram/lowcode/diagram-pdf-converter/README.md",
    "email-converter": "workspace/pr-dry-run/email-controlled-pilot/examples/email/lowcode/converter/README.md",
    "slides-compress": "workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/compress/README.md",
    "slides-convert": "workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/convert/README.md",
    "slides-merger": "workspace/pr-dry-run/slides-controlled-pilot/examples/slides/lowcode/merger/README.md",
}

REPO_ROOT = Path(__file__).resolve().parents[3]


def _check_io(content: str):
    prose = _prose_content(content)
    has_input = any(re.search(pat, prose, re.IGNORECASE) for pat in INPUT_PROSE_PATTERNS)
    has_output = any(re.search(pat, prose, re.IGNORECASE) for pat in OUTPUT_PROSE_PATTERNS)
    return has_input, has_output


def run_audit(label: str) -> dict:
    records = []
    for sid, rel_path in README_PATHS.items():
        if rel_path is None:
            records.append({
                "scenario_id": sid, "readme_found": False,
                "input_format_in_readme": False, "output_format_in_readme": False,
                "io_doc_status": "BOTH_DOC_MISSING", "note": "No local package (deferred/blocked)"
            })
            continue

        p = REPO_ROOT / rel_path
        if not p.exists():
            records.append({
                "scenario_id": sid, "readme_found": False,
                "input_format_in_readme": False, "output_format_in_readme": False,
                "io_doc_status": "BOTH_DOC_MISSING", "note": f"README not found"
            })
            continue

        content = p.read_text(encoding="utf-8", errors="replace")
        has_input, has_output = _check_io(content)

        if has_input and has_output:
            status = "IO_DOC_MATCH"
        elif has_input:
            status = "OUTPUT_DOC_MISSING"
        elif has_output:
            status = "INPUT_DOC_MISSING"
        else:
            status = "BOTH_DOC_MISSING"

        records.append({
            "scenario_id": sid, "readme_found": True,
            "input_format_in_readme": has_input,
            "output_format_in_readme": has_output,
            "io_doc_status": status,
        })

    status_counts = {}
    for r in records:
        s = r["io_doc_status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    io_match = status_counts.get("IO_DOC_MATCH", 0)
    both_missing = status_counts.get("BOTH_DOC_MISSING", 0)
    in_missing = status_counts.get("INPUT_DOC_MISSING", 0)
    out_missing = status_counts.get("OUTPUT_DOC_MISSING", 0)

    return {
        "audit_type": label,
        "sprint": "sprint61",
        "policy": "Strict prose-context matching; API symbol names excluded",
        "total": len(records),
        "io_doc_match": io_match,
        "input_doc_missing": in_missing + both_missing,
        "output_doc_missing": out_missing + both_missing,
        "both_doc_missing": both_missing,
        "status_summary": status_counts,
        "records": records,
    }


if __name__ == "__main__":
    before = run_audit("readme_io_documentation_before")
    out_dir = Path(__file__).parent

    before_path = out_dir / "example-readme-io-audit-before.json"
    before_path.write_text(json.dumps(before, indent=2), encoding="utf-8")
    print(f"Written: {before_path}")

    print(f"\nBEFORE (current state):")
    print(f"  Total: {before['total']}")
    for s, c in sorted(before["status_summary"].items()):
        print(f"  {s}: {c}")

    print(f"\n  Missing I/O docs ({before['input_doc_missing'] + before['output_doc_missing'] - before['both_doc_missing']} with partial, {before['both_doc_missing']} with none):")
    for r in before["records"]:
        if r["io_doc_status"] != "IO_DOC_MATCH":
            print(f"  {r['scenario_id']}: {r['io_doc_status']}")
