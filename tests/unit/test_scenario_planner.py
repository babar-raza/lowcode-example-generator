"""Unit tests for scenario_planner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.plugin_detector.proof_reporter import SourceOfTruthGateError
from plugin_examples.scenario_planner.planner import (
    PlanningResult,
    Scenario,
    plan_scenarios,
)
from plugin_examples.scenario_planner.scenario_catalog import (
    write_blocked_scenarios,
    write_scenario_catalog,
)


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
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "void", "is_static": True,
                             "is_obsolete": False, "parameters": []},
                        ],
                        "properties": [],
                        "constructors": [],
                    },
                    {
                        "name": "PdfConverter",
                        "full_name": "Aspose.Cells.LowCode.PdfConverter",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [
                            {"name": "Convert", "return_type": "void", "is_static": True,
                             "is_obsolete": False, "parameters": []},
                            {"name": "ConvertAsync", "return_type": "Task", "is_static": True,
                             "is_obsolete": False, "parameters": []},
                        ],
                        "properties": [],
                        "constructors": [],
                    },
                    {
                        "name": "JsonConverter",
                        "full_name": "Aspose.Cells.LowCode.JsonConverter",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "void", "is_static": True,
                             "is_obsolete": False, "parameters": []},
                        ],
                        "properties": [],
                        "constructors": [],
                    },
                    {
                        "name": "ObsoleteHelper",
                        "full_name": "Aspose.Cells.LowCode.ObsoleteHelper",
                        "kind": "class",
                        "is_obsolete": True,
                        "methods": [
                            {"name": "DoStuff", "return_type": "void", "is_static": True,
                             "is_obsolete": True, "parameters": []},
                        ],
                        "properties": [],
                        "constructors": [],
                    },
                    {
                        "name": "EmptyType",
                        "full_name": "Aspose.Cells.LowCode.EmptyType",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [],
                        "properties": [],
                        "constructors": [],
                    },
                    {
                        "name": "SaveFormat",
                        "full_name": "Aspose.Cells.LowCode.SaveFormat",
                        "kind": "enum",
                        "is_obsolete": False,
                        "enum_values": [
                            {"name": "Xlsx", "is_obsolete": False},
                            {"name": "Pdf", "is_obsolete": False},
                        ],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


def _make_proof(tmp_path: Path, eligible: bool = True) -> str:
    """Write a proof file and return its path."""
    proof_path = tmp_path / "proof.json"
    proof_path.write_text(json.dumps({
        "eligibility_status": "eligible" if eligible else "not_eligible",
        "eligibility_reason": "test",
    }))
    return str(proof_path)


class TestScenarioPlanner:
    def test_ready_scenarios_from_catalog(self, tmp_path):
        proof = _make_proof(tmp_path)
        result = plan_scenarios(
            family="cells",
            catalog=_make_catalog(),
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        assert result.ready_count >= 3  # SpreadsheetLocker, PdfConverter, JsonConverter

    def test_obsolete_types_blocked(self, tmp_path):
        proof = _make_proof(tmp_path)
        result = plan_scenarios(
            family="cells",
            catalog=_make_catalog(),
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        blocked_ids = [s.scenario_id for s in result.blocked_scenarios]
        assert any("obsolete" in bid.lower() for bid in blocked_ids)

    def test_empty_type_blocked_unclear(self, tmp_path):
        proof = _make_proof(tmp_path)
        result = plan_scenarios(
            family="cells",
            catalog=_make_catalog(),
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        blocked_statuses = [s.status for s in result.blocked_scenarios]
        assert "blocked_unclear_semantics" in blocked_statuses

    def test_enums_skipped(self, tmp_path):
        proof = _make_proof(tmp_path)
        result = plan_scenarios(
            family="cells",
            catalog=_make_catalog(),
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        all_types = [s.target_type for s in result.ready_scenarios + result.blocked_scenarios]
        assert "Aspose.Cells.LowCode.SaveFormat" not in all_types

    def test_required_symbols_populated(self, tmp_path):
        proof = _make_proof(tmp_path)
        result = plan_scenarios(
            family="cells",
            catalog=_make_catalog(),
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        for s in result.ready_scenarios:
            assert len(s.required_symbols) > 0
            assert s.target_type in s.required_symbols

    def test_only_plugin_namespaces_planned(self, tmp_path):
        proof = _make_proof(tmp_path)
        catalog = _make_catalog()
        catalog["namespaces"].append({
            "namespace": "Aspose.Cells",
            "types": [{"name": "Workbook", "full_name": "Aspose.Cells.Workbook",
                        "kind": "class", "is_obsolete": False,
                        "methods": [{"name": "Save", "return_type": "void",
                                     "is_static": False, "is_obsolete": False, "parameters": []}],
                        "properties": [], "constructors": []}],
        })
        result = plan_scenarios(
            family="cells",
            catalog=catalog,
            plugin_namespaces=["Aspose.Cells.LowCode"],
            source_of_truth_proof_path=proof,
        )
        for s in result.ready_scenarios:
            assert s.target_namespace == "Aspose.Cells.LowCode"

    def test_proof_gate_fails_not_eligible(self, tmp_path):
        proof = _make_proof(tmp_path, eligible=False)
        with pytest.raises(SourceOfTruthGateError):
            plan_scenarios(
                family="cells",
                catalog=_make_catalog(),
                plugin_namespaces=["Aspose.Cells.LowCode"],
                source_of_truth_proof_path=proof,
            )

    def test_proof_gate_fails_missing(self):
        with pytest.raises(SourceOfTruthGateError):
            plan_scenarios(
                family="cells",
                catalog=_make_catalog(),
                plugin_namespaces=["Aspose.Cells.LowCode"],
                source_of_truth_proof_path="/nonexistent/proof.json",
            )

    def test_no_proof_path_skips_gate(self):
        # Should work without proof path (no gate check)
        result = plan_scenarios(
            family="cells",
            catalog=_make_catalog(),
            plugin_namespaces=["Aspose.Cells.LowCode"],
        )
        assert result.ready_count >= 3


class TestScenarioCatalogWriter:
    def test_write_scenario_catalog(self, tmp_path):
        result = PlanningResult(
            family="cells",
            ready_scenarios=[
                Scenario(scenario_id="cells-test", title="Test", target_type="T",
                         target_namespace="NS", status="ready"),
            ],
        )
        path = write_scenario_catalog(result, tmp_path / "workspace" / "manifests")
        assert path.exists()
        assert path.name == "scenario-catalog.json"
        with open(path) as f:
            data = json.load(f)
        assert data["ready_count"] == 1

    def test_write_blocked_scenarios(self, tmp_path):
        result = PlanningResult(
            family="cells",
            blocked_scenarios=[
                Scenario(scenario_id="cells-blocked", title="Blocked", target_type="T",
                         target_namespace="NS", status="blocked_obsolete",
                         blocked_reason="Obsolete"),
            ],
        )
        path = write_blocked_scenarios(result, tmp_path / "workspace" / "verification")
        assert path.exists()
        assert "blocked-scenarios" in path.name
        with open(path) as f:
            data = json.load(f)
        assert data["blocked_count"] == 1

    def test_paths_use_workspace(self, tmp_path):
        result = PlanningResult(family="cells")
        cat_path = write_scenario_catalog(result, tmp_path / "workspace" / "manifests")
        blk_path = write_blocked_scenarios(result, tmp_path / "workspace" / "verification")
        assert "workspace" in str(cat_path)
        assert "workspace" in str(blk_path)
