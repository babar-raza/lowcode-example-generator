"""TC-MEGA-B02: Verify packet builder injects FormatContract into PromptPacket."""

from __future__ import annotations

import pytest
from plugin_examples.generator.packet_builder import PromptPacket, build_packet


def _minimal_catalog(family: str, type_name: str, ns: str, method: str) -> dict:
    full_name = f"{ns}.{type_name}"
    return {
        "namespaces": [
            {
                "namespace": ns,
                "types": [
                    {
                        "full_name": full_name,
                        "name": type_name,
                        "methods": [{"name": method, "signature": f"{method}(string, string)", "parameters": []}],
                        "properties": [],
                    }
                ],
            }
        ]
    }


def _minimal_scenario(family: str, type_name: str, ns: str, method: str) -> dict:
    return {
        "scenario_id": f"{family}-{type_name.lower()}",
        "target_type": f"{ns}.{type_name}",
        "target_namespace": ns,
        "target_methods": [method],
        "input_strategy": "generated_fixture_file",
        "input_files": ["input.xlsx"],
        "output_plan": f"Convert input to output using {type_name}",
        "required_fixtures": ["input.xlsx"],
        "format_contract_id": f"{family}/{type_name}",
    }


class TestPacketContractInjection:
    """Verify FormatContract is injected into PromptPacket constraints and dict."""

    def test_packet_has_format_contract_field(self):
        """PromptPacket.format_contract is a dict field."""
        p = PromptPacket(scenario_id="test", target_type="Foo", target_namespace="NS")
        assert isinstance(p.format_contract, dict)

    def test_spreadsheetconverter_contract_injected(self):
        """SpreadsheetConverter packet has format_contract dict with canonical .csv."""
        scenario = _minimal_scenario("cells", "SpreadsheetConverter",
                                     "Aspose.Cells.LowCode", "Process")
        catalog = _minimal_catalog("cells", "SpreadsheetConverter",
                                   "Aspose.Cells.LowCode", "Process")
        packet = build_packet(scenario, catalog)
        fc = packet.format_contract
        assert fc, "format_contract should not be empty for SpreadsheetConverter"
        assert fc.get("canonical_output_format") == ".csv"
        assert fc.get("input_format") == ".xlsx"

    def test_formexporter_contract_injected(self):
        """FormExporter packet has format_contract dict with canonical .json."""
        scenario = _minimal_scenario("pdf", "FormExporter",
                                     "Aspose.Pdf.LowCode", "Process")
        catalog = _minimal_catalog("pdf", "FormExporter",
                                   "Aspose.Pdf.LowCode", "Process")
        packet = build_packet(scenario, catalog)
        fc = packet.format_contract
        assert fc.get("canonical_output_format") == ".json"

    def test_constraints_include_contract_format(self):
        """Constraints list includes FORMAT CONTRACT with canonical output extension."""
        scenario = _minimal_scenario("cells", "SpreadsheetConverter",
                                     "Aspose.Cells.LowCode", "Process")
        catalog = _minimal_catalog("cells", "SpreadsheetConverter",
                                   "Aspose.Cells.LowCode", "Process")
        packet = build_packet(scenario, catalog)
        contract_constraints = [c for c in packet.constraints if "FORMAT CONTRACT" in c]
        assert contract_constraints, "No FORMAT CONTRACT in constraints"
        combined = " ".join(contract_constraints)
        assert ".csv" in combined, f"Expected .csv in FORMAT CONTRACT constraint, got: {combined}"

    def test_no_dot_out_in_constraints(self):
        """Constraints should not reference .out as valid format."""
        scenario = _minimal_scenario("pdf", "FormExporter",
                                     "Aspose.Pdf.LowCode", "Process")
        catalog = _minimal_catalog("pdf", "FormExporter",
                                   "Aspose.Pdf.LowCode", "Process")
        packet = build_packet(scenario, catalog)
        all_constraints = " ".join(packet.constraints)
        assert "output.out" not in all_constraints

    def test_stdout_type_gets_no_addoutput_constraint(self):
        """TextExtractor (stdout) constraint says do NOT use AddOutput."""
        scenario = _minimal_scenario("pdf", "TextExtractor",
                                     "Aspose.Pdf.LowCode", "Process")
        catalog = _minimal_catalog("pdf", "TextExtractor",
                                   "Aspose.Pdf.LowCode", "Process")
        packet = build_packet(scenario, catalog)
        contract_constraints = " ".join(c for c in packet.constraints if "FORMAT CONTRACT" in c)
        assert "stdout" in contract_constraints.lower() or "AddOutput" in contract_constraints
