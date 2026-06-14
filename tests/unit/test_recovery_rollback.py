"""Recovery and rollback tests — verify graceful degradation under corrupted or missing state.

These tests demonstrate P7-level resilient behavior: the system survives
corrupted inputs, missing files, and handler errors without crashing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestRunHistoryRecovery:
    def test_survives_corrupted_json(self, tmp_path: Path) -> None:
        """RunHistory.load() with invalid JSON returns empty history."""
        from plugin_examples.state.run_history import RunHistory

        history_file = tmp_path / "history.json"
        history_file.write_text("{{{NOT VALID JSON!!!", encoding="utf-8")
        history = RunHistory.load(history_file)
        assert history.records == []

    def test_survives_missing_file(self, tmp_path: Path) -> None:
        """RunHistory.load() with nonexistent path returns empty history."""
        from plugin_examples.state.run_history import RunHistory

        missing = tmp_path / "does-not-exist.json"
        history = RunHistory.load(missing)
        assert history.records == []


class TestPlannerLoopRecovery:
    def test_loop_result_default_metrics(self) -> None:
        """LoopResult starts with zeroed metrics."""
        from plugin_examples.planner_loop import LoopResult

        lr = LoopResult()
        assert lr.metrics.total_cycles == 0
        assert lr.metrics.handler_errors == 0
        assert lr.metrics.actions_executed == 0

    def test_loop_result_metrics_in_dict(self) -> None:
        """LoopResult.to_dict() includes metrics key."""
        from plugin_examples.planner_loop import LoopResult

        lr = LoopResult()
        d = lr.to_dict()
        assert "metrics" in d
        assert d["metrics"]["total_cycles"] == 0


class TestHealingLoaderRecovery:
    def test_handles_missing_directory(self, tmp_path: Path) -> None:
        """HealingIntelligenceLoader with nonexistent dir does not crash."""
        from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

        missing_dir = tmp_path / "nonexistent"
        loader = HealingIntelligenceLoader(registry_dir=missing_dir)
        # Should construct without crash; load() should not raise
        assert not loader.is_loaded()
        loader.load()
        # After load, failure patterns should be empty (no files to load)
        assert loader.get_failure_patterns() == []


class TestEHVValidatorRecovery:
    def test_ehv01_survives_syntax_error_in_src(self, tmp_path: Path) -> None:
        """EHV-01 scanner skips files with syntax errors gracefully."""
        from plugin_examples.fixture_factory.engineering_hygiene_validators import (
            _find_silent_bare_excepts,
        )

        src = tmp_path / "src"
        src.mkdir()
        # Write a file with invalid Python syntax
        (src / "broken.py").write_text("def foo(\n    this is not valid python\n", encoding="utf-8")
        # Write a clean file
        (src / "clean.py").write_text("def bar(): pass\n", encoding="utf-8")
        # Should not crash — should skip the broken file
        violations = _find_silent_bare_excepts(src)
        assert isinstance(violations, list)


class TestEvidenceContractRecovery:
    def test_survives_empty_bundle(self, tmp_path: Path) -> None:
        """Evidence contract check on empty bundle returns failures, does not crash."""
        from plugin_examples.evidence_contract import StrictEvidenceContract

        contract = StrictEvidenceContract()
        result = contract.validate_directory(tmp_path)
        # Should return a ContractResult with failures, not crash
        assert not result.passed
        assert len(result.failures) > 0
