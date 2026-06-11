"""TC-MEGA-D03: Verify runner evidence writer uses FormatContract authority."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from plugin_examples.format_authority.store import reset_store


@pytest.fixture(autouse=True)
def _reset():
    reset_store()
    yield
    reset_store()


def _make_scenario(scenario_id: str, target_type: str, input_fmt: str = ".xlsx") -> MagicMock:
    s = MagicMock()
    s.scenario_id = scenario_id
    s.target_type = f"Aspose.Cells.LowCode.{target_type}"
    s.required_input_format = input_fmt
    s.required_output_contract = ""  # not pre-populated — runner must look up contract
    s.format_contract_id = ""
    s.format_contract_hash = ""
    return s


class TestRunnerEvidenceUsesContract:
    """Verify _write_scenario_input_format_map() reads from FormatContract, not stale maps."""

    def test_spreadsheet_converter_evidence_has_csv(self, tmp_path):
        from plugin_examples.runner import _write_scenario_input_format_map

        planning = MagicMock()
        planning.ready_scenarios = [_make_scenario("cells-spreadsheetconverter", "SpreadsheetConverter")]
        _write_scenario_input_format_map(planning, tmp_path)

        evidence = json.loads((tmp_path / "latest" / "scenario-input-format-map.json").read_text())
        row = evidence["scenarios"][0]
        assert row["selected_output_format"] == ".csv", (
            f"Runner evidence recorded '{row['selected_output_format']}' for SpreadsheetConverter; "
            "expected '.csv' from contract (not '.xlsx' from stale planner map)"
        )
        assert (
            row["source"] == "format_contract"
        ), f"Source was '{row['source']}' — should be 'format_contract', not 'planner_map_deprecated'"

    def test_form_exporter_evidence_has_json(self, tmp_path):
        from plugin_examples.runner import _write_scenario_input_format_map

        planning = MagicMock()
        fe = MagicMock()
        fe.scenario_id = "pdf-formexporter"
        fe.target_type = "Aspose.Pdf.LowCode.FormExporter"
        fe.required_input_format = ".pdf"
        fe.required_output_contract = ""
        fe.format_contract_id = ""
        fe.format_contract_hash = ""
        planning.ready_scenarios = [fe]

        _write_scenario_input_format_map(planning, tmp_path)
        evidence = json.loads((tmp_path / "latest" / "scenario-input-format-map.json").read_text())
        row = evidence["scenarios"][0]
        assert row["selected_output_format"] == ".json", (
            f"Runner evidence recorded '{row['selected_output_format']}' for FormExporter; "
            "expected '.json' from contract (not '.xml' from stale map)"
        )

    def test_evidence_has_contract_id(self, tmp_path):
        from plugin_examples.runner import _write_scenario_input_format_map

        planning = MagicMock()
        planning.ready_scenarios = [_make_scenario("cells-spreadsheetconverter", "SpreadsheetConverter")]
        _write_scenario_input_format_map(planning, tmp_path)

        evidence = json.loads((tmp_path / "latest" / "scenario-input-format-map.json").read_text())
        row = evidence["scenarios"][0]
        assert row.get("contract_id"), "contract_id should be populated from FormatContract"
        assert row.get("confidence") == "high", f"Confidence should be 'high', got '{row.get('confidence')}'"

    def test_no_stale_map_deprecated_source(self, tmp_path):
        """No active type should record source=planner_map_deprecated."""
        from plugin_examples.runner import _write_scenario_input_format_map

        active = [
            ("cells", "SpreadsheetConverter"),
            ("cells", "JsonConverter"),
            ("words", "Converter"),
            ("pdf", "FormExporter"),
        ]
        planning = MagicMock()
        planning.ready_scenarios = [_make_scenario(f"{fam}-{t.lower()}", t) for fam, t in active]
        _write_scenario_input_format_map(planning, tmp_path)

        evidence = json.loads((tmp_path / "latest" / "scenario-input-format-map.json").read_text())
        for row in evidence["scenarios"]:
            assert row["source"] != "planner_map_deprecated", (
                f"{row['scenario_id']} recorded source='planner_map_deprecated' — "
                "contract lookup failed, stale map is being used"
            )
