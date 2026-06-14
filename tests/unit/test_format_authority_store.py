"""Tests for FormatContract model and store — repo-local authority.

These tests use pipeline/format-authority/ (repo-local) as the authority source.
No workspace run artifacts. No skips for missing files.
"""

import json
from pathlib import Path

import pytest

from plugin_examples.format_authority.contracts import FormatContract
from plugin_examples.format_authority.store import (
    MissingFormatContractError,
    get_all_contracts,
    get_contract,
    load_contracts_from_json,
    reset_store,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = REPO_ROOT / "pipeline" / "format-authority" / "manifest.json"


@pytest.fixture(autouse=True)
def _reset():
    """Reset the store before each test."""
    reset_store()
    yield
    reset_store()


# ── FormatContract model tests ──


def test_contract_creation():
    c = FormatContract(
        family="cells",
        type_name="SpreadsheetConverter",
        operation_kind="converter",
        input_format=".xlsx",
        input_cardinality="single",
        canonical_output_format=".csv",
        output_cardinality="single",
        output_kind="file",
    )
    assert c.family == "cells"
    assert c.type_name == "SpreadsheetConverter"
    assert c.canonical_output_format == ".csv"
    assert c.contract_id == "cells/SpreadsheetConverter"


def test_contract_hash_is_stable():
    c1 = FormatContract(
        family="cells",
        type_name="SpreadsheetConverter",
        operation_kind="converter",
        input_format=".xlsx",
        input_cardinality="single",
        canonical_output_format=".csv",
        output_cardinality="single",
        output_kind="file",
    )
    c2 = FormatContract(
        family="cells",
        type_name="SpreadsheetConverter",
        operation_kind="converter",
        input_format=".xlsx",
        input_cardinality="single",
        canonical_output_format=".csv",
        output_cardinality="single",
        output_kind="file",
    )
    assert c1.contract_hash == c2.contract_hash
    assert len(c1.contract_hash) == 16


def test_contract_serialize_deserialize():
    c = FormatContract(
        family="pdf",
        type_name="FormExporter",
        operation_kind="exporter",
        input_format=".pdf",
        input_cardinality="single",
        canonical_output_format=".json",
        output_cardinality="single",
        output_kind="file",
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
        family="",
        type_name="",
        operation_kind="",
        input_format="",
        input_cardinality="",
        canonical_output_format=".out",
        output_cardinality="single",
        output_kind="invalid",
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
        family="pdf",
        type_name="TextExtractor",
        operation_kind="extractor",
        input_format=".pdf",
        input_cardinality="single",
        canonical_output_format=".txt",
        output_cardinality="none",
        output_kind="stdout",
    )
    errors = c.validate()
    assert any("stdout" in e for e in errors)


def test_contract_validation_valid():
    c = FormatContract(
        family="pdf",
        type_name="TextExtractor",
        operation_kind="extractor",
        input_format=".pdf",
        input_cardinality="single",
        canonical_output_format="",
        output_cardinality="none",
        output_kind="stdout",
    )
    assert c.validate() == []


# ── Store tests — repo-local authority ──


def test_repo_local_manifest_exists():
    """The repo-local format authority manifest MUST exist."""
    assert MANIFEST_PATH.exists(), (
        f"Repo-local format authority missing: {MANIFEST_PATH}. " f"This is required for all format authority tests."
    )


def test_missing_contract_raises():
    """Missing contract must raise MissingFormatContractError."""
    with pytest.raises(MissingFormatContractError):
        get_contract("nonexistent", "NonexistentType")


def test_missing_manifest_fails_closed(tmp_path):
    """Loading from a nonexistent path must raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_contracts_from_json(tmp_path / "nonexistent.json")


def test_load_42_from_repo_local():
    """Load all 42 contracts from repo-local authority.

    42 contracts = canonical main-class workflow types only.
    words/Signer excluded: no Aspose.Words.LowCode.Signer class; SignerContext is CONTEXT_MODEL;
      DigitalSignatureUtil.Sign is in Aspose.Words.DigitalSignatures, not LowCode namespace.
    slides/ForEach excluded: ForEach is NON_RUNNABLE_HELPER (utility iterator), not a main workflow class.
    """
    count = load_contracts_from_json(MANIFEST_PATH)
    assert count == 42, f"Expected 42 contracts, got {count}"
    all_c = get_all_contracts()
    assert len(all_c) == 42


def test_spreadsheetconverter_canonical_is_csv():
    """SpreadsheetConverter canonical output MUST be .csv, not .xlsx."""
    load_contracts_from_json(MANIFEST_PATH)
    c = get_contract("cells", "SpreadsheetConverter")
    assert (
        c.canonical_output_format == ".csv"
    ), f"SpreadsheetConverter canonical output must be .csv, got {c.canonical_output_format}"


def test_formexporter_canonical_is_json():
    """FormExporter canonical output MUST be .json, not .xml."""
    load_contracts_from_json(MANIFEST_PATH)
    c = get_contract("pdf", "FormExporter")
    assert (
        c.canonical_output_format == ".json"
    ), f"FormExporter canonical output must be .json, got {c.canonical_output_format}"


def test_email_converter_output_kind_is_directory():
    """Email Converter output kind MUST be directory."""
    load_contracts_from_json(MANIFEST_PATH)
    c = get_contract("email", "Converter")
    assert c.output_kind == "directory", f"Email Converter output kind must be directory, got {c.output_kind}"


def test_text_extractor_stdout_no_output():
    """TextExtractor must have stdout output_kind and empty canonical_output_format."""
    load_contracts_from_json(MANIFEST_PATH)
    c = get_contract("pdf", "TextExtractor")
    assert c.output_kind == "stdout"
    assert c.canonical_output_format == ""


def test_diagram_converter_canonical_is_vdx():
    """DiagramConverter canonical output MUST be .vdx."""
    load_contracts_from_json(MANIFEST_PATH)
    c = get_contract("diagram", "DiagramConverter")
    assert c.canonical_output_format == ".vdx"


def test_no_contract_has_dot_out():
    """No contract in the store should have .out as canonical output."""
    load_contracts_from_json(MANIFEST_PATH)
    for key, c in get_all_contracts().items():
        assert c.canonical_output_format != ".out", f"{c.contract_id} has .out as canonical output"


def test_all_contracts_validate():
    """Every loaded contract must pass validation."""
    load_contracts_from_json(MANIFEST_PATH)
    for key, c in get_all_contracts().items():
        errors = c.validate()
        assert errors == [], f"{c.contract_id} validation errors: {errors}"


def test_auto_load_from_default_path():
    """get_contract should auto-load from default repo-local path."""
    # Don't call load_contracts_from_json — let auto-load work
    c = get_contract("cells", "JsonConverter")
    assert c.canonical_output_format == ".json"


def test_text_converter_input_is_xlsx():
    """TextConverter input MUST be .xlsx (family default), not .csv."""
    load_contracts_from_json(MANIFEST_PATH)
    c = get_contract("cells", "TextConverter")
    assert c.input_format == ".xlsx", f"TextConverter input must be .xlsx, got {c.input_format}"


def test_image_extractor_canonical_is_png():
    """ImageExtractor canonical output MUST be .png, not .jpg."""
    load_contracts_from_json(MANIFEST_PATH)
    c = get_contract("pdf", "ImageExtractor")
    assert c.canonical_output_format == ".png"
