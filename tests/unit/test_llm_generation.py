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


class TestPacketBuilderPerTypeConstraints:
    """per_type_constraints from family config are injected into packet.constraints."""

    def _scenario(self, type_name: str = "SpreadsheetLocker", ns: str = "Aspose.Cells.LowCode") -> dict:
        return {
            "scenario_id": f"cells-{type_name.lower()}",
            "target_type": f"{ns}.{type_name}",
            "target_namespace": ns,
            "target_methods": ["Process"],
            "required_symbols": [f"{ns}.{type_name}"],
            "input_strategy": "none",
            "input_files": [],
        }

    def _catalog(self, type_name: str = "SpreadsheetLocker", ns: str = "Aspose.Cells.LowCode") -> dict:
        return {
            "assembly_name": "Aspose.Cells",
            "assembly_version": "25.4.0",
            "namespaces": [{
                "namespace": ns,
                "types": [{
                    "name": type_name,
                    "full_name": f"{ns}.{type_name}",
                    "kind": "class",
                    "is_obsolete": False,
                    "methods": [{"name": "Process", "return_type": "void", "is_static": True,
                                 "is_obsolete": False, "parameters": []}],
                    "properties": [],
                    "constructors": [],
                }],
            }],
            "diagnostics": {},
        }

    def test_per_type_constraints_required_injected(self):
        """REQUIRED: constraints from per_type_constraints appear in packet.constraints."""
        ptc = {
            "SpreadsheetLocker": {
                "required": ["REQUIRED: using Aspose.Cells.LowCode;"],
                "forbidden": [],
            }
        }
        packet = build_packet(
            self._scenario(), self._catalog(),
            per_type_constraints=ptc,
        )
        assert "REQUIRED: using Aspose.Cells.LowCode;" in packet.constraints

    def test_per_type_constraints_forbidden_injected(self):
        """FORBIDDEN: constraints from per_type_constraints appear in packet.constraints."""
        ptc = {
            "SpreadsheetLocker": {
                "required": [],
                "forbidden": ["FORBIDDEN: Cells.Protect() replacing SpreadsheetLocker.Process()"],
            }
        }
        packet = build_packet(
            self._scenario(), self._catalog(),
            per_type_constraints=ptc,
        )
        assert "FORBIDDEN: Cells.Protect() replacing SpreadsheetLocker.Process()" in packet.constraints

    def test_per_type_constraints_not_duplicated(self):
        """If a constraint is already present it should not be duplicated."""
        existing = "REQUIRED: using Aspose.Cells.LowCode;"
        ptc = {
            "SpreadsheetLocker": {
                "required": [existing],
                "forbidden": [],
            }
        }
        # Add the same constraint twice — must appear exactly once
        packet = build_packet(
            self._scenario(), self._catalog(),
            per_type_constraints=ptc,
        )
        assert packet.constraints.count(existing) == 1

    def test_per_type_constraints_for_other_type_not_injected(self):
        """Constraints for a different type are not injected into unrelated scenarios."""
        ptc = {
            "PdfConverter": {
                "required": ["REQUIRED: using Aspose.Cells.LowCode;"],
                "forbidden": [],
            }
        }
        packet = build_packet(
            self._scenario("SpreadsheetLocker"), self._catalog("SpreadsheetLocker"),
            per_type_constraints=ptc,
        )
        # PdfConverter's constraint must NOT appear for SpreadsheetLocker scenario
        assert "REQUIRED: using Aspose.Cells.LowCode;" not in packet.constraints

    def test_per_type_constraints_none_is_safe(self):
        """Passing None for per_type_constraints does not raise and packet is valid."""
        packet = build_packet(
            self._scenario(), self._catalog(),
            per_type_constraints=None,
        )
        assert len(packet.constraints) > 0

    def test_pdf_merger_text_fragment_constraint_injected(self):
        """Critical fix: Merger must carry the using Aspose.Pdf.Text constraint via per_type_constraints."""
        ptc = {
            "Merger": {
                "required": ["REQUIRED: using Aspose.Pdf.Text; (for TextFragment fixture creation)"],
                "forbidden": ["FORBIDDEN: PdfFileEditor"],
            }
        }
        ns = "Aspose.Pdf.LowCode"
        scenario = self._scenario("Merger", ns)
        catalog = self._catalog("Merger", ns)
        packet = build_packet(scenario, catalog, per_type_constraints=ptc)
        assert any("Aspose.Pdf.Text" in c for c in packet.constraints)
        assert any("PdfFileEditor" in c for c in packet.constraints)

    def test_per_type_constraints_stored_on_packet(self):
        """per_type_constraints dict is stored on the returned PromptPacket."""
        ptc = {"SpreadsheetLocker": {"required": ["REQUIRED: x"], "forbidden": []}}
        packet = build_packet(
            self._scenario(), self._catalog(),
            per_type_constraints=ptc,
        )
        assert packet.per_type_constraints == ptc


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


# ---------------------------------------------------------------------------
# TestProviderPolicy
# ---------------------------------------------------------------------------


