"""Tests for registry code generator (TC-P3-05).

Validates:
- generate_code_from_registry produces valid C# code
- Code uses correct namespace, type, and method from registry entry
- GeneratedExample has correct scenario_id and generation_strategy
"""

from __future__ import annotations

from plugin_examples.generator.registry_code_generator import generate_code_from_registry
from plugin_examples.scenario_planner.planner import Scenario


def _make_scenario(
    scenario_id: str = "barcode-generate-barcode",
    target_type: str = "Aspose.BarCode.Generation.BarcodeGenerator",
    target_namespace: str = "Aspose.BarCode.Generation",
) -> Scenario:
    return Scenario(
        scenario_id=scenario_id,
        title=f"Use BarcodeGenerator from {target_namespace}",
        target_type=target_type,
        target_namespace=target_namespace,
        target_methods=["Save"],
        status="ready",
    )


def _make_registry_entry(
    type_name: str = "BarcodeGenerator",
    namespace: str = "Aspose.BarCode.Generation",
    method_name: str = "Save",
    constructor: str = "BarcodeGenerator(EncodeTypes, string)",
) -> dict:
    return {
        "type_name": type_name,
        "namespace": namespace,
        "method_name": method_name,
        "operation_kind": "BARCODE_GENERATION",
        "selected_api_mapping": {
            "type_name": type_name,
            "namespace": namespace,
            "method_name": method_name,
            "constructor": constructor,
            "output_format_enum": "BarCodeImageFormat",
        },
    }


class TestGenerateCodeFromRegistry:
    def test_produces_valid_cs_code(self) -> None:
        scenario = _make_scenario()
        entry = _make_registry_entry()

        example = generate_code_from_registry(scenario, entry, "Aspose.BarCode")

        assert "using Aspose.BarCode.Generation;" in example.code
        assert "BarcodeGenerator" in example.code
        assert "Save" in example.code
        assert "barcode-generate-barcode" in example.code

    def test_scenario_id_matches(self) -> None:
        scenario = _make_scenario(scenario_id="barcode-generate-qr")
        entry = _make_registry_entry()

        example = generate_code_from_registry(scenario, entry, "Aspose.BarCode")

        assert example.scenario_id == "barcode-generate-qr"

    def test_generation_strategy_is_registry_template(self) -> None:
        scenario = _make_scenario()
        entry = _make_registry_entry()

        example = generate_code_from_registry(scenario, entry, "Aspose.BarCode")

        assert example.generation_strategy == "registry_template"

    def test_claimed_symbols_include_type_and_method(self) -> None:
        scenario = _make_scenario()
        entry = _make_registry_entry()

        example = generate_code_from_registry(scenario, entry, "Aspose.BarCode")

        assert any("BarcodeGenerator" in s for s in example.claimed_symbols)
        assert any("Save" in s for s in example.claimed_symbols)

    def test_constructor_with_params(self) -> None:
        scenario = _make_scenario()
        entry = _make_registry_entry(constructor="BarcodeGenerator(EncodeTypes, string)")

        example = generate_code_from_registry(scenario, entry, "Aspose.BarCode")

        assert "EncodeTypes.Code128" in example.code
        assert '"' in example.code  # string parameter default

    def test_empty_constructor(self) -> None:
        scenario = _make_scenario()
        entry = _make_registry_entry(constructor="")

        example = generate_code_from_registry(scenario, entry, "Aspose.BarCode")

        assert "new BarcodeGenerator()" in example.code

    def test_read_method_pattern(self) -> None:
        scenario = _make_scenario(scenario_id="barcode-recognize-barcode")
        entry = {
            "type_name": "BarCodeReader",
            "namespace": "Aspose.BarCode.BarCodeRecognition",
            "method_name": "ReadBarCodes",
            "operation_kind": "BARCODE_RECOGNITION",
            "selected_api_mapping": {
                "type_name": "BarCodeReader",
                "namespace": "Aspose.BarCode.BarCodeRecognition",
                "method_name": "ReadBarCodes",
                "constructor": "BarCodeReader(string, DecodeType)",
            },
        }

        example = generate_code_from_registry(scenario, entry, "Aspose.BarCode")

        assert "ReadBarCodes" in example.code
        assert "BarCodeReader" in example.code
