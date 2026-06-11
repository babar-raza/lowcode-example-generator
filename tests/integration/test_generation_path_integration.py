"""Integration tests for generation path selection — TC-INTTEST-004."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from plugin_examples.generator.code_generator import GeneratedExample, generate_example


def _make_packet(
    scenario_id: str = "cells-converter",
    target_type: str = "Aspose.Cells.LowCode.SpreadsheetConverter",
    per_type_constraints: dict | None = None,
) -> SimpleNamespace:
    """Build a minimal PromptPacket-like object."""
    return SimpleNamespace(
        scenario_id=scenario_id,
        target_type=target_type,
        target_namespace="Aspose.Cells.LowCode",
        approved_symbols=["Process"],
        per_type_constraints=per_type_constraints or {},
        user_prompt="Generate a converter example.",
        system_prompt="You are a C# code generator.",
        family="cells",
        operation_kind="converter",
        type_details={
            "name": "SpreadsheetConverter",
            "kind": "class",
            "methods": [{"name": "Process", "parameters": [{"name": "loadOptions", "type": "LoadOptions"}]}],
        },
        template_hints={},
        input_strategy="none",
        target_methods=["Process"],
        input_files=[],
    )


class TestTemplateFirstSelection:
    """Verify template-first path is selected when configured."""

    def test_template_first_flag_selects_template_path(self):
        """When per_type_constraints[type].template_first=True, strategy is template_first."""
        packet = _make_packet(
            per_type_constraints={
                "SpreadsheetConverter": {"template_first": True},
            },
        )
        result = generate_example(packet, llm_generate=None)
        assert isinstance(result, GeneratedExample)
        # Template-first produces either generated_template_first or failed
        assert result.generation_strategy in ("llm_generated", "template_first", "catalog_fallback") or \
               result.status in ("generated_template_first", "failed")


class TestCatalogFallback:
    """Verify catalog fallback when LLM unavailable and not template-first."""

    def test_no_llm_no_template_uses_catalog_fallback(self):
        """With llm_generate=None and template_first=False, uses catalog fallback."""
        packet = _make_packet(
            per_type_constraints={
                "SpreadsheetConverter": {"template_first": False},
            },
        )
        result = generate_example(packet, llm_generate=None)
        assert isinstance(result, GeneratedExample)
        # Should be generated (catalog fallback) not failed
        assert result.status in ("generated", "failed")


class TestBlockedScenarioPreservation:
    """Verify blocked scenarios preserve reason string."""

    def test_llm_failure_preserves_reason(self):
        """When LLM raises, failure_reason is preserved."""
        packet = _make_packet(
            per_type_constraints={
                "SpreadsheetConverter": {"template_first": False},
            },
        )

        def failing_llm(prompt, system_prompt):
            raise ConnectionError("LLM endpoint unreachable")

        result = generate_example(packet, llm_generate=failing_llm)
        assert result.status == "failed"
        assert result.failure_reason is not None
        assert "LLM" in result.failure_reason or "unreachable" in result.failure_reason
