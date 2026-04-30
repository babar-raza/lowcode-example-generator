"""Tests for the LLM Code Quality and Expected-Output Verification Sprint.

Covers: prompt constraints, input format mapping, few-shot patterns,
build/runtime repair classification, semantic output validation,
deterministic fixture content, and discovery sweep.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from plugin_examples.generator.packet_builder import (
    PromptPacket,
    build_packet,
    _build_fixture_instruction,
    _build_fewshot_snippet,
)
from plugin_examples.generator.code_generator import _validate_code
from plugin_examples.scenario_planner.planner import (
    _build_scenario,
    _infer_input_format,
    _infer_output_format,
)
from plugin_examples.scenario_planner.runtime_feedback import (
    classify_runtime_failure,
)
from plugin_examples.fixture_registry.fixture_factory import (
    generate_xlsx,
    generate_csv,
    generate_txt,
    generate_json,
    generate_html,
)
from plugin_examples.verifier_bridge.output_validator import (
    validate_output_file_semantic,
)


# --- Test 1: Prompt forbids Console.ReadKey ---

class TestPromptForbidsConsoleReadKey:
    def test_prompt_forbids_console_readkey(self):
        """Prompt constraints must forbid Console.ReadKey."""
        scenario = {
            "scenario_id": "cells-test",
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
            "namespaces": [{
                "namespace": "Aspose.Cells.LowCode",
                "types": [{
                    "full_name": "Aspose.Cells.LowCode.HtmlConverter",
                    "name": "HtmlConverter",
                    "kind": "class",
                    "methods": [{
                        "name": "Process",
                        "is_static": True,
                        "is_obsolete": False,
                        "parameters": [
                            {"name": "inputFile", "type": "System.String"},
                            {"name": "outputFile", "type": "System.String"},
                        ],
                    }],
                }],
            }]
        }
        packet = build_packet(scenario, catalog)
        constraints_text = " ".join(packet.constraints)
        assert "Console.ReadKey" in constraints_text
        assert "Console.ReadLine" in constraints_text
        assert "headless" in constraints_text.lower() or "CI" in constraints_text


# --- Test 2: Prompt forbids Console.ReadLine ---

class TestPromptForbidsConsoleReadLine:
    def test_prompt_forbids_console_readline(self):
        """Prompt constraints must forbid Console.ReadLine."""
        scenario = {
            "scenario_id": "cells-test",
            "target_type": "Aspose.Cells.LowCode.HtmlConverter",
            "target_namespace": "Aspose.Cells.LowCode",
            "target_methods": ["Process"],
            "required_symbols": ["Aspose.Cells.LowCode.HtmlConverter",
                                 "Aspose.Cells.LowCode.HtmlConverter.Process"],
            "input_strategy": "none",
            "input_files": [],
        }
        catalog = {
            "namespaces": [{
                "namespace": "Aspose.Cells.LowCode",
                "types": [{
                    "full_name": "Aspose.Cells.LowCode.HtmlConverter",
                    "name": "HtmlConverter",
                    "kind": "class",
                    "methods": [{
                        "name": "Process",
                        "is_static": True,
                        "is_obsolete": False,
                        "parameters": [],
                    }],
                }],
            }]
        }
        packet = build_packet(scenario, catalog)
        constraints_text = " ".join(packet.constraints)
        assert "Console.ReadLine" in constraints_text


# --- Test 3: Code validator detects Console.ReadKey ---

class TestCodeValidatorDetectsInteractive:
    def test_validate_code_detects_readkey(self):
        code = 'Console.ReadKey();'
        issues = _validate_code(code)
        assert any("ReadKey" in i for i in issues)

    def test_validate_code_detects_readline(self):
        code = 'Console.ReadLine();'
        issues = _validate_code(code)
        assert any("ReadLine" in i for i in issues)

    def test_validate_code_passes_clean(self):
        code = 'Console.WriteLine("Done.");'
        issues = _validate_code(code)
        assert len(issues) == 0


# --- Test 4: Input format map for TextConverter ---

class TestInputFormatMapTextConverterNotXlsx:
    def test_input_format_map_text_converter_not_xlsx(self):
        """TextConverter must use CSV, not XLSX."""
        fmt = _infer_input_format("TextConverter", ".xlsx")
        assert fmt == ".csv"

    def test_input_format_map_html_converter(self):
        fmt = _infer_input_format("HtmlConverter", ".xlsx")
        assert fmt == ".xlsx"

    def test_input_format_map_unknown_uses_default(self):
        fmt = _infer_input_format("UnknownType", ".docx")
        assert fmt == ".docx"

    def test_text_converter_scenario_uses_csv(self):
        """Full scenario build for TextConverter must use .csv input."""
        type_info = {
            "full_name": "Aspose.Cells.LowCode.TextConverter",
            "name": "TextConverter",
            "kind": "class",
            "methods": [{
                "name": "Process",
                "is_static": True,
                "is_obsolete": False,
                "parameters": [
                    {"name": "inputFile", "type": "System.String"},
                    {"name": "outputFile", "type": "System.String"},
                ],
            }],
        }
        scenario = _build_scenario("cells", type_info, "Aspose.Cells.LowCode", None, ".xlsx")
        assert scenario.required_input_format == ".csv"
        assert scenario.input_files == ["input.csv"]
        assert scenario.status == "ready"


# --- Test 5: Few-shot snippet in LLM packet ---

class TestLlmPacketUsesVerifiedFewshotOnly:
    def test_llm_packet_uses_verified_fewshot_only(self):
        """Packet must include few-shot reference pattern for generated_fixture_file."""
        snippet = _build_fewshot_snippet("generated_fixture_file", ["input.xlsx"])
        assert "AppContext.BaseDirectory" in snippet
        assert "File.Exists" in snippet
        assert "FileNotFoundException" in snippet

    def test_no_fewshot_for_programmatic(self):
        snippet = _build_fewshot_snippet("programmatic_input", [])
        assert snippet == ""


# --- Test 6: Runtime failure classifies interactive console call ---

class TestRuntimeFailureClassifiesInteractiveConsoleCall:
    def test_runtime_failure_classifies_interactive_console_call(self):
        rc = classify_runtime_failure(
            "test-scenario", 1,
            stderr="Cannot read keys when either application does not have a console",
        )
        assert rc.classification == "interactive_console_call"
        assert rc.actionable is True

    def test_runtime_failure_classifies_wrong_input_format(self):
        rc = classify_runtime_failure(
            "test-scenario", 1,
            stderr="Only text based formats such as Csv, Tsv... are allowed",
        )
        assert rc.classification == "wrong_input_format"
        assert rc.actionable is True


# --- Test 7: Build repair reads stdout and stderr ---

class TestBuildRepairReadsStdoutAndStderr:
    def test_build_repair_reads_stdout_and_stderr(self):
        """Verify repair prompt captures both stdout and stderr from compiler."""
        # This is a structural test: the repair prompt in runner.py must reference
        # both build_stdout and build_stderr. We verify by checking the code structure.
        import inspect
        from plugin_examples.runner import _stage_validation
        source = inspect.getsource(_stage_validation)
        assert "build_stdout" in source
        assert "build_stderr" in source


# --- Test 8: Semantic validator checks CSV content ---

class TestSemanticValidatorChecksCsvContent:
    def test_semantic_validator_checks_csv_content(self, tmp_path):
        csv_file = tmp_path / "output.csv"
        csv_file.write_text("Name,Value\nAspose,10\n")
        result = validate_output_file_semantic(
            csv_file,
            {"content_contains": ["Aspose"], "content_not_contains": ["ERROR"]},
        )
        assert result["passed"] is True
        assert any(c["check"].startswith("contains_") for c in result["checks"])


# --- Test 9: Semantic validator checks JSON parse ---

class TestSemanticValidatorChecksJsonParse:
    def test_semantic_validator_checks_json_parse(self, tmp_path):
        json_file = tmp_path / "output.json"
        json_file.write_text('[{"Name": "Aspose"}]')
        result = validate_output_file_semantic(json_file)
        assert result["passed"] is True
        assert any(c["check"] == "json_parse" for c in result["checks"])

    def test_semantic_validator_fails_invalid_json(self, tmp_path):
        json_file = tmp_path / "bad.json"
        json_file.write_text("not json{{{")
        result = validate_output_file_semantic(json_file)
        assert result["passed"] is False


# --- Test 10: Semantic validator checks HTML content ---

class TestSemanticValidatorChecksHtmlContent:
    def test_semantic_validator_checks_html_content(self, tmp_path):
        html_file = tmp_path / "output.html"
        html_file.write_text("<html><body><table><tr><td>Aspose</td></tr></table></body></html>")
        result = validate_output_file_semantic(html_file)
        assert result["passed"] is True
        assert any(c["check"] == "html_has_table" for c in result["checks"])


# --- Test 11: Semantic validator checks PDF header ---

class TestSemanticValidatorChecksPdfHeader:
    def test_semantic_validator_checks_pdf_header(self, tmp_path):
        pdf_file = tmp_path / "output.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n" + b"x" * 200)
        result = validate_output_file_semantic(pdf_file)
        assert result["passed"] is True
        assert any(c["check"] == "pdf_header" and c["passed"] for c in result["checks"])

    def test_semantic_validator_rejects_invalid_pdf(self, tmp_path):
        pdf_file = tmp_path / "bad.pdf"
        pdf_file.write_bytes(b"not a pdf" * 10)
        result = validate_output_file_semantic(pdf_file)
        assert any(c["check"] == "pdf_header" and not c["passed"] for c in result["checks"])


# --- Test 12: Generated fixtures contain known values ---

class TestGeneratedFixtureContainsKnownValues:
    def test_generated_fixture_contains_known_values(self, tmp_path):
        """All generated text fixtures must contain Aspose, LowCode, Fixture."""
        csv_file = tmp_path / "input.csv"
        generate_csv(csv_file)
        content = csv_file.read_text()
        assert "Aspose" in content
        assert "LowCode" in content
        assert "Fixture" in content

    def test_json_fixture_known_values(self, tmp_path):
        json_file = tmp_path / "input.json"
        generate_json(json_file)
        data = json.loads(json_file.read_text())
        names = [r["Name"] for r in data]
        assert "Aspose" in names

    def test_html_fixture_known_values(self, tmp_path):
        html_file = tmp_path / "input.html"
        generate_html(html_file)
        content = html_file.read_text()
        assert "Aspose" in content
        assert "LowCode" in content

    def test_txt_fixture_known_values(self, tmp_path):
        txt_file = tmp_path / "input.txt"
        generate_txt(txt_file)
        content = txt_file.read_text()
        assert "Aspose" in content
        assert "LowCode" in content

    def test_xlsx_fixture_has_data_sheet(self, tmp_path):
        xlsx_file = tmp_path / "input.xlsx"
        generate_xlsx(xlsx_file)
        with zipfile.ZipFile(xlsx_file, "r") as zf:
            wb = zf.read("xl/workbook.xml").decode()
            assert 'name="Data"' in wb


# --- Test 13: Discovery sweep does not generate examples ---

class TestDiscoverLowcodeDoesNotGenerateExamples:
    def test_discover_lowcode_does_not_generate_examples(self):
        """Discovery sweep module must not import generator."""
        import inspect
        from plugin_examples import discovery_sweep
        source = inspect.getsource(discovery_sweep)
        assert "generate_example" not in source
        assert "generate_project" not in source


# --- Test 14: Discovery sweep does not call LLM ---

class TestDiscoverLowcodeDoesNotCallLlm:
    def test_discover_lowcode_does_not_call_llm(self):
        """Discovery sweep module must not import LLM router."""
        import inspect
        from plugin_examples import discovery_sweep
        source = inspect.getsource(discovery_sweep)
        assert "llm_router" not in source.lower()
        assert "LLMRouter" not in source


# --- Test 15: Discovery sweep writes family inventory ---

class TestDiscoverLowcodeWritesFamilyInventory:
    def test_discover_lowcode_writes_family_inventory(self, tmp_path):
        """Discovery sweep must produce all-family-lowcode-discovery.json."""
        from plugin_examples.discovery_sweep import run_discovery_sweep
        # Run with a non-existent family to test the blocked path
        result = run_discovery_sweep(
            families=["nonexistent_test_family"],
            repo_root=tmp_path,
        )
        assert result["total_families"] == 1
        assert result["families"][0]["status"] == "blocked_config_not_found"
        # Evidence file must be written
        evidence_file = tmp_path / "workspace" / "verification" / "latest" / "all-family-lowcode-discovery.json"
        assert evidence_file.exists()


# --- Test 16: Output format inference ---

class TestOutputFormatInference:
    def test_infer_output_text_converter(self):
        assert _infer_output_format("TextConverter") == ".txt"

    def test_infer_output_json_converter(self):
        assert _infer_output_format("JsonConverter") == ".json"

    def test_infer_output_pdf_converter(self):
        assert _infer_output_format("PdfConverter") == ".pdf"

    def test_infer_output_unknown(self):
        assert _infer_output_format("UnknownType") == ".out"
