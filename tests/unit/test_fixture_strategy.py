"""Tests for the Fixture Strategy and Self-Contained Example Healing Sprint.

Covers: fixture factory, fixture strategy planning, project generation with
fixtures, packet contract, and scenario blocking/demotion.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from plugin_examples.fixture_registry.fixture_factory import (
    SUPPORTED_FORMATS,
    GeneratedFixture,
    generate_fixture,
    generate_fixtures_for_scenario,
    generate_xlsx,
    generate_csv,
    generate_txt,
    generate_json,
    generate_html,
    write_generated_fixtures_evidence,
)
from plugin_examples.scenario_planner.planner import (
    Scenario,
    _build_scenario,
    _needs_fixture,
)
from plugin_examples.generator.packet_builder import (
    PromptPacket,
    build_packet,
    _build_fixture_instruction,
)
from plugin_examples.generator.project_generator import (
    generate_project,
    _generate_csproj,
)
from plugin_examples.generator.code_generator import GeneratedExample


# --- Test 1: Example-reviewer fixture system discovered ---

class TestExampleReviewerFixtureSystemDiscovered:
    def test_example_reviewer_fixture_system_discovered(self):
        """Discovery doc and JSON must exist after Step 1."""
        discovery_doc = Path("docs/discovery/example-reviewer-fixture-system.md")
        discovery_json = Path("workspace/verification/latest/example-reviewer-fixture-system.json")
        assert discovery_doc.exists(), "Discovery doc not found"
        assert discovery_json.exists(), "Discovery JSON not found"
        data = json.loads(discovery_json.read_text())
        assert data["reuse_mode"] == "copy"
        assert len(data["fixture_builders_found"]) > 0
        assert "xlsx" in data["supported_formats"]


# --- Test 2: Fixture strategy blocks without valid input ---

class TestFixtureStrategyBlocksWithoutInput:
    def test_fixture_strategy_blocks_without_input(self):
        """A scenario needing an unsupported fixture format must be blocked."""
        type_info = {
            "full_name": "Aspose.Imaging.LowCode.PsdProcessor",
            "name": "PsdProcessor",
            "kind": "class",
            "methods": [
                {
                    "name": "Process",
                    "is_static": False,
                    "is_obsolete": False,
                    "parameters": [
                        {"name": "inputFile", "type": "System.String"},
                        {"name": "outputFile", "type": "System.String"},
                    ],
                }
            ],
        }
        scenario = _build_scenario("imaging", type_info, "Aspose.Imaging.LowCode", None, ".psd")
        assert scenario.status == "blocked_no_fixture"
        assert scenario.input_strategy == "no_valid_input_strategy"

    def test_supported_format_uses_generated_fixture(self):
        """A scenario needing .xlsx should use generated_fixture_file strategy."""
        type_info = {
            "full_name": "Aspose.Cells.LowCode.HtmlConverter",
            "name": "HtmlConverter",
            "kind": "class",
            "methods": [
                {
                    "name": "Process",
                    "is_static": True,
                    "is_obsolete": False,
                    "parameters": [
                        {"name": "inputFile", "type": "System.String"},
                        {"name": "outputFile", "type": "System.String"},
                    ],
                }
            ],
        }
        scenario = _build_scenario("cells", type_info, "Aspose.Cells.LowCode", None, ".xlsx")
        assert scenario.status == "ready"
        assert scenario.input_strategy == "generated_fixture_file"
        assert "input.xlsx" in scenario.input_files


# --- Test 3: Generated fixture file exists before run ---

class TestGeneratedFixtureFileExistsBeforeRun:
    def test_xlsx_fixture_is_valid_zip(self, tmp_path):
        """Generated .xlsx fixture must be a valid ZIP/OOXML file."""
        dest = tmp_path / "input.xlsx"
        assert generate_xlsx(dest) is True
        assert dest.exists()
        assert dest.stat().st_size > 0
        with zipfile.ZipFile(dest, 'r') as zf:
            names = zf.namelist()
            assert '[Content_Types].xml' in names
            assert 'xl/workbook.xml' in names
            assert 'xl/worksheets/sheet1.xml' in names

    def test_csv_fixture_has_content(self, tmp_path):
        dest = tmp_path / "input.csv"
        assert generate_csv(dest) is True
        content = dest.read_text()
        assert "Name,Value,Category" in content

    def test_json_fixture_is_valid(self, tmp_path):
        dest = tmp_path / "input.json"
        assert generate_json(dest) is True
        data = json.loads(dest.read_text())
        assert isinstance(data, list)
        assert len(data) == 3

    def test_html_fixture_has_table(self, tmp_path):
        dest = tmp_path / "input.html"
        assert generate_html(dest) is True
        content = dest.read_text()
        assert "<table>" in content

    def test_txt_fixture_has_content(self, tmp_path):
        dest = tmp_path / "input.txt"
        assert generate_txt(dest) is True
        assert dest.stat().st_size > 0

    def test_unsupported_format_returns_none(self, tmp_path):
        result = generate_fixture("input.psd", tmp_path)
        assert result is None

    def test_generate_fixtures_for_scenario(self, tmp_path):
        fixtures = generate_fixtures_for_scenario(["input.xlsx", "data.csv"], tmp_path)
        assert len(fixtures) == 2
        assert all(f.ready for f in fixtures)
        assert (tmp_path / "input.xlsx").exists()
        assert (tmp_path / "data.csv").exists()


# --- Test 4: Programmatic input creates file before plugin call ---

class TestProgrammaticInputCreatesFileBeforePluginCall:
    def test_programmatic_strategy_does_not_generate_fixture(self, tmp_path):
        """Programmatic input strategy means code creates the file, not the pipeline."""
        type_info = {
            "full_name": "Aspose.Cells.LowCode.SpreadsheetMerger",
            "name": "SpreadsheetMerger",
            "kind": "class",
            "methods": [
                {
                    "name": "Process",
                    "is_static": True,
                    "is_obsolete": False,
                    "parameters": [
                        {"name": "inputFiles", "type": "System.String[]"},
                        {"name": "outputFile", "type": "System.String"},
                    ],
                }
            ],
        }
        # With registry having the fixture, should be existing_fixture
        fixture_registry = {"fixtures": [{"filename": "sample-cells.xlsx", "available": True}]}
        scenario = _build_scenario("cells", type_info, "Aspose.Cells.LowCode", fixture_registry, ".xlsx")
        # If fixture found in registry, uses existing_fixture
        assert scenario.input_strategy in ("existing_fixture", "generated_fixture_file")


# --- Test 5: LLM packet forbids unlisted input files ---

class TestLlmPacketForbidsUnlistedInputFiles:
    def test_packet_constraints_forbid_unlisted_files(self):
        """Packet must contain constraints against referencing unlisted files."""
        scenario = {
            "scenario_id": "cells-html-converter",
            "target_type": "Aspose.Cells.LowCode.HtmlConverter",
            "target_namespace": "Aspose.Cells.LowCode",
            "target_methods": ["Process"],
            "required_symbols": ["Aspose.Cells.LowCode.HtmlConverter",
                                 "Aspose.Cells.LowCode.HtmlConverter.Process"],
            "required_fixtures": ["input.xlsx"],
            "output_plan": "Convert to HTML",
            "input_strategy": "generated_fixture_file",
            "input_files": ["input.xlsx"],
        }
        catalog = {
            "namespaces": [
                {
                    "namespace": "Aspose.Cells.LowCode",
                    "types": [
                        {
                            "full_name": "Aspose.Cells.LowCode.HtmlConverter",
                            "name": "HtmlConverter",
                            "kind": "class",
                            "methods": [
                                {
                                    "name": "Process",
                                    "is_static": True,
                                    "is_obsolete": False,
                                    "parameters": [
                                        {"name": "inputFile", "type": "System.String"},
                                        {"name": "outputFile", "type": "System.String"},
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        packet = build_packet(scenario, catalog)
        # Must forbid unlisted input files
        constraints_text = " ".join(packet.constraints)
        assert "Do not reference input.xlsx" in constraints_text
        assert "Do not assume" in constraints_text
        # Must include fixture instruction
        assert "input.xlsx" in packet.user_prompt
        assert packet.input_strategy == "generated_fixture_file"
        assert packet.input_files == ["input.xlsx"]

    def test_fixture_instruction_generated_fixture(self):
        instruction = _build_fixture_instruction("generated_fixture_file", ["input.xlsx"])
        assert "AppContext.BaseDirectory" in instruction
        assert "input.xlsx" in instruction
        assert "Do NOT create" in instruction

    def test_fixture_instruction_programmatic(self):
        instruction = _build_fixture_instruction("programmatic_input", [])
        assert "programmatically" in instruction

    def test_fixture_instruction_none(self):
        instruction = _build_fixture_instruction("none", [])
        assert instruction == ""


# --- Test 6: Project generator copies existing fixture ---

class TestProjectGeneratorCopiesExistingFixture:
    def test_project_generator_writes_generated_fixture(self, tmp_path):
        """When input_strategy is generated_fixture_file, fixture must exist in project dir."""
        example = GeneratedExample(
            scenario_id="cells-test",
            code='using System;\nclass Program { static void Main() { Console.WriteLine("ok"); } }',
            claimed_symbols=["Aspose.Cells.LowCode.TestType"],
        )
        project = generate_project(
            example,
            package_id="Aspose.Cells",
            output_dir=tmp_path / "generated" / "cells",
            input_strategy="generated_fixture_file",
            input_files=["input.xlsx"],
        )
        project_dir = Path(project["project_dir"])
        # Fixture file must exist in the project directory
        fixture_path = project_dir / "input.xlsx"
        assert fixture_path.exists(), "Generated fixture not placed in project dir"
        assert fixture_path.stat().st_size > 0
        # Verify it's a valid XLSX
        with zipfile.ZipFile(fixture_path) as zf:
            assert 'xl/workbook.xml' in zf.namelist()


# --- Test 7: Project generator writes generated fixture ---

class TestProjectGeneratorWritesGeneratedFixture:
    def test_csproj_includes_fixture_copy_items(self, tmp_path):
        """Csproj must include CopyToOutputDirectory for fixture files."""
        csproj = _generate_csproj("Aspose.Cells", "net8.0", ["input.xlsx"])
        assert "input.xlsx" in csproj
        assert "CopyToOutputDirectory" in csproj
        assert "PreserveNewest" in csproj

    def test_csproj_no_fixtures_no_extra_items(self):
        """Csproj without fixtures should have no extra ItemGroup."""
        csproj = _generate_csproj("Aspose.Cells", "net8.0", [])
        assert "CopyToOutputDirectory" not in csproj


# --- Test 8: Expected output records input dependencies ---

class TestExpectedOutputRecordsInputDependencies:
    def test_expected_output_records_input_dependencies(self, tmp_path):
        example = GeneratedExample(
            scenario_id="cells-dep-test",
            code='class P { static void Main() {} }',
        )
        project = generate_project(
            example,
            package_id="Aspose.Cells",
            output_dir=tmp_path / "gen" / "cells",
            input_strategy="generated_fixture_file",
            input_files=["input.xlsx"],
        )
        expected_output = json.loads((Path(project["project_dir"]) / "expected-output.json").read_text())
        assert "input_dependencies" in expected_output
        assert "input.xlsx" in expected_output["input_dependencies"]


# --- Test 9: Missing input file demotes scenario ---

class TestMissingInputFileDemotesScenario:
    def test_missing_input_file_demotes_scenario(self):
        """Scenarios that fail runtime with FileNotFoundException must be demoted."""
        from plugin_examples.gates.example_gates import (
            evaluate_example_gates,
            build_scenario_feedback,
        )
        from dataclasses import dataclass

        @dataclass
        class _MockDotnetResult:
            operation: str
            success: bool
            exit_code: int = 0
            stdout: str = ""
            stderr: str = ""
            duration_ms: float = 100.0

        @dataclass
        class _MockValidationResult:
            scenario_id: str
            restore: _MockDotnetResult | None = None
            build: _MockDotnetResult | None = None
            run: _MockDotnetResult | None = None
            passed: bool = False
            failure_stage: str | None = None

        @dataclass
        class _MockRuntimeClassification:
            scenario_id: str
            exit_code: int = 1
            classification: str = "blocked_missing_fixture"
            detail: str = ""
            actionable: bool = False
            recommendation: str = ""

        vr = _MockValidationResult(
            scenario_id="cells-fail",
            restore=_MockDotnetResult("restore", True),
            build=_MockDotnetResult("build", True),
            run=_MockDotnetResult("run", False, exit_code=1,
                                  stderr="FileNotFoundException: Could not find file 'input.xlsx'"),
            passed=False,
            failure_stage="run",
        )
        rc = _MockRuntimeClassification("cells-fail")
        projects = [{"scenario_id": "cells-fail", "project_dir": "/gen/cells-fail",
                      "program_path": "/gen/cells-fail/Program.cs"}]

        eg = evaluate_example_gates([vr], projects, runtime_classifications=[rc])
        feedback = build_scenario_feedback(eg)
        assert feedback["demoted_scenarios"] == 1
        assert feedback["updates"][0]["new_status"] == "blocked_missing_fixture"


# --- Test 10: Cells converter scenario has valid input strategy ---

class TestCellsConverterScenarioHasValidInputStrategy:
    def test_cells_converter_scenario_has_valid_input_strategy(self):
        """Every Cells converter scenario must have a valid input strategy."""
        type_info = {
            "full_name": "Aspose.Cells.LowCode.HtmlConverter",
            "name": "HtmlConverter",
            "kind": "class",
            "methods": [
                {
                    "name": "Process",
                    "is_static": True,
                    "is_obsolete": False,
                    "parameters": [
                        {"name": "inputFile", "type": "System.String"},
                        {"name": "outputFile", "type": "System.String"},
                    ],
                }
            ],
        }
        scenario = _build_scenario("cells", type_info, "Aspose.Cells.LowCode", None, ".xlsx")
        assert scenario.input_strategy != "no_valid_input_strategy"
        assert scenario.input_strategy in (
            "existing_fixture", "generated_fixture_file", "programmatic_input", "none"
        )
        assert scenario.status == "ready"

    def test_all_supported_formats_produce_valid_strategy(self):
        """Every format in SUPPORTED_FORMATS must produce a ready scenario."""
        type_info = {
            "full_name": "Aspose.Test.LowCode.Converter",
            "name": "Converter",
            "kind": "class",
            "methods": [
                {
                    "name": "Process",
                    "is_static": True,
                    "is_obsolete": False,
                    "parameters": [
                        {"name": "inputFile", "type": "System.String"},
                        {"name": "outputFile", "type": "System.String"},
                    ],
                }
            ],
        }
        for fmt in SUPPORTED_FORMATS:
            scenario = _build_scenario("test", type_info, "Aspose.Test.LowCode", None, fmt)
            assert scenario.status == "ready", f"Format {fmt} should produce ready scenario"
            assert scenario.input_strategy == "generated_fixture_file"


# --- Evidence writer test ---

class TestFixtureEvidenceWriter:
    def test_write_generated_fixtures_evidence(self, tmp_path):
        fixtures = [
            GeneratedFixture(path="/gen/input.xlsx", format=".xlsx",
                             created_by="fixture_factory",
                             validity_check="file_exists_and_size_1234",
                             size_bytes=1234, ready=True),
        ]
        path = write_generated_fixtures_evidence(fixtures, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["total_generated"] == 1
        assert data["total_ready"] == 1
