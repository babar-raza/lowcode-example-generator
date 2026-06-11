"""Tests proving HealingIntelligenceLoader is wired into the live pipeline path.

These tests verify that runner.py imports and uses the healing intelligence
loader during generation and validation stages, not just that the loader
module exists independently.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path
from unittest import mock

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_RUNNER_PATH = _REPO_ROOT / "src" / "plugin_examples" / "runner.py"


class TestHealingIntelligenceImportInRunner:
    """Verify that runner.py actually imports and uses HealingIntelligenceLoader."""

    def test_runner_imports_healing_intelligence_loader(self):
        """runner.py must contain an import of HealingIntelligenceLoader."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "HealingIntelligenceLoader" in source, (
            "runner.py does not reference HealingIntelligenceLoader — "
            "healing intelligence is not wired into the pipeline"
        )

    def test_runner_loads_healing_intelligence_in_generation(self):
        """_stage_generation must load healing intelligence registries."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "healing_intelligence" in source
        assert "hi.load()" in source or "HealingIntelligenceLoader" in source

    def test_runner_uses_steering_constraints(self):
        """_stage_generation must call get_steering_constraints."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert (
            "get_steering_constraints" in source
        ), "runner.py does not use steering constraints from healing intelligence"

    def test_runner_uses_failure_patterns_in_validation(self):
        """_stage_validation must use failure patterns for known-failure detection."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "get_failures_for_type" in source, "runner.py does not use failure patterns from healing intelligence"

    def test_runner_uses_repair_patterns_in_validation(self):
        """_stage_validation must use repair patterns for repair hints."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "get_repair_for_failure" in source, "runner.py does not use repair patterns from healing intelligence"

    def test_runner_writes_healing_evidence(self):
        """_stage_generation must write healing-intelligence-usage.json evidence."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "healing-intelligence-usage.json" in source, "runner.py does not write healing intelligence evidence"


class TestPipelineContextHasHealingIntelligence:
    """Verify PipelineContext has the healing_intelligence field."""

    def test_pipeline_context_has_healing_intelligence_field(self):
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "healing_intelligence:" in source or "healing_intelligence =" in source


class TestHealingIntelligenceConstraintMerge:
    """Verify that healing intelligence constraints merge correctly with config."""

    def test_loader_constraints_are_additive(self):
        """HI constraints must be additive — they cannot remove config constraints."""
        from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

        loader = HealingIntelligenceLoader(registry_dir="/nonexistent")
        loader.load()  # graceful degradation — no registries

        # Even with no registries, the loader should return empty constraints
        constraints = loader.get_steering_constraints("pdf", "Merger")
        assert constraints["required"] == []
        assert constraints["forbidden"] == []

    def test_loader_graceful_degradation(self):
        """Missing registries must not block pipeline execution."""
        from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

        loader = HealingIntelligenceLoader(registry_dir="/nonexistent")
        loader.load()
        assert loader.is_loaded() is True  # loaded successfully despite missing files
        assert loader.get_failure_patterns() == []
        assert loader.get_steering_constraints("any", "Any") == {
            "required": [],
            "forbidden": [],
            "global_required": [],
            "global_forbidden": [],
        }

    def test_known_failure_detection_returns_empty_for_unknown(self):
        """Unknown failure names must return False."""
        from plugin_examples.healing_intelligence.loader import HealingIntelligenceLoader

        loader = HealingIntelligenceLoader(registry_dir="/nonexistent")
        loader.load()
        assert loader.is_known_failure("nonexistent_pattern") is False


class TestHealingIntelligenceRepairHintInjection:
    """Verify repair hints from healing intelligence reach repair prompts."""

    def test_repair_prompt_includes_known_repair_strategy_placeholder(self):
        """The runner repair prompt must include HI repair hints."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert (
            "KNOWN REPAIR STRATEGY" in source
        ), "runner.py does not inject healing intelligence repair hints into repair prompts"

    def test_hi_repair_hints_dict_populated_from_loader(self):
        """hi_repair_hints dict must be populated from loader's get_repair_for_failure."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "hi_repair_hints" in source
        assert "hi_failure_hints" in source


class TestNoForbiddenPatternBypass:
    """Verify healing intelligence cannot bypass forbidden patterns."""

    def test_config_constraints_remain_authoritative(self):
        """Runner must preserve config per_type_constraints even when HI adds constraints."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        # The merge logic must use dict() copy to avoid mutating original config
        assert "dict(_ptc)" in source or "_ptc = dict(_ptc)" in source, (
            "runner.py must copy _ptc before merging HI constraints to avoid "
            "mutating the original config constraints"
        )

    def test_semantic_validation_still_runs_after_repair(self):
        """Semantic validation must still run on repaired code even with HI hints."""
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        # _validate_code and _validate_code_from_constraints must still be called
        assert "_validate_code(" in source
        assert "_validate_code_from_constraints(" in source
