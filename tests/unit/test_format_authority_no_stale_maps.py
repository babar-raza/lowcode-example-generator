"""Stale-map guard tests — verify pipeline functions return FormatContract values,
not legacy map values, for known-defective types.

Uses repo-local authority at pipeline/format-authority/.
No workspace run artifacts. No skips for missing authority files.
"""

import pytest
from pathlib import Path

from plugin_examples.format_authority.store import (
    get_contract,
    get_all_contracts,
    reset_store,
    MissingFormatContractError,
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
    def test_output_matches_contract_not_legacy(
        self, family, type_name, family_default, old_wrong, contract_correct
    ):
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
    def test_input_matches_contract_not_legacy(
        self, family, type_name, family_default, old_wrong, contract_correct
    ):
        result = _infer_input_format(type_name, family_default=family_default, family=family)
        assert result == contract_correct, (
            f"{family}:{type_name} returned '{result}' — "
            f"expected contract value '{contract_correct}', "
            f"old stale value was '{old_wrong}'"
        )


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


class TestContractStoreCoversAllFamilies:
    @pytest.mark.parametrize(
        "family,type_name", _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_contract_exists(self, family, type_name):
        fc = get_contract(family, type_name)
        assert fc.family == family
        assert fc.type_name == type_name

    @pytest.mark.parametrize(
        "family,type_name", _ALL_ACTIVE,
        ids=[f"{f}:{t}" for f, t in _ALL_ACTIVE],
    )
    def test_contract_no_dot_out(self, family, type_name):
        fc = get_contract(family, type_name)
        assert fc.canonical_output_format != ".out", (
            f"{family}:{type_name} contract has .out output"
        )

    def test_total_count(self):
        assert len(_ALL_ACTIVE) == 42

    def test_store_fails_closed_on_missing(self):
        with pytest.raises(MissingFormatContractError):
            get_contract("fake", "FakeType")

    def test_repo_local_authority_loaded(self):
        all_c = get_all_contracts()
        assert len(all_c) >= 42, f"Expected >= 42 contracts, got {len(all_c)}"
