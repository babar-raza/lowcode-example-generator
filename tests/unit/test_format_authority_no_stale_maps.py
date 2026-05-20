"""Stale-map guard tests — verify pipeline functions return FormatContract values,
not legacy map values, for known-defective types.

These tests detect regression to pre-contract format decisions.
"""

import pytest

from plugin_examples.format_authority.store import get_contract, MissingFormatContractError
from plugin_examples.scenario_planner.planner import (
    _infer_input_format,
    _infer_output_format,
)


# Types where FormatContract differs from the old legacy map values.
# (family, type_name, family_default, old_wrong_output, contract_correct_output)
_KNOWN_DEFECTIVE_OUTPUTS = [
    ("cells", "SpreadsheetConverter", ".xlsx", ".xlsx", ".csv"),
    ("pdf", "FormExporter", ".pdf", ".xml", ".json"),
    ("email", "Converter", ".eml", ".eml", "directory"),
]

# Types where FormatContract differs from the old legacy map input values.
# (family, type_name, family_default, old_wrong_input, contract_correct_input)
_KNOWN_DEFECTIVE_INPUTS = [
    ("cells", "TextConverter", ".xlsx", ".csv", ".xlsx"),
]


class TestOutputFormatNotStale:
    """Verify _infer_output_format returns contract values, not legacy map values."""

    @pytest.mark.parametrize(
        "family,type_name,family_default,old_wrong,contract_correct",
        _KNOWN_DEFECTIVE_OUTPUTS,
        ids=[f"{f}:{t}" for f, t, *_ in _KNOWN_DEFECTIVE_OUTPUTS],
    )
    def test_output_matches_contract_not_legacy(
        self, family, type_name, family_default, old_wrong, contract_correct
    ):
        result = _infer_output_format(type_name, family_default=family_default, family=family)
        assert result == contract_correct, (
            f"{family}:{type_name} returned '{result}' — "
            f"expected contract value '{contract_correct}', "
            f"old stale value was '{old_wrong}'"
        )
        assert result != old_wrong, (
            f"{family}:{type_name} still returns stale legacy value '{old_wrong}'"
        )


class TestInputFormatNotStale:
    """Verify _infer_input_format returns contract values, not legacy map values."""

    @pytest.mark.parametrize(
        "family,type_name,family_default,old_wrong,contract_correct",
        _KNOWN_DEFECTIVE_INPUTS,
        ids=[f"{f}:{t}" for f, t, *_ in _KNOWN_DEFECTIVE_INPUTS],
    )
    def test_input_matches_contract_not_legacy(
        self, family, type_name, family_default, old_wrong, contract_correct
    ):
        result = _infer_input_format(type_name, family_default=family_default, family=family)
        assert result == contract_correct, (
            f"{family}:{type_name} returned '{result}' — "
            f"expected contract value '{contract_correct}', "
            f"old stale value was '{old_wrong}'"
        )


class TestContractStoreCoversAllFamilies:
    """Verify FormatContract store has entries for all 42 active types."""

    _ALL_ACTIVE = [
        ("cells", "SpreadsheetConverter"), ("cells", "JsonConverter"),
        ("cells", "HtmlConverter"), ("cells", "TextConverter"),
        ("cells", "ImageConverter"), ("cells", "SpreadsheetMerger"),
        ("cells", "SpreadsheetSplitter"), ("cells", "SpreadsheetLocker"),
        ("cells", "PdfConverter"),
        ("words", "Converter"), ("words", "Merger"), ("words", "Splitter"),
        ("words", "Comparer"), ("words", "MailMerger"), ("words", "ReportBuilder"),
        ("words", "Watermarker"), ("words", "Replacer"),
        ("pdf", "DocConverter"), ("pdf", "XlsConverter"), ("pdf", "Html"),
        ("pdf", "Jpeg"), ("pdf", "Png"), ("pdf", "Tiff"),
        ("pdf", "TextExtractor"), ("pdf", "Merger"), ("pdf", "Splitter"),
        ("pdf", "Optimizer"), ("pdf", "PdfAConverter"), ("pdf", "TocGenerator"),
        ("pdf", "TableGenerator"), ("pdf", "ImageExtractor"), ("pdf", "Security"),
        ("pdf", "FormFlattener"), ("pdf", "FormEditor"), ("pdf", "FormExporter"),
        ("pdf", "Signature"),
        ("diagram", "DiagramConverter"), ("diagram", "PdfConverter"),
        ("email", "Converter"),
        ("slides", "Convert"), ("slides", "Merger"), ("slides", "Compress"),
    ]

    @pytest.mark.parametrize(
        "family,type_name",
        _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_contract_exists(self, family, type_name):
        """Every active type must have a FormatContract in the store."""
        try:
            fc = get_contract(family, type_name)
        except (MissingFormatContractError, KeyError) as exc:
            pytest.fail(f"No FormatContract for {family}:{type_name}: {exc}")
        assert fc.family == family
        assert fc.type_name == type_name

    @pytest.mark.parametrize(
        "family,type_name",
        _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_contract_no_dot_out(self, family, type_name):
        """No FormatContract should have .out as canonical output."""
        fc = get_contract(family, type_name)
        assert fc.canonical_output_format != ".out", (
            f"{family}:{type_name} contract has .out output"
        )

    def test_total_count(self):
        assert len(self._ALL_ACTIVE) == 42
