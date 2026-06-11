"""TC-MEGA-D01-D02: Verify example.manifest.json and expected-output.json contain contract fields."""

from __future__ import annotations

import json
import pytest
from pathlib import Path


class TestManifestContractFields:
    """Verify generate_project writes contract fields to manifest."""

    def test_manifest_has_contract_fields_when_contract_available(self, tmp_path):
        """Manifest should contain contract_* fields when FormatContract is found."""
        from plugin_examples.generator.project_generator import generate_project, GeneratedExample
        from plugin_examples.format_authority.store import get_contract, reset_store

        reset_store()
        fc = get_contract("cells", "SpreadsheetConverter")

        example = GeneratedExample(
            scenario_id="cells-spreadsheetconverter",
            code='Console.WriteLine("Example: cells-spreadsheetconverter");',
        )
        # Inject format_contract via attribute (project_generator reads via getattr)
        example.format_contract = fc.to_dict()

        result = generate_project(
            example=example,
            package_id="Aspose.Cells",
            package_version="26.5.1",
            output_dir=tmp_path,
            input_strategy="generated_fixture_file",
            input_files=["input.xlsx"],
        )
        manifest_path = Path(result["project_dir"]) / "example.manifest.json"
        assert manifest_path.exists()
        manifest = json.loads(manifest_path.read_text())
        assert manifest.get("contract_output_format") == ".csv"
        assert manifest.get("contract_input_format") == ".xlsx"
        assert manifest.get("contract_operation_kind") == "converter"
        assert manifest.get("contract_output_kind") == "file"
        assert manifest.get("contract_id"), "contract_id should be non-empty"

    def test_expected_output_has_contract_extension(self, tmp_path):
        """expected-output.json should contain expected_output_extension from contract."""
        from plugin_examples.generator.project_generator import generate_project, GeneratedExample
        from plugin_examples.format_authority.store import get_contract, reset_store

        reset_store()
        fc = get_contract("cells", "SpreadsheetConverter")

        example = GeneratedExample(
            scenario_id="cells-spreadsheetconverter",
            code='Console.WriteLine("Example: cells-spreadsheetconverter");',
        )
        example.format_contract = fc.to_dict()

        result = generate_project(
            example=example,
            package_id="Aspose.Cells",
            package_version="26.5.1",
            output_dir=tmp_path,
            input_strategy="generated_fixture_file",
            input_files=["input.xlsx"],
        )
        eo_path = Path(result["project_dir"]) / "expected-output.json"
        assert eo_path.exists()
        eo = json.loads(eo_path.read_text())
        assert eo.get("expected_output_extension") == ".csv"
        assert eo.get("expected_output_kind") == "file"
        assert eo.get("expected_output_cardinality") == "single"

    def test_manifest_without_contract_has_no_stale_dot_out(self, tmp_path):
        """Manifest written without any contract should not have .out in output_format."""
        from plugin_examples.generator.project_generator import generate_project, GeneratedExample
        from plugin_examples.format_authority.store import reset_store

        reset_store()

        example = GeneratedExample(
            scenario_id="cells-spreadsheetconverter",
            code='Console.WriteLine("Example: cells-spreadsheetconverter");',
        )
        # No format_contract attribute — fallback lookup may or may not succeed
        result = generate_project(
            example=example,
            package_id="Aspose.Cells",
            package_version="26.5.1",
            output_dir=tmp_path,
            input_strategy="generated_fixture_file",
            input_files=["input.xlsx"],
        )
        manifest_path = Path(result["project_dir"]) / "example.manifest.json"
        manifest = json.loads(manifest_path.read_text())
        # output_format may be empty or inferred, but must not be the stale .out fallback
        output_fmt = manifest.get("output_format", "")
        assert output_fmt != ".out", f"Manifest output_format is '{output_fmt}' — stale .out from legacy map is leaking"