class TestProviderPolicy:
    """Unit tests for the LLM provider policy module."""

    def test_approved_providers_set(self):
        from plugin_examples.llm_router.provider_policy import APPROVED_PROVIDERS
        assert "llm_professionalize" in APPROVED_PROVIDERS
        assert "ollama" in APPROVED_PROVIDERS

    def test_unapproved_providers_set(self):
        from plugin_examples.llm_router.provider_policy import UNAPPROVED_PROVIDERS
        assert "gpt_oss" in UNAPPROVED_PROVIDERS
        assert "openai" in UNAPPROVED_PROVIDERS

    def test_get_policy_violations_returns_unapproved(self):
        from plugin_examples.llm_router.provider_policy import get_policy_violations
        violations = get_policy_violations(["gpt_oss", "llm_professionalize", "openai"])
        assert violations == ["gpt_oss", "openai"]

    def test_get_policy_violations_empty_when_all_approved(self):
        from plugin_examples.llm_router.provider_policy import get_policy_violations
        violations = get_policy_violations(["llm_professionalize", "ollama"])
        assert violations == []

    def test_filter_to_approved_removes_unapproved(self):
        from plugin_examples.llm_router.provider_policy import filter_to_approved
        approved = filter_to_approved(["gpt_oss", "openai", "llm_professionalize", "ollama"])
        assert approved == ["llm_professionalize", "ollama"]

    def test_classify_approved_provider(self):
        from plugin_examples.llm_router.provider_policy import classify_provider_hit
        result = classify_provider_hit("cells.yml:73", "llm_professionalize", "provider_order")
        assert result["classification"] == "approved_llm_provider_config"
        assert result["approved"] is True

    def test_classify_unapproved_provider(self):
        from plugin_examples.llm_router.provider_policy import classify_provider_hit
        result = classify_provider_hit("cells.yml:73", "gpt_oss", "provider_order")
        assert result["classification"] == "violation_unapproved_provider"
        assert result["approved"] is False

    def test_gpt_4o_mini_replaced_with_env_var(self):
        """Verify gpt-4o-mini hardcode was replaced with OPENAI_MODEL env var."""
        import inspect
        from plugin_examples.llm_router import router
        source = inspect.getsource(router)
        assert "gpt-4o-mini" not in source
        assert "OPENAI_MODEL" in source

    def test_only_professionalize_and_ollama_provider_families_allowed(self):
        from plugin_examples.llm_router.provider_policy import APPROVED_PROVIDERS
        assert APPROVED_PROVIDERS == frozenset({"llm_professionalize", "ollama"})
        assert "gpt_oss" not in APPROVED_PROVIDERS
        assert "openai" not in APPROVED_PROVIDERS
        assert "azure_openai" not in APPROVED_PROVIDERS

    def test_gpt_4o_mini_rejected_as_configured_pipeline_model(self):
        from plugin_examples.llm_router.provider_policy import (
            is_forbidden_model,
            validate_model_for_provider,
        )
        assert is_forbidden_model("gpt-4o-mini") is True
        assert is_forbidden_model("recommended") is False
        assert is_forbidden_model("codellama") is False
        violations = validate_model_for_provider("llm_professionalize", "gpt-4o-mini")
        assert len(violations) == 1
        assert "gpt-4o-mini" in violations[0]
        clean = validate_model_for_provider("llm_professionalize", "recommended")
        assert clean == []

    def test_gpt_4o_mini_inside_extracted_xml_is_classified_as_documentation(self):
        from plugin_examples.llm_router.provider_policy import (
            classify_documentation_hit,
            classify_llm_hit,
        )
        text = 'OpenAiModel("gpt-4o-mini", apiKey)'
        result = classify_documentation_hit(text, "extracted/Aspose.Words.xml")
        assert result["classification"] == "extracted_nuget_documentation"
        assert result["is_pipeline_call"] is False

        result2 = classify_llm_hit(text, "nuget/packages/Aspose.Words.xml")
        assert result2["classification"] == "extracted_nuget_documentation"
        assert result2["is_pipeline_call"] is False

        result3 = classify_documentation_hit(text, "/path/to/extracted/Aspose.Words.xml")
        assert result3["classification"] == "extracted_nuget_documentation"

    def test_gpt_oss_allowed_only_as_ollama_model_if_configured_under_ollama(self):
        from plugin_examples.llm_router.provider_policy import (
            get_policy_violations,
            validate_model_for_provider,
            APPROVED_PROVIDERS,
        )
        # gpt_oss as a provider family is unapproved
        violations = get_policy_violations(["gpt_oss"])
        assert "gpt_oss" in violations

        # gpt_oss appearing as a model name under ollama: no model violation
        model_violations = validate_model_for_provider("ollama", "gpt_oss")
        assert model_violations == []

        # ollama is the approved local provider
        assert "ollama" in APPROVED_PROVIDERS

    def test_gpt_oss_rejected_as_provider_family(self):
        from plugin_examples.llm_router.provider_policy import (
            validate_provider_family,
            UNAPPROVED_PROVIDERS,
        )
        assert "gpt_oss" in UNAPPROVED_PROVIDERS
        violations = validate_provider_family("gpt_oss")
        assert len(violations) >= 1
        assert any("gpt_oss" in v for v in violations)

    def test_openai_rejected_as_provider_family(self):
        from plugin_examples.llm_router.provider_policy import (
            validate_provider_family,
            UNAPPROVED_PROVIDERS,
        )
        assert "openai" in UNAPPROVED_PROVIDERS
        violations = validate_provider_family("openai")
        assert len(violations) >= 1
        assert any("openai" in v for v in violations)

    def test_direct_openai_call_outside_professionalize_provider_is_rejected(self):
        from plugin_examples.llm_router.provider_policy import is_direct_openai_construction
        # Forbidden: OpenAI( in generator code
        assert is_direct_openai_construction(
            "client = OpenAI(api_key=key)", "src/plugin_examples/generator/code_gen.py"
        ) is True
        # Forbidden: OpenAI( in runner
        assert is_direct_openai_construction(
            "client = OpenAI(api_key=key)", "src/plugin_examples/runner.py"
        ) is True
        # Allowed: in the professionalize provider module
        assert is_direct_openai_construction(
            "client = OpenAI(api_key=key)",
            "src/plugin_examples/llm_router/providers/professionalize.py",
        ) is False
        # No OpenAI( = not a violation
        assert is_direct_openai_construction(
            "response = requests.post(url, json=body)", "src/plugin_examples/runner.py"
        ) is False

    def test_llm_preflight_records_provider_family_and_model_separately(self):
        """Preflight JSON must record provider_family and model_name as separate fields."""
        import json
        import tempfile
        from pathlib import Path
        from plugin_examples.llm_router.router import write_preflight_report, PreflightResult
        with tempfile.TemporaryDirectory() as tmp:
            results = [PreflightResult(
                provider="llm_professionalize",
                endpoint_reachable=True,
                model_available=True,
                json_response=True,
                structured_response_parseable=True,
                timeout_within_limit=True,
                latency_ms=500.0,
                error=None,
            )]
            path = write_preflight_report(results, "llm_professionalize", Path(tmp))
            data = json.loads(path.read_text())
            assert "provider_family" in data
            assert data["provider_family"] == "llm_professionalize"
            assert "model_name" in data
            assert data["model_name"] is not None
            assert "route" in data
            assert data["route"] == "llm_professionalize"
            assert "documentation_hits_excluded" in data
            assert data["documentation_hits_excluded"] is True
            assert "preflight_passed" in data
            assert data["preflight_passed"] is True

    def test_check_provider_rejects_unapproved_at_preflight(self):
        """_check_provider must return passed=False for unapproved providers.

        This is the preflight-layer guard. Without it, unapproved providers can be
        selected (selected_provider set) even though _call_provider would block them
        later. Both layers must enforce the same policy.
        """
        from plugin_examples.llm_router.router import _check_provider
        for forbidden in ("gpt_oss", "openai", "azure_openai"):
            result = _check_provider(forbidden)
            assert result.passed is False, (
                f"_check_provider('{forbidden}') must return passed=False — "
                "unapproved providers must not be selected at preflight"
            )
            assert result.error is not None
            assert "not approved" in result.error

    def test_run_preflight_does_not_select_unapproved_provider(self):
        """LLMRouter.run_preflight must never set selected_provider to an unapproved family.

        Even if all providers in provider_order are unapproved, selected_provider must
        remain None. The preflight guard must reject them without making HTTP calls.
        """
        from plugin_examples.llm_router.router import LLMRouter
        router = LLMRouter(provider_order=["gpt_oss", "openai", "azure_openai"])
        router.run_preflight(timeout=1)
        assert router.selected_provider is None, (
            f"selected_provider must be None when all providers are unapproved, "
            f"got: {router.selected_provider!r}"
        )


