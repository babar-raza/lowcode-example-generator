"""Unit tests for llm_router and generator modules."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.llm_router.router import (
    LLMProviderError,
    LLMRouter,
    PreflightResult,
    write_preflight_report,
)
from plugin_examples.generator.packet_builder import (
    PromptPacket,
    UnknownSymbolError,
    build_packet,
)
from plugin_examples.generator.code_generator import (
    GeneratedExample,
    generate_example,
)
from plugin_examples.generator.project_generator import generate_project
from plugin_examples.generator.manifest_writer import write_example_index


def _make_catalog() -> dict:
    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": "25.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Cells.LowCode",
                "types": [
                    {
                        "name": "SpreadsheetLocker",
                        "full_name": "Aspose.Cells.LowCode.SpreadsheetLocker",
                        "kind": "class", "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "void",
                             "is_static": True, "is_obsolete": False,
                             "parameters": [
                                 {"name": "templateFile", "type": "System.String", "is_optional": False},
                                 {"name": "resultFile", "type": "System.String", "is_optional": False},
                                 {"name": "password", "type": "System.String", "is_optional": False},
                             ]},
                        ],
                        "properties": [], "constructors": [],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


def _make_html_converter_catalog() -> dict:
    """Catalog with HtmlConverter having two overloads."""
    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": "25.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Cells.LowCode",
                "types": [
                    {
                        "name": "HtmlConverter",
                        "full_name": "Aspose.Cells.LowCode.HtmlConverter",
                        "kind": "class", "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "void",
                             "is_static": True, "is_obsolete": False,
                             "parameters": [
                                 {"name": "templateFile", "type": "System.String", "is_optional": False},
                                 {"name": "resultFile", "type": "System.String", "is_optional": False},
                             ]},
                            {"name": "Process", "return_type": "void",
                             "is_static": True, "is_obsolete": False,
                             "parameters": [
                                 {"name": "loadOptions", "type": "Aspose.Cells.LowCode.LowCodeLoadOptions", "is_optional": False},
                                 {"name": "saveOptions", "type": "Aspose.Cells.LowCode.LowCodeSaveOptions", "is_optional": False},
                             ]},
                        ],
                        "properties": [], "constructors": [],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


def _make_abstract_catalog() -> dict:
    """Catalog with an abstract class type."""
    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": "25.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Cells.LowCode",
                "types": [
                    {
                        "name": "AbstractLowCodeLoadOptionsProvider",
                        "full_name": "Aspose.Cells.LowCode.AbstractLowCodeLoadOptionsProvider",
                        "kind": "abstract_class", "is_obsolete": False,
                        "methods": [
                            {"name": "MoveNext", "return_type": "bool",
                             "is_static": False, "is_obsolete": False, "parameters": []},
                        ],
                        "properties": [], "constructors": [],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


def _make_scenario() -> dict:
    return {
        "scenario_id": "cells-spreadsheet-locker",
        "title": "Use SpreadsheetLocker",
        "target_type": "Aspose.Cells.LowCode.SpreadsheetLocker",
        "target_namespace": "Aspose.Cells.LowCode",
        "target_methods": ["Process"],
        "required_symbols": [
            "Aspose.Cells.LowCode.SpreadsheetLocker",
            "Aspose.Cells.LowCode.SpreadsheetLocker.Process",
        ],
        "required_fixtures": [],
        "output_plan": "Console output",
        "validation_plan": "Build succeeds",
        "status": "ready",
    }


# --- Tests: LLM Router ---


class TestLLMRouter:
    def test_preflight_no_providers(self):
        router = LLMRouter(provider_order=[])
        results = router.run_preflight()
        assert len(results) == 0
        assert router.selected_provider is None

    def test_get_provider_raises_when_none(self):
        router = LLMRouter(provider_order=[])
        with pytest.raises(LLMProviderError):
            router.get_provider()

    def test_preflight_connection_refused(self):
        router = LLMRouter(provider_order=["ollama"])
        with patch("plugin_examples.llm_router.router.requests.get") as mock_get:
            import requests as req
            mock_get.side_effect = req.exceptions.ConnectionError("refused")
            results = router.run_preflight()
        assert len(results) == 1
        assert not results[0].passed
        assert "refused" in results[0].error

    def test_preflight_success_selects_provider(self):
        router = LLMRouter(provider_order=["ollama"])
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": []}
        with patch("plugin_examples.llm_router.router.requests.get", return_value=mock_resp):
            results = router.run_preflight()
        assert results[0].passed
        assert router.selected_provider == "ollama"

    def test_write_preflight_report(self, tmp_path):
        results = [PreflightResult(provider="ollama", endpoint_reachable=True,
                                    model_available=True, json_response=True,
                                    structured_response_parseable=True,
                                    timeout_within_limit=True)]
        path = write_preflight_report(results, "ollama",
                                       tmp_path / "workspace" / "verification")
        assert path.exists()
        assert "llm-preflight" in path.name


# --- Tests: Packet Builder ---


class TestPacketBuilder:
    def test_valid_symbols_pass(self):
        packet = build_packet(_make_scenario(), _make_catalog())
        assert packet.scenario_id == "cells-spreadsheet-locker"
        assert len(packet.approved_symbols) > 0

    def test_unknown_symbols_raise(self):
        scenario = _make_scenario()
        scenario["required_symbols"].append("Aspose.Cells.LowCode.FakeType")
        with pytest.raises(UnknownSymbolError, match="FakeType"):
            build_packet(scenario, _make_catalog())

    def test_constraints_populated(self):
        packet = build_packet(_make_scenario(), _make_catalog())
        assert len(packet.constraints) > 0
        assert any("TODO" in c for c in packet.constraints)

    def test_prompts_populated(self):
        packet = build_packet(_make_scenario(), _make_catalog())
        assert len(packet.system_prompt) > 0
        assert len(packet.user_prompt) > 0


# --- Tests: Code Generator ---


class TestCodeGenerator:
    def test_template_generation_no_llm(self):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        assert example.status == "generated"
        assert "SpreadsheetLocker" in example.code
        assert example.scenario_id == "cells-spreadsheet-locker"

    def test_template_has_no_todo(self):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        assert "TODO" not in example.code

    def test_template_has_no_absolute_paths(self):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        assert "C:\\" not in example.code

    def test_llm_failure_returns_failed(self):
        packet = build_packet(_make_scenario(), _make_catalog())

        def failing_llm(prompt, system):
            raise Exception("LLM unavailable")

        example = generate_example(packet, llm_generate=failing_llm)
        assert example.status == "failed"

    def test_claimed_symbols_populated(self):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        assert len(example.claimed_symbols) > 0

    def test_template_static_method_has_args(self):
        """Static Process must be called with proper arguments, not Process()."""
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        assert "Process()" not in example.code
        assert 'Process("input.xlsx"' in example.code

    def test_template_includes_input_creation(self):
        """Template must create input files before calling API."""
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        assert "Workbook()" in example.code
        assert 'Save("input.xlsx")' in example.code

    def test_template_output_extension_html(self):
        """HtmlConverter must produce output.html."""
        scenario = {
            "scenario_id": "cells-html-converter",
            "title": "Use HtmlConverter",
            "target_type": "Aspose.Cells.LowCode.HtmlConverter",
            "target_namespace": "Aspose.Cells.LowCode",
            "target_methods": ["Process"],
            "required_symbols": [
                "Aspose.Cells.LowCode.HtmlConverter",
                "Aspose.Cells.LowCode.HtmlConverter.Process",
            ],
            "required_fixtures": [],
            "output_plan": "",
            "status": "ready",
        }
        packet = build_packet(scenario, _make_html_converter_catalog())
        example = generate_example(packet)
        assert '"output.html"' in example.code

    def test_type_details_in_packet(self):
        """build_packet must populate type_details from catalog."""
        packet = build_packet(_make_scenario(), _make_catalog())
        assert packet.type_details != {}
        assert packet.type_details["name"] == "SpreadsheetLocker"
        assert len(packet.type_details["methods"]) > 0

    def test_select_simplest_overload_prefers_string_string(self):
        """Given (string,string) and (Options,Options), select (string,string)."""
        from plugin_examples.generator.code_generator import _select_simplest_overload
        methods = _make_html_converter_catalog()["namespaces"][0]["types"][0]["methods"]
        result = _select_simplest_overload(methods, "Process")
        assert result is not None
        params = result["parameters"]
        assert len(params) == 2
        assert all(p["type"] == "System.String" for p in params)

    def test_unsupported_overload_produces_comment(self):
        """If only overload has non-string params, template should have a skip comment."""
        catalog = {
            "assembly_name": "Test",
            "assembly_version": "1.0",
            "namespaces": [{
                "namespace": "Test.LowCode",
                "types": [{
                    "name": "SplitterOnly",
                    "full_name": "Test.LowCode.SplitterOnly",
                    "kind": "class", "is_obsolete": False,
                    "methods": [{
                        "name": "Process", "return_type": "void",
                        "is_static": True, "is_obsolete": False,
                        "parameters": [
                            {"name": "input", "type": "System.String", "is_optional": False},
                            {"name": "opts", "type": "Test.LowCode.SplitOptions", "is_optional": False},
                        ],
                    }],
                    "properties": [], "constructors": [],
                }],
            }],
            "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
        }
        scenario = {
            "scenario_id": "test-splitter",
            "title": "Use SplitterOnly",
            "target_type": "Test.LowCode.SplitterOnly",
            "target_namespace": "Test.LowCode",
            "target_methods": ["Process"],
            "required_symbols": [
                "Test.LowCode.SplitterOnly",
                "Test.LowCode.SplitterOnly.Process",
            ],
            "required_fixtures": [],
            "output_plan": "",
            "status": "ready",
        }
        packet = build_packet(scenario, catalog)
        example = generate_example(packet)
        # Should NOT have Process() call, should have a skip comment
        assert "Process(" not in example.code or "unsupported" in example.code.lower() or "skipped" in example.code.lower()

    def test_infer_output_extension(self):
        from plugin_examples.generator.code_generator import _infer_output_extension
        assert _infer_output_extension("HtmlConverter") == ".html"
        assert _infer_output_extension("PdfConverter") == ".pdf"
        assert _infer_output_extension("JsonConverter") == ".json"
        assert _infer_output_extension("TextConverter") == ".txt"
        assert _infer_output_extension("ImageConverter") == ".png"
        assert _infer_output_extension("SpreadsheetConverter") == ".xlsx"


# --- Tests: Project Generator ---


class TestProjectGenerator:
    def test_generates_project_files(self, tmp_path):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        result = generate_project(
            example, package_id="Aspose.Cells",
            output_dir=tmp_path / "workspace" / "runs" / "test" / "generated",
        )
        assert Path(result["csproj_path"]).exists()
        assert Path(result["program_path"]).exists()

    def test_csproj_has_package_reference(self, tmp_path):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        result = generate_project(
            example, package_id="Aspose.Cells", package_version="26.4.0",
            output_dir=tmp_path / "generated",
        )
        csproj = Path(result["csproj_path"]).read_text()
        assert "Aspose.Cells" in csproj
        # Version is now managed by Directory.Packages.props, not inline
        assert 'Version=' not in csproj

    def test_generates_readme_and_manifest(self, tmp_path):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        result = generate_project(
            example, package_id="Aspose.Cells",
            output_dir=tmp_path / "workspace" / "runs" / "test" / "generated",
        )
        project_dir = Path(result["project_dir"])
        assert (project_dir / "README.md").exists()
        assert (project_dir / "example.manifest.json").exists()
        assert (project_dir / "expected-output.json").exists()

    def test_run_level_build_files(self, tmp_path):
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        generate_project(
            example, package_id="Aspose.Cells", package_version="26.4.0",
            output_dir=tmp_path / "generated",
        )
        run_dir = tmp_path
        assert (run_dir / "Directory.Packages.props").exists()
        assert (run_dir / "Directory.Build.props").exists()
        assert (run_dir / "global.json").exists()
        props = (run_dir / "Directory.Packages.props").read_text()
        assert "26.4.0" in props


# --- Tests: Manifest Writer ---


class TestManifestWriter:
    def test_write_example_index(self, tmp_path):
        examples = [
            {"scenario_id": "test-1", "status": "generated"},
            {"scenario_id": "test-2", "status": "failed"},
        ]
        path = write_example_index(examples, tmp_path / "workspace" / "manifests")
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["total_examples"] == 2
        assert data["generated"] == 1
        assert data["failed"] == 1

    def test_paths_use_workspace(self, tmp_path):
        path = write_example_index([], tmp_path / "workspace" / "manifests")
        assert "workspace" in str(path)


# --- Tests: Multi-Family Template Hints ---


def _make_words_catalog() -> dict:
    """Catalog simulating Aspose.Words.LowCode."""
    return {
        "assembly_name": "Aspose.Words",
        "assembly_version": "25.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Words.LowCode",
                "types": [
                    {
                        "name": "Converter",
                        "full_name": "Aspose.Words.LowCode.Converter",
                        "kind": "class", "is_obsolete": False,
                        "methods": [
                            {"name": "Convert", "return_type": "void",
                             "is_static": True, "is_obsolete": False,
                             "parameters": [
                                 {"name": "inputFile", "type": "System.String", "is_optional": False},
                                 {"name": "outputFile", "type": "System.String", "is_optional": False},
                             ]},
                        ],
                        "properties": [], "constructors": [],
                    },
                    {
                        "name": "Merger",
                        "full_name": "Aspose.Words.LowCode.Merger",
                        "kind": "class", "is_obsolete": False,
                        "methods": [
                            {"name": "Merge", "return_type": "void",
                             "is_static": True, "is_obsolete": False,
                             "parameters": [
                                 {"name": "outputFile", "type": "System.String", "is_optional": False},
                                 {"name": "inputFiles", "type": "System.String[]", "is_optional": False},
                             ]},
                        ],
                        "properties": [], "constructors": [],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


_WORDS_HINTS = {
    "default_input_extension": ".docx",
    "default_input_filename": "input.docx",
    "array_input_filenames": ["input1.docx", "input2.docx"],
    "input_creation_lines": [
        'var doc = new Document();',
        'var builder = new DocumentBuilder(doc);',
        'builder.Writeln("Hello World");',
        'doc.Save("input.docx");',
    ],
    "merger_input_creation_lines": [
        'var doc1 = new Document();',
        'new DocumentBuilder(doc1).Writeln("Document 1");',
        'doc1.Save("input1.docx");',
        'var doc2 = new Document();',
        'new DocumentBuilder(doc2).Writeln("Document 2");',
        'doc2.Save("input2.docx");',
    ],
    "additional_usings": ["Aspose.Words"],
    "default_output_extension": ".docx",
    "default_fixture_extension": ".docx",
}


class TestMultiFamilyHints:
    def test_words_template_uses_docx_input(self):
        """Words-like generation must use .docx, not .xlsx."""
        scenario = {
            "scenario_id": "words-converter",
            "title": "Use Converter",
            "target_type": "Aspose.Words.LowCode.Converter",
            "target_namespace": "Aspose.Words.LowCode",
            "target_methods": ["Convert"],
            "required_symbols": [
                "Aspose.Words.LowCode.Converter",
                "Aspose.Words.LowCode.Converter.Convert",
            ],
            "required_fixtures": [],
            "output_plan": "",
            "status": "ready",
        }
        packet = build_packet(scenario, _make_words_catalog(), template_hints=_WORDS_HINTS)
        example = generate_example(packet)
        assert '"input.docx"' in example.code
        assert '"output.docx"' in example.code or '"output.' in example.code

    def test_words_template_no_workbook_leakage(self):
        """Words-like generation must not contain Workbook or .xlsx."""
        scenario = {
            "scenario_id": "words-converter",
            "title": "Use Converter",
            "target_type": "Aspose.Words.LowCode.Converter",
            "target_namespace": "Aspose.Words.LowCode",
            "target_methods": ["Convert"],
            "required_symbols": [
                "Aspose.Words.LowCode.Converter",
                "Aspose.Words.LowCode.Converter.Convert",
            ],
            "required_fixtures": [],
            "output_plan": "",
            "status": "ready",
        }
        packet = build_packet(scenario, _make_words_catalog(), template_hints=_WORDS_HINTS)
        example = generate_example(packet)
        assert "Workbook" not in example.code
        assert ".xlsx" not in example.code

    def test_words_template_has_document_creation(self):
        """Words hints should produce Document-based input creation."""
        scenario = {
            "scenario_id": "words-converter",
            "title": "Use Converter",
            "target_type": "Aspose.Words.LowCode.Converter",
            "target_namespace": "Aspose.Words.LowCode",
            "target_methods": ["Convert"],
            "required_symbols": [
                "Aspose.Words.LowCode.Converter",
                "Aspose.Words.LowCode.Converter.Convert",
            ],
            "required_fixtures": [],
            "output_plan": "",
            "status": "ready",
        }
        packet = build_packet(scenario, _make_words_catalog(), template_hints=_WORDS_HINTS)
        example = generate_example(packet)
        assert "Document()" in example.code
        assert "DocumentBuilder" in example.code

    def test_words_merger_uses_docx_arrays(self):
        """Words Merger must use .docx array inputs."""
        scenario = {
            "scenario_id": "words-merger",
            "title": "Use Merger",
            "target_type": "Aspose.Words.LowCode.Merger",
            "target_namespace": "Aspose.Words.LowCode",
            "target_methods": ["Merge"],
            "required_symbols": [
                "Aspose.Words.LowCode.Merger",
                "Aspose.Words.LowCode.Merger.Merge",
            ],
            "required_fixtures": [],
            "output_plan": "",
            "status": "ready",
        }
        packet = build_packet(scenario, _make_words_catalog(), template_hints=_WORDS_HINTS)
        example = generate_example(packet)
        assert '"input1.docx"' in example.code
        assert '"input2.docx"' in example.code

    def test_additional_usings_respected(self):
        """additional_usings from hints must appear in generated code."""
        scenario = {
            "scenario_id": "words-converter",
            "title": "Use Converter",
            "target_type": "Aspose.Words.LowCode.Converter",
            "target_namespace": "Aspose.Words.LowCode",
            "target_methods": ["Convert"],
            "required_symbols": [
                "Aspose.Words.LowCode.Converter",
                "Aspose.Words.LowCode.Converter.Convert",
            ],
            "required_fixtures": [],
            "output_plan": "",
            "status": "ready",
        }
        packet = build_packet(scenario, _make_words_catalog(), template_hints=_WORDS_HINTS)
        example = generate_example(packet)
        assert "using Aspose.Words;" in example.code

    def test_infer_output_extension_docx(self):
        """Generic inference for Word/Docx types."""
        from plugin_examples.generator.code_generator import _infer_output_extension
        assert _infer_output_extension("DocxConverter") == ".docx"
        assert _infer_output_extension("WordConverter") == ".docx"

    def test_infer_output_extension_with_hints_fallback(self):
        """Unknown type name falls back to hints default_output_extension."""
        from plugin_examples.generator.code_generator import _infer_output_extension
        hints = {"default_output_extension": ".docx"}
        assert _infer_output_extension("UnknownProcessor", hints) == ".docx"

    def test_infer_output_extension_pptx(self):
        from plugin_examples.generator.code_generator import _infer_output_extension
        assert _infer_output_extension("PresentationConverter") == ".pptx"

    def test_infer_output_extension_eml(self):
        from plugin_examples.generator.code_generator import _infer_output_extension
        assert _infer_output_extension("EmailConverter") == ".eml"

    def test_no_hints_uses_cells_fallback(self):
        """When no hints provided, backward-compat Cells fallback applies."""
        packet = build_packet(_make_scenario(), _make_catalog())
        example = generate_example(packet)
        assert "Workbook()" in example.code
        assert "input.xlsx" in example.code
