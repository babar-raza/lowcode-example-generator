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


class TestPdfAConverterConstraint:
    """Sprint 58 regression: PdfAConverter must require 'using Aspose.Pdf.Text;'.

    Root cause of pdf-pdf-aconverter Sprint 57 failure: LLM generated code using
    TextFragment without the required using directive, causing CS0246 compile error.
    Fix: 'using Aspose.Pdf.Text;' added to per_type_constraints.PdfAConverter.REQUIRED in pdf.yml.
    """

    def _load_pdf_per_type_constraints(self) -> dict:
        """Load per_type_constraints from pipeline/configs/families/pdf.yml."""
        import yaml
        from pathlib import Path
        config_path = (
            Path(__file__).resolve().parents[2]
            / "pipeline" / "configs" / "families" / "pdf.yml"
        )
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("per_type_constraints", {})

    def test_pdfaconverter_config_requires_using_aspose_pdf_text(self):
        """Sprint 58 regression: pdf.yml PdfAConverter.required must contain 'using Aspose.Pdf.Text;'.

        This was the root cause of the pdf-pdf-aconverter Sprint 57 failure.
        The LLM omitted the using directive for TextFragment, causing CS0246.
        """
        ptc = self._load_pdf_per_type_constraints()
        pdfaconverter_required = ptc.get("PdfAConverter", {}).get("required", [])
        text_ns_entries = [e for e in pdfaconverter_required if "Aspose.Pdf.Text" in e]
        assert text_ns_entries, (
            "pdf.yml PdfAConverter.required must include 'using Aspose.Pdf.Text;' "
            "(missing directive caused Sprint 57 pdf-pdf-aconverter build failure). "
            f"Current required entries: {pdfaconverter_required}"
        )

    def test_pdfaconverter_code_missing_using_pdf_text_fails_validation(self):
        """Sprint 58 regression: Code with TextFragment but no using Aspose.Pdf.Text; must fail.

        Validates that _validate_code_from_constraints correctly catches the
        missing directive when PdfAConverter per_type_constraints are applied.
        """
        from plugin_examples.generator.code_generator import _validate_code_from_constraints

        ptc = self._load_pdf_per_type_constraints()
        pdfaconverter_constraints = ptc.get("PdfAConverter", {})
        # Code that omits using Aspose.Pdf.Text; — valid C# pattern but missing using
        code_missing_using = (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "var doc = new Document();\n"
            "var page = doc.Pages.Add();\n"
            "page.Paragraphs.Add(new TextFragment(\"Hello PDF/A\"));\n"
            "doc.Save(\"input.pdf\");\n"
            "var options = new PdfAConvertOptions();\n"
            "options.AddInput(new FileDataSource(\"input.pdf\"));\n"
            "options.AddOutput(new FileDataSource(\"output.pdf\"));\n"
            "var result = new PdfAConverter().Process(options);\n"
        )
        issues = _validate_code_from_constraints(code_missing_using, pdfaconverter_constraints)
        assert any("Aspose.Pdf.Text" in i for i in issues), (
            "PdfAConverter validation must flag missing 'using Aspose.Pdf.Text;' directive. "
            f"Issues found: {issues}"
        )

    def test_pdfaconverter_code_with_using_pdf_text_passes_validation(self):
        """Sprint 58 regression: Code with TextFragment AND using Aspose.Pdf.Text; must pass."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints

        ptc = self._load_pdf_per_type_constraints()
        pdfaconverter_constraints = ptc.get("PdfAConverter", {})
        code_with_using = (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.Text;\n"
            "var doc = new Document();\n"
            "var page = doc.Pages.Add();\n"
            "page.Paragraphs.Add(new TextFragment(\"Hello PDF/A\"));\n"
            "doc.Save(\"input.pdf\");\n"
            "var options = new PdfAConvertOptions();\n"
            "options.AddInput(new FileDataSource(\"input.pdf\"));\n"
            "options.AddOutput(new FileDataSource(\"output.pdf\"));\n"
            "var result = new PdfAConverter().Process(options);\n"
        )
        issues = _validate_code_from_constraints(code_with_using, pdfaconverter_constraints)
        assert len(issues) == 0, (
            f"PdfAConverter code with all required using directives must pass validation. "
            f"Unexpected issues: {issues}"
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

    def test_splitter_packet_does_not_require_using_aspose_pdf_text(self):
        """Regression: Splitter must NOT carry 'using Aspose.Pdf.Text;' as a REQUIRED constraint.
        Splitter does not use TextFragment — this constraint was a false-positive removed in Sprint 24."""
        scenario = _make_pdf_scenario("Splitter", "splitter")
        packet = build_packet(scenario, _make_pdf_splitter_catalog())
        text_namespace_required = [
            c for c in packet.constraints
            if "Aspose.Pdf.Text" in c and "REQUIRED" in c
        ]
        assert not text_namespace_required, (
            f"Splitter must NOT have REQUIRED: using Aspose.Pdf.Text; constraint "
            f"(false-positive removed Sprint 24). Found: {text_namespace_required}"
        )

    def test_splitter_code_without_using_pdf_text_passes_from_constraints(self):
        """Regression: Splitter code that lacks 'using Aspose.Pdf.Text;' must not be flagged
        by _validate_code_from_constraints when the Splitter per_type_constraints are used."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        splitter_constraints = {
            "required": [
                "REQUIRED: new Splitter().Process(options) — use the LowCode Splitter plugin, not PdfFileEditor",
                "REQUIRED: using Aspose.Pdf; (for Document fixture creation)",
            ],
            "forbidden": [
                "FORBIDDEN: PdfFileEditor — use Aspose.Pdf.LowCode.Splitter instead",
            ],
        }
        code = (
            'using Aspose.Pdf;\n'
            'using Aspose.Pdf.LowCode;\n'
            'var doc = new Document();\n'
            'doc.Pages.Add();\n'
            'doc.Save("input.pdf");\n'
            'var options = new SplitOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            'var result = new Splitter().Process(options);\n'
        )
        issues = _validate_code_from_constraints(code, splitter_constraints)
        assert len(issues) == 0, (
            f"Splitter code without 'using Aspose.Pdf.Text;' must pass validation. Issues: {issues}"
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

    def test_literal_string_required_absent_flagged(self):
        """Literal-string REQUIRED constraint (no parentheses) flags code missing the string."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                'REQUIRED: "output.jpg" — JPEG output filename MUST be output.jpg (not output.pdf)'
            ]
        }
        # Code has output.pdf — the literal "output.jpg" is absent
        code = 'string outputPath = Path.Combine(Path.GetTempPath(), "output.pdf");\nnew Jpeg().Process(options);'
        issues = _validate_code_from_constraints(code, constraints)
        assert any('"output.jpg"' in i or "output.jpg" in i for i in issues)

    def test_literal_string_required_present_passes(self):
        """Literal-string REQUIRED constraint passes when the string appears in code."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                'REQUIRED: "output.jpg" — JPEG output filename MUST be output.jpg (not output.pdf)'
            ]
        }
        code = 'string outputPath = Path.Combine(Path.GetTempPath(), "output.jpg");\nnew Jpeg().Process(options);'
        issues = _validate_code_from_constraints(code, constraints)
        assert not any('"output.jpg"' in i for i in issues)

    def test_literal_string_tiff_extension_absent_flagged(self):
        """Literal-string REQUIRED for output.tiff flags code using output.tif."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                'REQUIRED: "output.tiff" — TIFF output filename MUST be output.tiff (not output.tif)'
            ]
        }
        # Code uses .tif (wrong) — "output.tiff" is absent
        code = 'string outputPath = "output.tif";\nnew Tiff().Process(options);'
        issues = _validate_code_from_constraints(code, constraints)
        assert any("output.tiff" in i for i in issues)

    def test_literal_string_tiff_extension_present_passes(self):
        """Literal-string REQUIRED for output.tiff passes when code uses output.tiff."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                'REQUIRED: "output.tiff" — TIFF output filename MUST be output.tiff (not output.tif)'
            ]
        }
        code = 'string outputPath = Path.Combine(Path.GetTempPath(), "output.tiff");\nnew Tiff().Process(options);'
        issues = _validate_code_from_constraints(code, constraints)
        assert not any("output.tiff" in i for i in issues)

    def test_literal_string_combined_with_method_constraint(self):
        """Literal-string and method-call REQUIRED constraints work together."""
        from plugin_examples.generator.code_generator import _validate_code_from_constraints
        constraints = {
            "required": [
                'REQUIRED: new Jpeg().Process(options) — use the LowCode Jpeg plugin',
                'REQUIRED: "output.jpg" — JPEG output filename MUST be output.jpg',
            ]
        }
        # Has Jpeg().Process but uses wrong output extension
        code = (
            'var options = new JpegOptions();\n'
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            'new Jpeg().Process(options);\n'
        )
        issues = _validate_code_from_constraints(code, constraints)
        # Method call is present, but "output.jpg" is absent — only filename issue flagged
        assert any("output.jpg" in i for i in issues)
        assert not any("new Jpeg" in i for i in issues)

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


