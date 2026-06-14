"""Heuristic matcher for non-LowCode plugin candidate discovery.

Enforces PR-01 through PR-03 before returning any candidate mapping.
PR-01: type_name must exist in catalog types (exact match)
PR-02: method_name must exist in that type's methods (exact match)
PR-03: type must not be abstract or an interface; must have a public constructor or static factory
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Catalog input models (minimal — used by this matcher only)
# ---------------------------------------------------------------------------


@dataclass
class MethodInfo:
    name: str
    is_static: bool = False
    return_type: str = ""


@dataclass
class TypeInfo:
    name: str
    namespace: str
    methods: list[MethodInfo] = field(default_factory=list)
    is_abstract: bool = False
    is_interface: bool = False
    has_public_constructor: bool = True


@dataclass
class ReflectionCatalog:
    """Simplified reflection catalog produced by DllReflector."""

    package_id: str
    types: list[TypeInfo] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Candidate mapping
# ---------------------------------------------------------------------------


@dataclass
class CandidateMapping:
    """A matched type+method candidate for probe generation.

    status is always PROBE_CANDIDATE (authoritative enum value from REPAIR A).
    reflection_confirmed=True means PR-01 and PR-02 passed.
    ai_source_flag=False means this was heuristic-matched, not AI-suggested.
    """

    type_name: str
    namespace: str
    method_name: str
    confidence_score: float  # in [0.0, 1.05]
    score_breakdown: dict
    match_rationale: str
    status: str = "PROBE_CANDIDATE"
    ai_source_flag: bool = False
    reflection_confirmed: bool = True


# ---------------------------------------------------------------------------
# Heuristic matcher
# ---------------------------------------------------------------------------

# Verb → likely class name fragment mappings
_VERB_TYPE_HINTS: dict[str, list[str]] = {
    "convert": ["Converter", "Conversion", "Convert"],
    "generate": ["Generator", "Generate", "Builder"],
    "read": ["Reader", "Loader", "Parser"],
    "write": ["Writer", "Saver"],
    "save": ["Saver", "Writer", "Converter"],
    "merge": ["Merger", "Combiner"],
    "split": ["Splitter", "Divider"],
    "compress": ["Compressor", "Archiver"],
    "extract": ["Extractor"],
    "recognize": ["Recognizer", "Scanner"],
    "render": ["Renderer"],
    "watermark": ["Watermarker"],
    "sign": ["Signer"],
    "protect": ["Protector"],
    "edit": ["Editor"],
    "annotate": ["Annotator"],
}

# Method name patterns considered as primary "operation" methods
_OPERATION_METHODS: set[str] = {
    "Generate",
    "Save",
    "Convert",
    "Process",
    "Execute",
    "Read",
    "Write",
    "Export",
    "Import",
    "Load",
    "Create",
    "Merge",
    "Split",
    "Compress",
    "Extract",
    "Recognize",
    "Render",
    "Sign",
    "Watermark",
    "Protect",
}


class HeuristicMatcher:
    """Match plugin verbs against a reflection catalog.

    Returns CandidateMapping objects only when PR-01, PR-02, PR-03 all pass.
    Returns empty list when no safe match can be made.
    """

    def match(self, catalog: ReflectionCatalog, plugin_verb: str) -> list[CandidateMapping]:
        """Match a plugin verb against the reflection catalog.

        Returns a list of CandidateMapping objects (may be empty).
        """
        verb_lower = plugin_verb.lower()
        type_hints = _VERB_TYPE_HINTS.get(verb_lower, [verb_lower.capitalize()])

        results: list[CandidateMapping] = []

        for type_info in catalog.types:
            # PR-03: reject abstract types and interfaces
            if type_info.is_abstract or type_info.is_interface:
                continue

            # PR-03: must have a public constructor OR a static factory method
            has_factory = any(m.is_static for m in type_info.methods)
            if not type_info.has_public_constructor and not has_factory:
                continue

            # PR-01: type name must match a hint (case-insensitive fragment match)
            name_matches = any(hint.lower() in type_info.name.lower() for hint in type_hints)
            if not name_matches:
                continue

            # PR-02: method must exist in this type's methods (exact match)
            for method in type_info.methods:
                if method.name not in _OPERATION_METHODS:
                    continue

                # Score the candidate
                name_score = 0.4 if any(h.lower() == type_info.name.lower() for h in type_hints) else 0.25
                method_score = 0.35 if method.name in _OPERATION_METHODS else 0.1
                constructor_score = 0.15 if type_info.has_public_constructor else 0.05
                static_bonus = 0.05 if method.is_static else 0.0
                confidence = min(1.05, name_score + method_score + constructor_score + static_bonus)

                results.append(
                    CandidateMapping(
                        type_name=type_info.name,
                        namespace=type_info.namespace,
                        method_name=method.name,
                        confidence_score=confidence,
                        score_breakdown={
                            "name_match": name_score,
                            "method_match": method_score,
                            "constructor": constructor_score,
                            "static_bonus": static_bonus,
                        },
                        match_rationale=(
                            f"Type '{type_info.name}' matched verb '{plugin_verb}' via hint "
                            f"{type_hints}; method '{method.name}' is an operation method."
                        ),
                        status="PROBE_CANDIDATE",
                        ai_source_flag=False,
                        reflection_confirmed=True,
                    )
                )

        # Sort by confidence descending
        results.sort(key=lambda c: c.confidence_score, reverse=True)
        return results