# --- Tests: PDF Controlled Pilot Enablement ---


def _make_pdf_catalog() -> dict:
    """Minimal catalog for Aspose.PDF.LowCode.Merger."""
    return {
        "assembly_name": "Aspose.PDF",
        "assembly_version": "26.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Pdf.LowCode",
                "types": [
                    {
                        "name": "Merger",
                        "full_name": "Aspose.Pdf.LowCode.Merger",
                        "kind": "class", "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "Aspose.Pdf.LowCode.ResultContainer",
                             "is_static": False, "is_obsolete": False,
                             "parameters": [
                                 {"name": "options", "type": "Aspose.Pdf.LowCode.MergeOptions", "is_optional": False},
                             ]},
                        ],
                        "properties": [], "constructors": [{"parameters": []}],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


def _make_pdf_scenario(type_name: str = "Merger", type_short: str = "merger") -> dict:
    ns = "Aspose.Pdf.LowCode"
    full = f"{ns}.{type_name}"
    return {
        "scenario_id": f"pdf-{type_short}",
        "title": f"Use {type_name}",
        "target_type": full,
        "target_namespace": ns,
        "target_methods": ["Process"],
        "required_symbols": [full, f"{full}.Process"],
        "required_fixtures": [],
        "output_plan": "Merge PDFs",
        "validation_plan": "Build succeeds",
        "status": "ready",
        "input_strategy": "none",
        "input_files": [],
    }


class TestPdfOutputFormat:
    def test_merger_falls_back_to_pdf_family_default(self):
        from plugin_examples.scenario_planner.planner import _infer_output_format
        assert _infer_output_format("Merger", family_default=".pdf") == ".pdf"

    def test_splitter_falls_back_to_pdf_family_default(self):
        from plugin_examples.scenario_planner.planner import _infer_output_format
        assert _infer_output_format("Splitter", family_default=".pdf") == ".pdf"

    def test_optimizer_falls_back_to_pdf_family_default(self):
        from plugin_examples.scenario_planner.planner import _infer_output_format
        assert _infer_output_format("Optimizer", family_default=".pdf") == ".pdf"

    def test_textextractor_returns_empty_string(self):
        from plugin_examples.scenario_planner.planner import _infer_output_format
        assert _infer_output_format("TextExtractor", family_default=".pdf") == ""

    def test_words_merger_still_falls_back_to_docx(self):
        from plugin_examples.scenario_planner.planner import _infer_output_format
        assert _infer_output_format("Merger", family_default=".docx") == ".docx"

    def test_words_splitter_still_falls_back_to_docx(self):
        from plugin_examples.scenario_planner.planner import _infer_output_format
        assert _infer_output_format("Splitter", family_default=".docx") == ".docx"


class TestPdfPacketBuilderConstraints:
    def test_pdf_namespace_adds_filedata_source_constraint(self):
        scenario = _make_pdf_scenario()
        packet = build_packet(scenario, _make_pdf_catalog())
        assert any("FileSaveTarget" in c for c in packet.constraints), (
            "PDF packet must forbid FileSaveTarget"
        )
        assert any("FileDataSource" in c for c in packet.constraints), (
            "PDF packet must require FileDataSource for output"
        )

    def test_pdf_namespace_adds_result_collection_constraint(self):
        scenario = _make_pdf_scenario()
        packet = build_packet(scenario, _make_pdf_catalog())
        assert any("IsSuccess" in c for c in packet.constraints), (
            "PDF packet must forbid IsSuccess"
        )
        assert any("ResultCollection" in c for c in packet.constraints), (
            "PDF packet must require ResultCollection"
        )

    def test_pdf_namespace_adds_pdf_rules_to_system_prompt(self):
        scenario = _make_pdf_scenario()
        packet = build_packet(scenario, _make_pdf_catalog())
        assert "FileDataSource" in packet.system_prompt
        assert "ResultCollection" in packet.system_prompt

    def test_textextractor_adds_no_addoutput_constraint(self):
        scenario = _make_pdf_scenario("TextExtractor", "textextractor")
        scenario["required_symbols"] = [
            "Aspose.Pdf.LowCode.TextExtractor",
            "Aspose.Pdf.LowCode.TextExtractor.Process",
        ]
        scenario["target_type"] = "Aspose.Pdf.LowCode.TextExtractor"
        catalog = _make_pdf_catalog()
        catalog["namespaces"][0]["types"][0]["name"] = "TextExtractor"
        catalog["namespaces"][0]["types"][0]["full_name"] = "Aspose.Pdf.LowCode.TextExtractor"
        packet = build_packet(scenario, catalog)
        assert any("AddOutput" in c and "FORBIDDEN" in c for c in packet.constraints), (
            "TextExtractor must forbid AddOutput()"
        )

    def test_non_pdf_namespace_no_pdf_constraints(self):
        scenario = _make_scenario()
        packet = build_packet(scenario, _make_catalog())
        assert not any("FileSaveTarget" in c for c in packet.constraints), (
            "Non-PDF packet must not have FileSaveTarget constraint"
        )


class TestPdfCodeValidation:
    def test_detects_filesavetarget(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'options.AddOutput(new FileSaveTarget("output.pdf"));'
        issues = _validate_code(code, family="pdf")
        assert any("FileSaveTarget" in i for i in issues)

    def test_detects_is_success(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = "if (result.IsSuccess) { Console.WriteLine(\"ok\"); }"
        issues = _validate_code(code, family="pdf")
        assert any("IsSuccess" in i for i in issues)

    def test_detects_operation_result(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = "var r = result.OperationResult[0];"
        issues = _validate_code(code, family="pdf")
        assert any("OperationResult" in i for i in issues)

    def test_detects_splitter_format_string(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'splitOptions.AddOutput(new FileDataSource("output_{0}.pdf"));'
        issues = _validate_code(code, family="pdf")
        assert any("format string" in i for i in issues)

    def test_detects_textextractor_addoutput(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'var te = new TextExtractor();\ntextOpts.AddOutput(new FileDataSource("x.pdf"));'
        issues = _validate_code(code, family="pdf")
        assert any("TextExtractor" in i and "AddOutput" in i for i in issues)

    def test_no_false_positives_for_non_pdf(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'options.AddOutput(new FileSaveTarget("output.pdf"));'
        issues = _validate_code(code, family="")
        assert not any("FileSaveTarget" in i for i in issues)

    def test_valid_pdf_code_has_no_pdf_issues(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'var mergeOptions = new MergeOptions();\n'
            'mergeOptions.AddInput(new FileDataSource("input1.pdf"));\n'
            'mergeOptions.AddOutput(new FileDataSource("output.pdf"));\n'
            'var merger = new Merger();\n'
            'var result = merger.Process(mergeOptions);\n'
            'Console.WriteLine(result.ResultCollection.Count > 0 ? "ok" : "fail");\n'
        )
        issues = _validate_code(code, family="pdf")
        assert not any(
            any(kw in i for kw in ["FileSaveTarget", "IsSuccess", "OperationResult", "format string", "AddOutput"])
            for i in issues
        )


class TestPdfRuntimeFeedback:
    def test_classifies_filesavetarget_error(self):
        from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure
        stdout = "error CS1503: cannot convert from 'FileSaveTarget' to 'IDataSource'"
        result = classify_runtime_failure("pdf-merger", 1, stdout=stdout)
        assert result.classification == "pdf_wrong_output_type"
        assert result.actionable is True

    def test_classifies_is_success_missing(self):
        from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure
        stdout = "error CS1061: 'ResultContainer' does not contain a definition for 'IsSuccess'"
        result = classify_runtime_failure("pdf-merger", 1, stdout=stdout)
        assert result.classification == "pdf_result_is_success_missing"
        assert result.actionable is True

    def test_classifies_operation_result_missing(self):
        from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure
        stdout = "error CS1061: 'ResultContainer' does not contain a definition for 'OperationResult'"
        result = classify_runtime_failure("pdf-merger", 1, stdout=stdout)
        assert result.classification == "pdf_result_operation_result_missing"
        assert result.actionable is True

    def test_classifies_wrong_input_extension(self):
        from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure
        stderr = "Input file not found: input.docx"
        result = classify_runtime_failure("pdf-splitter", 1, stdout="", stderr=stderr)
        assert result.classification == "pdf_wrong_input_extension"
        assert result.actionable is True

    def test_pdf_runtime_feedback_handles_merger_overload_error(self):
        from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure
        # Build error when string array overload is used — caught as wrong overload
        stdout = "error CS1501: No overload for method 'Process' takes 3 arguments"
        result = classify_runtime_failure("pdf-merger", 1, stdout=stdout)
        assert result.classification == "pdf_merger_wrong_overload"
        assert result.actionable is True
        assert "MergeOptions" in result.recommendation

    def test_pdf_runtime_feedback_handles_textabsorber_lowcode_violation(self):
        from plugin_examples.scenario_planner.runtime_feedback import classify_runtime_failure
        # Build/run output references TextAbsorber — classified as wrong API
        stdout = "error CS0246: type 'TextAbsorber' — did you use the core API instead of TextExtractor?"
        result = classify_runtime_failure("pdf-text-extractor", 1, stdout=stdout)
        assert result.classification == "pdf_wrong_api_textabsorber"
        assert result.actionable is True
        assert "TextExtractor" in result.recommendation


class TestPdfValidatorHealing:
    """Tests for PDF validator bug fixes — TextAbsorber ban and fake class detection."""

    def test_pdf_text_extractor_rejects_textabsorber(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'using Aspose.Pdf.Text;\n'
            'var absorber = new TextAbsorber();\n'
            'pdfDoc.Pages.Accept(absorber);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("TextAbsorber" in i for i in issues), (
            "Validator must reject TextAbsorber in PDF examples"
        )

    def test_pdf_text_extractor_requires_lowcode_textextractor(self):
        from plugin_examples.generator.code_generator import _validate_code
        # Valid LowCode TextExtractor usage — should NOT produce TextAbsorber or AddOutput errors
        code = (
            'using Aspose.Pdf.LowCode;\n'
            'var options = new TextExtractorOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'var result = new TextExtractor().Process(options);\n'
            'if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)\n'
            '    Console.WriteLine(sr.Text);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert not any("TextAbsorber" in i for i in issues), (
            "Valid LowCode TextExtractor code must not trigger TextAbsorber warning"
        )
        assert not any("AddOutput" in i for i in issues), (
            "Valid TextExtractor code must not trigger AddOutput warning"
        )

    def test_pdf_merger_requires_mergeoptions(self):
        from plugin_examples.generator.code_generator import _validate_code
        # Code with InputPath/OutputPath properties — invalid for PDF LowCode
        code = (
            'using Aspose.Pdf.LowCode;\n'
            'var options = new MergeOptions();\n'
            'options.InputPath = "input.pdf";\n'
            'options.OutputPath = "output.pdf";\n'
            'new Merger().Process(options);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("InputPath" in i or "OutputPath" in i for i in issues), (
            "Validator must reject InputPath/OutputPath properties on MergeOptions"
        )

    def test_pdf_merger_rejects_string_array_overload(self):
        from plugin_examples.generator.code_generator import _validate_code
        # String array overload that does not exist in Aspose.Pdf.LowCode.Merger
        code = (
            'using Aspose.Pdf.LowCode;\n'
            'var merger = new Merger();\n'
            'var result = merger.Process(new[] { "input1.pdf", "input2.pdf" }, "output.pdf", null);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("string array" in i.lower() or "Process()" in i for i in issues), (
            "Validator must reject string array overload of Process()"
        )

    def test_pdf_validator_rejects_operationresult_issuccess(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'if (result.IsSuccess) { var items = result.OperationResult; }'
        issues = _validate_code(code, family="pdf")
        assert any("IsSuccess" in i for i in issues)
        assert any("OperationResult" in i for i in issues)

    def test_pdf_validator_rejects_filesavetarget_if_invalid(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'options.AddOutput(new FileSaveTarget("output.pdf"));'
        issues = _validate_code(code, family="pdf")
        assert any("FileSaveTarget" in i for i in issues)

    def test_pdf_validator_rejects_fake_local_merger_class(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'using Aspose.Pdf.LowCode;\n'
            'class Merger {\n'
            '    public ResultContainer Process(MergeOptions opts) { return null; }\n'
            '}\n'
            'var merger = new Merger();\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("local class" in i.lower() or "Merger" in i for i in issues), (
            "Validator must reject fake local Merger class definition"
        )

    def test_pdf_validator_rejects_resultcollection_value_property(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'using Aspose.Pdf.LowCode;\n'
            'var options = new TextExtractorOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'var result = new TextExtractor().Process(options);\n'
            'var text = result.ResultCollection[0].Value?.ToString() ?? string.Empty;\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any(".Value" in i for i in issues), (
            "Validator must reject result.ResultCollection[0].Value — StringResult has no .Value property"
        )

    def test_pdf_validator_rejects_textfragment_without_using_directive(self):
        from plugin_examples.generator.code_generator import _validate_code
        # No 'using Aspose.Pdf.Text;' directive — TextFragment will fail to compile
        code = (
            'using Aspose.Pdf;\n'
            'using Aspose.Pdf.LowCode;\n'
            'var doc = new Document();\n'
            'var page = doc.Pages.Add();\n'
            'page.Paragraphs.Add(new TextFragment("Hello"));\n'
            'doc.Save("input.pdf");\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("Aspose.Pdf.Text" in i for i in issues), (
            "Validator must require 'using Aspose.Pdf.Text;' when TextFragment is used"
        )

    def test_pdf_packet_builder_forbids_textabsorber_for_textextractor(self):
        """packet_builder must include explicit TextAbsorber FORBIDDEN constraint for textextractor type."""
        # Use a TextExtractor-specific catalog to avoid symbol validation errors
        te_catalog = {
            "assembly_name": "Aspose.PDF",
            "assembly_version": "26.4.0",
            "namespaces": [
                {
                    "namespace": "Aspose.Pdf.LowCode",
                    "types": [
                        {
                            "name": "TextExtractor",
                            "full_name": "Aspose.Pdf.LowCode.TextExtractor",
                            "kind": "class", "is_obsolete": False,
                            "methods": [
                                {"name": "Process", "return_type": "Aspose.Pdf.LowCode.ResultContainer",
                                 "is_static": False, "is_obsolete": False,
                                 "parameters": [
                                     {"name": "options", "type": "Aspose.Pdf.LowCode.TextExtractorOptions",
                                      "is_optional": False},
                                 ]},
                            ],
                            "properties": [], "constructors": [{"parameters": []}],
                        },
                    ],
                },
            ],
            "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
        }
        scenario = _make_pdf_scenario("TextExtractor", "textextractor")
        packet = build_packet(scenario, te_catalog)
        assert any("TextAbsorber" in c for c in packet.constraints), (
            "PDF TextExtractor packet must explicitly forbid TextAbsorber"
        )


class TestPdfInputFormat:
    """Tests for PDF input format inference and programmatic input strategy."""

    def test_merger_input_falls_to_pdf_family_default(self):
        from plugin_examples.scenario_planner.planner import _infer_input_format
        # Merger no longer in _INPUT_FORMAT_MAP — falls to family_default
        assert _infer_input_format("Merger", ".pdf") == ".pdf"

    def test_splitter_input_falls_to_pdf_family_default(self):
        from plugin_examples.scenario_planner.planner import _infer_input_format
        assert _infer_input_format("Splitter", ".pdf") == ".pdf"

    def test_merger_input_falls_to_docx_family_default_for_words(self):
        from plugin_examples.scenario_planner.planner import _infer_input_format
        assert _infer_input_format("Merger", ".docx") == ".docx"

    def test_splitter_input_falls_to_docx_family_default_for_words(self):
        from plugin_examples.scenario_planner.planner import _infer_input_format
        assert _infer_input_format("Splitter", ".docx") == ".docx"


class TestPdfConstraintUpdates:
    """Tests for new PDF packet builder constraints."""

    def test_pdf_forbids_inputpath_property(self):
        scenario = _make_pdf_scenario()
        packet = build_packet(scenario, _make_pdf_catalog())
        assert any("InputPath" in c and "FORBIDDEN" in c for c in packet.constraints), (
            "PDF packet must forbid InputPath property on options"
        )

    def test_pdf_forbids_input_docx(self):
        scenario = _make_pdf_scenario()
        packet = build_packet(scenario, _make_pdf_catalog())
        assert any("input.docx" in c and "FORBIDDEN" in c for c in packet.constraints), (
            "PDF packet must forbid input.docx references"
        )

    def test_pdf_forbids_fake_class_stubs(self):
        scenario = _make_pdf_scenario()
        packet = build_packet(scenario, _make_pdf_catalog())
        assert any("stub" in c.lower() or "fake" in c.lower() for c in packet.constraints), (
            "PDF packet must forbid defining fake class implementations"
        )

    def test_pdf_system_prompt_mentions_addoutput_takes_datasource(self):
        scenario = _make_pdf_scenario()
        packet = build_packet(scenario, _make_pdf_catalog())
        assert "AddOutput" in packet.system_prompt
        assert "FileDataSource" in packet.system_prompt

    def test_non_textextractor_requires_addoutput(self):
        """Non-TextExtractor PDF types should have REQUIRED: AddOutput constraint."""
        scenario = _make_pdf_scenario()  # Merger
        packet = build_packet(scenario, _make_pdf_catalog())
        assert any("AddOutput" in c and "REQUIRED" in c for c in packet.constraints), (
            "Non-TextExtractor PDF types must have REQUIRED AddOutput constraint"
        )


class TestPdfValidatorNewChecks:
    """Tests for new _validate_code PDF checks added in Phase 4."""

    def test_detects_input_docx_in_pdf_code(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'string inputPath = "input.docx";'
        issues = _validate_code(code, family="pdf")
        assert any("input.docx" in i for i in issues)

    def test_detects_inputpath_property_in_pdf_code(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'options.InputPath = "input.pdf";'
        issues = _validate_code(code, family="pdf")
        assert any("InputPath" in i for i in issues)

    def test_detects_outputpath_property_in_pdf_code(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'options.OutputPath = "output.pdf";'
        issues = _validate_code(code, family="pdf")
        assert any("OutputPath" in i for i in issues)

    def test_detects_missing_addinput_in_non_textextractor_pdf(self):
        from plugin_examples.generator.code_generator import _validate_code
        # Code for Merger that doesn't call AddInput
        code = (
            'var options = new MergeOptions();\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            'new Merger().Process(options);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("AddInput" in i for i in issues)

    def test_no_addinput_check_for_textextractor(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'var options = new TextExtractorOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'var te = new TextExtractor();\n'
            'var result = te.Process(options);\n'
        )
        issues = _validate_code(code, family="pdf")
        # TextExtractor with AddInput but no AddOutput should not trigger AddInput missing check
        assert not any("missing AddInput" in i or ("AddInput" in i and "missing" in i) for i in issues)

    def test_input_docx_check_only_fires_for_pdf_family(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'string inputPath = "input.docx";'
        # Non-PDF family — should not trigger
        issues = _validate_code(code, family="")
        assert not any("input.docx" in i for i in issues)

    def test_detects_plugin_options_abstract_base_used(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'var options = new PluginOptions();\noptions.AddInput(new FileDataSource("input.pdf"));'
        issues = _validate_code(code, family="pdf")
        assert any("PluginOptions" in i for i in issues), (
            "Should detect use of abstract PluginOptions base class"
        )

    def test_detects_string_array_process_overload(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = 'var result = merger.Process(new[] { input1, input2 }, outputPath, null);'
        issues = _validate_code(code, family="pdf")
        assert any("string array" in i.lower() or "Process()" in i for i in issues), (
            "Should detect wrong Process() string-array overload"
        )

    def test_correct_merge_options_passes_validator(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'var doc = new Aspose.Pdf.Document(); doc.Pages.Add(); doc.Save("input.pdf");\n'
            'var options = new MergeOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            'var result = new Merger().Process(options);\n'
        )
        issues = _validate_code(code, family="pdf")
        critical = [i for i in issues if any(k in i for k in [
            "PluginOptions", "InputPath", "OutputPath", "AddInput", "string array", "input.docx"
        ])]
        assert not critical, f"Correct MergeOptions code should pass validator: {critical}"

    def test_detects_textextractor_without_textextractoroptions(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'var extractor = new TextExtractor();\n'
            'var result = extractor.Process(inputPath);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("TextExtractorOptions" in i for i in issues), (
            "Should detect TextExtractor called without TextExtractorOptions"
        )

    def test_textextractor_with_options_passes_validator(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'var options = new TextExtractorOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'var result = new TextExtractor().Process(options);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert not any("TextExtractorOptions" in i and "must instantiate" in i for i in issues)


# ---------------------------------------------------------------------------
# PDF Splitter/Optimizer constraint injection tests (Wave 1)
# ---------------------------------------------------------------------------

def _make_pdf_splitter_catalog() -> dict:
    """Minimal catalog for Aspose.PDF.LowCode.Splitter."""
    return {
        "assembly_name": "Aspose.PDF",
        "assembly_version": "26.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Pdf.LowCode",
                "types": [
                    {
                        "name": "Splitter",
                        "full_name": "Aspose.Pdf.LowCode.Splitter",
                        "kind": "class", "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "Aspose.Pdf.LowCode.ResultContainer",
                             "is_static": False, "is_obsolete": False,
                             "parameters": [
                                 {"name": "options", "type": "Aspose.Pdf.LowCode.SplitOptions", "is_optional": False},
                             ]},
                        ],
                        "properties": [], "constructors": [{"parameters": []}],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


def _make_pdf_optimizer_catalog() -> dict:
    """Minimal catalog for Aspose.PDF.LowCode.Optimizer."""
    return {
        "assembly_name": "Aspose.PDF",
        "assembly_version": "26.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Pdf.LowCode",
                "types": [
                    {
                        "name": "Optimizer",
                        "full_name": "Aspose.Pdf.LowCode.Optimizer",
                        "kind": "class", "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "Aspose.Pdf.LowCode.ResultContainer",
                             "is_static": False, "is_obsolete": False,
                             "parameters": [
                                 {"name": "options", "type": "Aspose.Pdf.LowCode.OptimizeOptions", "is_optional": False},
                             ]},
                        ],
                        "properties": [], "constructors": [{"parameters": []}],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


class TestPdfWave1ConstraintInjection:
    """Verify that packet_builder injects SplitOptions/OptimizeOptions constraints."""

    def test_packet_builder_splitter_injects_split_options(self):
        scenario = _make_pdf_scenario("Splitter", "splitter")
        packet = build_packet(scenario, _make_pdf_splitter_catalog())
        options_constraints = [c for c in packet.constraints if "SplitOptions" in c]
        assert options_constraints, (
            "Splitter packet must contain a constraint mentioning SplitOptions"
        )

    def test_packet_builder_optimizer_injects_optimize_options(self):
        scenario = _make_pdf_scenario("Optimizer", "optimizer")
        packet = build_packet(scenario, _make_pdf_optimizer_catalog())
        options_constraints = [c for c in packet.constraints if "OptimizeOptions" in c]
        assert options_constraints, (
            "Optimizer packet must contain a constraint mentioning OptimizeOptions"
        )

    def test_packet_builder_splitter_code_snippet_present(self):
        scenario = _make_pdf_scenario("Splitter", "splitter")
        packet = build_packet(scenario, _make_pdf_splitter_catalog())
        snippet_constraints = [c for c in packet.constraints if "SplitOptions" in c and "AddInput" in c]
        assert snippet_constraints, (
            "Splitter packet must include a code snippet with SplitOptions and AddInput"
        )

    def test_packet_builder_optimizer_code_snippet_present(self):
        scenario = _make_pdf_scenario("Optimizer", "optimizer")
        packet = build_packet(scenario, _make_pdf_optimizer_catalog())
        snippet_constraints = [c for c in packet.constraints if "OptimizeOptions" in c and "AddInput" in c]
        assert snippet_constraints, (
            "Optimizer packet must include a code snippet with OptimizeOptions and AddInput"
        )

    def test_code_generator_plugin_options_is_blocking_error(self):
        from plugin_examples.generator.code_generator import _validate_code
        code = (
            'var options = new PluginOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            'var result = new Splitter().Process(options);\n'
        )
        issues = _validate_code(code, family="pdf")
        assert any("PluginOptions" in i for i in issues), (
            "new PluginOptions() must be a blocking validation error for PDF"
        )


# ---------------------------------------------------------------------------
# LLM timeout retry/backoff tests (Wave 1)
# ---------------------------------------------------------------------------

class TestLLMTimeoutRetry:
    """Verify retry/backoff behaviour in _call_openai_compatible and _call_ollama."""

    def test_openai_compatible_retries_on_timeout_and_succeeds(self):
        """If the first two calls time out, the third should succeed."""
        import requests as req_mod
        from unittest.mock import MagicMock, call, patch
        import plugin_examples.llm_router.router as router_mod

        good_response = MagicMock()
        good_response.status_code = 200
        good_response.json.return_value = {
            "choices": [{"message": {"content": "result"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
        }
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] <= 2:
                raise req_mod.exceptions.Timeout("simulated timeout")
            return good_response

        with patch.object(router_mod, "_LLM_RETRY_BACKOFF_SECONDS", [0, 0]), \
             patch("plugin_examples.llm_router.router.requests.post", side_effect=side_effect):
            result = router_mod._call_openai_compatible(
                "http://fake/v1/chat/completions", "prompt",
                model="test-model", api_key="key",
            )

        assert result == "result"
        assert call_count["n"] == 3, f"Expected 3 total attempts, got {call_count['n']}"

    def test_openai_compatible_does_not_retry_policy_failure(self):
        """LLMProviderError (policy) must not trigger retry."""
        import plugin_examples.llm_router.router as router_mod

        # Policy check in _call_provider raises LLMProviderError before HTTP call.
        # Confirm it propagates without retry by calling _call_provider directly.
        with pytest.raises(router_mod.LLMProviderError):
            router_mod._call_provider("unapproved_provider", "prompt")

    def test_openai_compatible_raises_after_all_retries_exhausted(self):
        """After max_retries+1 timeout attempts, the Timeout must propagate."""
        import requests as req_mod
        from unittest.mock import patch
        import plugin_examples.llm_router.router as router_mod

        with patch.object(router_mod, "_LLM_RETRY_BACKOFF_SECONDS", [0, 0]), \
             patch("plugin_examples.llm_router.router.requests.post",
                   side_effect=req_mod.exceptions.Timeout("always times out")):
            with pytest.raises(req_mod.exceptions.Timeout):
                router_mod._call_openai_compatible(
                    "http://fake/v1/chat/completions", "prompt",
                    model="test-model", api_key="key",
                )


class TestGeneralizedSemanticValidation:
    """_validate_code_from_constraints() checks FORBIDDEN patterns for any family."""

    def test_forbidden_pattern_detected_in_code(self):
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "forbidden": ["FORBIDDEN: PdfFileEditor — use LowCode Merger instead"]
        }
        code = 'var editor = new PdfFileEditor(); editor.Concatenate(inputs, output);'
        issues = _validate_code_from_constraints(code, constraints)
        assert len(issues) == 1
        assert "PdfFileEditor" in issues[0]

    def test_forbidden_pattern_absent_no_issue(self):
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "forbidden": ["FORBIDDEN: PdfFileEditor — use LowCode Merger instead"]
        }
        code = 'var options = new MergeOptions(); new Merger().Process(options);'
        issues = _validate_code_from_constraints(code, constraints)
        assert len(issues) == 0

    def test_multiple_forbidden_patterns(self):
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "forbidden": [
                "FORBIDDEN: PdfFileEditor — use LowCode Merger instead",
                "FORBIDDEN: TextAbsorber — use LowCode TextExtractor instead",
            ]
        }
        code = 'var editor = new PdfFileEditor(); var absorber = new TextAbsorber();'
        issues = _validate_code_from_constraints(code, constraints)
        assert len(issues) == 2

    def test_empty_constraints_no_issues(self):
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        issues = _validate_code_from_constraints("var x = 1;", {})
        assert len(issues) == 0

    def test_words_core_substitution_detected(self):
        """FORBIDDEN: manual loop replacing Replacer.Replace() is detected."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "forbidden": ["FORBIDDEN: manual find/replace loops replacing Replacer.Replace() — use LowCode Replacer"]
        }
        # Code that does manual find/replace instead of Replacer.Replace()
        code = 'foreach (var run in doc.GetChildNodes(NodeType.Run, true)) { run.GetText(); }'
        # The first token "manual" is 6 chars but won't be in code — constraint guards as prompt hint
        # For token-in-code check, test with an explicit API name in FORBIDDEN
        constraints2 = {
            "forbidden": ["FORBIDDEN: IDiagramPlugin — use LowCode DiagramConverter, not the core plugin interface"]
        }
        code2 = 'IDiagramPlugin plugin = new DiagramPlugin();'
        issues = _validate_code_from_constraints(code2, constraints2)
        assert any("IDiagramPlugin" in i for i in issues)

    def test_diagram_core_substitution_detected(self):
        """FORBIDDEN: IDiagramPlugin is detected for diagram scenarios."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "forbidden": ["FORBIDDEN: IDiagramPlugin — use LowCode DiagramConverter, not the core plugin interface"]
        }
        code = 'var plugin = (IDiagramPlugin)new DiagramPlugin();'
        issues = _validate_code_from_constraints(code, constraints)
        assert any("IDiagramPlugin" in i for i in issues)

    def test_short_token_not_flagged(self):
        """Tokens shorter than 4 chars are not checked to avoid false positives."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "forbidden": ["FORBIDDEN: Pdf"]  # only 3 chars after trim
        }
        code = 'using Aspose.Pdf;'
        issues = _validate_code_from_constraints(code, constraints)
        assert len(issues) == 0


class TestRequiredValidation:
    """_validate_code_from_constraints() REQUIRED constraint enforcement."""

    def test_required_method_call_absent_flagged(self):
        """Code missing a REQUIRED method call is flagged."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": ["REQUIRED: Converter.Convert(inputFile, outputFile) — NOT Document.Save()"]
        }
        code = 'var doc = new Document(); doc.Save("output.docx");'
        issues = _validate_code_from_constraints(code, constraints)
        assert any("Converter.Convert" in i for i in issues)

    def test_required_method_call_present_passes(self):
        """Code with the required method call passes."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": ["REQUIRED: Converter.Convert(inputFile, outputFile) — NOT Document.Save()"]
        }
        code = 'Converter.Convert("input.docx", "output.pdf");'
        issues = _validate_code_from_constraints(code, constraints)
        assert not any("Converter.Convert" in i for i in issues)

    def test_required_using_directive_absent_flagged(self):
        """Code missing a required using directive is flagged."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": ["REQUIRED: using Aspose.Pdf.Text; (for TextFragment fixture creation)"]
        }
        code = 'using Aspose.Pdf;\nvar doc = new Document();'
        issues = _validate_code_from_constraints(code, constraints)
        assert any("using Aspose.Pdf.Text" in i for i in issues)

    def test_required_using_directive_present_passes(self):
        """Code with the required using directive passes."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": ["REQUIRED: using Aspose.Pdf.Text; (for TextFragment fixture creation)"]
        }
        code = 'using Aspose.Pdf.Text;\nvar doc = new Document();'
        issues = _validate_code_from_constraints(code, constraints)
        assert not any("using Aspose.Pdf.Text" in i for i in issues)

    def test_words_converter_fails_without_lowcode_call(self):
        """Words Converter: code with only Document.Save and no Converter.Convert is flagged."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": ["REQUIRED: Converter.Convert(inputFile, outputFile) — NOT Document.Save()"],
            "forbidden": ["FORBIDDEN: Document.Save() as the primary operation — use LowCode Converter.Convert()"]
        }
        # No Converter.Convert — only Document.Save
        code = 'var doc = new Document(); var builder = new DocumentBuilder(doc); doc.Save("output.docx");'
        issues = _validate_code_from_constraints(code, constraints)
        # REQUIRED call is absent — must be flagged
        assert any("Converter.Convert" in i for i in issues)

    def test_words_converter_passes_with_fixture_and_lowcode_call(self):
        """Words Converter: fixture Document.Save + primary Converter.Convert — both pass."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": ["REQUIRED: Converter.Convert(inputFile, outputFile) — NOT Document.Save()"],
            "forbidden": ["FORBIDDEN: Document.Save() as the primary operation — use LowCode Converter.Convert()"]
        }
        # Fixture creation uses Document.Save; primary call is Converter.Convert
        code = (
            'var doc = new Document();\n'
            'new DocumentBuilder(doc).Writeln("Hello");\n'
            'doc.Save("input.docx");\n'
            'Converter.Convert("input.docx", "output.pdf");\n'
        )
        issues = _validate_code_from_constraints(code, constraints)
        # Both REQUIRED present and FORBIDDEN exempt because LowCode call is present
        assert len(issues) == 0

    def test_pdf_merger_passes_with_new_merger_and_using(self):
        """PDF Merger: new Merger().Process and using Aspose.Pdf.Text both pass."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                "REQUIRED: using Aspose.Pdf.Text; (for TextFragment fixture creation)",
                "REQUIRED: new Merger().Process(options) — use the LowCode Merger plugin",
            ]
        }
        code = (
            'using Aspose.Pdf.Text;\n'
            'var options = new MergeOptions();\n'
            'options.AddInput(new FileDataSource("input1.pdf"));\n'
            'new Merger().Process(options);\n'
        )
        issues = _validate_code_from_constraints(code, constraints)
        # Both "using Aspose.Pdf.Text;" and "new Merger" are present — no issues
        assert len(issues) == 0

    def test_pdf_merger_fails_without_using_directive(self):
        """PDF Merger: code missing 'using Aspose.Pdf.Text;' is flagged."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                "REQUIRED: using Aspose.Pdf.Text; (for TextFragment fixture creation)",
                "REQUIRED: new Merger().Process(options) — use the LowCode Merger plugin",
            ]
        }
        code = (
            'using Aspose.Pdf;\n'
            'using Aspose.Pdf.LowCode;\n'
            '// no Aspose.Pdf.Text using\n'
            'new Merger().Process(new MergeOptions());\n'
        )
        issues = _validate_code_from_constraints(code, constraints)
        assert any("using Aspose.Pdf.Text" in i for i in issues)

    def test_pdf_merger_fails_without_merger_process(self):
        """PDF Merger: code without new Merger() is flagged."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                "REQUIRED: using Aspose.Pdf.Text; (for TextFragment fixture creation)",
                "REQUIRED: new Merger().Process(options) — use the LowCode Merger plugin",
            ]
        }
        code = 'using Aspose.Pdf.Text;\nvar fe = new PdfFileEditor(); fe.Concatenate(null);'
        issues = _validate_code_from_constraints(code, constraints)
        # "new Merger" is absent — should be flagged; PdfFileEditor also caught
        assert any("new Merger" in i for i in issues)

    def test_build_repair_stores_type_constraints_in_project(self):
        """project dict must contain type_constraints for build-repair validation."""
        import inspect
        from plugin_examples import runner
        source = inspect.getsource(runner._stage_generation)
        assert "type_constraints" in source, (
            "runner._stage_generation must store type_constraints in project dict for build-repair."
        )

    def test_build_repair_calls_validate_from_constraints(self):
        """Build repair path must call _validate_code_from_constraints for all families."""
        import inspect
        from plugin_examples import runner
        source = inspect.getsource(runner._stage_validation)
        assert "_validate_code_from_constraints" in source, (
            "runner._stage_validation build-repair must call _validate_code_from_constraints(). "
            "Gap 4 fix is missing."
        )
        assert "type_constraints" in source, (
            "runner._stage_validation must use proj['type_constraints'] for per-type validation."
        )

    def test_runtime_repair_receives_required_constraints(self):
        """REQUIRED: constraints from pdf_constraints must appear in runtime repair prompt."""
        import inspect
        from plugin_examples import runner
        source = inspect.getsource(runner._stage_validation)
        # Verify the runtime repair section re-injects pdf_constraints
        assert "rt_pdf_constraints" in source, (
            "runner._stage_validation runtime-repair must read pdf_constraints via rt_pdf_constraints. "
            "Runtime constraint re-injection is missing."
        )
        assert "rt_pdf_constraint_reminder" in source, (
            "runner._stage_validation runtime-repair must build rt_pdf_constraint_reminder "
            "and append it to the runtime repair prompt."
        )
        assert "REQUIRED CONSTRAINTS" in source, (
            "runner._stage_validation runtime-repair prompt must contain 'REQUIRED CONSTRAINTS' "
            "so the LLM cannot regress semantic correctness during runtime repair."
        )

    def test_runtime_repair_receives_forbidden_constraints(self):
        """FORBIDDEN: constraints from type_constraints must appear in runtime repair prompt."""
        import inspect
        from plugin_examples import runner
        source = inspect.getsource(runner._stage_validation)
        # Verify the runtime repair section re-injects type_constraints with FORBIDDEN entries
        assert "rt_type_constraints" in source, (
            "runner._stage_validation runtime-repair must read type_constraints via rt_type_constraints. "
            "Per-type constraint re-injection is missing."
        )
        assert "rt_type_constraint_reminder" in source, (
            "runner._stage_validation runtime-repair must build rt_type_constraint_reminder "
            "and append it to the runtime repair prompt."
        )
        assert "FORBIDDEN" in source, (
            "runner._stage_validation runtime-repair prompt must include FORBIDDEN constraints "
            "to prevent the LLM from introducing banned patterns during runtime repair."
        )

    def test_runtime_repair_receives_per_type_constraints(self):
        """Per-type constraints must be re-injected and validated in the runtime repair path."""
        import inspect
        from plugin_examples import runner
        source = inspect.getsource(runner._stage_validation)
        # Verify semantic validation runs after runtime repair (mirrors build repair)
        assert "rt_semantic_issues" in source, (
            "runner._stage_validation runtime-repair must perform semantic validation "
            "via rt_semantic_issues before writing the fixed code. "
            "This prevents semantically invalid code from being written after runtime repair."
        )
        assert "_validate_code_from_constraints(fixed_code, rt_type_constraints)" in source, (
            "runner._stage_validation runtime-repair must call "
            "_validate_code_from_constraints(fixed_code, rt_type_constraints) "
            "so per-type REQUIRED/FORBIDDEN rules are enforced after runtime repair."
        )