# ---------------------------------------------------------------------------
# Sprint 14 Lane C — PDF reference example injection tests
# Verify that code_generator.generate_example injects the correct MANDATORY
# REFERENCE EXAMPLE into the repair prompt for each failing PDF type.
# ---------------------------------------------------------------------------


def _make_failing_pdf_packet(type_short: str, namespace_type: str) -> object:
    """Create a minimal PromptPacket-like object for a failing PDF type."""
    from plugin_examples.generator.packet_builder import PromptPacket
    return PromptPacket(
        scenario_id=f"pdf-{type_short}",
        target_type=f"Aspose.Pdf.LowCode.{namespace_type}",
        target_namespace="Aspose.Pdf.LowCode",
        target_methods=["Process"],
        user_prompt="Generate a C# example.",
        system_prompt="You are a C# developer.",
        approved_symbols=[],
        constraints=[
            f"REQUIRED: new {namespace_type}().Process(options)",
            "REQUIRED: options.AddInput(new FileDataSource(",
        ],
        template_hints={},
        input_strategy="generated",
        input_files=[],
        type_details=None,
        per_type_constraints={},
    )


class TestPdfReferenceExampleInjection:
    """Verify MANDATORY REFERENCE EXAMPLEs are injected into repair prompts
    for Sprint 14 Lane C PDF types: Optimizer, PdfAConverter, DocConverter,
    XlsConverter, Html."""

    def _get_repair_reminder(self, type_short: str, namespace_type: str) -> str:
        """Run generate_example with an LLM that always returns invalid code,
        capture what the repair prompt contains."""
        from plugin_examples.generator.code_generator import generate_example

        captured_prompts = []

        def mock_llm(prompt: str, system: str) -> str:
            captured_prompts.append(prompt)
            # Return code that always fails validation (missing required patterns)
            return "```csharp\nusing System;\nclass Program { static void Main() {} }\n```"

        packet = _make_failing_pdf_packet(type_short, namespace_type)
        generate_example(packet, llm_generate=mock_llm, max_repairs=1)
        # The second call (repair) contains the constraint_reminder
        assert len(captured_prompts) >= 2, f"Expected repair call for {type_short}"
        return captured_prompts[1]  # repair prompt

    def test_optimizer_reference_example_injected(self):
        """Optimizer repair prompt must include OptimizeOptions and new Optimizer().Process pattern."""
        reminder = self._get_repair_reminder("optimizer", "Optimizer")
        assert "MANDATORY REFERENCE EXAMPLE for Optimizer" in reminder
        assert "new Optimizer().Process(options)" in reminder
        assert "OptimizeOptions" in reminder

    def test_pdfaconverter_reference_example_injected(self):
        """PdfAConverter repair prompt must include PdfAConvertOptions and new PdfAConverter().Process."""
        reminder = self._get_repair_reminder("pdfaconverter", "PdfAConverter")
        assert "MANDATORY REFERENCE EXAMPLE for PdfAConverter" in reminder
        assert "new PdfAConvertOptions()" in reminder
        assert "new PdfAConverter().Process(options)" in reminder

    def test_docconverter_reference_example_injected(self):
        """DocConverter repair prompt must include PdfToDocOptions and SaveFormat.DocX."""
        reminder = self._get_repair_reminder("docconverter", "DocConverter")
        assert "MANDATORY REFERENCE EXAMPLE for DocConverter" in reminder
        assert "new PdfToDocOptions()" in reminder
        assert "options.SaveFormat = Aspose.Pdf.LowCode.SaveFormat.DocX" in reminder
        assert "new DocConverter().Process(options)" in reminder

    def test_xlsconverter_reference_example_injected(self):
        """XlsConverter repair prompt must include PdfToXlsOptions and ExcelFormat.XLSX."""
        reminder = self._get_repair_reminder("xlsconverter", "XlsConverter")
        assert "MANDATORY REFERENCE EXAMPLE for XlsConverter" in reminder
        assert "new PdfToXlsOptions()" in reminder
        assert "options.Format = PdfToXlsOptions.ExcelFormat.XLSX" in reminder
        assert "new XlsConverter().Process(options)" in reminder

    def test_html_reference_example_injected(self):
        """Html repair prompt must include HtmlToPdfOptions and File.WriteAllText for HTML input."""
        reminder = self._get_repair_reminder("html", "Html")
        assert "MANDATORY REFERENCE EXAMPLE for Html" in reminder
        assert "new HtmlToPdfOptions()" in reminder
        assert "File.WriteAllText" in reminder
        assert "input.html" in reminder
        assert "new Html().Process(options)" in reminder

    def test_optimizer_reference_not_injected_for_other_types(self):
        """The Optimizer reference example must NOT appear in non-Optimizer repair prompts."""
        reminder = self._get_repair_reminder("xlsconverter", "XlsConverter")
        assert "MANDATORY REFERENCE EXAMPLE for Optimizer" not in reminder

    def test_docconverter_reference_not_injected_for_html(self):
        """DocConverter reference must NOT appear in Html repair prompt."""
        reminder = self._get_repair_reminder("html", "Html")
        assert "MANDATORY REFERENCE EXAMPLE for DocConverter" not in reminder


