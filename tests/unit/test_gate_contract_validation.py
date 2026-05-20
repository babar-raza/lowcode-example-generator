"""TC-MEGA-E02: Verify code contract validator is wired into example gates."""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from plugin_examples.gates.example_gates import ExampleGateResult


class TestGateContractValidationField:
    """Verify ExampleGateResult has code_contract_validation_status field."""

    def test_gate_result_has_contract_validation_field(self):
        eg = ExampleGateResult(scenario_id="test", example_path="/tmp/test")
        assert hasattr(eg, "code_contract_validation_status")
        assert eg.code_contract_validation_status == "not_evaluated"


class TestAdvisoryCodeContractValidation:
    """Verify _advisory_code_contract_validation runs correctly."""

    def test_no_code_returns_advisory_no_code(self, tmp_path):
        from plugin_examples.gates.example_gates import _advisory_code_contract_validation
        result = _advisory_code_contract_validation(str(tmp_path), "cells-spreadsheetconverter")
        assert result == "advisory_no_code"

    def test_correct_code_advisory_passed(self, tmp_path):
        from plugin_examples.gates.example_gates import _advisory_code_contract_validation
        # Write Program.cs with correct output for SpreadsheetConverter
        code = 'SpreadsheetConverter.Process("input.xlsx", "output.csv");'
        (tmp_path / "Program.cs").write_text(code, encoding="utf-8")
        # Write manifest with contract
        manifest = {
            "scenario_id": "cells-spreadsheetconverter",
            "contract_id": "cells/SpreadsheetConverter",
            "contract_output_format": ".csv",
            "contract_input_format": ".xlsx",
            "contract_output_kind": "file",
            "contract_output_cardinality": "single",
            "contract_operation_kind": "converter",
        }
        (tmp_path / "example.manifest.json").write_text(json.dumps(manifest))
        result = _advisory_code_contract_validation(str(tmp_path), "cells-spreadsheetconverter")
        assert result == "advisory_passed"

    def test_wrong_output_ext_advisory_failed(self, tmp_path):
        from plugin_examples.gates.example_gates import _advisory_code_contract_validation
        # Write Program.cs with WRONG output for SpreadsheetConverter (xlsx instead of csv)
        code = 'SpreadsheetConverter.Process("input.xlsx", "output.xlsx");'
        (tmp_path / "Program.cs").write_text(code, encoding="utf-8")
        manifest = {
            "scenario_id": "cells-spreadsheetconverter",
            "contract_id": "cells/SpreadsheetConverter",
            "contract_output_format": ".csv",
            "contract_input_format": ".xlsx",
            "contract_output_kind": "file",
            "contract_output_cardinality": "single",
            "contract_operation_kind": "converter",
        }
        (tmp_path / "example.manifest.json").write_text(json.dumps(manifest))
        result = _advisory_code_contract_validation(str(tmp_path), "cells-spreadsheetconverter")
        assert result == "advisory_failed"

    def test_no_manifest_falls_back_to_store(self, tmp_path):
        from plugin_examples.gates.example_gates import _advisory_code_contract_validation
        # No manifest — falls back to store lookup by scenario_id
        code = 'SpreadsheetConverter.Process("input.xlsx", "output.csv");'
        (tmp_path / "Program.cs").write_text(code, encoding="utf-8")
        result = _advisory_code_contract_validation(str(tmp_path), "cells-spreadsheetconverter")
        # Should either pass (contract found via store) or no_contract
        assert result in ("advisory_passed", "advisory_no_contract", "not_evaluated")

    def test_advisory_never_blocks(self, tmp_path):
        """Advisory validation result is never a blocking verdict."""
        from plugin_examples.gates.example_gates import _advisory_code_contract_validation
        code = 'Bad code with output.out'
        (tmp_path / "Program.cs").write_text(code, encoding="utf-8")
        result = _advisory_code_contract_validation(str(tmp_path), "unknown-type")
        # Even with bad code, advisory should not raise
        assert isinstance(result, str)
