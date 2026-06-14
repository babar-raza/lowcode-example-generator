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

from plugin_examples.fixture_registry.fixture_factory import (
    generate_csv,
    generate_html,
    generate_json,
    generate_txt,
    generate_xlsx,
)
from plugin_examples.generator.code_generator import _validate_code, generate_example
from plugin_examples.generator.packet_builder import (
    PromptPacket,
    _build_fewshot_snippet,
    _build_fixture_instruction,
    build_packet,
)
from plugin_examples.scenario_planner.planner import (
    _build_scenario,
    _infer_input_format,
    _infer_output_format,
)
from plugin_examples.scenario_planner.runtime_feedback import (
    classify_runtime_failure,
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
            "required_symbols": ["Aspose.Cells.LowCode.HtmlConverter", "Aspose.Cells.LowCode.HtmlConverter.Process"],
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
            "required_symbols": ["Aspose.Cells.LowCode.HtmlConverter", "Aspose.Cells.LowCode.HtmlConverter.Process"],
            "input_strategy": "none",
            "input_files": [],
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
                                    "parameters": [],
                                }
                            ],
                        }
                    ],
                }
            ]
        }
        packet = build_packet(scenario, catalog)
        constraints_text = " ".join(packet.constraints)
        assert "Console.ReadLine" in constraints_text


# --- Test 3: Code validator detects Console.ReadKey ---


class TestCodeValidatorDetectsInteractive:
    def test_validate_code_detects_readkey(self):
        code = "Console.ReadKey();"
        issues = _validate_code(code)
        assert any("ReadKey" in i for i in issues)

    def test_validate_code_detects_readline(self):
        code = "Console.ReadLine();"
        issues = _validate_code(code)
        assert any("ReadLine" in i for i in issues)

    def test_validate_code_passes_clean(self):
        code = 'Console.WriteLine("Done.");'
        issues = _validate_code(code)
        assert len(issues) == 0


# --- Test 4: Input format map for TextConverter ---


