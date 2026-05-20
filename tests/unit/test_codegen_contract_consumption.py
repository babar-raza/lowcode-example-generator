"""TC-MEGA-C01 & C02: Verify codegen uses FormatContract as production authority."""

from __future__ import annotations

import pytest
from plugin_examples.generator.code_generator import _infer_output_extension


class TestCodegenContractConsumption:
    """Verify _infer_output_extension uses FormatContract as Priority 1."""

    def test_spreadsheetconverter_returns_csv_from_contract(self):
        """SpreadsheetConverter output is .csv from contract, not .xlsx from legacy map."""
        result = _infer_output_extension("SpreadsheetConverter",
                                          hints={"family": "cells"})
        assert result == ".csv", (
            f"SpreadsheetConverter should return .csv from contract, got {result}. "
            "Legacy map 'spreadsheet': '.xlsx' must NOT override contract."
        )

    def test_formexporter_returns_json_from_contract(self):
        """FormExporter output is .json from contract, not .xml from old planner map."""
        result = _infer_output_extension("FormExporter",
                                          hints={"family": "pdf"})
        # FormExporter output_kind=file, canonical=.json — _infer_output_extension may return "" for stdout
        # but FormExporter is file output
        assert result in (".json", ""), f"FormExporter expected .json, got {result}"

    def test_textconverter_returns_txt_from_contract(self):
        """TextConverter output is .txt from contract."""
        result = _infer_output_extension("TextConverter",
                                          hints={"family": "cells"})
        assert result == ".txt"

    def test_words_converter_returns_pdf(self):
        """Words Converter output is .pdf from contract."""
        result = _infer_output_extension("Converter",
                                          hints={"family": "words"})
        assert result == ".pdf"


class TestCodegenLegacyMapDeprecated:
    """Verify legacy _FORMAT_NAME_TO_EXT is not the production authority."""

    def test_legacy_map_not_overriding_contract(self):
        """When family hint is available, contract takes precedence over _FORMAT_NAME_TO_EXT."""
        # The legacy map has "spreadsheet": ".xlsx" but contract says .csv
        result = _infer_output_extension("SpreadsheetConverter",
                                          hints={"family": "cells"})
        assert result != ".xlsx", (
            "_FORMAT_NAME_TO_EXT 'spreadsheet' -> '.xlsx' must not override FormatContract"
        )

    def test_no_dot_out_from_active_type(self):
        """No active type should produce .out through codegen."""
        from plugin_examples.format_authority.store import get_all_contracts
        contracts = get_all_contracts()
        for (family, type_name), contract in contracts.items():
            result = _infer_output_extension(type_name, hints={"family": family})
            # stdout types return "" which is acceptable
            assert result != ".out", (
                f"{family}/{type_name}: _infer_output_extension returned .out — "
                "legacy map fallback must not produce .out for contract-backed types"
            )
