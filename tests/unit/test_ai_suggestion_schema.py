"""Tests for AI suggestion schema and HallucinationValidator — TC-IMPL-009."""

from __future__ import annotations

import pytest

from plugin_examples.ai_acceleration.suggestion import AiSuggestion
from plugin_examples.ai_acceleration.validator import HallucinationValidator
from plugin_examples.plugin_detector.heuristic_matcher import (
    MethodInfo,
    ReflectionCatalog,
    TypeInfo,
)


def _make_catalog(type_name: str, method_name: str) -> ReflectionCatalog:
    return ReflectionCatalog(
        package_id="Test.Package",
        types=[
            TypeInfo(
                name=type_name,
                namespace="Aspose.Test",
                methods=[MethodInfo(name=method_name)],
            )
        ],
    )


class TestAiSuggestionAcceptsValidDraft:
    def test_ai_suggestion_accepts_valid_ai_draft(self):
        """A valid AI_DRAFT suggestion must construct without error."""
        s = AiSuggestion(
            type_name="BarcodeGenerator",
            method_name="Generate",
            status="AI_DRAFT",
            confidence=0.75,
            model="MANUAL_MAPPING",
        )
        assert s.status == "AI_DRAFT"
        assert s.model == "MANUAL_MAPPING"
        assert s.probe_evidence is None

    def test_from_dict_constructs_ai_draft(self):
        """from_dict with status=AI_DRAFT must succeed."""
        data = {
            "type_name": "ImageConverter",
            "method_name": "Convert",
            "status": "AI_DRAFT",
            "confidence": 0.6,
            "model": "MANUAL_MAPPING",
        }
        s = AiSuggestion.from_dict(data)
        assert s.type_name == "ImageConverter"
        assert s.status == "AI_DRAFT"


class TestAiSuggestionRejectsInvalidSchema:
    def test_ai_suggestion_rejects_probe_confirmed_without_evidence(self):
        """PROBE_CONFIRMED without probe_evidence must raise ValueError."""
        with pytest.raises(ValueError, match="probe_evidence"):
            AiSuggestion(
                type_name="BarcodeGenerator",
                method_name="Generate",
                status="PROBE_CONFIRMED",
                confidence=0.9,
                model="MANUAL_MAPPING",
                probe_evidence=None,
            )

    def test_ai_suggestion_rejects_invalid_status(self):
        """An invalid status value must raise ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            AiSuggestion(
                type_name="BarcodeGenerator",
                method_name="Generate",
                status="MADE_UP_STATUS",
                confidence=0.5,
                model="MANUAL_MAPPING",
            )


class TestHallucinationValidator:
    def test_hallucination_validator_rejects_type_not_in_reflection(self):
        """Type absent from reflection → REJECTED_BY_VALIDATOR with TYPE_NOT_IN_REFLECTION."""
        catalog = _make_catalog("SomeOtherType", "Generate")
        suggestion = AiSuggestion(
            type_name="NonExistentType",
            method_name="Generate",
            status="AI_DRAFT",
            confidence=0.8,
            model="MANUAL_MAPPING",
        )
        validator = HallucinationValidator()
        result = validator.validate(suggestion, catalog)
        assert result.status == "REJECTED_BY_VALIDATOR"
        assert result.rejection_reason == "TYPE_NOT_IN_REFLECTION"

    def test_hallucination_validator_advances_to_reflection_confirmed_when_both_present(self):
        """Type AND method both in reflection → REFLECTION_CONFIRMED."""
        catalog = _make_catalog("BarcodeGenerator", "Generate")
        suggestion = AiSuggestion(
            type_name="BarcodeGenerator",
            method_name="Generate",
            status="AI_DRAFT",
            confidence=0.85,
            model="MANUAL_MAPPING",
        )
        validator = HallucinationValidator()
        result = validator.validate(suggestion, catalog)
        assert result.status == "REFLECTION_CONFIRMED"
        assert result.rejection_reason is None

    def test_hallucination_validator_rejects_method_not_in_reflection(self):
        """Type present but method absent → REJECTED_BY_VALIDATOR with METHOD_NOT_IN_REFLECTION."""
        catalog = _make_catalog("BarcodeGenerator", "Generate")
        suggestion = AiSuggestion(
            type_name="BarcodeGenerator",
            method_name="NonExistentMethod",
            status="AI_DRAFT",
            confidence=0.7,
            model="MANUAL_MAPPING",
        )
        validator = HallucinationValidator()
        result = validator.validate(suggestion, catalog)
        assert result.status == "REJECTED_BY_VALIDATOR"
        assert result.rejection_reason == "METHOD_NOT_IN_REFLECTION"
