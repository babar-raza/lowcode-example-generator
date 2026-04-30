"""Tests for the Options-Aware API Usage Sprint.

Covers: options misuse detection in code validator, prompt constraints for
single-overload usage, runtime failure classifications for options errors,
and scenario planner overload preference.
"""

from __future__ import annotations

import pytest

from plugin_examples.generator.packet_builder import (
    PromptPacket,
    build_packet,
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


# --- Helpers ---

def _make_catalog(type_name: str, methods: list[dict]) -> dict:
    full_name = f"Aspose.Cells.LowCode.{type_name}"
    return {
        "namespaces": [{
            "namespace": "Aspose.Cells.LowCode",
            "types": [{
                "full_name": full_name,
                "name": type_name,
                "kind": "class",
                "methods": methods,
            }],
        }]
    }


def _make_scenario(type_name: str, methods: list[str], **overrides) -> dict:
    full_name = f"Aspose.Cells.LowCode.{type_name}"
    base = {
        "scenario_id": f"cells-{type_name.lower()}",
        "target_type": full_name,
        "target_namespace": "Aspose.Cells.LowCode",
        "target_methods": methods,
        "required_symbols": [full_name] + [f"{full_name}.{m}" for m in methods],
        "input_strategy": "generated_fixture_file",
        "input_files": ["input.xlsx"],
    }
    base.update(overrides)
    return base


# --- Test 1: Prompt forbids null options ---

class TestPromptForbidsNullOptions:
    def test_prompt_forbids_null_lowcode_options(self):
        """Prompt constraints must forbid passing null for LowCodeLoadOptions/LowCodeSaveOptions."""
        scenario = _make_scenario("HtmlConverter", ["Process"])
        catalog = _make_catalog("HtmlConverter", [{
            "name": "Process",
            "is_static": True,
            "is_obsolete": False,
            "parameters": [
                {"name": "templateFile", "type": "System.String"},
                {"name": "resultFile", "type": "System.String"},
            ],
        }])
        packet = build_packet(scenario, catalog)
        constraints_text = " ".join(packet.constraints)
        assert "null" in constraints_text.lower()
        assert "LowCodeLoadOptions" in constraints_text or "LowCodeSaveOptions" in constraints_text

    def test_prompt_requires_single_overload(self):
        """Prompt must instruct LLM to call only ONE overload."""
        scenario = _make_scenario("HtmlConverter", ["Process"])
        catalog = _make_catalog("HtmlConverter", [{
            "name": "Process",
            "is_static": True,
            "is_obsolete": False,
            "parameters": [
                {"name": "templateFile", "type": "System.String"},
                {"name": "resultFile", "type": "System.String"},
            ],
        }])
        packet = build_packet(scenario, catalog)
        constraints_text = " ".join(packet.constraints)
        assert "ONE overload" in constraints_text or "one overload" in constraints_text.lower()


# --- Test 2: Code validator detects null options ---

class TestCodeValidatorDetectsNullOptions:
    def test_detects_null_load_options(self):
        code = 'HtmlConverter.Process((LowCodeLoadOptions)null, saveOpts);'
        issues = _validate_code(code)
        assert any("null" in i.lower() and "LowCodeLoadOptions" in i for i in issues)

    def test_detects_null_save_options(self):
        code = 'HtmlConverter.Process(loadOpts, (LowCodeSaveOptions)null);'
        issues = _validate_code(code)
        assert any("null" in i.lower() and "LowCodeSaveOptions" in i for i in issues)

    def test_passes_simple_overload(self):
        code = 'HtmlConverter.Process(inputPath, outputPath);'
        issues = _validate_code(code)
        assert len(issues) == 0


# --- Test 3: Code validator detects empty options without properties ---

class TestCodeValidatorDetectsEmptyOptions:
    def test_detects_empty_load_options(self):
        code = """var loadOpts = new LowCodeLoadOptions();
var saveOpts = new LowCodeSaveOptions();
saveOpts.OutputFile = "out.html";
HtmlConverter.Process(loadOpts, saveOpts);"""
        issues = _validate_code(code)
        assert any("InputFile" in i for i in issues)

    def test_passes_load_options_with_input_file(self):
        code = """var loadOpts = new LowCodeLoadOptions();
loadOpts.InputFile = inputPath;
var saveOpts = new LowCodeSaveOptions();
saveOpts.OutputFile = outputPath;
HtmlConverter.Process(loadOpts, saveOpts);"""
        issues = _validate_code(code)
        # Should not complain about empty load options
        assert not any("InputFile" in i for i in issues)

    def test_detects_empty_save_options(self):
        code = """var loadOpts = new LowCodeLoadOptions();
loadOpts.InputFile = "input.xlsx";
var saveOpts = new LowCodeSaveOptions();
HtmlConverter.Process(loadOpts, saveOpts);"""
        issues = _validate_code(code)
        assert any("OutputFile" in i for i in issues)


# --- Test 4: Code validator detects multiple Process calls ---

class TestCodeValidatorDetectsMultipleProcessCalls:
    def test_detects_multiple_process_calls(self):
        code = """HtmlConverter.Process(inputPath, outputPath);
HtmlConverter.Process(loadOpts, saveOpts);"""
        issues = _validate_code(code)
        assert any("Process()" in i and "ONE" in i for i in issues)

    def test_passes_single_process_call(self):
        code = 'HtmlConverter.Process(inputPath, outputPath);'
        issues = _validate_code(code)
        assert not any("Process()" in i for i in issues)


# --- Test 5: Runtime failure classifies missing options input ---

class TestRuntimeFailureClassifiesMissingOptionsInput:
    def test_classifies_no_input_specified(self):
        rc = classify_runtime_failure(
            "test-scenario", 1,
            stderr="Unhandled exception. Aspose.Cells.CellsException: No input has been specified for the process.",
        )
        assert rc.classification == "missing_options_input"
        assert rc.actionable is True

    def test_classifies_null_ref_as_actionable(self):
        rc = classify_runtime_failure(
            "test-scenario", 1,
            stderr="Unhandled exception. System.NullReferenceException: Object reference not set to an instance of an object.",
        )
        assert rc.classification == "blocked_runtime_context_required"
        assert rc.actionable is True


# --- Test 6: Runtime failure classifies interactive call (still works) ---

class TestRuntimeClassificationsUnchanged:
    def test_interactive_console_still_classified(self):
        rc = classify_runtime_failure(
            "test-scenario", 1,
            stderr="Cannot read keys when either application does not have a console",
        )
        assert rc.classification == "interactive_console_call"
        assert rc.actionable is True

    def test_wrong_input_format_still_classified(self):
        rc = classify_runtime_failure(
            "test-scenario", 1,
            stderr="Only text based formats such as Csv, Tsv... are allowed",
        )
        assert rc.classification == "wrong_input_format"
        assert rc.actionable is True


# --- Test 7: System prompt forbids null options ---

class TestSystemPromptForbidsNullOptions:
    def test_system_prompt_mentions_null_options(self):
        scenario = _make_scenario("HtmlConverter", ["Process"])
        catalog = _make_catalog("HtmlConverter", [{
            "name": "Process",
            "is_static": True,
            "is_obsolete": False,
            "parameters": [
                {"name": "templateFile", "type": "System.String"},
                {"name": "resultFile", "type": "System.String"},
            ],
        }])
        packet = build_packet(scenario, catalog)
        assert "null" in packet.system_prompt.lower()
        assert "LowCodeLoadOptions" in packet.system_prompt or "ONE overload" in packet.system_prompt

    def test_system_prompt_mentions_single_overload(self):
        scenario = _make_scenario("HtmlConverter", ["Process"])
        catalog = _make_catalog("HtmlConverter", [{
            "name": "Process",
            "is_static": True,
            "is_obsolete": False,
            "parameters": [
                {"name": "templateFile", "type": "System.String"},
                {"name": "resultFile", "type": "System.String"},
            ],
        }])
        packet = build_packet(scenario, catalog)
        assert "ONE overload" in packet.system_prompt or "one overload" in packet.system_prompt.lower()


# --- Test 8: User prompt no longer suggests null ---

class TestUserPromptDoesNotSuggestNull:
    def test_user_prompt_does_not_say_use_null(self):
        scenario = _make_scenario("HtmlConverter", ["Process"])
        catalog = _make_catalog("HtmlConverter", [{
            "name": "Process",
            "is_static": True,
            "is_obsolete": False,
            "parameters": [
                {"name": "templateFile", "type": "System.String"},
                {"name": "resultFile", "type": "System.String"},
            ],
        }])
        packet = build_packet(scenario, catalog)
        # The old prompt said "use null or a mock value" — this must be removed
        assert "use null or a mock value" not in packet.user_prompt


# --- Test 9: SpreadsheetLocker simple overload preferred ---

class TestSpreadsheetLockerOverloadPreference:
    def test_spreadsheet_locker_uses_xlsx_input(self):
        fmt = _infer_input_format("SpreadsheetLocker", ".xlsx")
        assert fmt == ".xlsx"

    def test_spreadsheet_locker_output_is_xlsx(self):
        fmt = _infer_output_format("SpreadsheetLocker")
        assert fmt == ".xlsx"


# --- Test 10: HtmlConverter simple overload preferred ---

class TestHtmlConverterOverloadPreference:
    def test_html_converter_uses_xlsx_input(self):
        fmt = _infer_input_format("HtmlConverter", ".xlsx")
        assert fmt == ".xlsx"

    def test_html_converter_output_is_html(self):
        fmt = _infer_output_format("HtmlConverter")
        assert fmt == ".html"


# --- Test 11: Validate code passes clean single-overload examples ---

class TestValidateCodePassesCleanExamples:
    def test_clean_html_converter_example(self):
        code = """using System;
using System.IO;
using Aspose.Cells.LowCode;

namespace HtmlConverterDemo
{
    class Program
    {
        static void Main()
        {
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
            if (!File.Exists(inputPath))
                throw new FileNotFoundException("Input file not found", inputPath);
            string outputPath = Path.Combine(AppContext.BaseDirectory, "output.html");
            HtmlConverter.Process(inputPath, outputPath);
            if (File.Exists(outputPath))
                Console.WriteLine($"Done. Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
            else
                throw new InvalidOperationException("Output file was not created");
        }
    }
}"""
        issues = _validate_code(code)
        assert len(issues) == 0

    def test_clean_locker_example(self):
        code = """using System;
using System.IO;
using Aspose.Cells.LowCode;

namespace LockerDemo
{
    class Program
    {
        static void Main()
        {
            string inputPath = Path.Combine(AppContext.BaseDirectory, "input.xlsx");
            if (!File.Exists(inputPath))
                throw new FileNotFoundException("Input file not found", inputPath);
            string outputPath = Path.Combine(AppContext.BaseDirectory, "output.xlsx");
            SpreadsheetLocker.Process(inputPath, outputPath, "open-pwd", "write-pwd");
            if (File.Exists(outputPath))
                Console.WriteLine($"Done. Output: {outputPath} ({new FileInfo(outputPath).Length} bytes)");
            else
                throw new InvalidOperationException("Output file was not created");
        }
    }
}"""
        issues = _validate_code(code)
        assert len(issues) == 0


# --- Test 12: Validate code rejects the exact failing patterns from pilot ---

class TestValidateCodeRejectsFailingPilotPatterns:
    def test_rejects_html_converter_pilot_pattern(self):
        """The exact pattern that caused the NullRef in the pilot run."""
        code = """HtmlConverter.Process(inputPath, outputPath);
HtmlConverter.Process((LowCodeLoadOptions)null, (LowCodeSaveOptions)null);"""
        issues = _validate_code(code)
        assert len(issues) >= 2  # null options + multiple Process calls

    def test_rejects_locker_pilot_pattern(self):
        """The exact pattern that caused 'No input specified' in the pilot run."""
        code = """SpreadsheetLocker.Process(inputPath, outputPath, "", "");
var loadOptions = new LowCodeLoadOptions();
var saveOptions = new LowCodeSaveOptions();
SpreadsheetLocker.Process(loadOptions, saveOptions, "", "");"""
        issues = _validate_code(code)
        assert len(issues) >= 2  # empty options + multiple Process calls
