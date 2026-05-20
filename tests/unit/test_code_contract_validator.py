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
    code = '''
using System;
Console.WriteLine("Example: cells-spreadsheet-converter");
var inputPath = "input.xlsx";
var outputPath = "output.csv";
SpreadsheetConverter.Process(inputPath, outputPath);
'''
    contract = _make_contract()
    result = validate_code_against_contract(code, contract)
    assert result.valid


def test_wrong_output_extension_fails():
    code = '''
var outputPath = "output.xlsx";
SpreadsheetConverter.Process("input.xlsx", outputPath);
'''
    contract = _make_contract(canonical_output_format=".csv")
    result = validate_code_against_contract(code, contract)
    assert not result.valid
    failed = [c for c in result.checks if not c["passed"]]
    assert any("output_extension_match" in c["check"] for c in failed)


def test_dot_out_fails():
    code = '''
var outputPath = "output.out";
'''
    contract = _make_contract()
    result = validate_code_against_contract(code, contract)
    assert not result.valid
    failed = [c for c in result.checks if not c["passed"]]
    assert any("no_dot_out" in c["check"] for c in failed)


def test_stdout_type_no_add_output():
    code = '''
var options = new TextExtractorOptions();
options.AddInput(new FileDataSource("input.pdf"));
var result = new TextExtractor().Process(options);
'''
    contract = _make_contract(
        family="pdf", type_name="TextExtractor",
        operation_kind="extractor", input_format=".pdf",
        canonical_output_format="", output_kind="stdout",
    )
    result = validate_code_against_contract(code, contract)
    assert result.valid


def test_stdout_type_with_add_output_fails():
    code = '''
var options = new TextExtractorOptions();
options.AddInput(new FileDataSource("input.pdf"));
options.AddOutput(new FileDataSource("output.pdf"));
var result = new TextExtractor().Process(options);
'''
    contract = _make_contract(
        family="pdf", type_name="TextExtractor",
        operation_kind="extractor", input_format=".pdf",
        canonical_output_format="", output_kind="stdout",
    )
    result = validate_code_against_contract(code, contract)
    assert not result.valid


def test_same_format_converter_guard():
    code = '''
SpreadsheetConverter.Process("input.xlsx", "output.xlsx");
'''
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
    code = '''
var inputPath = "input.xlsx";
var outputPath = "output.csv";
'''
    contract = _make_contract(input_format=".xlsx", canonical_output_format=".csv")
    result = validate_code_against_contract(code, contract)
    assert result.valid


def test_wrong_input_extension():
    code = '''
var inputPath = "input.pdf";
var outputPath = "output.csv";
'''
    contract = _make_contract(input_format=".xlsx", canonical_output_format=".csv")
    result = validate_code_against_contract(code, contract)
    assert not result.valid
