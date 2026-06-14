"""Tests for stage I/O contracts — TC-S4-04."""

from __future__ import annotations

import json

import pytest

from plugin_examples.contracts.stage_contracts import (
    CONTRACTS_BY_NAME,
    STAGE_CONTRACTS,
    StageContract,
    check_contract_consistency,
    get_cumulative_produces,
)

# ---------------------------------------------------------------------------
# Contract consistency tests
# ---------------------------------------------------------------------------


class TestContractConsistency:
    """Verify every stage's requires are produced by a prior stage."""

    def test_no_consistency_errors(self):
        errors = check_contract_consistency()
        assert errors == [], f"Contract consistency errors: {errors}"

    @pytest.mark.parametrize("contract", STAGE_CONTRACTS, ids=lambda c: c.stage_name)
    def test_each_stage_requires_are_available(self, contract: StageContract):
        available = get_cumulative_produces(contract.order - 1)
        missing = contract.requires - available
        assert not missing, (
            f"Stage '{contract.stage_name}' requires {sorted(missing)} "
            f"but they are not produced by any prior stage"
        )

    @pytest.mark.parametrize("contract", STAGE_CONTRACTS, ids=lambda c: c.stage_name)
    def test_each_stage_produces_something(self, contract: StageContract):
        assert contract.produces, f"Stage '{contract.stage_name}' produces nothing"

    @pytest.mark.parametrize("contract", STAGE_CONTRACTS, ids=lambda c: c.stage_name)
    def test_each_stage_requires_something(self, contract: StageContract):
        assert contract.requires, f"Stage '{contract.stage_name}' requires nothing"

    def test_no_circular_dependencies(self):
        """Verify stages are strictly ordered — no stage reads its own output."""
        for contract in STAGE_CONTRACTS:
            overlap = contract.requires & contract.produces
            assert not overlap, (
                f"Stage '{contract.stage_name}' both requires and produces: {sorted(overlap)}"
            )


# ---------------------------------------------------------------------------
# Contract shape tests
# ---------------------------------------------------------------------------


class TestContractShape:
    """Verify contracts have valid structure."""

    def test_all_critical_path_stages_covered(self):
        expected = {
            "load_config", "nuget_fetch", "extraction", "reflection",
            "plugin_detection", "scenario_planning", "generation", "validation",
        }
        actual = {c.stage_name for c in STAGE_CONTRACTS}
        assert expected == actual

    def test_stages_are_ordered(self):
        orders = [c.order for c in STAGE_CONTRACTS]
        assert orders == sorted(orders), "STAGE_CONTRACTS must be in execution order"

    def test_no_duplicate_stage_names(self):
        names = [c.stage_name for c in STAGE_CONTRACTS]
        assert len(names) == len(set(names)), f"Duplicate stage names: {names}"

    def test_no_duplicate_orders(self):
        orders = [c.order for c in STAGE_CONTRACTS]
        assert len(orders) == len(set(orders)), f"Duplicate orders: {orders}"

    @pytest.mark.parametrize("contract", STAGE_CONTRACTS, ids=lambda c: c.stage_name)
    def test_requires_are_frozenset(self, contract: StageContract):
        assert isinstance(contract.requires, frozenset)

    @pytest.mark.parametrize("contract", STAGE_CONTRACTS, ids=lambda c: c.stage_name)
    def test_produces_are_frozenset(self, contract: StageContract):
        assert isinstance(contract.produces, frozenset)

    @pytest.mark.parametrize("contract", STAGE_CONTRACTS, ids=lambda c: c.stage_name)
    def test_optional_reads_are_frozenset(self, contract: StageContract):
        assert isinstance(contract.optional_reads, frozenset)


# ---------------------------------------------------------------------------
# Contract field validation against PipelineContext
# ---------------------------------------------------------------------------


