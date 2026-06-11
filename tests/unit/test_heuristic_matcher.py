"""Tests for HeuristicMatcher — TC-IMPL-004."""

from __future__ import annotations

import pytest

from plugin_examples.plugin_detector.heuristic_matcher import (
    CandidateMapping,
    HeuristicMatcher,
    MethodInfo,
    ReflectionCatalog,
    TypeInfo,
)


def _make_catalog(*types: TypeInfo) -> ReflectionCatalog:
    return ReflectionCatalog(package_id="Test.Package", types=list(types))


def _converter_type(
    name: str = "BarcodeConverter",
    *,
    is_abstract: bool = False,
    is_interface: bool = False,
    has_public_constructor: bool = True,
    methods: list[MethodInfo] | None = None,
) -> TypeInfo:
    if methods is None:
        methods = [MethodInfo(name="Convert"), MethodInfo(name="Save")]
    return TypeInfo(
        name=name,
        namespace="Aspose.BarCode.LowCode",
        methods=methods,
        is_abstract=is_abstract,
        is_interface=is_interface,
        has_public_constructor=has_public_constructor,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestHeuristicMatcher:
    def test_converter_verb_matches_converter_class(self):
        """A 'convert' verb must match a type whose name contains 'Converter'."""
        catalog = _make_catalog(_converter_type("BarcodeConverter"))
        matcher = HeuristicMatcher()
        results = matcher.match(catalog, "convert")
        type_names = [r.type_name for r in results]
        assert "BarcodeConverter" in type_names

    def test_converter_verb_matches_save_method(self):
        """'convert' verb must produce CandidateMapping(method_name='Save') for a Converter type."""
        catalog = _make_catalog(_converter_type("ImageConverter"))
        matcher = HeuristicMatcher()
        results = matcher.match(catalog, "convert")
        method_names = {r.method_name for r in results}
        assert "Save" in method_names

    def test_abstract_class_is_rejected(self):
        """Abstract types must never appear in results (PR-03)."""
        catalog = _make_catalog(_converter_type("AbstractConverter", is_abstract=True))
        matcher = HeuristicMatcher()
        results = matcher.match(catalog, "convert")
        assert results == []

    def test_interface_type_is_rejected(self):
        """Interface types must never appear in results (PR-03)."""
        catalog = _make_catalog(_converter_type("IConverter", is_interface=True))
        matcher = HeuristicMatcher()
        results = matcher.match(catalog, "convert")
        assert results == []

    def test_confidence_score_in_valid_range(self):
        """All confidence scores must be in [0.0, 1.05]."""
        types = [
            _converter_type("BarcodeConverter"),
            TypeInfo(
                name="ImageGenerator",
                namespace="Aspose.Imaging",
                methods=[MethodInfo(name="Generate", is_static=True)],
                has_public_constructor=False,
            ),
        ]
        catalog = _make_catalog(*types)
        matcher = HeuristicMatcher()
        for verb in ("convert", "generate"):
            for result in matcher.match(catalog, verb):
                assert (
                    0.0 <= result.confidence_score <= 1.05
                ), f"confidence_score {result.confidence_score} out of range for {result}"

    def test_candidate_mapping_status_is_probe_candidate(self):
        """Every CandidateMapping must have status='PROBE_CANDIDATE' (authoritative enum)."""
        catalog = _make_catalog(_converter_type("PdfConverter"))
        matcher = HeuristicMatcher()
        results = matcher.match(catalog, "convert")
        assert results, "Expected at least one result"
        for r in results:
            assert r.status == "PROBE_CANDIDATE"
            assert r.ai_source_flag is False
            assert r.reflection_confirmed is True

    def test_no_public_constructor_and_no_static_factory_rejected(self):
        """Type with no constructor AND no static factory must be rejected (PR-03)."""
        t = TypeInfo(
            name="SecretConverter",
            namespace="Aspose.Secret",
            methods=[MethodInfo(name="Convert", is_static=False)],
            has_public_constructor=False,
        )
        catalog = _make_catalog(t)
        matcher = HeuristicMatcher()
        results = matcher.match(catalog, "convert")
        assert results == []

    def test_static_factory_compensates_for_missing_constructor(self):
        """Type with no public constructor but a static method IS accepted (PR-03)."""
        t = TypeInfo(
            name="BarcodeConverter",
            namespace="Aspose.BarCode",
            methods=[MethodInfo(name="Convert", is_static=True)],
            has_public_constructor=False,
        )
        catalog = _make_catalog(t)
        matcher = HeuristicMatcher()
        results = matcher.match(catalog, "convert")
        assert results, "Expected static-factory type to be accepted"
