"""TC-MEGA-B01: Verify planner production calls consume FormatContract with no legacy fallback."""

from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock
from plugin_examples.scenario_planner.planner import _infer_input_format, _infer_output_format
from plugin_examples.format_authority.store import MissingFormatContractError


class TestPlannerContractFirstNoLegacyFallback:
    """Verify allow_legacy_format_inference=False is the production default for direct calls."""

    def test_infer_input_format_uses_contract(self):
        """With family set, input format comes from FormatContract."""
        result = _infer_input_format("SpreadsheetConverter", ".xlsx", family="cells",
                                     allow_legacy_format_inference=False)
        assert result == ".xlsx"

    def test_infer_output_format_spreadsheetconverter_csv(self):
        """SpreadsheetConverter output is .csv from contract, not .xlsx from legacy map."""
        result = _infer_output_format("SpreadsheetConverter", family_default=".xlsx", family="cells",
                                      allow_legacy_format_inference=False)
        assert result == ".csv", f"Expected .csv (contract), got {result}"

    def test_infer_output_format_formexporter_json(self):
        """FormExporter output is .json from contract, not .xml or .out."""
        result = _infer_output_format("FormExporter", family_default=".out", family="pdf",
                                      allow_legacy_format_inference=False)
        assert result == ".json"

    def test_infer_output_format_textextractor_empty(self):
        """TextExtractor canonical_output_format is empty (stdout)."""
        result = _infer_output_format("TextExtractor", family_default=".out", family="pdf",
                                      allow_legacy_format_inference=False)
        assert result == ""  # stdout types have empty canonical_output_format

    def test_infer_output_format_email_converter(self):
        """Email Converter output_kind is directory — contract returns 'directory'."""
        result = _infer_output_format("Converter", family_default=".eml", family="email",
                                      allow_legacy_format_inference=False)
        # Email Converter directory output: canonical_output_format = "directory"
        assert result == "directory", f"Expected 'directory' from contract, got: {result!r}"

    def test_infer_input_no_fallback_to_wrong_map(self):
        """With allow_legacy_format_inference=False, missing contract raises MissingFormatContractError.
        Sprint 57: fail-closed — unknown types raise instead of returning stale map values."""
        with pytest.raises(MissingFormatContractError):
            _infer_input_format("NonExistentType", ".xlsx", family="cells",
                                allow_legacy_format_inference=False)

    def test_infer_output_no_fallback_to_dot_out(self):
        """With allow_legacy_format_inference=False, missing contract raises MissingFormatContractError.
        Sprint 57: fail-closed — unknown types raise instead of returning .out from stale map."""
        with pytest.raises(MissingFormatContractError):
            _infer_output_format("NonExistentType", family_default=".xlsx", family="cells",
                                 allow_legacy_format_inference=False)

    def test_textconverter_input_is_xlsx(self):
        """TextConverter input is .xlsx from contract."""
        result = _infer_input_format("TextConverter", ".xlsx", family="cells",
                                     allow_legacy_format_inference=False)
        assert result == ".xlsx"

    def test_textconverter_output_is_txt(self):
        """TextConverter output is .txt from contract."""
        result = _infer_output_format("TextConverter", family_default=".xlsx", family="cells",
                                      allow_legacy_format_inference=False)
        assert result == ".txt"

    def test_words_converter_output_is_pdf(self):
        """Words Converter output is .pdf from contract."""
        result = _infer_output_format("Converter", family_default=".docx", family="words",
                                      allow_legacy_format_inference=False)
        assert result == ".pdf"