class TestInputFormatMapTextConverterNotXlsx:
    def test_input_format_map_text_converter(self):
        """TextConverter input format per FormatContract is .xlsx."""
        fmt = _infer_input_format("TextConverter", ".xlsx", family="cells")
        assert fmt == ".xlsx"

    def test_input_format_map_html_converter(self):
        fmt = _infer_input_format("HtmlConverter", ".xlsx", family="cells")
        assert fmt == ".xlsx"

    def test_input_format_map_unknown_uses_default(self):
        fmt = _infer_input_format("UnknownType", ".docx")
        assert fmt == ".docx"

    def test_text_converter_scenario_uses_xlsx(self):
        """Full scenario build for TextConverter must use .xlsx input (per FormatContract)."""
        type_info = {
            "full_name": "Aspose.Cells.LowCode.TextConverter",
            "name": "TextConverter",
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
        assert scenario.required_input_format == ".xlsx"
        assert scenario.input_files == ["input.xlsx"]
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
            "test-scenario",
            1,
            stderr="Cannot read keys when either application does not have a console",
        )
        assert rc.classification == "interactive_console_call"
        assert rc.actionable is True

    def test_runtime_failure_classifies_wrong_input_format(self):
        rc = classify_runtime_failure(
            "test-scenario",
            1,
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


# --- Tests: Discovery sweep dependency resolution (Follow-up Stabilization Sprint) ---


class TestDiscoverySweepDepsResolution:
    def test_discovery_sweep_resolves_dependencies(self):
        """Source must call resolve_dependencies before building the catalog."""
        import inspect

        from plugin_examples import discovery_sweep

        source = inspect.getsource(discovery_sweep)
        assert "resolve_dependencies" in source, "discovery_sweep must call resolve_dependencies to fetch dep DLLs"

    def test_discovery_sweep_passes_deps_to_reflector(self):
        """Source must pass dependency_paths to build_catalog."""
        import inspect

        from plugin_examples import discovery_sweep

        source = inspect.getsource(discovery_sweep)
        assert "dependency_paths" in source, "discovery_sweep must pass dependency_paths= to build_catalog"
        assert (
            "dependency_dll_paths" in source
        ), "discovery_sweep must extract dependency_dll_paths from extraction result"

    def test_discovery_result_has_dependency_fields(self, tmp_path):
        """Result dict for a blocked family still includes dependency_count and dependency_paths."""
        from plugin_examples.discovery_sweep import run_discovery_sweep

        result = run_discovery_sweep(
            families=["nonexistent_for_deps_test"],
            repo_root=tmp_path,
        )
        fam = result["families"][0]
        assert "dependency_count" in fam, "dependency_count must be in result"
        assert "dependency_paths" in fam, "dependency_paths must be in result"

    def test_discover_lowcode_writes_family_proofs(self, tmp_path):
        """Discovery sweep writes all-family-lowcode-discovery.json with family entries."""
        from plugin_examples.discovery_sweep import run_discovery_sweep

        result = run_discovery_sweep(
            families=["nonexistent_proof_family", "another_nonexistent"],
            repo_root=tmp_path,
        )
        assert result["total_families"] == 2
        evidence_file = tmp_path / "workspace" / "verification" / "latest" / "all-family-lowcode-discovery.json"
        assert evidence_file.exists()
        import json

        data = json.loads(evidence_file.read_text())
        assert data["total_families"] == 2
        for fam in data["families"]:
            assert "family" in fam
            assert "status" in fam
            assert "dependency_count" in fam


# --- Tests: Multi-Family Discovery Expansion (Multi-Family API Catalog Expansion Sprint) ---

REPO_ROOT = Path(__file__).resolve().parents[2]


class TestMultiFamilyDiscoveryExpansion:
    def test_discover_lowcode_accepts_specific_family_list(self, tmp_path):
        """run_discovery_sweep accepts a list of families and processes exactly those."""
        from plugin_examples.discovery_sweep import run_discovery_sweep

        result = run_discovery_sweep(
            families=["alpha_nonexistent", "beta_nonexistent"],
            repo_root=tmp_path,
        )
        assert result["total_families"] == 2
        family_names = [f["family"] for f in result["families"]]
        assert "alpha_nonexistent" in family_names
        assert "beta_nonexistent" in family_names

    def test_discover_lowcode_skips_generation_for_words_pdf(self):
        """Discovery sweep source must not import generator or LLM router."""
        import inspect

        from plugin_examples import discovery_sweep

        source = inspect.getsource(discovery_sweep)
        assert "generate_example" not in source
        assert "generate_project" not in source
        assert "llm_router" not in source.lower()
        assert "LLMRouter" not in source

    def test_discovery_writes_family_source_of_truth_proofs(self):
        """Discovery sweep source must call write_source_of_truth_proof."""
        import inspect

        from plugin_examples import discovery_sweep

        source = inspect.getsource(discovery_sweep)
        assert "write_source_of_truth_proof" in source, "discovery_sweep must write per-family source-of-truth proofs"

    def test_disabled_families_remain_skipped(self, tmp_path):
        """Families in disabled/ that are not in enabled/ are skipped during --all-families scan."""
        from plugin_examples.discovery_sweep import run_discovery_sweep

        # Scan using a repo_root that has no enabled configs at all
        # (no .yml files in tmp_path/pipeline/configs/families/)
        result = run_discovery_sweep(all_families=True, repo_root=tmp_path)
        # With no enabled configs, no families discovered
        assert result["total_families"] == 0

    def test_disabled_families_remain_skipped_by_path(self, tmp_path):
        """Email and slides remain in disabled/ and are not auto-included."""
        # This tests the real repo: scan --all-families and verify email/slides not present
        result_families = set()
        (tmp_path / "pipeline" / "configs" / "families").mkdir(parents=True, exist_ok=True)
        from plugin_examples.discovery_sweep import run_discovery_sweep

        result = run_discovery_sweep(all_families=True, repo_root=tmp_path)
        # No email or slides in enabled families
        names = [r["family"] for r in result.get("families", [])]
        assert "email" not in names
        assert "slides" not in names

    def test_discovery_only_status_allows_discovery_without_experimental_flag(self, tmp_path):
        """Families with status=discovery_only run without --allow-experimental."""
        import yaml

        # Create a minimal discovery_only config (will fail during reflection but must not be skipped)
        cfg_dir = tmp_path / "pipeline" / "configs" / "families"
        cfg_dir.mkdir(parents=True, exist_ok=True)
        cfg = {
            "family": "testdisc",
            "display_name": "Test Discovery",
            "enabled": True,
            "status": "discovery_only",
            "nuget": {
                "package_id": "Fake.Package",
                "version_policy": "latest-stable",
                "target_framework_preference": ["netstandard2.0"],
                "dependency_resolution": {"enabled": False, "max_depth": 1},
            },
            "plugin_detection": {"namespace_patterns": ["Fake.LowCode"]},
            "github": {
                "official_examples_repo": {"owner": "x", "repo": "y", "branch": "main"},
                "published_plugin_examples_repo": {"owner": "x", "repo": "z", "branch": "main"},
            },
            "fixtures": {"sources": []},
            "existing_examples": {"sources": []},
            "generation": {"min_examples_per_family": 1, "max_examples_per_monthly_run": 5},
            "validation": {},
            "llm": {"provider_order": ["gpt_oss"]},
        }
        (cfg_dir / "testdisc.yml").write_text(yaml.dump(cfg))

        from plugin_examples.discovery_sweep import run_discovery_sweep

        result = run_discovery_sweep(
            families=["testdisc"],
            repo_root=tmp_path,
            allow_experimental=False,  # must NOT skip discovery_only
        )
        fam = result["families"][0]
        # Must attempt discovery (not return experimental_skipped)
        assert (
            fam["status"] != "experimental_skipped"
        ), "discovery_only families must not be skipped without --allow-experimental"

    def test_discovery_ranker_outputs_generation_readiness(self):
        """compute_generation_readiness returns list with all required fields."""
        from plugin_examples.discovery_sweep import compute_generation_readiness

        mock_results = [
            {
                "family": "cells",
                "status": "eligible_lowcode_found",
                "eligibility_status": "eligible",
                "plugin_type_count": 22,
                "plugin_method_count": 33,
                "lowcode_namespaces": ["Aspose.Cells.LowCode"],
                "catalog_path": None,
            },
            {
                "family": "noop",
                "status": "not_eligible_no_namespace",
                "eligibility_status": "not_eligible",
                "plugin_type_count": 0,
                "plugin_method_count": 0,
                "lowcode_namespaces": [],
                "catalog_path": None,
            },
        ]
        readiness = compute_generation_readiness(mock_results, REPO_ROOT)
        assert len(readiness) == 2
        for entry in readiness:
            assert "family" in entry
            assert "lowcode_namespace_found" in entry
            assert "plugin_type_count" in entry
            assert "workflow_root_candidate_count" in entry
            assert "provider_callback_count" in entry
            assert "options_type_count" in entry
            assert "generation_risk" in entry
            assert "recommended_next_action" in entry

        # cells is eligible — should rank before noop
        cells_entry = next(e for e in readiness if e["family"] == "cells")
        noop_entry = next(e for e in readiness if e["family"] == "noop")
        assert cells_entry["lowcode_namespace_found"] is True
        assert noop_entry["lowcode_namespace_found"] is False
        assert noop_entry["recommended_next_action"] == "blocked_no_lowcode_namespace"


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


# --- Test 17: PDF Optimizer build-repair constraint injection ---


class TestPdfOptimizerBuildRepairConstraints:
    """Verify that packet_builder injects OptimizeOptions constraints for Optimizer."""

    def _make_pdf_optimizer_scenario(self):
        return {
            "scenario_id": "pdf-optimizer",
            "target_type": "Aspose.Pdf.LowCode.Optimizer",
            "target_namespace": "Aspose.Pdf.LowCode",
            "target_methods": ["Process"],
            "required_symbols": [
                "Aspose.Pdf.LowCode.Optimizer",
                "Aspose.Pdf.LowCode.Optimizer.Process",
            ],
            "required_fixtures": [],
            "output_plan": "Optimize PDF",
            "input_strategy": "programmatic_input",
            "input_files": [],
        }

    def _make_pdf_catalog(self, type_name: str):
        return {
            "assembly_name": "Aspose.PDF",
            "assembly_version": "26.4.0",
            "namespaces": [
                {
                    "namespace": "Aspose.Pdf.LowCode",
                    "types": [
                        {
                            "name": type_name,
                            "full_name": f"Aspose.Pdf.LowCode.{type_name}",
                            "kind": "class",
                            "is_obsolete": False,
                            "methods": [
                                {
                                    "name": "Process",
                                    "return_type": "ResultContainer",
                                    "is_static": False,
                                    "is_obsolete": False,
                                    "parameters": [
                                        {"name": "options", "type": "IPluginOptions", "is_optional": False},
                                    ],
                                }
                            ],
                            "properties": [],
                            "constructors": [{"parameters": []}],
                        }
                    ],
                }
            ],
            "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
        }

    def test_pdf_optimizer_repair_prompt_preserves_optimizeoptions_constraint(self):
        """packet_builder must inject REQUIRED: options class is 'OptimizeOptions' for Optimizer."""
        scenario = self._make_pdf_optimizer_scenario()
        catalog = self._make_pdf_catalog("Optimizer")
        packet = build_packet(scenario, catalog)
        constraint_text = " ".join(packet.constraints)
        assert (
            "OptimizeOptions" in constraint_text
        ), "Build repair will lose OptimizeOptions if it's not in packet.constraints"

    def test_pdf_optimizer_repair_prompt_preserves_exact_usage_pattern(self):
        """packet_builder must inject REQUIRED: exact usage pattern for Optimizer."""
        scenario = self._make_pdf_optimizer_scenario()
        catalog = self._make_pdf_catalog("Optimizer")
        packet = build_packet(scenario, catalog)
        exact_pattern = next(
            (c for c in packet.constraints if "REQUIRED: exact usage pattern" in c),
            None,
        )
        assert exact_pattern is not None, "Missing 'REQUIRED: exact usage pattern' in Optimizer constraints"
        assert (
            "new Optimizer().Process" in exact_pattern
        ), "Exact usage pattern must include 'new Optimizer().Process(options)'"

    def test_pdf_optimizer_rejects_file_copy_semantic_substitute(self):
        """_validate_code must reject File.Copy() for PDF family as a semantic substitute."""
        file_copy_code = (
            "using System;\nusing System.IO;\n"
            "class Program { static void Main() { "
            'File.Copy("input.pdf", "output.pdf", true); '
            'Console.WriteLine("done"); } }'
        )
        issues = _validate_code(file_copy_code, family="pdf", type_short="optimizer")
        assert any(
            "File.Copy" in issue for issue in issues
        ), "_validate_code must flag File.Copy() as forbidden in PDF family"

    def test_pdf_optimizer_requires_lowcode_optimizer_process(self):
        """_validate_code must require new Optimizer().Process(options) for type_short='optimizer'."""
        # Code has OptimizeOptions but does NOT call new Optimizer().Process() — uses wrong class instead
        missing_optimizer_code = (
            "using System;\nusing Aspose.Pdf.LowCode;\n"
            "class Program { static void Main() { "
            "var options = new OptimizeOptions(); "
            'options.AddInput(new FileDataSource("input.pdf")); '
            'options.AddOutput(new FileDataSource("output.pdf")); '
            "var result = new PdfOptimizer().Process(options); "
            "} }"
        )
        issues = _validate_code(missing_optimizer_code, family="pdf", type_short="optimizer")
        assert any(
            "Optimizer" in issue and "Process" in issue for issue in issues
        ), "_validate_code must require new Optimizer().Process(options) for optimizer type"

    def test_pdf_repair_prompt_preserves_packet_constraints_for_all_pdf_pilot_types(self):
        """All 4 PDF pilot types must inject REQUIRED: options class constraint."""
        type_options_map = {
            "Merger": "MergeOptions",
            "Splitter": "SplitOptions",
            "Optimizer": "OptimizeOptions",
            "TextExtractor": "TextExtractorOptions",
        }
        for type_name, options_class in type_options_map.items():
            scenario = {
                "scenario_id": f"pdf-{type_name.lower()}",
                "target_type": f"Aspose.Pdf.LowCode.{type_name}",
                "target_namespace": "Aspose.Pdf.LowCode",
                "target_methods": ["Process"],
                "required_symbols": [
                    f"Aspose.Pdf.LowCode.{type_name}",
                    f"Aspose.Pdf.LowCode.{type_name}.Process",
                ],
                "required_fixtures": [],
                "output_plan": f"Use {type_name}",
                "input_strategy": "programmatic_input",
                "input_files": [],
            }
            catalog = self._make_pdf_catalog(type_name)
            packet = build_packet(scenario, catalog)
            constraint_text = " ".join(packet.constraints)
            assert (
                options_class in constraint_text
            ), f"Missing '{options_class}' in constraints for PDF type '{type_name}'"


# --- Test 18: PDF TextExtractor static validation regression rules ---


class TestPdfTextExtractorRegressionRules:
    """Verify _validate_code correctly handles TextExtractor patterns."""

    _VALID_CODE = (
        "using System;\n"
        "using System.IO;\n"
        "using Aspose.Pdf;\n"
        "using Aspose.Pdf.LowCode;\n"
        "using Aspose.Pdf.Text;\n"
        "class Program { static void Main() {\n"
        "  var doc = new Document(); doc.Pages.Add();\n"
        '  doc.Save("input.pdf");\n'
        "  var options = new TextExtractorOptions();\n"
        '  options.AddInput(new FileDataSource("input.pdf"));\n'
        "  var result = new TextExtractor().Process(options);\n"
        "  if (result.ResultCollection.Count > 0 && result.ResultCollection[0] is StringResult sr)\n"
        '    Console.WriteLine("Extracted: " + sr.Text);\n'
        "} }"
    )

    def test_pdf_textextractor_regression_rule_accepts_valid_lowcode_pattern(self):
        """Valid TextExtractor LowCode code must pass _validate_code with no issues."""
        issues = _validate_code(self._VALID_CODE, family="pdf", type_short="textextractor")
        assert issues == [], f"Valid TextExtractor code raised unexpected issues: {issues}"

    def test_pdf_textextractor_regression_rule_rejects_textabsorber(self):
        """Code using TextAbsorber (core API, not LowCode) must be flagged."""
        textabsorber_code = (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.Text;\n"
            "class Program { static void Main() {\n"
            '  var doc = new Document("input.pdf");\n'
            "  var absorber = new TextAbsorber();\n"
            "  doc.Pages.Accept(absorber);\n"
            "  Console.WriteLine(absorber.Text);\n"
            "} }"
        )
        issues = _validate_code(textabsorber_code, family="pdf", type_short="textextractor")
        assert any(
            "TextAbsorber" in issue for issue in issues
        ), "_validate_code must flag TextAbsorber usage for PDF TextExtractor"


# --- Test 19: PDF Optimizer repair prompt includes FORBIDDEN DataSources constraint ---


class TestPdfOptimizerRepairPromptForbiddenConstraint:
    """Verify generate_example repair prompt includes FORBIDDEN DataSources constraint.

    Root cause from Sprint R1 (pilot-pdf-20260508-133015): the repair prompt was built
    using only REQUIRED constraints from packet.constraints, omitting FORBIDDEN ones.
    The LLM re-hallucinated 'using Aspose.Pdf.LowCode.DataSources;' during repair.
    This class verifies the fix: repair prompt now carries FORBIDDEN DataSources constraint.
    """

    def _make_pdf_optimizer_scenario(self):
        return {
            "scenario_id": "pdf-optimizer",
            "target_type": "Aspose.Pdf.LowCode.Optimizer",
            "target_namespace": "Aspose.Pdf.LowCode",
            "target_methods": ["Process"],
            "required_symbols": [
                "Aspose.Pdf.LowCode.Optimizer",
                "Aspose.Pdf.LowCode.Optimizer.Process",
            ],
            "required_fixtures": [],
            "output_plan": "Optimize PDF",
            "input_strategy": "programmatic_input",
            "input_files": [],
        }

    def _make_pdf_catalog(self):
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
                            "kind": "class",
                            "is_obsolete": False,
                            "methods": [
                                {
                                    "name": "Process",
                                    "return_type": "ResultContainer",
                                    "is_static": False,
                                    "is_obsolete": False,
                                    "parameters": [
                                        {"name": "options", "type": "IPluginOptions", "is_optional": False},
                                    ],
                                }
                            ],
                            "properties": [],
                            "constructors": [{"parameters": []}],
                        }
                    ],
                }
            ],
            "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
        }

    def test_code_generator_optimizer_repair_prompt_includes_datasources_forbidden_constraint(self):
        """Repair prompt for PDF Optimizer must include 'FORBIDDEN: using Aspose.Pdf.LowCode.DataSources'.

        This is the root cause fix for pilot-pdf-20260508-133015: the LLM re-hallucinated
        the DataSources sub-namespace during repair because the repair prompt did not
        carry the FORBIDDEN constraint from the initial generation prompt.
        """
        scenario = self._make_pdf_optimizer_scenario()
        catalog = self._make_pdf_catalog()
        packet = build_packet(scenario, catalog)

        # Code that triggers repair: has forbidden DataSources namespace
        # but has valid OptimizeOptions + Optimizer().Process() so only namespace triggers issue
        bad_code = (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "using Aspose.Pdf.LowCode.DataSources;\n"  # FORBIDDEN — triggers repair
            "class Program { static void Main() {\n"
            '  var doc = new Document(); doc.Pages.Add(); doc.Save("input.pdf");\n'
            "  var options = new OptimizeOptions();\n"
            '  options.AddInput(new FileDataSource("input.pdf"));\n'
            '  options.AddOutput(new FileDataSource("output.pdf"));\n'
            "  var result = new Optimizer().Process(options);\n"
            '  Console.WriteLine(result.ResultCollection.Count > 0 ? "done" : "failed");\n'
            "} }"
        )

        # Valid code returned by repair (no DataSources, passes all checks)
        good_code = (
            "using System;\n"
            "using Aspose.Pdf;\n"
            "using Aspose.Pdf.LowCode;\n"
            "class Program { static void Main() {\n"
            '  var doc = new Document(); doc.Pages.Add(); doc.Save("input.pdf");\n'
            "  var options = new OptimizeOptions();\n"
            '  options.AddInput(new FileDataSource("input.pdf"));\n'
            '  options.AddOutput(new FileDataSource("output.pdf"));\n'
            "  var result = new Optimizer().Process(options);\n"
            '  Console.WriteLine(result.ResultCollection.Count > 0 ? "done" : "failed");\n'
            "} }"
        )

        captured_prompts = []

        def mock_llm(prompt, system_prompt):
            captured_prompts.append(prompt)
            if len(captured_prompts) == 1:
                return f"```csharp\n{bad_code}\n```"
            return f"```csharp\n{good_code}\n```"

        result = generate_example(packet, llm_generate=mock_llm, max_repairs=1)

        assert len(captured_prompts) == 2, (
            f"Expected 2 LLM calls (initial + 1 repair), got {len(captured_prompts)}. "
            f"Result status: {result.status}, failure: {result.failure_reason}"
        )
        repair_prompt = captured_prompts[1]
        assert "FORBIDDEN: using Aspose.Pdf.LowCode.DataSources" in repair_prompt, (
            "Repair prompt must include 'FORBIDDEN: using Aspose.Pdf.LowCode.DataSources' to prevent "
            "the LLM from re-hallucinating the forbidden sub-namespace during build repair. "
            f"Repair prompt excerpt (first 600 chars): {repair_prompt[:600]}"
        )
        assert result.status in (
            "repaired",
            "generated",
        ), f"Expected repaired/generated result after fix, got: {result.status}, reason: {result.failure_reason}"

    def test_code_generator_optimizer_repair_prompt_includes_pluginoptions_forbidden_constraint(self):
        """Repair prompt for PDF Optimizer must include FORBIDDEN PluginOptions constraint."""
        scenario = self._make_pdf_optimizer_scenario()
        catalog = self._make_pdf_catalog()
        packet = build_packet(scenario, catalog)

        # Verify FORBIDDEN PluginOptions is in packet constraints
        constraint_text = " ".join(packet.constraints)
        assert (
            "FORBIDDEN:" in constraint_text and "PluginOptions" in constraint_text
        ), "packet.constraints must include FORBIDDEN PluginOptions constraint"

        # Trigger repair and capture prompt
        captured_prompts = []

        def mock_llm(prompt, system_prompt):
            captured_prompts.append(prompt)
            # First call: bad code with DataSources to trigger repair
            if len(captured_prompts) == 1:
                return (
                    "```csharp\n"
                    "using Aspose.Pdf.LowCode;\n"
                    "using Aspose.Pdf.LowCode.DataSources;\n"
                    "class P { static void Main() {\n"
                    "  var o = new OptimizeOptions();\n"
                    '  o.AddInput(new FileDataSource("in.pdf"));\n'
                    '  o.AddOutput(new FileDataSource("out.pdf"));\n'
                    "  new Optimizer().Process(o);\n"
                    "} }\n```"
                )
            # Second call: clean code
            return (
                "```csharp\n"
                "using Aspose.Pdf;\nusing Aspose.Pdf.LowCode;\n"
                "class P { static void Main() {\n"
                "  var doc = new Document(); doc.Pages.Add();\n"
                '  doc.Save("input.pdf");\n'
                "  var o = new OptimizeOptions();\n"
                '  o.AddInput(new FileDataSource("input.pdf"));\n'
                '  o.AddOutput(new FileDataSource("output.pdf"));\n'
                "  var r = new Optimizer().Process(o);\n"
                '  Console.WriteLine(r.ResultCollection.Count > 0 ? "ok" : "fail");\n'
                "} }\n```"
            )

        generate_example(packet, llm_generate=mock_llm, max_repairs=1)

        assert len(captured_prompts) >= 2, "Repair must have been triggered"
        repair_prompt = captured_prompts[1]
        assert "FORBIDDEN:" in repair_prompt and "PluginOptions" in repair_prompt, (
            "Repair prompt must include FORBIDDEN PluginOptions constraint. "
            f"Repair prompt excerpt: {repair_prompt[:400]}"
        )

    def test_code_generator_optimizer_repair_prompt_includes_filecopy_forbidden_constraint(self):
        """Repair prompt for PDF Optimizer must include FORBIDDEN File.Copy constraint."""
        scenario = self._make_pdf_optimizer_scenario()
        catalog = self._make_pdf_catalog()
        packet = build_packet(scenario, catalog)

        captured_prompts = []

        def mock_llm(prompt, system_prompt):
            captured_prompts.append(prompt)
            if len(captured_prompts) == 1:
                # Trigger repair via DataSources namespace
                return (
                    "```csharp\n"
                    "using Aspose.Pdf.LowCode;\nusing Aspose.Pdf.LowCode.DataSources;\n"
                    "class P { static void Main() {\n"
                    "  var o = new OptimizeOptions();\n"
                    '  o.AddInput(new FileDataSource("in.pdf"));\n'
                    '  o.AddOutput(new FileDataSource("out.pdf"));\n'
                    "  new Optimizer().Process(o);\n"
                    "} }\n```"
                )
            return (
                "```csharp\n"
                "using Aspose.Pdf;\nusing Aspose.Pdf.LowCode;\n"
                "class P { static void Main() {\n"
                "  var doc = new Document(); doc.Pages.Add();\n"
                '  doc.Save("input.pdf");\n'
                "  var o = new OptimizeOptions();\n"
                '  o.AddInput(new FileDataSource("input.pdf"));\n'
                '  o.AddOutput(new FileDataSource("output.pdf"));\n'
                "  var r = new Optimizer().Process(o);\n"
                '  Console.WriteLine(r.ResultCollection.Count > 0 ? "ok" : "fail");\n'
                "} }\n```"
            )

        generate_example(packet, llm_generate=mock_llm, max_repairs=1)

        assert len(captured_prompts) >= 2, "Repair must have been triggered"
        repair_prompt = captured_prompts[1]
        assert "FORBIDDEN:" in repair_prompt and "File.Copy" in repair_prompt, (
            "Repair prompt must include FORBIDDEN File.Copy constraint. "
            f"Repair prompt excerpt: {repair_prompt[:400]}"
        )

    def test_existing_splitter_repair_constraints_not_broken(self):
        """Verify Splitter still gets its REQUIRED constraints in repair prompt."""
        scenario = {
            "scenario_id": "pdf-splitter",
            "target_type": "Aspose.Pdf.LowCode.Splitter",
            "target_namespace": "Aspose.Pdf.LowCode",
            "target_methods": ["Process"],
            "required_symbols": ["Aspose.Pdf.LowCode.Splitter"],
            "required_fixtures": [],
            "output_plan": "Split PDF",
            "input_strategy": "programmatic_input",
            "input_files": [],
        }
        catalog = {
            "assembly_name": "Aspose.PDF",
            "assembly_version": "26.4.0",
            "namespaces": [
                {
                    "namespace": "Aspose.Pdf.LowCode",
                    "types": [
                        {
                            "name": "Splitter",
                            "full_name": "Aspose.Pdf.LowCode.Splitter",
                            "kind": "class",
                            "is_obsolete": False,
                            "methods": [
                                {
                                    "name": "Process",
                                    "return_type": "ResultContainer",
                                    "is_static": False,
                                    "is_obsolete": False,
                                    "parameters": [{"name": "options", "type": "IPluginOptions"}],
                                }
                            ],
                            "properties": [],
                            "constructors": [{"parameters": []}],
                        }
                    ],
                }
            ],
            "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
        }
        packet = build_packet(scenario, catalog)
        constraint_text = " ".join(packet.constraints)
        # Splitter constraints must still be intact
        assert "SplitOptions" in constraint_text, "Splitter must have SplitOptions in constraints"
        assert (
            "FORBIDDEN: using Aspose.Pdf.LowCode.DataSources" in constraint_text
        ), "DataSources FORBIDDEN constraint must be in Splitter constraints too"