# ---------------------------------------------------------------------------
# Lane A — LLM empty-model 400 fix tests
# ---------------------------------------------------------------------------

class TestLLMEmptyModelFix:
    """Tests proving GPT_OSS_MODEL='' is treated the same as absent (=> 'recommended').

    Root cause of Sprint 14 400 error:
      Background command used $GPT_OSS_MODEL shell expansion.
      GPT_OSS_MODEL was unset in bash → expanded to "" → subprocess got GPT_OSS_MODEL="".
      os.environ.get("GPT_OSS_MODEL", "recommended") returns "" (key present, value empty).
      _call_openai_compatible: `if model:` is False for "" → model field omitted from body.
      API returns 400: "Invalid model name passed in model=None."

    Fix: (os.environ.get("GPT_OSS_MODEL") or "").strip() or "recommended"
    """

    def test_get_provider_model_absent_returns_recommended(self, monkeypatch):
        """GPT_OSS_MODEL absent → _get_provider_model returns 'recommended'."""
        from plugin_examples.llm_router.router import _get_provider_model
        monkeypatch.delenv("GPT_OSS_MODEL", raising=False)
        assert _get_provider_model("llm_professionalize") == "recommended"

    def test_get_provider_model_empty_string_returns_recommended(self, monkeypatch):
        """GPT_OSS_MODEL='' (shell expansion of unset var) → 'recommended', not ''."""
        from plugin_examples.llm_router.router import _get_provider_model
        monkeypatch.setenv("GPT_OSS_MODEL", "")
        assert _get_provider_model("llm_professionalize") == "recommended"

    def test_get_provider_model_whitespace_returns_recommended(self, monkeypatch):
        """GPT_OSS_MODEL='   ' (whitespace only) → 'recommended'."""
        from plugin_examples.llm_router.router import _get_provider_model
        monkeypatch.setenv("GPT_OSS_MODEL", "   ")
        assert _get_provider_model("llm_professionalize") == "recommended"

    def test_get_provider_model_explicit_value_preserved(self, monkeypatch):
        """GPT_OSS_MODEL='my-model' → 'my-model' preserved as-is."""
        from plugin_examples.llm_router.router import _get_provider_model
        monkeypatch.setenv("GPT_OSS_MODEL", "my-model")
        assert _get_provider_model("llm_professionalize") == "my-model"

    def test_call_provider_empty_model_uses_recommended(self, monkeypatch):
        """_call_provider for llm_professionalize uses 'recommended' when GPT_OSS_MODEL=''."""
        import unittest.mock as mock
        from plugin_examples.llm_router.router import _call_provider
        monkeypatch.setenv("GPT_OSS_MODEL", "")
        monkeypatch.setenv("GPT_OSS_ENDPOINT", "https://llm.example.com/v1/")
        monkeypatch.setenv("GPT_OSS_API_KEY", "test-key")

        captured = {}
        def fake_call_openai(endpoint, prompt, *, system_prompt="", timeout=120,
                             api_key="", model="", **kwargs):
            captured["model"] = model
            return "ok"

        with mock.patch("plugin_examples.llm_router.router._call_openai_compatible", fake_call_openai):
            result = _call_provider("llm_professionalize", "hello")

        assert captured["model"] == "recommended", (
            f"Expected 'recommended' when GPT_OSS_MODEL='', got {captured['model']!r}"
        )

    def test_call_provider_absent_model_uses_recommended(self, monkeypatch):
        """_call_provider uses 'recommended' when GPT_OSS_MODEL is completely absent."""
        import unittest.mock as mock
        from plugin_examples.llm_router.router import _call_provider
        monkeypatch.delenv("GPT_OSS_MODEL", raising=False)
        monkeypatch.setenv("GPT_OSS_ENDPOINT", "https://llm.example.com/v1/")
        monkeypatch.setenv("GPT_OSS_API_KEY", "test-key")

        captured = {}
        def fake_call_openai(endpoint, prompt, *, system_prompt="", timeout=120,
                             api_key="", model="", **kwargs):
            captured["model"] = model
            return "ok"

        with mock.patch("plugin_examples.llm_router.router._call_openai_compatible", fake_call_openai):
            result = _call_provider("llm_professionalize", "hello")

        assert captured["model"] == "recommended"

    def test_model_field_included_in_request_body_when_recommended(self, monkeypatch):
        """When model='recommended', the model field IS included in the JSON body (not omitted)."""
        import unittest.mock as mock
        import requests as req_lib
        from plugin_examples.llm_router import router

        monkeypatch.delenv("GPT_OSS_MODEL", raising=False)
        monkeypatch.setenv("GPT_OSS_ENDPOINT", "https://llm.example.com/v1/")
        monkeypatch.setenv("GPT_OSS_API_KEY", "test-key")

        sent_bodies = []

        class FakeResp:
            status_code = 200
            def raise_for_status(self): pass
            def json(self):
                return {"choices": [{"message": {"content": "ok"}}], "usage": {}}

        def fake_post(url, json=None, headers=None, timeout=None):
            sent_bodies.append(json)
            return FakeResp()

        with mock.patch.object(req_lib, "post", fake_post):
            router._call_provider("llm_professionalize", "hello")

        assert sent_bodies, "No request was sent"
        body = sent_bodies[0]
        assert "model" in body, f"'model' key missing from request body: {body}"
        assert body["model"] == "recommended", f"Expected 'recommended', got {body['model']!r}"


