"""HallucinationValidator — validates AI suggestions against DllReflector output.

Rules:
  type_name absent in reflection → REJECTED_BY_VALIDATOR (TYPE_NOT_IN_REFLECTION)
  method_name absent in reflection → REJECTED_BY_VALIDATOR (METHOD_NOT_IN_REFLECTION)
  both confirmed → REFLECTION_CONFIRMED
"""

from __future__ import annotations

from dataclasses import replace

from plugin_examples.ai_acceleration.suggestion import AiSuggestion
from plugin_examples.plugin_detector.heuristic_matcher import ReflectionCatalog


class HallucinationValidator:
    """Validate an AiSuggestion against a ReflectionCatalog.

    Returns a new AiSuggestion with updated status.
    Never mutates the input suggestion.
    """

    def validate(
        self, suggestion: AiSuggestion, catalog: ReflectionCatalog
    ) -> AiSuggestion:
        """Check type and method presence in catalog.

        Returns a new AiSuggestion with status=REFLECTION_CONFIRMED or
        status=REJECTED_BY_VALIDATOR with rejection_reason populated.
        """
        type_info = next(
            (t for t in catalog.types if t.name == suggestion.type_name), None
        )

        if type_info is None:
            return AiSuggestion(
                type_name=suggestion.type_name,
                method_name=suggestion.method_name,
                status="REJECTED_BY_VALIDATOR",
                confidence=suggestion.confidence,
                model=suggestion.model,
                rejection_reason="TYPE_NOT_IN_REFLECTION",
                rationale=suggestion.rationale,
            )

        method_found = any(
            m.name == suggestion.method_name for m in type_info.methods
        )
        if not method_found:
            return AiSuggestion(
                type_name=suggestion.type_name,
                method_name=suggestion.method_name,
                status="REJECTED_BY_VALIDATOR",
                confidence=suggestion.confidence,
                model=suggestion.model,
                rejection_reason="METHOD_NOT_IN_REFLECTION",
                rationale=suggestion.rationale,
            )

        return AiSuggestion(
            type_name=suggestion.type_name,
            method_name=suggestion.method_name,
            status="REFLECTION_CONFIRMED",
            confidence=suggestion.confidence,
            model=suggestion.model,
            probe_evidence=suggestion.probe_evidence,
            rationale=suggestion.rationale,
        )
