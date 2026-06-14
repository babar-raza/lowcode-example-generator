"""Sprint 67 Phase 5 — Root README cardinality display tests.

Verifies that sprint67 root README files contain cardinality annotations
for multi-input and multi-output types (merger, splitter, extractor).
"""

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
README_DIR = REPO / "reports/sprint67/root-readme/per-family"

# Types that must have input cardinality markers in sprint67 READMEs
# Format: (family, example_slug, annotation_expected_substring)
MULTI_INPUT_TYPES = [
    ("cells", "spreadsheet-merger", "×N"),
    ("words", "comparer", "2×"),
    ("words", "merger", "×N"),
    ("slides", "merger", "×N"),
]

# Types that must have output cardinality markers
MULTI_OUTPUT_TYPES = [
    ("cells", "spreadsheet-splitter", "×N"),
    ("words", "splitter", "×N"),
    ("email", "converter", "html dir"),
]


def get_readme_lines(family: str):
    path = README_DIR / f"{family}-root-readme.md"
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").split("\n")


def find_table_row(lines, example_slug):
    """Find the table row for a given example slug."""
    for line in lines:
        if f"| `{example_slug}`" in line or f"| `{example_slug} " in line:
            return line
    return None


class TestRootReadmeCardinality:
    """Sprint67 root READMEs must contain cardinality markers for multi-cardinality types."""

    def test_readme_files_exist(self):
        families = ["cells", "words", "pdf", "diagram", "email", "slides"]
        for fam in families:
            path = README_DIR / f"{fam}-root-readme.md"
            assert path.exists(), f"Missing sprint67 root README: {fam}"

    def test_multi_input_annotations_present(self):
        for family, slug, expected in MULTI_INPUT_TYPES:
            lines = get_readme_lines(family)
            assert lines, f"README for {family} is empty or missing"
            row = find_table_row(lines, slug)
            assert row is not None, f"{family}: table row for '{slug}' not found"
            assert expected in row, f"{family}/{slug}: expected cardinality marker '{expected}' in row: {row!r}"

    def test_multi_output_annotations_present(self):
        for family, slug, expected in MULTI_OUTPUT_TYPES:
            lines = get_readme_lines(family)
            assert lines, f"README for {family} is empty or missing"
            row = find_table_row(lines, slug)
            assert row is not None, f"{family}: table row for '{slug}' not found"
            assert expected in row, f"{family}/{slug}: expected cardinality marker '{expected}' in row: {row!r}"

    def test_cardinality_key_legend_present_in_patched_families(self):
        """Families with cardinality changes must have the legend note."""
        patched_families = ["cells", "words", "email", "slides"]
        for fam in patched_families:
            path = README_DIR / f"{fam}-root-readme.md"
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            assert "Cardinality key" in content, f"{fam}: missing 'Cardinality key' legend in sprint67 README"

    def test_cells_single_cardinality_types_unchanged(self):
        """Single-cardinality types must NOT have ×N markers."""
        lines = get_readme_lines("cells")
        single_slugs = [
            "html-converter",
            "image-converter",
            "json-converter",
            "pdf-converter",
            "spreadsheet-converter",
            "spreadsheet-locker",
            "text-converter",
        ]
        for slug in single_slugs:
            row = find_table_row(lines, slug)
            if row is None:
                continue
            # The ×N marker must not be in the input or output columns for single-cardinality
            # We check the row does not have ×N or 2× at start of input/output cell
            cells = [c.strip() for c in row.split("|")]
            # cells[2] = example slug, cells[3] = API, cells[4] = input, cells[5] = output
            if len(cells) >= 6:
                assert (
                    "×N" not in cells[4] and "2×" not in cells[4]
                ), f"{slug}: single-input type should not have cardinality marker in input: {cells[4]!r}"

    def test_words_single_cardinality_types_unchanged(self):
        """Words single-cardinality types must NOT have ×N markers."""
        lines = get_readme_lines("words")
        single_slugs = ["converter", "mail-merger", "replacer", "report-builder", "watermarker"]
        for slug in single_slugs:
            row = find_table_row(lines, slug)
            if row is None:
                continue
            cells = [c.strip() for c in row.split("|")]
            if len(cells) >= 6:
                assert (
                    "×N" not in cells[4] and "2×" not in cells[4]
                ), f"words/{slug}: single-input type should not have cardinality marker in input: {cells[4]!r}"

    def test_diagram_readme_unchanged_no_cardinality_markers(self):
        """Diagram has only single-cardinality types — no ×N markers expected."""
        lines = get_readme_lines("diagram")
        content = "\n".join(lines)
        assert (
            "×N" not in content
        ), "diagram README: unexpected ×N cardinality marker (diagram has no multi-cardinality types)"
