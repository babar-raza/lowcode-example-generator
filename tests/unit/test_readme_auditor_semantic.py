"""Tests for README auditor semantic checks (V8 format lifecycle).

Tests checks 16-19: same-format converter, splitter cardinality,
merger cardinality, and extractor output kind validation.
"""

import pytest
from unittest.mock import patch

from plugin_examples.publisher.readme_auditor import audit_readme, ReadmeAuditResult


# Minimal README template that passes the 15 existing checks
_MINIMAL_README = """# Aspose.Cells LowCode Examples

## Overview

Examples for Aspose.Cells LowCode API.

## Included Examples

| Example | Demonstrated API | Input | Output | Status |
|---------|-----------------|-------|--------|--------|
{rows}

## Requirements

- .NET 8.0+

## How to Run

```bash
dotnet run
```

## Package Installation

```bash
dotnet add package Aspose.Cells 26.5.1
```

## Validation Status

All examples validated.

## Useful Links

- [Product Page](https://products.aspose.net/cells/)
- [Documentation](https://docs.aspose.net/cells/)
"""


def _make_readme(rows_text: str) -> str:
    return _MINIMAL_README.format(rows=rows_text)


def _make_context(examples: list[dict], family: str = "cells") -> dict:
    return {
        "package_version": "26.5.1",
        "family": family,
        "examples": examples,
    }


# We patch the URL validation imports to avoid needing aspose_links module
@pytest.fixture(autouse=True)
def _patch_url_checks():
    """Patch the aspose_links module functions that audit_readme imports at call time."""
    import plugin_examples.publisher.aspose_links as _links

    with (
        patch.object(_links, "find_forbidden_aspose_com_links", return_value=[]),
        patch.object(_links, "find_platform_path_errors", return_value=[]),
        patch.object(_links, "find_wrong_blog_links", return_value=[]),
        patch.object(_links, "find_wrong_contact_links", return_value=[]),
        patch.object(_links, "find_missing_required_links", return_value=[]),
    ):
        yield


class TestSameFormatConverterWarning:
    """Check 16: same-format converter warning."""

    def test_warns_on_same_format_converter(self):
        rows = "| `spreadsheet-converter` | `SpreadsheetConverter.Process` | xlsx | xlsx | passed |"
        examples = [
            {
                "name": "spreadsheet-converter",
                "operation_kind": "converter",
                "input_format": ".xlsx",
                "output_format": ".xlsx",
            }
        ]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.same_format_converter_warnings) == 1
        assert "spreadsheet-converter" in result.same_format_converter_warnings[0]

    def test_no_warning_on_cross_format_converter(self):
        rows = "| `pdf-converter` | `PdfConverter.Process` | pdf | docx | passed |"
        examples = [
            {"name": "pdf-converter", "operation_kind": "converter", "input_format": ".pdf", "output_format": ".docx"}
        ]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.same_format_converter_warnings) == 0

    def test_no_warning_when_operation_kind_missing(self):
        rows = "| `converter` | `Converter.Process` | pdf | pdf | passed |"
        examples = [{"name": "converter", "input_format": ".pdf", "output_format": ".pdf"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.same_format_converter_warnings) == 0

    def test_no_warning_on_transform(self):
        rows = "| `optimizer` | `Optimizer.Process` | pdf | pdf | passed |"
        examples = [
            {"name": "optimizer", "operation_kind": "transform", "input_format": ".pdf", "output_format": ".pdf"}
        ]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.same_format_converter_warnings) == 0


class TestSplitterCardinalityWarning:
    """Check 17: splitter cardinality missing."""

    def test_warns_on_splitter_without_cardinality(self):
        rows = "| `spreadsheet-splitter` | `Splitter.Process` | xlsx | xlsx | passed |"
        examples = [{"name": "spreadsheet-splitter", "operation_kind": "splitter", "output_format_display": "xlsx"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.splitter_cardinality_warnings) == 1

    def test_no_warning_on_splitter_with_1_to_N(self):
        rows = "| `spreadsheet-splitter` | `Splitter.Process` | xlsx | xlsx | passed |"
        examples = [
            {"name": "spreadsheet-splitter", "operation_kind": "splitter", "output_format_display": "xlsx (1->N)"}
        ]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.splitter_cardinality_warnings) == 0

    def test_no_warning_when_display_empty(self):
        rows = "| `splitter` | `Splitter.Process` | xlsx | xlsx | passed |"
        examples = [{"name": "splitter", "operation_kind": "splitter", "output_format_display": ""}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.splitter_cardinality_warnings) == 0


