"""
Build Sprint 67 root README files with cardinality annotations.
Reads sprint66 versions, patches the Included Examples table.
"""
import re
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
src_dir = repo / "reports/sprint66/root-readme/per-family"
dst_dir = repo / "reports/sprint67/root-readme/per-family"
dst_dir.mkdir(parents=True, exist_ok=True)

# Cardinality overrides: (family, example_slug) -> (input_display, output_display)
# Format: None means keep original
CARDINALITY = {
    # Cells
    ("cells", "spreadsheet-merger"):  ("xlsx (×N)",  "xlsx"),
    ("cells", "spreadsheet-splitter"):("xlsx",       "xlsx (×N)"),
    # Words
    ("words", "comparer"):  ("2× docx",     "docx"),
    ("words", "merger"):    ("docx (×N)",   "docx"),
    ("words", "splitter"):  ("docx",        "docx (×N)"),
    # PDF
    ("pdf", "merger"):         ("pdf (×N)",   "pdf"),
    ("pdf", "splitter"):       ("pdf",        "pdf (×N)"),
    ("pdf", "jpeg"):           ("pdf",        "jpeg (×N)"),
    ("pdf", "png"):            ("pdf",        "png (×N)"),
    ("pdf", "image-extractor"):("pdf",        "image (×N)"),
    # Email
    ("email", "converter"):  ("eml",  "html dir"),
    # Slides
    ("slides", "merger"): ("pptx (×N)", "pptx"),
}

def patch_table_row(line: str, family: str) -> str:
    """Patch a table row that matches a cardinality override."""
    # Table rows look like: | `example-name` | `API.Method` | `fmt` | `fmt` | `dotnet run...` |
    m = re.match(r"^\| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| `([^`]*)` \| (.+) \|$", line)
    if not m:
        return line
    slug, api, inp, out, run = m.groups()
    key = (family, slug)
    if key in CARDINALITY:
        new_inp, new_out = CARDINALITY[key]
        return f"| `{slug}` | `{api}` | `{new_inp}` | `{new_out}` | {run} |"
    return line

FAMILY_HEADERS = {
    "cells": "Cells",
    "words": "Words",
    "pdf": "PDF",
    "diagram": "Diagram",
    "email": "Email",
    "slides": "Slides",
}

CARDINALITY_NOTE = """\

> **Cardinality key:** `×N` in the Input column means the operation merges N input files into one.
> `×N` in the Output column means the operation splits or extracts into N output files.
> `2×` prefix means exactly two inputs are required.

"""

patched_count = 0

for fam in ["cells", "words", "pdf", "diagram", "email", "slides"]:
    src = src_dir / f"{fam}-root-readme.md"
    dst = dst_dir / f"{fam}-root-readme.md"

    if not src.exists():
        print(f"MISSING: {src}")
        continue

    content = src.read_text(encoding="utf-8")

    # Remove any stale version comment at the top (PDF has one)
    content = re.sub(r"^<!-- PDF version:.*?-->\n", "", content, flags=re.MULTILINE)

    lines = content.split("\n")
    result = []
    in_examples_table = False
    note_inserted = False

    for line in lines:
        # Detect the Included Examples table header
        if "| Example |" in line and "| Demonstrated API |" in line:
            in_examples_table = True
            result.append(line)
            continue

        if in_examples_table:
            if line.startswith("|"):
                patched = patch_table_row(line, fam)
                result.append(patched)
                if patched != line:
                    patched_count += 1
                continue
            else:
                in_examples_table = False
                # Insert cardinality note after the table if any cardinality changes exist
                if any(k[0] == fam for k in CARDINALITY) and not note_inserted:
                    result.append(CARDINALITY_NOTE)
                    note_inserted = True

        result.append(line)

    # Update Generated On timestamp
    updated = "\n".join(result)
    updated = re.sub(
        r"Generated on: [\d\- :UTC]+",
        "Generated on: 2026-05-22 (Sprint 67 — cardinality annotations added)",
        updated
    )

    dst.write_text(updated, encoding="utf-8")
    print(f"Wrote: {dst.name}")

print(f"\nTotal table rows patched: {patched_count}")
