"""Tests for TC-PSAL-02: min_examples_per_family enforcement in scenario planner."""

from __future__ import annotations

import pytest

from plugin_examples.scenario_planner.planner import PlanningResult, plan_scenarios_from_registry


def _make_registry_entry(*, slug, status="PROBE_CONFIRMED"):
    return {
        "family": "imaging",
        "plugin_slug": slug,
        "type_name": "Image",
        "namespace": "Aspose.Imaging",
        "method_name": "Save",
        "status": status,
        "candidate_methods": [],
        "selected_api_mapping": {},
        "operation_kind": "IMAGE_CONVERSION",
    }


class TestSufficiencyStatus:
    def test_sufficient_when_above_minimum(self):
        entries = [
            _make_registry_entry(slug="convert"),
            _make_registry_entry(slug="resize"),
            _make_registry_entry(slug="crop"),
        ]
        result = plan_scenarios_from_registry(
            family="imaging",
            registry_entries=entries,
            min_examples=3,
        )

        assert result.sufficiency_status == "SUFFICIENT"
        assert result.ready_count == 3

    def test_below_minimum_when_few_entries(self):
        entries = [_make_registry_entry(slug="convert")]
        result = plan_scenarios_from_registry(
            family="imaging",
            registry_entries=entries,
            min_examples=3,
        )

        assert result.sufficiency_status == "BELOW_MINIMUM"
        assert result.ready_count == 1

    def test_registry_incomplete_when_entries_exist_but_not_ready(self):
        entries = [
            _make_registry_entry(slug="convert", status="PROBE_CONFIRMED"),
            _make_registry_entry(slug="resize", status="WEBSITE_DISCOVERED"),
            _make_registry_entry(slug="crop", status="WEBSITE_DISCOVERED"),
        ]
        result = plan_scenarios_from_registry(
            family="imaging",
            registry_entries=entries,
            min_examples=3,
        )

        assert result.sufficiency_status == "REGISTRY_INCOMPLETE"
        assert result.ready_count == 1
        assert result.blocked_count == 2

    def test_min_examples_defaults_to_three(self):
        entries = [_make_registry_entry(slug="convert")]
        result = plan_scenarios_from_registry(
            family="imaging",
            registry_entries=entries,
        )

        assert result.min_examples_required == 3

    def test_total_registry_entries_tracked(self):
        entries = [
            _make_registry_entry(slug="a"),
            _make_registry_entry(slug="b"),
            _make_registry_entry(slug="c", status="UNKNOWN"),
        ]
        result = plan_scenarios_from_registry(
            family="test",
            registry_entries=entries,
            min_examples=3,
        )

        assert result.total_registry_entries == 3

    def test_empty_registry(self):
        result = plan_scenarios_from_registry(
            family="empty",
            registry_entries=[],
            min_examples=3,
        )

        assert result.sufficiency_status == "BELOW_MINIMUM"
        assert result.ready_count == 0
        assert result.total_registry_entries == 0
