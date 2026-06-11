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

        code = "Bad code with output.out"
        (tmp_path / "Program.cs").write_text(code, encoding="utf-8")
        result = _advisory_code_contract_validation(str(tmp_path), "unknown-type")
        # Even with bad code, advisory should not raise
        assert isinstance(result, str)


class TestContractBlockingMode:
    """TC-REGEN-B01: Verify contract_blocking_mode promotes advisory->blocking."""

    def _make_valid_vr(self, scenario_id: str, project_path: str):
        """Helper: create a passed ValidationResult-like object."""

        class FakeBuild:
            success = True

        class FakeRun:
            success = True

        class FakeVR:
            restore = None

        vr = FakeVR()
        vr.scenario_id = scenario_id
        vr.build = FakeBuild()
        vr.run = FakeRun()
        return vr

    def test_blocking_mode_blocks_on_code_contract_failed(self, tmp_path):
        """When contract_blocking_mode=True and code contract fails, example is blocked."""
        from plugin_examples.gates.example_gates import evaluate_example_gates

        proj_dir = tmp_path / "cells-spreadsheetconverter"
        proj_dir.mkdir()
        # Wrong output extension → advisory_failed
        code = 'SpreadsheetConverter.Process("input.xlsx", "output.xlsx");'
        (proj_dir / "Program.cs").write_text(code, encoding="utf-8")
        manifest = {
            "scenario_id": "cells-spreadsheetconverter",
            "contract_id": "cells/SpreadsheetConverter",
            "contract_output_format": ".csv",
            "contract_input_format": ".xlsx",
            "contract_output_kind": "file",
            "contract_output_cardinality": "single",
            "contract_operation_kind": "converter",
        }
        (proj_dir / "example.manifest.json").write_text(json.dumps(manifest))
        vr = self._make_valid_vr("cells-spreadsheetconverter", str(proj_dir))
        gp = [{"scenario_id": "cells-spreadsheetconverter", "project_dir": str(proj_dir)}]
        results = evaluate_example_gates(
            validation_results=[vr],
            generated_projects=gp,
            contract_blocking_mode=True,
        )
        assert len(results) == 1
        assert results[0].final_example_verdict == "EXAMPLE_BLOCKED_CODE_CONTRACT_FAILED"
        assert results[0].publish_candidate is False

    def test_advisory_mode_does_not_block_on_code_contract_failed(self, tmp_path):
        """When contract_blocking_mode=False and code contract fails, example still passes."""
        from plugin_examples.gates.example_gates import evaluate_example_gates

        proj_dir = tmp_path / "cells-spreadsheetconverter"
        proj_dir.mkdir()
        code = 'SpreadsheetConverter.Process("input.xlsx", "output.xlsx");'
        (proj_dir / "Program.cs").write_text(code, encoding="utf-8")
        manifest = {
            "scenario_id": "cells-spreadsheetconverter",
            "contract_id": "cells/SpreadsheetConverter",
            "contract_output_format": ".csv",
            "contract_input_format": ".xlsx",
            "contract_output_kind": "file",
            "contract_output_cardinality": "single",
            "contract_operation_kind": "converter",
        }
        (proj_dir / "example.manifest.json").write_text(json.dumps(manifest))
        vr = self._make_valid_vr("cells-spreadsheetconverter", str(proj_dir))
        gp = [{"scenario_id": "cells-spreadsheetconverter", "project_dir": str(proj_dir)}]
        results = evaluate_example_gates(
            validation_results=[vr],
            generated_projects=gp,
            contract_blocking_mode=False,
        )
        assert len(results) == 1
        # Advisory mode: contract failure doesn't block
        assert results[0].final_example_verdict == "EXAMPLE_READY_FOR_PR_DRY_RUN"
        assert results[0].publish_candidate is True

    def test_blocking_mode_passes_on_correct_contract(self, tmp_path):
        """When contract_blocking_mode=True and code contract passes, example is ready."""
        from plugin_examples.gates.example_gates import evaluate_example_gates

        proj_dir = tmp_path / "cells-spreadsheetconverter"
        proj_dir.mkdir()
        # Correct output extension
        code = 'SpreadsheetConverter.Process("input.xlsx", "output.csv");'
        (proj_dir / "Program.cs").write_text(code, encoding="utf-8")
        manifest = {
            "scenario_id": "cells-spreadsheetconverter",
            "contract_id": "cells/SpreadsheetConverter",
            "contract_output_format": ".csv",
            "contract_input_format": ".xlsx",
            "contract_output_kind": "file",
            "contract_output_cardinality": "single",
            "contract_operation_kind": "converter",
        }
        (proj_dir / "example.manifest.json").write_text(json.dumps(manifest))
        vr = self._make_valid_vr("cells-spreadsheetconverter", str(proj_dir))
        gp = [{"scenario_id": "cells-spreadsheetconverter", "project_dir": str(proj_dir)}]
        results = evaluate_example_gates(
            validation_results=[vr],
            generated_projects=gp,
            contract_blocking_mode=True,
        )
        assert len(results) == 1
        assert results[0].final_example_verdict == "EXAMPLE_READY_FOR_PR_DRY_RUN"
        assert results[0].publish_candidate is True