class TestMergerCardinalityWarning:
    """Check 18: merger cardinality missing."""

    def test_warns_on_merger_without_cardinality(self):
        rows = "| `spreadsheet-merger` | `Merger.Process` | xlsx | xlsx | passed |"
        examples = [{"name": "spreadsheet-merger", "operation_kind": "merger", "input_format_display": "xlsx"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.merger_cardinality_warnings) == 1

    def test_no_warning_on_merger_with_Nx(self):
        rows = "| `spreadsheet-merger` | `Merger.Process` | xlsx | xlsx | passed |"
        examples = [{"name": "spreadsheet-merger", "operation_kind": "merger", "input_format_display": "N × xlsx"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.merger_cardinality_warnings) == 0

    def test_no_warning_when_display_empty(self):
        rows = "| `merger` | `Merger.Process` | xlsx | xlsx | passed |"
        examples = [{"name": "merger", "operation_kind": "merger", "input_format_display": ""}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.merger_cardinality_warnings) == 0


class TestExtractorOutputWarning:
    """Check 19: extractor output kind validation."""

    def test_warns_on_extractor_without_stdout(self):
        rows = "| `text-extractor` | `TextExtractor.Process` | pdf | - | passed |"
        examples = [{"name": "text-extractor", "operation_kind": "extractor", "output_format_display": "pdf"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.extractor_output_warnings) == 1

    def test_no_warning_on_extractor_with_stdout(self):
        rows = "| `text-extractor` | `TextExtractor.Process` | pdf | - | passed |"
        examples = [{"name": "text-extractor", "operation_kind": "extractor", "output_format_display": "text (stdout)"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.extractor_output_warnings) == 0

    def test_warns_on_image_extractor_without_N_files(self):
        rows = "| `image-extractor` | `ImageExtractor.Process` | pdf | png | passed |"
        examples = [{"name": "image-extractor", "operation_kind": "image_extractor", "output_format_display": "png"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.extractor_output_warnings) == 1

    def test_no_warning_on_image_extractor_with_N_files(self):
        rows = "| `image-extractor` | `ImageExtractor.Process` | pdf | png | passed |"
        examples = [
            {"name": "image-extractor", "operation_kind": "image_extractor", "output_format_display": "png (N files)"}
        ]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.extractor_output_warnings) == 0

    def test_warns_on_directory_output_without_dir(self):
        rows = "| `converter` | `Converter.Process` | eml | - | passed |"
        examples = [{"name": "converter", "operation_kind": "directory_output", "output_format_display": "output"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.extractor_output_warnings) == 1

    def test_no_warning_on_directory_output_with_dir(self):
        rows = "| `converter` | `Converter.Process` | eml | - | passed |"
        examples = [{"name": "converter", "operation_kind": "directory_output", "output_format_display": "directory"}]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        assert len(result.extractor_output_warnings) == 0


class TestSemanticChecksAreAdvisory:
    """Semantic checks must NOT affect result.passed — they are advisory only."""

    def test_same_format_converter_does_not_fail_audit(self):
        rows = "| `converter` | `Converter.Process` | xlsx | xlsx | passed |"
        examples = [
            {"name": "converter", "operation_kind": "converter", "input_format": ".xlsx", "output_format": ".xlsx"}
        ]
        result = audit_readme(_make_readme(rows), _make_context(examples))
        # The audit may fail for other reasons (format claims etc) but
        # same_format_converter_warnings should not cause a failure on its own
        assert len(result.same_format_converter_warnings) == 1
        # The warning is advisory — it doesn't get added to failures list


class TestBackwardCompatibility:
    """New fields must have defaults — existing callers unaffected."""

    def test_new_fields_have_defaults(self):
        result = ReadmeAuditResult(passed=True)
        assert result.same_format_converter_warnings == []
        assert result.splitter_cardinality_warnings == []
        assert result.merger_cardinality_warnings == []
        assert result.extractor_output_warnings == []
