"""Stale-map guard tests — verify pipeline functions return FormatContract values,
not legacy map values, for known-defective types.

Uses repo-local authority at pipeline/format-authority/.
No workspace run artifacts. No skips for missing authority files.
"""

from pathlib import Path

import pytest

from plugin_examples.format_authority.store import (
    MissingFormatContractError,
    get_all_contracts,
    get_contract,
    reset_store,
)
from plugin_examples.scenario_planner.planner import (
    _infer_input_format,
    _infer_output_format,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_store()
    yield
    reset_store()


# Types where FormatContract differs from the old legacy map values.
_KNOWN_DEFECTIVE_OUTPUTS = [
    ("cells", "SpreadsheetConverter", ".xlsx", ".xlsx", ".csv"),
    ("pdf", "FormExporter", ".pdf", ".xml", ".json"),
    ("email", "Converter", ".eml", ".eml", "directory"),
]

_KNOWN_DEFECTIVE_INPUTS = [
    ("cells", "TextConverter", ".xlsx", ".csv", ".xlsx"),
]


class TestOutputFormatNotStale:
    @pytest.mark.parametrize(
        "family,type_name,family_default,old_wrong,contract_correct",
        _KNOWN_DEFECTIVE_OUTPUTS,
        ids=[f"{f}:{t}" for f, t, *_ in _KNOWN_DEFECTIVE_OUTPUTS],
    )
    def test_output_matches_contract_not_legacy(self, family, type_name, family_default, old_wrong, contract_correct):
        result = _infer_output_format(type_name, family_default=family_default, family=family)
        assert result == contract_correct, (
            f"{family}:{type_name} returned '{result}' — "
            f"expected contract value '{contract_correct}', "
            f"old stale value was '{old_wrong}'"
        )


class TestInputFormatNotStale:
    @pytest.mark.parametrize(
        "family,type_name,family_default,old_wrong,contract_correct",
        _KNOWN_DEFECTIVE_INPUTS,
        ids=[f"{f}:{t}" for f, t, *_ in _KNOWN_DEFECTIVE_INPUTS],
    )
    def test_input_matches_contract_not_legacy(self, family, type_name, family_default, old_wrong, contract_correct):
        result = _infer_input_format(type_name, family_default=family_default, family=family)
        assert result == contract_correct, (
            f"{family}:{type_name} returned '{result}' — "
            f"expected contract value '{contract_correct}', "
            f"old stale value was '{old_wrong}'"
        )


_ALL_ACTIVE = [
    ("cells", "SpreadsheetConverter"),
    ("cells", "JsonConverter"),
    ("cells", "HtmlConverter"),
    ("cells", "TextConverter"),
    ("cells", "ImageConverter"),
    ("cells", "SpreadsheetMerger"),
    ("cells", "SpreadsheetSplitter"),
    ("cells", "SpreadsheetLocker"),
    ("cells", "PdfConverter"),
    ("words", "Converter"),
    ("words", "Merger"),
    ("words", "Splitter"),
    ("words", "Comparer"),
    ("words", "MailMerger"),
    ("words", "ReportBuilder"),
    ("words", "Watermarker"),
    ("words", "Replacer"),
    ("pdf", "DocConverter"),
    ("pdf", "XlsConverter"),
    ("pdf", "Html"),
    ("pdf", "Jpeg"),
    ("pdf", "Png"),
    ("pdf", "Tiff"),
    ("pdf", "TextExtractor"),
    ("pdf", "Merger"),
    ("pdf", "Splitter"),
    ("pdf", "Optimizer"),
    ("pdf", "PdfAConverter"),
    ("pdf", "TocGenerator"),
    ("pdf", "TableGenerator"),
    ("pdf", "ImageExtractor"),
    ("pdf", "Security"),
    ("pdf", "FormFlattener"),
    ("pdf", "FormEditor"),
    ("pdf", "FormExporter"),
    ("pdf", "Signature"),
    ("diagram", "DiagramConverter"),
    ("diagram", "PdfConverter"),
    ("email", "Converter"),
    ("slides", "Convert"),
    ("slides", "Merger"),
    ("slides", "Compress"),
]


class TestContractStoreCoversAllFamilies:
    @pytest.mark.parametrize(
        "family,type_name",
        _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_contract_exists(self, family, type_name):
        fc = get_contract(family, type_name)
        assert fc.family == family
        assert fc.type_name == type_name

    @pytest.mark.parametrize(
        "family,type_name",
        _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_contract_no_dot_out(self, family, type_name):
        fc = get_contract(family, type_name)
        assert fc.canonical_output_format != ".out", f"{family}:{type_name} contract has .out output"

    def test_total_count(self):
        assert len(_ALL_ACTIVE) == 42

    def test_store_fails_closed_on_missing(self):
        with pytest.raises(MissingFormatContractError):
            get_contract("fake", "FakeType")

    def test_repo_local_authority_loaded(self):
        all_c = get_all_contracts()
        assert len(all_c) >= 42, f"Expected >= 42 contracts, got {len(all_c)}"


# ---------------------------------------------------------------------------
# TC-MEGA-G02: Stale-Map Guards
# ---------------------------------------------------------------------------


class TestPlannerProductionFailClosed:
    """Guard: planner production mode never falls back to stale legacy maps."""

    def test_spreadsheet_converter_not_xlsx_with_fail_closed(self):
        """SpreadsheetConverter must return .csv (contract), not .xlsx (stale map)."""
        result = _infer_output_format(
            "SpreadsheetConverter", family_default=".xlsx", family="cells", allow_legacy_format_inference=False
        )
        assert result != ".xlsx", "SpreadsheetConverter returned .xlsx — stale map is leaking into production"
        assert result == ".csv", f"SpreadsheetConverter should return .csv from contract, got: {result}"

    def test_form_exporter_not_xml_with_fail_closed(self):
        """FormExporter must return .json (contract), not .xml (stale map)."""
        result = _infer_output_format(
            "FormExporter", family_default=".pdf", family="pdf", allow_legacy_format_inference=False
        )
        assert result != ".xml", "FormExporter returned .xml — stale map is leaking"
        assert result == ".json", f"Expected .json from contract, got: {result}"

    def test_text_converter_input_not_csv_with_fail_closed(self):
        """TextConverter input must return .xlsx (contract), not .csv (stale map)."""
        result = _infer_input_format(
            "TextConverter", family_default=".xlsx", family="cells", allow_legacy_format_inference=False
        )
        assert result != ".csv", "TextConverter input returned .csv — stale map leaking"
        assert result == ".xlsx", f"Expected .xlsx from contract, got: {result}"

    def test_unknown_type_returns_family_default_not_out(self):
        """Unknown type with fail_closed=True raises MissingFormatContractError — not .out stale map.
        Sprint 57: fail-closed means unknown types propagate a typed error, never fall back."""
        with pytest.raises(MissingFormatContractError):
            _infer_output_format(
                "BogusType", family_default=".xlsx", family="cells", allow_legacy_format_inference=False
            )

    @pytest.mark.parametrize(
        "family,type_name",
        _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_all_active_types_return_contract_value_not_out(self, family, type_name):
        """With fail-closed enabled, every active type should return a non-.out value."""
        family_defaults = {
            "cells": ".xlsx",
            "words": ".docx",
            "pdf": ".pdf",
            "diagram": ".vsdx",
            "email": ".eml",
            "slides": ".pptx",
        }
        result = _infer_output_format(
            type_name,
            family_default=family_defaults.get(family, ".out"),
            family=family,
            allow_legacy_format_inference=False,
        )
        assert result != ".out", f"{family}:{type_name} returned .out — contract is missing or not loaded"


class TestCodegenMapProductionGuard:
    """Guard: codegen _infer_output_extension uses contract over stale _FORMAT_NAME_TO_EXT."""

    def test_spreadsheet_converter_returns_csv_not_xlsx(self):
        """With family hint, SpreadsheetConverter should return .csv, not .xlsx."""
        from plugin_examples.generator.code_generator import _infer_output_extension

        result = _infer_output_extension("SpreadsheetConverter", hints={"family": "cells"})
        assert result != ".xlsx", (
            "SpreadsheetConverter codegen returned .xlsx — 'spreadsheet' entry in "
            "_FORMAT_NAME_TO_EXT is leaking (should be overridden by contract)"
        )
        assert result == ".csv", f"Expected .csv from contract, got: {result}"

    def test_form_exporter_returns_json_not_xml(self):
        """With family hint, FormExporter should return .json, not .xml."""
        from plugin_examples.generator.code_generator import _infer_output_extension

        result = _infer_output_extension("FormExporter", hints={"family": "pdf"})
        assert result != ".xml", "FormExporter codegen returned .xml — stale map leak"
        assert result == ".json", f"Expected .json from contract, got: {result}"

    @pytest.mark.parametrize(
        "family,type_name",
        _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_codegen_no_dot_out_when_family_known(self, family, type_name):
        """With family hint, codegen must never return .out for any active type."""
        from plugin_examples.generator.code_generator import _infer_output_extension

        result = _infer_output_extension(type_name, hints={"family": family})
        assert result != ".out", f"codegen returned .out for {family}:{type_name} — contract not loaded or missing"
