"""Tests for registry-based scenario planning (TC-P2-04).

Validates:
- plan_scenarios_from_registry creates ready scenarios from PROBE_CONFIRMED entries
- Non-ready entries (REFLECTION_CANDIDATE) are blocked
- Scenario fields are correctly populated from registry entries
- Empty entries produce zero ready scenarios
- Multiple entries produce multiple scenarios
- Real barcode.yaml produces valid scenarios (TC-H11)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from plugin_examples.scenario_planner.planner import (
    PlanningResult,
    plan_scenarios_from_registry,
)


def _make_entry(
    slug: str,
    status: str = "PROBE_CONFIRMED",
    type_name: str = "BarcodeGenerator",
    namespace: str = "Aspose.BarCode.Generation",
    method_name: str = "Save",
    operation_kind: str = "BARCODE_GENERATION",
) -> dict:
    return {
        "plugin_slug": slug,
        "status": status,
        "type_name": type_name,
        "namespace": namespace,
        "method_name": method_name,
        "operation_kind": operation_kind,
        "candidate_methods": [method_name],
        "selected_api_mapping": {
            "type_name": type_name,
            "namespace": namespace,
            "method_name": method_name,
            "constructor": f"{type_name}(EncodeTypes, string)",
        },
    }


class TestPlanFromRegistry:
    def test_creates_scenarios_from_probe_confirmed(self) -> None:
        entries = [_make_entry("generate-barcode")]
        result = plan_scenarios_from_registry(family="barcode", registry_entries=entries)

        assert isinstance(result, PlanningResult)
        assert result.ready_count == 1
        assert result.blocked_count == 0
        assert result.ready_scenarios[0].status == "ready"

    def test_blocks_non_ready_entries(self) -> None:
        entries = [_make_entry("recognize-barcode", status="REFLECTION_CANDIDATE")]
        result = plan_scenarios_from_registry(family="barcode", registry_entries=entries)

        assert result.ready_count == 0
        assert result.blocked_count == 1
        assert result.blocked_scenarios[0].status == "blocked_probe_pending"

    def test_scenario_fields_correct(self) -> None:
        entries = [_make_entry("generate-barcode")]
        result = plan_scenarios_from_registry(family="barcode", registry_entries=entries)

        scenario = result.ready_scenarios[0]
        assert scenario.scenario_id == "barcode-generate-barcode"
        assert scenario.target_type == "Aspose.BarCode.Generation.BarcodeGenerator"
        assert scenario.target_namespace == "Aspose.BarCode.Generation"
        assert "Save" in scenario.target_methods
        assert scenario.input_strategy == "programmatic_input"

    def test_empty_entries_zero_ready(self) -> None:
        result = plan_scenarios_from_registry(family="barcode", registry_entries=[])

        assert result.ready_count == 0
        assert result.blocked_count == 0

    def test_multiple_entries(self) -> None:
        entries = [
            _make_entry("generate-barcode"),
            _make_entry(
                "generate-qr-code",
                type_name="BarcodeGenerator",
                operation_kind="QR_CODE_GENERATION",
            ),
            _make_entry("recognize-barcode", status="REFLECTION_CANDIDATE"),
        ]
        result = plan_scenarios_from_registry(family="barcode", registry_entries=entries)

        assert result.ready_count == 2
        assert result.blocked_count == 1

    def test_verified_publishable_is_ready(self) -> None:
        entries = [_make_entry("generate-barcode", status="VERIFIED_PUBLISHABLE")]
        result = plan_scenarios_from_registry(family="barcode", registry_entries=entries)

        assert result.ready_count == 1
        assert result.ready_scenarios[0].status == "ready"

    def test_probe_failed_is_blocked(self) -> None:
        entries = [_make_entry("generate-barcode", status="PROBE_FAILED")]
        result = plan_scenarios_from_registry(family="barcode", registry_entries=entries)

        assert result.ready_count == 0
        assert result.blocked_count == 1


class TestRealRegistryYaml:
    """TC-H11: Verify plan_scenarios_from_registry works with real barcode.yaml."""

    _REAL_REGISTRY = Path(__file__).resolve().parents[2] / "pipeline" / "plugin-capability-registry" / "barcode.yaml"

    @pytest.mark.skipif(
        not (Path(__file__).resolve().parents[2] / "pipeline" / "plugin-capability-registry" / "barcode.yaml").exists(),
        reason="Real barcode.yaml not found (running outside repo root)",
    )
    def test_real_barcode_yaml_produces_scenarios(self) -> None:
        with open(self._REAL_REGISTRY, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        entries = data.get("entries", [])
        assert len(entries) >= 1, "barcode.yaml should have at least 1 entry"

        result = plan_scenarios_from_registry(family="barcode", registry_entries=entries)

        # At least the generate-barcode entry is PROBE_CONFIRMED
        assert result.ready_count >= 1, f"Expected >=1 ready scenarios, got {result.ready_count}"
        scenario_ids = [s.scenario_id for s in result.ready_scenarios]
        assert "barcode-generate-barcode" in scenario_ids

        # Verify scenario fields from real data
        gen_scenario = next(s for s in result.ready_scenarios if s.scenario_id == "barcode-generate-barcode")
        assert gen_scenario.target_type == "Aspose.BarCode.Generation.BarcodeGenerator"
        assert gen_scenario.target_namespace == "Aspose.BarCode.Generation"
        assert "Save" in gen_scenario.target_methods
