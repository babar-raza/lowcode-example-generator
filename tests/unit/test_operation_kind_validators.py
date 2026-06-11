"""Unit tests for operation-kind validators OKV-01..04 — TC-OKV-001."""

from __future__ import annotations

import pytest

from plugin_examples.fixture_factory.operation_kind_validators import (
    DEFAULT_OPERATION_KINDS,
    OkvResult,
    okv_01_all_types_have_operation_kind,
    okv_02_operation_kind_in_matrix,
    okv_03_cardinality_consistent,
    okv_04_no_unknown_kinds,
)


class TestOkv01AllTypesHaveOperationKind:
    def test_passes_when_all_mapped(self):
        types_with_kinds = {"Converter": "converter", "Merger": "merger"}
        results = okv_01_all_types_have_operation_kind(types_with_kinds, ["Converter", "Merger"])
        assert all(r.passed for r in results)

    def test_fails_when_missing(self):
        types_with_kinds = {"Converter": "converter"}
        results = okv_01_all_types_have_operation_kind(types_with_kinds, ["Converter", "Splitter"])
        assert not results[1].passed
        assert "MISSING" in results[1].detail


class TestOkv02OperationKindInMatrix:
    def test_passes_for_known_kinds(self):
        types_with_kinds = {"Conv": "converter", "Merg": "merger"}
        results = okv_02_operation_kind_in_matrix(types_with_kinds, DEFAULT_OPERATION_KINDS)
        assert all(r.passed for r in results)

    def test_fails_for_unknown_kind(self):
        types_with_kinds = {"Foo": "blender"}
        results = okv_02_operation_kind_in_matrix(types_with_kinds, DEFAULT_OPERATION_KINDS)
        assert not results[0].passed
        assert "NOT IN MATRIX" in results[0].detail


class TestOkv03CardinalityConsistent:
    def test_passes_with_matrix_entry(self):
        matrix = {"operation_kinds": {"converter": {"input_cardinality": "single"}}}
        results = okv_03_cardinality_consistent({"Conv": "converter"}, matrix)
        assert all(r.passed for r in results)


class TestOkv04NoUnknownKinds:
    def test_passes_when_all_known(self):
        types_with_kinds = {"A": "converter", "B": "merger"}
        results = okv_04_no_unknown_kinds(types_with_kinds, DEFAULT_OPERATION_KINDS)
        assert results[0].passed

    def test_fails_when_unknown(self):
        types_with_kinds = {"A": "converter", "B": "teleporter"}
        results = okv_04_no_unknown_kinds(types_with_kinds, DEFAULT_OPERATION_KINDS)
        assert not results[0].passed
        assert "teleporter" in results[0].detail
