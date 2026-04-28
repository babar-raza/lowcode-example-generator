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
                             "is_static": True, "is_obsolete": False, "parameters": []},
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
            example, package_id="Aspose.Cells",
            output_dir=tmp_path / "generated",
        )
        csproj = Path(result["csproj_path"]).read_text()
        assert "Aspose.Cells" in csproj
        assert 'Version="' not in csproj  # No inline version


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