# ---------------------------------------------------------------------------
# Lane C — PDF Jpeg/Tiff/Png MANDATORY REFERENCE EXAMPLE injection tests
# ---------------------------------------------------------------------------

class TestPdfImageWaveReferenceInjection:
    """Verify MANDATORY REFERENCE EXAMPLEs are injected for Jpeg, Tiff, Png
    so the LLM uses correct output filenames and validation patterns.

    Root cause of Sprint 9 Wave C failures:
    - Jpeg: LLM used output.pdf instead of output.jpg
    - Tiff: LLM used output.tif instead of output.tiff
    - Png: LLM used File.Exists("output.png") (always False — plugin writes output_0.png)
    """

    def _get_repair_reminder(self, type_short: str, namespace_type: str) -> str:
        """Capture repair prompt content for a given PDF image type."""
        from plugin_examples.generator.code_generator import generate_example

        captured_prompts = []

        def mock_llm(prompt: str, system: str) -> str:
            captured_prompts.append(prompt)
            return "```csharp\nusing System;\nclass Program { static void Main() {} }\n```"

        packet = _make_failing_pdf_packet(type_short, namespace_type)
        generate_example(packet, llm_generate=mock_llm, max_repairs=1)
        assert len(captured_prompts) >= 2, f"Expected repair call for {type_short}"
        return captured_prompts[1]

    def test_jpeg_reference_example_injected(self):
        """Jpeg repair prompt must include output.jpg reference, never output.pdf."""
        reminder = self._get_repair_reminder("jpeg", "Jpeg")
        assert "MANDATORY REFERENCE EXAMPLE for Jpeg" in reminder
        assert 'output.jpg' in reminder
        assert "JpegOptions" in reminder
        assert "new Jpeg().Process(options)" in reminder

    def test_jpeg_reference_forbids_output_pdf(self):
        """Jpeg reference explicitly forbids output.pdf filename."""
        reminder = self._get_repair_reminder("jpeg", "Jpeg")
        assert "NEVER output.pdf" in reminder or "not output.pdf" in reminder

    def test_tiff_reference_example_injected(self):
        """Tiff repair prompt must include output.tiff reference (four letters, never .tif)."""
        reminder = self._get_repair_reminder("tiff", "Tiff")
        assert "MANDATORY REFERENCE EXAMPLE for Tiff" in reminder
        assert 'output.tiff' in reminder
        assert "TiffOptions" in reminder
        assert "new Tiff().Process(options)" in reminder

    def test_tiff_reference_forbids_output_tif(self):
        """Tiff reference explicitly forbids output.tif (three letters)."""
        reminder = self._get_repair_reminder("tiff", "Tiff")
        assert "NEVER output.tif" in reminder or "not output.tif" in reminder

    def test_png_reference_example_injected(self):
        """Png repair prompt must validate via result.ResultCollection.Count, not File.Exists."""
        reminder = self._get_repair_reminder("png", "Png")
        assert "MANDATORY REFERENCE EXAMPLE for Png" in reminder
        assert "result.ResultCollection.Count" in reminder
        assert "PngOptions" in reminder
        assert "new Png().Process(options)" in reminder

    def test_png_reference_forbids_file_exists(self):
        """Png reference explicitly forbids File.Exists (output_0.png page-numbering issue)."""
        reminder = self._get_repair_reminder("png", "Png")
        assert "File.Exists" in reminder  # must mention it as forbidden
        assert "always return false" in reminder or "always returns false" in reminder

    def test_jpeg_reference_not_injected_for_tiff(self):
        """Jpeg reference must NOT appear in Tiff repair prompt."""
        reminder = self._get_repair_reminder("tiff", "Tiff")
        assert "MANDATORY REFERENCE EXAMPLE for Jpeg" not in reminder

    def test_tiff_reference_not_injected_for_jpeg(self):
        """Tiff reference must NOT appear in Jpeg repair prompt."""
        reminder = self._get_repair_reminder("jpeg", "Jpeg")
        assert "MANDATORY REFERENCE EXAMPLE for Tiff" not in reminder


