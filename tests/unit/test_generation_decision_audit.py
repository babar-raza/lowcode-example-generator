"""Unit tests for generation decision audit — TC-AUDIT-001."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from plugin_examples.generator.decision_audit import (
    _count_strategies,
    write_generation_decision_audit,
)


def _make_ctx(tmp_path: Path, projects: list[dict] | None = None):
    """Build a minimal context for audit testing."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    ctx = SimpleNamespace(
        family="cells",
        run_id="test-run-001",
        evidence_dir=evidence_dir,
        llm_available=True,
        generated_projects=projects or [],
    )
    return ctx


class TestWriteGenerationDecisionAudit:
    def test_writes_audit_json(self, tmp_path):
        projects = [
            {
                "scenario_id": "cells-converter",
                "type_name": "SpreadsheetConverter",
                "operation_kind": "converter",
                "generation_strategy": "template_first",
                "template_first_eligible": True,
                "status": "generated_template_first",
            },
            {
                "scenario_id": "cells-merger",
                "type_name": "SpreadsheetMerger",
                "operation_kind": "merger",
                "generation_strategy": "llm_generated",
                "template_first_eligible": False,
                "status": "generated",
            },
        ]
        ctx = _make_ctx(tmp_path, projects)
        path = write_generation_decision_audit(ctx)
        assert path is not None
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["audit_type"] == "generation_decision"
        assert data["total_scenarios"] == 2
        assert data["strategy_counts"]["template_first"] == 1
        assert data["strategy_counts"]["llm_generated"] == 1
        assert len(data["records"]) == 2

    def test_returns_none_when_no_projects(self, tmp_path):
        ctx = _make_ctx(tmp_path, [])
        assert write_generation_decision_audit(ctx) is None

    def test_audit_record_has_required_fields(self, tmp_path):
        projects = [{
            "scenario_id": "cells-conv",
            "generation_strategy": "catalog_fallback",
            "status": "generated",
        }]
        ctx = _make_ctx(tmp_path, projects)
        path = write_generation_decision_audit(ctx)
        data = json.loads(path.read_text(encoding="utf-8"))
        record = data["records"][0]
        assert "scenario_id" in record
        assert "family" in record
        assert "generation_strategy" in record
        assert "llm_available" in record


class TestCountStrategies:
    def test_counts_correctly(self):
        records = [
            {"generation_strategy": "template_first"},
            {"generation_strategy": "llm_generated"},
            {"generation_strategy": "template_first"},
        ]
        counts = _count_strategies(records)
        assert counts == {"template_first": 2, "llm_generated": 1}
