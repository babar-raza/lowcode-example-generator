"""Tests for plugin_examples.policy.loader — YAML policy/goal/SLO loading."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from plugin_examples.policy.loader import (
    GatePolicy,
    GoalSpec,
    SLODefinition,
    load_gate_policy,
    load_goals,
    load_slos,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# load_gate_policy
# ---------------------------------------------------------------------------


class TestLoadGatePolicy:
    def test_loads_from_yaml(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "pipeline" / "policies" / "gates.yml", {
            "hard_stop_stages": ["load_config", "nuget_fetch"],
            "approval_gated_types": ["MERGE_READY_PR"],
            "publishable_verdicts": ["PR_READY"],
            "deprioritization": {
                "consecutive_failure_threshold": 5,
                "cooldown_runs": 3,
            },
        })
        policy = load_gate_policy(tmp_path)
        assert policy.hard_stop_stages == frozenset({"load_config", "nuget_fetch"})
        assert policy.approval_gated_types == frozenset({"MERGE_READY_PR"})
        assert policy.publishable_verdicts == frozenset({"PR_READY"})
        assert policy.deprioritization_threshold == 5
        assert policy.deprioritization_cooldown == 3

    def test_returns_defaults_when_file_missing(self, tmp_path: Path) -> None:
        policy = load_gate_policy(tmp_path)
        assert "MERGE_READY_PR" in policy.approval_gated_types
        assert "load_config" in policy.hard_stop_stages
        assert policy.deprioritization_threshold == 3

    def test_returns_defaults_on_invalid_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "pipeline" / "policies" / "gates.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{{invalid yaml", encoding="utf-8")
        policy = load_gate_policy(tmp_path)
        assert "MERGE_READY_PR" in policy.approval_gated_types

    def test_empty_yaml_returns_empty_sets(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "pipeline" / "policies" / "gates.yml", {})
        policy = load_gate_policy(tmp_path)
        assert policy.hard_stop_stages == frozenset()
        assert policy.approval_gated_types == frozenset()

    def test_loads_from_real_project(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / "pipeline" / "policies" / "gates.yml"
        if not path.exists():
            pytest.skip("gates.yml not present in project")
        policy = load_gate_policy(repo_root)
        assert len(policy.approval_gated_types) >= 1
        assert len(policy.hard_stop_stages) >= 1


# ---------------------------------------------------------------------------
# load_goals
# ---------------------------------------------------------------------------


class TestLoadGoals:
    def test_loads_goals_from_yaml(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "pipeline" / "configs" / "goals.yml", {
            "goals": [
                {"id": "g1", "metric": "build_pass_rate", "threshold": 0.9, "weight": 3, "description": "test"},
                {"id": "g2", "metric": "evidence_chain_pass_rate", "threshold": 1.0, "weight": 1},
            ],
        })
        goals = load_goals(tmp_path)
        assert len(goals) == 2
        assert goals[0].id == "g1"
        assert goals[0].threshold == 0.9
        assert goals[0].weight == 3
        assert goals[1].description == ""

    def test_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        goals = load_goals(tmp_path)
        assert goals == []

    def test_returns_empty_on_invalid_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "pipeline" / "configs" / "goals.yml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{{bad", encoding="utf-8")
        goals = load_goals(tmp_path)
        assert goals == []

    def test_goal_to_dict(self) -> None:
        g = GoalSpec(id="test", metric="m", threshold=0.5, weight=2, description="d")
        d = g.to_dict()
        assert d["id"] == "test"
        assert d["threshold"] == 0.5

    def test_loads_from_real_project(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / "pipeline" / "configs" / "goals.yml"
        if not path.exists():
            pytest.skip("goals.yml not present in project")
        goals = load_goals(repo_root)
        assert len(goals) >= 1
        assert all(g.id for g in goals)


# ---------------------------------------------------------------------------
# load_slos
# ---------------------------------------------------------------------------


class TestLoadSLOs:
    def test_loads_slos_from_yaml(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "pipeline" / "configs" / "slo.yml", {
            "slos": [
                {"id": "s1", "metric": "build_pass_rate", "target": 0.95, "window_runs": 10, "severity": "critical"},
            ],
        })
        slos = load_slos(tmp_path)
        assert len(slos) == 1
        assert slos[0].id == "s1"
        assert slos[0].target == 0.95
        assert slos[0].severity == "critical"

    def test_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        slos = load_slos(tmp_path)
        assert slos == []

    def test_slo_to_dict(self) -> None:
        s = SLODefinition(id="test", metric="m", target=0.9, window_runs=5, severity="info")
        d = s.to_dict()
        assert d["id"] == "test"
        assert d["window_runs"] == 5

    def test_default_severity(self, tmp_path: Path) -> None:
        _write_yaml(tmp_path / "pipeline" / "configs" / "slo.yml", {
            "slos": [{"id": "s1", "metric": "m", "target": 0.5, "window_runs": 3}],
        })
        slos = load_slos(tmp_path)
        assert slos[0].severity == "warning"

    def test_loads_from_real_project(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        path = repo_root / "pipeline" / "configs" / "slo.yml"
        if not path.exists():
            pytest.skip("slo.yml not present in project")
        slos = load_slos(repo_root)
        assert len(slos) >= 1
        assert all(s.id for s in slos)
