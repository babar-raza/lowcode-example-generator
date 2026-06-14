"""Tests for publication format gate — repo-local authority."""

import json
from pathlib import Path

import pytest

from plugin_examples.format_authority.store import reset_store
from plugin_examples.gates.publication_gate import (
    PublicationGateResult,
    check_repo_local_authority_exists,
    check_unfreeze_criteria,
    evaluate_publication_gate,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_store()
    yield
    reset_store()


def test_repo_local_authority_exists():
    """Publication gate requires repo-local format authority."""
    assert check_repo_local_authority_exists()


def test_gate_blocks_without_contract():
    """Gate blocks if FormatContract not found."""
    result = evaluate_publication_gate(
        scenario_id="fake-type",
        family="fake",
        type_name="FakeType",
    )
    assert not result.passed
    assert not result.contract_exists
    assert len(result.reasons) > 0


def test_gate_contract_exists_for_real_type():
    """Gate finds contract for a real type."""
    result = evaluate_publication_gate(
        scenario_id="cells-json-converter",
        family="cells",
        type_name="JsonConverter",
    )
    assert result.contract_exists
    # Still blocked because no Program.cs or manifest
    assert not result.passed


def test_gate_passes_with_valid_code_and_manifest(tmp_path):
    """Gate passes when contract exists, code validates, and manifest has contract snapshot."""
    # Write a valid Program.cs
    code = """using Aspose.Cells.LowCode;
var converter = new JsonConverter();
converter.Process("input.xlsx", "output.json");
Console.WriteLine("Example: cells-json-converter");
"""
    program_cs = tmp_path / "Program.cs"
    program_cs.write_text(code)

    # Write a manifest with contract snapshot
    from plugin_examples.format_authority.store import get_contract

    fc = get_contract("cells", "JsonConverter")
    manifest_data = {
        "scenario_id": "cells-json-converter",
        "contract_id": fc.contract_id,
        "contract_hash": fc.contract_hash,
    }
    manifest = tmp_path / "example.manifest.json"
    manifest.write_text(json.dumps(manifest_data))

    result = evaluate_publication_gate(
        scenario_id="cells-json-converter",
        family="cells",
        type_name="JsonConverter",
        program_cs_path=program_cs,
        manifest_path=manifest,
    )
    assert result.contract_exists
    assert result.code_validates
    assert result.manifest_has_contract
    assert result.passed


def test_unfreeze_criteria_check():
    """Unfreeze criteria check should report store coverage."""
    result = check_unfreeze_criteria()
    # First criterion (42/42 coverage) should be met with repo-local authority
    assert result.criteria[0]["met"] is True
    assert "42/42" in result.criteria[0]["detail"]
    # Overall should be frozen (not all criteria verifiable without test runs)
    assert "PUBLICATION_FROZEN" in result.recommendation
