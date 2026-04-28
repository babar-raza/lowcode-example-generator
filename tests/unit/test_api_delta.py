"""Unit tests for api_delta: delta_engine, impact_mapper."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.api_delta.delta_engine import (
    DeltaResult,
    compute_delta,
    write_delta_report,
)
from plugin_examples.api_delta.impact_mapper import (
    ImpactReport,
    map_impact,
    write_impact_report,
)


def _make_catalog(version: str = "1.0.0.0", types: list[dict] | None = None) -> dict:
    """Create a test catalog."""
    if types is None:
        types = [
            {
                "name": "Converter",
                "full_name": "Aspose.Cells.LowCode.Converter",
                "kind": "class",
                "is_obsolete": False,
                "methods": [
                    {"name": "Process", "return_type": "void", "is_static": True,
                     "is_obsolete": False, "parameters": []},
                ],
                "properties": [
                    {"name": "Options", "type": "ConvertOptions", "can_read": True,
                     "can_write": True, "is_obsolete": False},
                ],
                "constructors": [],
            },
        ]
    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": version,
        "namespaces": [{"namespace": "Aspose.Cells.LowCode", "types": types}],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


class TestDeltaEngine:
    def test_initial_run_all_added(self):
        catalog = _make_catalog()
        delta = compute_delta(catalog)
        assert delta.initial_run is True
        assert len(delta.added_types) == 1
        assert delta.added_types[0].full_name == "Aspose.Cells.LowCode.Converter"
        assert delta.has_changes

    def test_no_change_returns_empty(self):
        c1 = _make_catalog("1.0.0")
        c2 = _make_catalog("1.0.0")
        delta = compute_delta(c2, c1)
        assert not delta.has_changes
        assert delta.total_changes == 0

    def test_added_type_detected(self):
        old = _make_catalog("1.0.0")
        new_types = old["namespaces"][0]["types"] + [{
            "name": "Merger", "full_name": "Aspose.Cells.LowCode.Merger",
            "kind": "class", "is_obsolete": False,
            "methods": [{"name": "Merge", "return_type": "void", "is_static": True,
                         "is_obsolete": False, "parameters": []}],
            "properties": [], "constructors": [],
        }]
        new = _make_catalog("2.0.0", new_types)
        delta = compute_delta(new, old)
        assert len(delta.added_types) == 1
        assert delta.added_types[0].full_name == "Aspose.Cells.LowCode.Merger"

    def test_removed_type_detected(self):
        old = _make_catalog("1.0.0")
        new = _make_catalog("2.0.0", [])  # empty types
        delta = compute_delta(new, old)
        assert len(delta.removed_types) == 1

    def test_modified_type_detected(self):
        old = _make_catalog("1.0.0")
        modified_types = [{
            "name": "Converter", "full_name": "Aspose.Cells.LowCode.Converter",
            "kind": "class", "is_obsolete": False,
            "methods": [
                {"name": "Process", "return_type": "void", "is_static": True,
                 "is_obsolete": False, "parameters": []},
                {"name": "ProcessAsync", "return_type": "Task", "is_static": True,
                 "is_obsolete": False, "parameters": []},
            ],
            "properties": [
                {"name": "Options", "type": "ConvertOptions", "can_read": True,
                 "can_write": True, "is_obsolete": False},
            ],
            "constructors": [],
        }]
        new = _make_catalog("2.0.0", modified_types)
        delta = compute_delta(new, old)
        assert len(delta.modified_types) == 1
        assert "ProcessAsync" in delta.modified_types[0].added_methods

    def test_write_delta_report(self, tmp_path):
        delta = compute_delta(_make_catalog())
        path = write_delta_report(delta, tmp_path / "workspace" / "verification")
        assert path.exists()
        with open(path) as f:
            report = json.load(f)
        assert report["initial_run"] is True
        assert "workspace" in str(path)
        assert "verification" in str(path)


class TestImpactMapper:
    def test_initial_run_all_new(self):
        delta = compute_delta(_make_catalog())
        impact = map_impact(delta)
        assert impact.initial_run
        assert len(impact.new_api_examples_needed) == 1

    def test_removed_type_impacts_example(self):
        old = _make_catalog("1.0.0")
        new = _make_catalog("2.0.0", [])
        delta = compute_delta(new, old)
        existing = {
            "examples": [
                {"example_id": "ex1", "used_symbols": ["Aspose.Cells.LowCode.Converter"]},
            ]
        }
        impact = map_impact(delta, existing)
        assert len(impact.existing_example_impacts) == 1
        assert impact.existing_example_impacts[0].action == "deprecate"

    def test_modified_type_impacts_example(self):
        old = _make_catalog("1.0.0")
        modified = [{
            "name": "Converter", "full_name": "Aspose.Cells.LowCode.Converter",
            "kind": "class", "is_obsolete": False,
            "methods": [], "properties": [], "constructors": [],
        }]
        new = _make_catalog("2.0.0", modified)
        delta = compute_delta(new, old)
        existing = {
            "examples": [
                {"example_id": "ex1", "used_symbols": ["Aspose.Cells.LowCode.Converter"]},
            ]
        }
        impact = map_impact(delta, existing)
        assert len(impact.existing_example_impacts) == 1
        assert impact.existing_example_impacts[0].action == "update"

    def test_no_impact_unaffected_example(self):
        old = _make_catalog("1.0.0")
        new_types = old["namespaces"][0]["types"] + [{
            "name": "Merger", "full_name": "Aspose.Cells.LowCode.Merger",
            "kind": "class", "is_obsolete": False,
            "methods": [], "properties": [], "constructors": [],
        }]
        new = _make_catalog("2.0.0", new_types)
        delta = compute_delta(new, old)
        existing = {
            "examples": [
                {"example_id": "ex1", "used_symbols": ["Aspose.Cells.LowCode.Converter"]},
            ]
        }
        impact = map_impact(delta, existing)
        assert len(impact.existing_example_impacts) == 0

    def test_write_impact_report(self, tmp_path):
        delta = compute_delta(_make_catalog())
        impact = map_impact(delta)
        path = write_impact_report(impact, tmp_path / "workspace" / "verification")
        assert path.exists()
        assert "workspace" in str(path)
