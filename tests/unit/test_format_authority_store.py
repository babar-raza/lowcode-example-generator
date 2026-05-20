"""Tests for FormatContract model and store — Lane A foundation."""

import json
import pytest
from pathlib import Path

from plugin_examples.format_authority.contracts import FormatContract
from plugin_examples.format_authority.store import (
    get_contract,
    get_all_contracts,
    load_contracts_from_json,
    reset_store,
    MissingFormatContractError,
)


@pytest.fixture(autouse=True)
def _reset():
    """Reset the store before each test."""
    reset_store()
    yield
    reset_store()


# ── FormatContract model tests ──

def test_contract_creation():
    c = FormatContract(
        family="cells", type_name="SpreadsheetConverter",
        operation_kind="converter", input_format=".xlsx",
        input_cardinality="single", canonical_output_format=".csv",
        output_cardinality="single", output_kind="file",
    )
    assert c.family == "cells"
    assert c.type_name == "SpreadsheetConverter"
    assert c.canonical_output_format == ".csv"
    assert c.contract_id == "cells/SpreadsheetConverter"


def test_contract_hash_is_stable():
    c1 = FormatContract(
        family="cells", type_name="SpreadsheetConverter",
        operation_kind="converter", input_format=".xlsx",
        input_cardinality="single", canonical_output_format=".csv",
        output_cardinality="single", output_kind="file",
    )
    c2 = FormatContract(
        family="cells", type_name="SpreadsheetConverter",
        operation_kind="converter", input_format=".xlsx",
        input_cardinality="single", canonical_output_format=".csv",
        output_cardinality="single", output_kind="file",
    )
    assert c1.contract_hash == c2.contract_hash
    assert len(c1.contract_hash) == 16


def test_contract_serialize_deserialize():
    c = FormatContract(
        family="pdf", type_name="FormExporter",
        operation_kind="exporter", input_format=".pdf",
        input_cardinality="single", canonical_output_format=".json",
        output_cardinality="single", output_kind="file",
        alternate_output_formats=(".csv",),
    )
    d = c.to_dict()
    c2 = FormatContract.from_dict(d)
    assert c2.family == c.family
    assert c2.type_name == c.type_name
    assert c2.canonical_output_format == ".json"
    assert c2.alternate_output_formats == (".csv",)
    assert c2.contract_hash == c.contract_hash


def test_contract_validation_missing_fields():
    c = FormatContract(
        family="", type_name="",
        operation_kind="", input_format="",
        input_cardinality="", canonical_output_format=".out",
        output_cardinality="single", output_kind="invalid",
    )
    errors = c.validate()
    assert any("family" in e for e in errors)
    assert any("type_name" in e for e in errors)
    assert any("operation_kind" in e for e in errors)
    assert any("input_format" in e for e in errors)
    assert any(".out" in e for e in errors)
    assert any("output_kind" in e for e in errors)


def test_contract_validation_stdout_with_output():
    c = FormatContract(
        family="pdf", type_name="TextExtractor",
        operation_kind="extractor", input_format=".pdf",
        input_cardinality="single", canonical_output_format=".txt",
        output_cardinality="none", output_kind="stdout",
    )
    errors = c.validate()
    assert any("stdout" in e for e in errors)


def test_contract_validation_valid():
    c = FormatContract(
        family="pdf", type_name="TextExtractor",
        operation_kind="extractor", input_format=".pdf",
        input_cardinality="single", canonical_output_format="",
        output_cardinality="none", output_kind="stdout",
    )
    assert c.validate() == []


# ── Store tests ──

def test_missing_contract_raises():
    with pytest.raises(MissingFormatContractError):
        get_contract("nonexistent", "NonexistentType")