class TestContractFieldsMatchContext:
    """Verify contract fields correspond to real PipelineContext attributes."""

    def test_all_produced_fields_are_context_attributes(self):
        from plugin_examples.runner import PipelineContext
        ctx_fields = set(PipelineContext.__dataclass_fields__.keys())
        for contract in STAGE_CONTRACTS:
            for field_name in contract.produces:
                assert field_name in ctx_fields, (
                    f"Stage '{contract.stage_name}' produces '{field_name}' "
                    f"which is not a PipelineContext field"
                )

    def test_all_required_fields_are_context_attributes_or_init(self):
        from plugin_examples.runner import PipelineContext
        ctx_fields = set(PipelineContext.__dataclass_fields__.keys())
        for contract in STAGE_CONTRACTS:
            for field_name in contract.requires:
                assert field_name in ctx_fields, (
                    f"Stage '{contract.stage_name}' requires '{field_name}' "
                    f"which is not a PipelineContext field"
                )


# ---------------------------------------------------------------------------
# Cumulative produces
# ---------------------------------------------------------------------------


class TestCumulativeProduces:
    """Verify cumulative produces logic."""

    def test_order_0_has_init_fields(self):
        available = get_cumulative_produces(0)
        assert "family" in available
        assert "repo_root" in available
        assert "evidence_dir" in available

    def test_order_1_includes_config(self):
        available = get_cumulative_produces(1)
        assert "config" in available

    def test_order_5_includes_catalog(self):
        available = get_cumulative_produces(5)
        assert "catalog" in available
        assert "catalog_path" in available

    def test_final_order_includes_validation_results(self):
        max_order = max(c.order for c in STAGE_CONTRACTS)
        available = get_cumulative_produces(max_order)
        assert "validation_results" in available
        assert "generated_projects" in available


# ---------------------------------------------------------------------------
# Contract registry lookup
# ---------------------------------------------------------------------------


class TestContractRegistry:
    """Verify CONTRACTS_BY_NAME registry."""

    def test_registry_has_all_stages(self):
        assert len(CONTRACTS_BY_NAME) == len(STAGE_CONTRACTS)

    def test_lookup_by_name(self):
        c = CONTRACTS_BY_NAME["load_config"]
        assert c.stage_name == "load_config"
        assert "config" in c.produces

    def test_registry_is_frozen(self):
        c = CONTRACTS_BY_NAME["reflection"]
        assert isinstance(c, StageContract)
        assert c.produces == frozenset({"catalog", "catalog_path"})


# ---------------------------------------------------------------------------
# Snapshot regression guard
# ---------------------------------------------------------------------------


class TestContractSnapshot:
    """Verify contract definitions match known snapshot."""

    def test_contract_snapshot_matches(self):
        snapshot = [
            {"name": c.stage_name, "order": c.order,
             "requires": sorted(c.requires), "produces": sorted(c.produces)}
            for c in STAGE_CONTRACTS
        ]
        # If this test fails, review the change and update this snapshot
        expected = [
            {"name": "load_config", "order": 1, "requires": ["family"], "produces": ["config"]},
            {"name": "nuget_fetch", "order": 2, "requires": ["config"], "produces": ["download_manifest"]},
            {"name": "extraction", "order": 4, "requires": ["config", "download_manifest"], "produces": ["extraction"]},
            {"name": "reflection", "order": 5, "requires": ["extraction"], "produces": ["catalog", "catalog_path"]},
            {"name": "plugin_detection", "order": 6, "requires": ["catalog", "config"], "produces": ["detection", "proof_path"]},
            {"name": "scenario_planning", "order": 12, "requires": ["catalog", "config", "detection"], "produces": ["planning"]},
            {"name": "generation", "order": 14, "requires": ["catalog", "config", "planning"], "produces": ["generated_projects", "lifecycle_registry"]},
            {"name": "validation", "order": 15, "requires": ["generated_projects"], "produces": ["validation_results"]},
        ]
        assert snapshot == expected
