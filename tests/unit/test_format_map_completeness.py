"""Test format map completeness — every active LowCode type must resolve
to a correct (non-.out) output format via the planner's _infer_output_format,
and a correct input format via _infer_input_format.

Parametrized across all 42 active types in the 6 active families.
"""

import pytest

from plugin_examples.scenario_planner.planner import (
    _infer_input_format,
    _infer_output_format,
)

# (family, type_name, family_default_input, expected_input, expected_output)
# expected_output="" means stdout/no-file (valid for extractors).
_ACTIVE_TYPES = [
    # Cells (9) — all workflow_root types from cells denominator
    ("cells", "SpreadsheetConverter", ".xlsx", ".xlsx", ".csv"),
    ("cells", "JsonConverter", ".xlsx", ".xlsx", ".json"),
    ("cells", "HtmlConverter", ".xlsx", ".xlsx", ".html"),
    ("cells", "TextConverter", ".xlsx", ".xlsx", ".txt"),
    ("cells", "ImageConverter", ".xlsx", ".xlsx", ".png"),
    ("cells", "SpreadsheetMerger", ".xlsx", ".xlsx", ".xlsx"),
    ("cells", "SpreadsheetSplitter", ".xlsx", ".xlsx", ".xlsx"),
    ("cells", "SpreadsheetLocker", ".xlsx", ".xlsx", ".xlsx"),
    ("cells", "PdfConverter", ".xlsx", ".xlsx", ".pdf"),
    # Words (8) — from words config allowed_types
    ("words", "Converter", ".docx", ".docx", ".pdf"),
    ("words", "Merger", ".docx", ".docx", ".docx"),
    ("words", "Splitter", ".docx", ".docx", ".docx"),
    ("words", "Comparer", ".docx", ".docx", ".docx"),
    ("words", "MailMerger", ".docx", ".docx", ".docx"),
    ("words", "ReportBuilder", ".docx", ".docx", ".docx"),
    ("words", "Watermarker", ".docx", ".docx", ".docx"),
    ("words", "Replacer", ".docx", ".docx", ".docx"),
    # PDF (19) — from pdf config allowed_types
    ("pdf", "DocConverter", ".pdf", ".pdf", ".docx"),
    ("pdf", "XlsConverter", ".pdf", ".pdf", ".xlsx"),
    ("pdf", "Html", ".pdf", ".html", ".pdf"),
    ("pdf", "Jpeg", ".pdf", ".pdf", ".jpg"),
    ("pdf", "Png", ".pdf", ".pdf", ".png"),
    ("pdf", "Tiff", ".pdf", ".pdf", ".tiff"),
    ("pdf", "TextExtractor", ".pdf", ".pdf", ""),
    ("pdf", "Merger", ".pdf", ".pdf", ".pdf"),
    ("pdf", "Splitter", ".pdf", ".pdf", ".pdf"),
    ("pdf", "Optimizer", ".pdf", ".pdf", ".pdf"),
    ("pdf", "PdfAConverter", ".pdf", ".pdf", ".pdf"),
    ("pdf", "TocGenerator", ".pdf", ".pdf", ".pdf"),
    ("pdf", "TableGenerator", ".pdf", ".pdf", ".pdf"),
    ("pdf", "ImageExtractor", ".pdf", ".pdf", ".png"),
    ("pdf", "Security", ".pdf", ".pdf", ".pdf"),
    ("pdf", "FormFlattener", ".pdf", ".pdf", ".pdf"),
    ("pdf", "FormEditor", ".pdf", ".pdf", ".pdf"),
    ("pdf", "FormExporter", ".pdf", ".pdf", ".json"),
    ("pdf", "Signature", ".pdf", ".pdf", ".pdf"),
    # Diagram (2) — from diagram config allowed_types
    ("diagram", "DiagramConverter", ".vsdx", ".vsdx", ".vdx"),
    ("diagram", "PdfConverter", ".vsdx", ".vsdx", ".pdf"),
    # Email (1) — from email config allowed_types
    ("email", "Converter", ".eml", ".eml", "directory"),
    # Slides (3) — from slides config allowed_types
    ("slides", "Convert", ".pptx", ".pptx", ".pdf"),
    ("slides", "Merger", ".pptx", ".pptx", ".pptx"),
    ("slides", "Compress", ".pptx", ".pptx", ".pptx"),
]


@pytest.mark.parametrize(
    "family,type_name,family_default,expected_input,expected_output",
    _ACTIVE_TYPES,
    ids=[f"{f}:{t}" for f, t, *_ in _ACTIVE_TYPES],
)
def test_output_format_not_dot_out(
    family, type_name, family_default, expected_input, expected_output
):
    """No active type should fall through to .out default when called with
    the correct family default (which is what happens in production)."""
    result = _infer_output_format(type_name, family_default=family_default, family=family)
    assert result != ".out", (
        f"{family}:{type_name} fell through to .out — missing planner map entry"
    )


@pytest.mark.parametrize(
    "family,type_name,family_default,expected_input,expected_output",
    _ACTIVE_TYPES,
    ids=[f"{f}:{t}" for f, t, *_ in _ACTIVE_TYPES],
)
def test_output_format_correct(
    family, type_name, family_default, expected_input, expected_output
):
    """Output format matches expected value from the matrix."""
    result = _infer_output_format(type_name, family_default=family_default, family=family)
    assert result == expected_output, (
        f"{family}:{type_name}: expected output '{expected_output}', got '{result}'"
    )


@pytest.mark.parametrize(
    "family,type_name,family_default,expected_input,expected_output",
    _ACTIVE_TYPES,
    ids=[f"{f}:{t}" for f, t, *_ in _ACTIVE_TYPES],
)
def test_input_format_correct(
    family, type_name, family_default, expected_input, expected_output
):
    """Input format matches expected value from the matrix."""
    result = _infer_input_format(type_name, family_default=family_default, family=family)
    assert result == expected_input, (
        f"{family}:{type_name}: expected input '{expected_input}', got '{result}'"
    )


@pytest.mark.parametrize(
    "family,type_name,family_default,expected_input,expected_output",
    [t for t in _ACTIVE_TYPES if t[4]],  # Only types with non-empty output
    ids=[f"{f}:{t}" for f, t, *_ in _ACTIVE_TYPES if _ACTIVE_TYPES[_ACTIVE_TYPES.index((f, t, *_))][4]],
)
def test_output_format_not_dot_out_with_dot_out_default(
    family, type_name, family_default, expected_input, expected_output
):
    """Types with explicit output entries should NOT fall to .out even when
    family_default is .out. Extractors (empty output) are excluded."""
    result = _infer_output_format(type_name, family_default=".out", family=family)
    assert result != ".out", (
        f"{family}:{type_name} fell through to .out with .out default — "
        f"needs explicit planner map entry"
    )


def test_active_type_count():
    """Ensure the test covers exactly 42 active types."""
    assert len(_ACTIVE_TYPES) == 42, (
        f"Expected 42 active types, got {len(_ACTIVE_TYPES)}"
    )