def test_load_from_api_authority():
    """Load all 42 contracts from the prior API authority run."""
    authority_path = (
        Path(__file__).resolve().parents[2]
        / "workspace" / "verification"
        / "lowcode-api-format-authority-20260519-153439"
        / "reports" / "api-backed-format-contracts.json"
    )
    if not authority_path.exists():
        pytest.skip("API authority file not available")

    count = load_contracts_from_json(authority_path)
    assert count == 42, f"Expected 42 contracts, got {count}"

    all_c = get_all_contracts()
    assert len(all_c) == 42


def test_spreadsheetconverter_canonical_is_csv():
    """SpreadsheetConverter canonical output MUST be .csv, not .xlsx."""
    authority_path = (
        Path(__file__).resolve().parents[2]
        / "workspace" / "verification"
        / "lowcode-api-format-authority-20260519-153439"
        / "reports" / "api-backed-format-contracts.json"
    )
    if not authority_path.exists():
        pytest.skip("API authority file not available")

    load_contracts_from_json(authority_path)
    c = get_contract("cells", "SpreadsheetConverter")
    assert c.canonical_output_format == ".csv", (
        f"SpreadsheetConverter canonical output must be .csv, got {c.canonical_output_format}"
    )


def test_formexporter_canonical_is_json():
    """FormExporter canonical output MUST be .json, not .xml."""
    authority_path = (
        Path(__file__).resolve().parents[2]
        / "workspace" / "verification"
        / "lowcode-api-format-authority-20260519-153439"
        / "reports" / "api-backed-format-contracts.json"
    )
    if not authority_path.exists():
        pytest.skip("API authority file not available")

    load_contracts_from_json(authority_path)
    c = get_contract("pdf", "FormExporter")
    assert c.canonical_output_format == ".json", (
        f"FormExporter canonical output must be .json, got {c.canonical_output_format}"
    )


def test_email_converter_output_kind_is_directory():
    """Email Converter output kind MUST be directory."""
    authority_path = (
        Path(__file__).resolve().parents[2]
        / "workspace" / "verification"
        / "lowcode-api-format-authority-20260519-153439"
        / "reports" / "api-backed-format-contracts.json"
    )
    if not authority_path.exists():
        pytest.skip("API authority file not available")

    load_contracts_from_json(authority_path)
    c = get_contract("email", "Converter")
    assert c.output_kind == "directory", (
        f"Email Converter output kind must be directory, got {c.output_kind}"
    )


def test_diagram_converter_canonical_is_vdx():
    """DiagramConverter canonical output MUST be .vdx."""
    authority_path = (
        Path(__file__).resolve().parents[2]
        / "workspace" / "verification"
        / "lowcode-api-format-authority-20260519-153439"
        / "reports" / "api-backed-format-contracts.json"
    )
    if not authority_path.exists():
        pytest.skip("API authority file not available")

    load_contracts_from_json(authority_path)
    c = get_contract("diagram", "DiagramConverter")
    assert c.canonical_output_format == ".vdx"


def test_no_contract_has_dot_out():
    """No contract in the store should have .out as canonical output."""
    authority_path = (
        Path(__file__).resolve().parents[2]
        / "workspace" / "verification"
        / "lowcode-api-format-authority-20260519-153439"
        / "reports" / "api-backed-format-contracts.json"
    )
    if not authority_path.exists():
        pytest.skip("API authority file not available")

    load_contracts_from_json(authority_path)
    for key, c in get_all_contracts().items():
        assert c.canonical_output_format != ".out", (
            f"{c.contract_id} has .out as canonical output"
        )


def test_all_contracts_validate():
    """Every contract must pass validation."""
    authority_path = (
        Path(__file__).resolve().parents[2]
        / "workspace" / "verification"
        / "lowcode-api-format-authority-20260519-153439"
        / "reports" / "api-backed-format-contracts.json"
    )
    if not authority_path.exists():
        pytest.skip("API authority file not available")

    load_contracts_from_json(authority_path)
    for key, c in get_all_contracts().items():
        errors = c.validate()
        assert errors == [], f"{c.contract_id} validation errors: {errors}"