class TestPdfNextWaveReferenceInjection(TestPdfImageWaveReferenceInjection):
    """Tests for Sprint 16 next-wave types: TocGenerator, ImageExtractor.

    Inherits _get_repair_reminder from parent class.
    """

    def test_tocgenerator_reference_example_injected(self):
        """TocGenerator repair prompt must include TocOptions and TocGenerator pattern."""
        reminder = self._get_repair_reminder("tocgenerator", "TocGenerator")
        assert "MANDATORY REFERENCE EXAMPLE for TocGenerator" in reminder
        assert "TocOptions" in reminder
        assert "new TocGenerator().Process(options)" in reminder
        assert "result.ResultCollection.Count" in reminder

    def test_tocgenerator_reference_forbids_plugin_options(self):
        """TocGenerator reference must forbid abstract PluginOptions."""
        reminder = self._get_repair_reminder("tocgenerator", "TocGenerator")
        assert "PluginOptions" in reminder

    def test_tocgenerator_has_add_input_and_add_output(self):
        """TocGenerator reference must include AddInput and AddOutput."""
        reminder = self._get_repair_reminder("tocgenerator", "TocGenerator")
        assert "AddInput" in reminder
        assert "AddOutput" in reminder

    def test_imageextractor_reference_example_injected(self):
        """ImageExtractor repair prompt must include ImageExtractorOptions and no AddOutput."""
        reminder = self._get_repair_reminder("imageextractor", "ImageExtractor")
        assert "MANDATORY REFERENCE EXAMPLE for ImageExtractor" in reminder
        assert "ImageExtractorOptions" in reminder
        assert "new ImageExtractor().Process(options)" in reminder
        assert "result.ResultCollection" in reminder

    def test_imageextractor_reference_forbids_add_output(self):
        """ImageExtractor reference must warn against AddOutput (extractor, not converter)."""
        reminder = self._get_repair_reminder("imageextractor", "ImageExtractor")
        assert "AddOutput" in reminder  # mentioned as forbidden in the text

    def test_imageextractor_reference_forbids_pdf_extractor_facades(self):
        """ImageExtractor reference must forbid PdfExtractor from Facades."""
        reminder = self._get_repair_reminder("imageextractor", "ImageExtractor")
        assert "PdfExtractor" in reminder

    def test_tocgenerator_reference_not_injected_for_imageextractor(self):
        """TocGenerator reference must NOT appear in ImageExtractor repair prompt."""
        reminder = self._get_repair_reminder("imageextractor", "ImageExtractor")
        assert "MANDATORY REFERENCE EXAMPLE for TocGenerator" not in reminder

    def test_imageextractor_reference_not_injected_for_tocgenerator(self):
        """ImageExtractor reference must NOT appear in TocGenerator repair prompt."""
        reminder = self._get_repair_reminder("tocgenerator", "TocGenerator")
        assert "MANDATORY REFERENCE EXAMPLE for ImageExtractor" not in reminder


# ---------------------------------------------------------------------------
# Sprint 17 Lane C — Template-first generation architecture tests
# Verify that template_first: true in per_type_constraints causes
# generate_example() to bypass LLM and emit deterministic, validated code.
# ---------------------------------------------------------------------------


