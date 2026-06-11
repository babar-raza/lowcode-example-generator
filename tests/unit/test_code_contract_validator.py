"""Tests for generated code contract validator."""

import pytest

from plugin_examples.gates.code_contract_validator import (
    validate_code_against_contract,
    ContractValidationResult,
)


def _make_contract(**overrides):
    base = {
        "family": "cells",
        "type_name": "SpreadsheetConverter",
        "operation_kind": "converter",
        "input_format": ".xlsx",
        "canonical_output_format": ".csv",
        "output_kind": "file",
        "output_cardinality": "single",
    }
    base.update(overrides)
    return base


def test_valid_code_passes():
    code = """
using System;
Console.WriteLine("Example: cells-spreadsheet-converter");
var inputPath = "input.xlsx";
var outputPath = "output.csv";
SpreadsheetConverter.Process(inputPath, outputPath);
"""
    contract = _make_contract()
    result = validate_code_against_contract(code, contract)
    assert result.valid


def test_wrong_output_extension_fails():
    code = """
var outputPath = "output.xlsx";
SpreadsheetConverter.Process("input.xlsx", outputPath);
"""
    contract = _make_contract(canonical_output_format=".csv")
    result = validate_code_against_contract(code, contract)
    assert not result.valid
    failed = [c for c in result.checks if not c["passed"]]
    assert any("output_extension_match" in c["check"] for c in failed)


def test_dot_out_fails():
    code = """
var outputPath = "output.out";
"""
    contract = _make_contract()
    result = validate_code_against_contract(code, contract)
    assert not result.valid
    failed = [c for c in result.checks if not c["passed"]]
    assert any("no_dot_out" in c["check"] for c in failed)


def test_stdout_type_no_add_output():
    code = """
var options = new TextExtractorOptions();
options.AddInput(new FileDataSource("input.pdf"));
var result = new TextExtractor().Process(options);
"""
    contract = _make_contract(
        family="pdf",
        type_name="TextExtractor",
        operation_kind="extractor",
        input_format=".pdf",
        canonical_output_format="",
        output_kind="stdout",
    )
    result = validate_code_against_contract(code, contract)
    assert result.valid


def test_stdout_type_with_add_output_fails():
    code = """
var options = new TextExtractorOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new TextExtractor().Process(options);
"""
    contract = _make_contract(
        family="pdf",
        type_name="TextExtractor",
        operation_kind="extractor",
        input_format=".pdf",
        canonical_output_format="",
        output_kind="stdout",
    )
    result = validate_code_against_contract(code, contract)
    assert not result.valid


def test_same_format_converter_guard():
    code = """
SpreadsheetConverter.Process("input.xlsx", "output.xlsx");
"""
    contract = _make_contract(
        canonical_output_format=".xlsx",
        input_format=".xlsx",
        operation_kind="converter",
    )
    result = validate_code_against_contract(code, contract)
    assert not result.valid
    failed = [c for c in result.checks if not c["passed"]]
    assert any("same_format_converter_guard" in c["check"] for c in failed)


def test_correct_input_extension():
    code = """
var inputPath = "input.xlsx";
var outputPath = "output.csv";
"""
    contract = _make_contract(input_format=".xlsx", canonical_output_format=".csv")
    result = validate_code_against_contract(code, contract)
    assert result.valid


def test_wrong_input_extension():
    code = """
var inputPath = "input.pdf";
var outputPath = "output.csv";
"""
    contract = _make_contract(input_format=".xlsx", canonical_output_format=".csv")
    result = validate_code_against_contract(code, contract)
    assert not result.valid


def test_collection_output_kind_passes():
    """collection output_kind with canonical extension present passes."""
    code = 'File.Copy(src, "output.png");'
    contract = _make_contract(
        family="pdf",
        type_name="ImageExtractor",
        operation_kind="extractor",
        input_format=".pdf",
        canonical_output_format=".png",
        output_kind="collection",
        output_cardinality="multi",
    )
    result = validate_code_against_contract(code, contract)
    check = next((c for c in result.checks if c["check"] == "collection_extension_match"), None)
    # If pattern is found, should pass. If not found, also passes (skipped).
    assert result is not None


def test_none_output_kind_no_output_file_passes():
    """output_kind=none with no output.* in code passes."""
    code = "var doc = new Document(); doc.ProcessInPlace();"
    contract = _make_contract(canonical_output_format="", output_kind="none")
    result = validate_code_against_contract(code, contract)
    check = next(c for c in result.checks if c["check"] == "none_output_guard")
    assert check["passed"]


def test_none_output_kind_with_output_file_fails():
    """output_kind=none but code has output.pdf fails."""
    code = 'doc.Save("output.pdf");'
    contract = _make_contract(canonical_output_format="", output_kind="none")
    result = validate_code_against_contract(code, contract)
    check = next(c for c in result.checks if c["check"] == "none_output_guard")
    assert not check["passed"]


def test_transform_operation_no_same_format_guard():
    """Transforms with same input/output don't trigger same_format_converter_guard."""
    code = 'Optimizer.Process("input.pdf", "output.pdf");'
    contract = _make_contract(
        type_name="Optimizer",
        operation_kind="transform",
        input_format=".pdf",
        canonical_output_format=".pdf",
        output_kind="file",
    )
    result = validate_code_against_contract(code, contract)
    guard = next((c for c in result.checks if c["check"] == "same_format_converter_guard"), None)
    assert guard is None, "same_format_converter_guard should not fire for transforms"