def _make_template_first_packet(type_short: str, namespace_type: str) -> object:
    """Create a PromptPacket with template_first=True for the given PDF type."""
    from plugin_examples.generator.packet_builder import PromptPacket
    return PromptPacket(
        scenario_id=f"pdf-{type_short}",
        target_type=f"Aspose.Pdf.LowCode.{namespace_type}",
        target_namespace="Aspose.Pdf.LowCode",
        target_methods=["Process"],
        user_prompt="Generate a C# example.",
        system_prompt="You are a C# developer.",
        approved_symbols=[],
        constraints=[],
        template_hints={},
        input_strategy="generated",
        input_files=[],
        type_details=None,
        per_type_constraints={namespace_type: {"template_first": True, "required": [], "forbidden": []}},
    )


class TestTemplateFIrstGeneration:
    """template_first: true causes generate_example to bypass LLM entirely."""

    def test_docconverter_template_first_bypasses_llm(self):
        """With template_first, LLM callable is never invoked for DocConverter."""
        packet = _make_template_first_packet("docconverter", "DocConverter")
        llm_called = []

        def llm_should_not_be_called(prompt, system):
            llm_called.append(True)
            return "```csharp\nusing System;\n```"

        example = generate_example(packet, llm_generate=llm_should_not_be_called)
        assert not llm_called, "LLM must NOT be called when template_first=True"
        assert example.status == "generated_template_first"

    def test_xlsconverter_template_first_status(self):
        """XlsConverter template-first returns generated_template_first status."""
        packet = _make_template_first_packet("xlsconverter", "XlsConverter")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_html_template_first_bypasses_llm(self):
        """Html (HTML-to-PDF) template-first returns generated_template_first."""
        packet = _make_template_first_packet("html", "Html")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_jpeg_template_first_bypasses_llm(self):
        """Jpeg template-first returns generated_template_first."""
        packet = _make_template_first_packet("jpeg", "Jpeg")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_tiff_template_first_bypasses_llm(self):
        """Tiff template-first returns generated_template_first."""
        packet = _make_template_first_packet("tiff", "Tiff")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_png_template_first_bypasses_llm(self):
        """Png template-first returns generated_template_first."""
        packet = _make_template_first_packet("png", "Png")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_docconverter_template_contains_required_patterns(self):
        """DocConverter template must include PdfToDocOptions and SaveFormat.DocX."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("docconverter", "DocConverter")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "PdfToDocOptions" in code
        assert "SaveFormat.DocX" in code
        assert "new DocConverter().Process(options)" in code
        assert "output.docx" in code

    def test_xlsconverter_template_contains_required_patterns(self):
        """XlsConverter template must include PdfToXlsOptions and ExcelFormat.XLSX."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("xlsconverter", "XlsConverter")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "PdfToXlsOptions" in code
        assert "PdfToXlsOptions.ExcelFormat.XLSX" in code
        assert "new XlsConverter().Process(options)" in code
        assert "output.xlsx" in code

    def test_html_template_contains_required_patterns(self):
        """Html template must use HtmlToPdfOptions and File.WriteAllText for HTML input."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("html", "Html")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "HtmlToPdfOptions" in code
        assert "File.WriteAllText" in code
        assert "input.html" in code
        assert "new Html().Process(options)" in code
        assert "output.pdf" in code

    def test_jpeg_template_contains_required_patterns(self):
        """Jpeg template must use JpegOptions and output.jpg (not output.pdf)."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("jpeg", "Jpeg")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "JpegOptions" in code
        assert "output.jpg" in code
        assert "new Jpeg().Process(options)" in code
        assert "output.pdf" not in code

    def test_tiff_template_contains_required_patterns(self):
        """Tiff template must use TiffOptions and output.tiff (not output.tif)."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("tiff", "Tiff")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "TiffOptions" in code
        assert "output.tiff" in code
        assert "output.tif" not in code.replace("output.tiff", "")
        assert "new Tiff().Process(options)" in code

    def test_png_template_contains_required_patterns(self):
        """Png template must use PngOptions and result.ResultCollection.Count (not File.Exists)."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("png", "Png")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "PngOptions" in code
        assert "output.png" in code
        assert "new Png().Process(options)" in code
        assert "result.ResultCollection.Count" in code
        assert "File.Exists" not in code

    def test_tocgenerator_template_first_bypasses_llm(self):
        """TocGenerator template-first returns generated_template_first status."""
        packet = _make_template_first_packet("tocgenerator", "TocGenerator")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_imageextractor_template_first_bypasses_llm(self):
        """ImageExtractor template-first returns generated_template_first status."""
        packet = _make_template_first_packet("imageextractor", "ImageExtractor")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_tocgenerator_template_contains_required_patterns(self):
        """TocGenerator template must use TocOptions, AddInput, AddOutput, result.ResultCollection.Count."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("tocgenerator", "TocGenerator")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "new TocOptions()" in code
        assert "new TocGenerator().Process(options)" in code
        assert 'options.AddInput(new FileDataSource("input.pdf"))' in code
        assert 'options.AddOutput(new FileDataSource("output.pdf"))' in code
        assert "result.ResultCollection.Count > 0" in code

    def test_imageextractor_template_contains_required_patterns(self):
        """ImageExtractor template must embed an image, use ImageExtractorOptions, no AddOutput."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("imageextractor", "ImageExtractor")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "new ImageExtractorOptions()" in code
        assert "new ImageExtractor().Process(options)" in code
        assert "options.AddInput(new FileDataSource(" in code
        assert "options.AddOutput" not in code
        assert "page.Resources.Images.Add(" in code
        assert "result.ResultCollection.Count > 0" in code

    def test_template_first_false_does_not_bypass_llm(self):
        """When template_first is absent/false, LLM IS called normally."""
        from plugin_examples.generator.packet_builder import PromptPacket
        packet = PromptPacket(
            scenario_id="pdf-merger",
            target_type="Aspose.Pdf.LowCode.Merger",
            target_namespace="Aspose.Pdf.LowCode",
            target_methods=["Process"],
            user_prompt="Generate a C# example.",
            system_prompt="You are a C# developer.",
            approved_symbols=[],
            constraints=[],
            template_hints={},
            input_strategy="generated",
            input_files=[],
            type_details=None,
            per_type_constraints={"Merger": {"required": [], "forbidden": []}},
        )
        llm_called = []

        def counting_llm(prompt, system):
            llm_called.append(True)
            return "```csharp\nusing System;\nclass P { static void Main() {} }\n```"

        generate_example(packet, llm_generate=counting_llm, max_repairs=0)
        assert llm_called, "LLM MUST be called when template_first is absent/false"

    def test_template_first_none_per_type_constraints_does_not_bypass_llm(self):
        """When per_type_constraints is None, LLM is called normally (no template_first)."""
        from plugin_examples.generator.packet_builder import PromptPacket
        packet = PromptPacket(
            scenario_id="pdf-merger",
            target_type="Aspose.Pdf.LowCode.Merger",
            target_namespace="Aspose.Pdf.LowCode",
            target_methods=["Process"],
            user_prompt="Generate a C# example.",
            system_prompt="You are a C# developer.",
            approved_symbols=[],
            constraints=[],
            template_hints={},
            input_strategy="generated",
            input_files=[],
            type_details=None,
            per_type_constraints=None,
        )
        llm_called = []

        def counting_llm(prompt, system):
            llm_called.append(True)
            return "```csharp\nusing System;\nclass P { static void Main() {} }\n```"

        generate_example(packet, llm_generate=counting_llm, max_repairs=0)
        assert llm_called

    def test_family_config_loader_uses_utf8_encoding(self):
        """Loader must open YAML with UTF-8 so em-dash separators in constraints survive."""
        from plugin_examples.family_config.loader import load_family_config
        cfg = load_family_config("pipeline/configs/families/pdf.yml")
        ptc = cfg.per_type_constraints
        dc = ptc.get("DocConverter", {})
        # The em-dash separator (U+2014) must round-trip correctly so validation
        # can strip the description suffix.  If the loader used cp1252 the
        # constraint would contain â€" instead of — and separation would fail.
        savefmt_req = next(
            (r for r in dc.get("required", []) if "SaveFormat.DocX" in r), None
        )
        assert savefmt_req is not None
        # After stripping REQUIRED: prefix and splitting on em-dash the token
        # must be exactly the code pattern (no mojibake, no description suffix).
        stripped = savefmt_req.replace("REQUIRED:", "").strip()
        token = stripped.split("\u2014")[0].strip()  # U+2014 em-dash
        assert token == "options.SaveFormat = Aspose.Pdf.LowCode.SaveFormat.DocX"

    def test_security_template_first_bypasses_llm(self):
        """Security template-first returns generated_template_first status."""
        packet = _make_template_first_packet("security", "Security")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_formflattener_template_first_bypasses_llm(self):
        """FormFlattener template-first returns generated_template_first status."""
        packet = _make_template_first_packet("formflattener", "FormFlattener")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_security_template_contains_required_patterns(self):
        """Security template must use EncryptionOptions, DocumentPrivilege, AddInput/AddOutput."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("security", "Security")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "EncryptionOptions" in code
        assert "DocumentPrivilege" in code
        assert "Aspose.Pdf.Facades" in code
        assert "new Security().Process(encOptions)" in code
        assert 'encOptions.AddInput(new FileDataSource("input.pdf"))' in code
        assert 'encOptions.AddOutput(new FileDataSource("output.pdf"))' in code
        assert "result.ResultCollection.Count > 0" in code

    def test_formflattener_template_contains_required_patterns(self):
        """FormFlattener template must use AcroForm fixture, FormFlattenAllFieldsOptions, AddInput/AddOutput."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("formflattener", "FormFlattener")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "FormFlattenAllFieldsOptions" in code
        assert "TextBoxField" in code
        assert "Aspose.Pdf.Forms" in code
        assert "doc.Form.Add(textBox, 1)" in code
        assert "new FormFlattener().Process(flattenOptions)" in code
        assert 'flattenOptions.AddInput(new FileDataSource("input.pdf"))' in code
        assert 'flattenOptions.AddOutput(new FileDataSource("output.pdf"))' in code
        assert "result.ResultCollection.Count > 0" in code

    def test_formeditor_template_first_bypasses_llm(self):
        """FormEditor template-first returns generated_template_first status."""
        packet = _make_template_first_packet("formeditor", "FormEditor")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_formeditor_template_first_works_without_llm(self):
        """Template-first types must use deterministic template even when llm_generate=None.
        Fix: template_first check is now ordered before the llm_generate is None fallback."""
        packet = _make_template_first_packet("formeditor", "FormEditor")
        example = generate_example(packet, llm_generate=None)
        assert example.status == "generated_template_first", (
            f"FormEditor with llm_generate=None must use template_first path, got: {example.status}"
        )

    def test_formexporter_template_first_works_without_llm(self):
        """Template-first types must use deterministic template even when llm_generate=None."""
        packet = _make_template_first_packet("formexporter", "FormExporter")
        example = generate_example(packet, llm_generate=None)
        assert example.status == "generated_template_first", (
            f"FormExporter with llm_generate=None must use template_first path, got: {example.status}"
        )

    def test_all_template_first_types_work_without_llm(self):
        """All 14 template_first PDF types must produce generated_template_first even when llm_generate=None."""
        from unittest.mock import MagicMock
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        for type_name in [
            "DocConverter", "XlsConverter", "Html", "Jpeg", "Tiff", "Png",
            "TocGenerator", "TableGenerator", "ImageExtractor",
            "Security", "FormFlattener", "FormEditor", "FormExporter", "Signature",
        ]:
            packet = _make_template_first_packet(type_name.lower(), type_name)
            example = generate_example(packet, llm_generate=None)
            assert example.status == "generated_template_first", (
                f"{type_name} with llm_generate=None must use template_first, got: {example.status}"
            )

    def test_formeditor_template_contains_required_patterns(self):
        """FormEditor template must use AcroForm fixture, FormRemoveAllFieldsOptions (NOT abstract FormEditorRemoveOptions)."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("formeditor", "FormEditor")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "FormRemoveAllFieldsOptions" in code, "Must use concrete FormRemoveAllFieldsOptions"
        assert "FormEditorRemoveOptions" not in code, "Must NOT use abstract FormEditorRemoveOptions"
        assert "TextBoxField" in code
        assert "Aspose.Pdf.Forms" in code
        assert "doc.Form.Add(textBox, 1)" in code
        assert "new FormEditor().Process(removeOptions)" in code
        assert 'removeOptions.AddInput(new FileDataSource("input.pdf"))' in code
        assert 'removeOptions.AddOutput(new FileDataSource("output.pdf"))' in code
        assert "result.ResultCollection.Count > 0" in code

    def test_formexporter_template_first_bypasses_llm(self):
        """FormExporter template-first returns generated_template_first status."""
        packet = _make_template_first_packet("formexporter", "FormExporter")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_formexporter_template_contains_required_patterns(self):
        """FormExporter template must use AcroForm fixture, FormExporterToJsonOptions, JSON output."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("formexporter", "FormExporter")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "FormExporterToJsonOptions" in code
        assert "TextBoxField" in code
        assert "Aspose.Pdf.Forms" in code
        assert "doc.Form.Add(textBox, 1)" in code
        assert "new FormExporter().Process(exportOptions)" in code
        assert 'exportOptions.AddInput(new FileDataSource("input.pdf"))' in code
        assert 'exportOptions.AddOutput(new FileDataSource("output.json"))' in code
        assert "result.ResultCollection.Count > 0" in code

    def test_signature_template_first_works_without_llm(self):
        """Signature template-first must produce generated_template_first even when llm_generate=None."""
        packet = _make_template_first_packet("signature", "Signature")
        example = generate_example(packet, llm_generate=None)
        assert example.status == "generated_template_first", (
            f"Signature with llm_generate=None must use template_first path, got: {example.status}"
        )

    def test_signature_template_first_bypasses_llm(self):
        """Signature template-first returns generated_template_first status even with stub LLM."""
        packet = _make_template_first_packet("signature", "Signature")
        example = generate_example(packet, llm_generate=lambda p, s: "")
        assert example.status == "generated_template_first"

    def test_signature_template_contains_required_patterns(self):
        """Signature template must use self-signed PFX, SignOptions 2-arg ctor, LowCode Signature.Process()."""
        from plugin_examples.generator.code_generator import _generate_deterministic_template_for_scenario
        packet = _make_template_first_packet("signature", "Signature")
        code = _generate_deterministic_template_for_scenario(packet)
        assert "SignOptions" in code, "Must use SignOptions"
        assert "RSA.Create" in code, "Must create self-signed cert via RSA.Create"
        assert "CertificateRequest" in code, "Must create self-signed cert via CertificateRequest"
        assert "new Signature().Process(signOptions)" in code, "Must call LowCode Signature.Process()"
        assert "FileDataSource" in code, "Must use FileDataSource for input/output"
        assert "System.Security.Cryptography" in code, "Must import System.Security.Cryptography"
        assert "X509ContentType.Pfx" in code, "Must export cert as PFX"
        assert "AddInput" in code, "Must call AddInput on SignOptions"
        assert "AddOutput" in code, "Must call AddOutput on SignOptions"
        assert "result.ResultCollection.Count > 0" in code, "Must check ResultCollection.Count"
        assert "PdfFileSignature" not in code, "Must NOT use core PdfFileSignature"

    def test_all_template_first_types_pass_validation_with_utf8_config(self):
        """All template-first types must produce code that passes constraint validation."""
        from plugin_examples.generator.code_generator import (
            _validate_code_from_constraints,
            _generate_deterministic_template_for_scenario,
        )
        from plugin_examples.family_config.loader import load_family_config
        from unittest.mock import MagicMock

        cfg = load_family_config("pipeline/configs/families/pdf.yml")
        ptc = cfg.per_type_constraints

        for type_name in [
            "DocConverter", "XlsConverter", "Html",
            "Jpeg", "Tiff", "Png", "TableGenerator",
            "TocGenerator", "ImageExtractor",
            "Security", "FormFlattener",
            "FormEditor", "FormExporter", "Signature",
        ]:
            packet = MagicMock()
            packet.target_type = f"Aspose.Pdf.LowCode.{type_name}"
            code = _generate_deterministic_template_for_scenario(packet)
            issues = _validate_code_from_constraints(code, ptc.get(type_name, {}))
            assert not issues, f"{type_name} template failed validation: {issues}"
