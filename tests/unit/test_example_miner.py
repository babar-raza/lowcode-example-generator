"""Unit tests for example_miner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.example_miner.miner import (
    MiningResult,
    extract_symbols_from_code,
    mine_examples,
    write_examples_index,
    write_stale_report,
)
from plugin_examples.example_miner.symbol_validator import (
    SymbolValidationResult,
    validate_symbols,
)


CELLS_SOURCES = [
    {
        "type": "github",
        "owner": "aspose-cells",
        "repo": "Aspose.Cells-for-.NET",
        "branch": "master",
        "paths": ["Examples/CSharp"],
    }
]


def _make_catalog() -> dict:
    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": "25.4.0",
        "namespaces": [
            {
                "namespace": "Aspose.Cells.LowCode",
                "types": [
                    {
                        "name": "SpreadsheetLocker",
                        "full_name": "Aspose.Cells.LowCode.SpreadsheetLocker",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [
                            {"name": "Process", "return_type": "void",
                             "is_static": True, "is_obsolete": False, "parameters": []},
                        ],
                        "properties": [
                            {"name": "Password", "type": "string", "can_read": True,
                             "can_write": True, "is_obsolete": False},
                        ],
                        "constructors": [],
                    },
                ],
            },
        ],
        "diagnostics": {"xml_documentation_loaded": False, "metadata_only": True},
    }


class TestMiner:
    def test_mine_from_config(self):
        result = mine_examples("cells", CELLS_SOURCES)
        assert result.family == "cells"
        assert result.total > 0

    def test_example_provenance(self):
        result = mine_examples("cells", CELLS_SOURCES)
        assert result.examples[0].provenance == "aspose-cells/Aspose.Cells-for-.NET:master"

    def test_write_examples_index(self, tmp_path):
        result = mine_examples("cells", CELLS_SOURCES)
        manifests = tmp_path / "workspace" / "manifests"
        path = write_examples_index(result, manifests)
        assert path.exists()
        assert path.name == "existing-examples-index.json"
        with open(path) as f:
            data = json.load(f)
        assert data["family"] == "cells"

    def test_write_stale_report(self, tmp_path):
        result = mine_examples("cells", CELLS_SOURCES)
        verification = tmp_path / "workspace" / "verification"
        path = write_stale_report(result, verification)
        assert path.exists()
        assert "stale-existing-examples" in path.name

    def test_paths_use_workspace(self, tmp_path):
        result = mine_examples("cells", CELLS_SOURCES)
        idx_path = write_examples_index(result, tmp_path / "workspace" / "manifests")
        stale_path = write_stale_report(result, tmp_path / "workspace" / "verification")
        assert "workspace" in str(idx_path)
        assert "workspace" in str(stale_path)


class TestSymbolExtraction:
    def test_extract_qualified_names(self):
        code = "var locker = new Aspose.Cells.LowCode.SpreadsheetLocker();"
        symbols = extract_symbols_from_code(code)
        assert "Aspose.Cells.LowCode.SpreadsheetLocker" in symbols

    def test_extract_new_instance(self):
        code = "var wb = new Workbook();"
        symbols = extract_symbols_from_code(code)
        assert "Workbook" in symbols


class TestSymbolValidator:
    def test_valid_symbols_pass(self):
        catalog = _make_catalog()
        result = validate_symbols(
            ["Aspose.Cells.LowCode.SpreadsheetLocker"],
            catalog,
            example_id="ex1",
        )
        assert result.is_valid
        assert not result.stale

    def test_invalid_symbols_mark_stale(self):
        catalog = _make_catalog()
        result = validate_symbols(
            ["Aspose.Cells.LowCode.NonExistentClass"],
            catalog,
            example_id="ex1",
        )
        assert not result.is_valid
        assert result.stale
        assert "NonExistentClass" in result.stale_reason

    def test_mixed_symbols(self):
        catalog = _make_catalog()
        result = validate_symbols(
            ["Aspose.Cells.LowCode.SpreadsheetLocker", "Aspose.Cells.Fake"],
            catalog,
            example_id="ex1",
        )
        assert len(result.valid_symbols) == 1
        assert len(result.invalid_symbols) == 1
        assert result.stale

    def test_empty_symbols_invalid(self):
        catalog = _make_catalog()
        result = validate_symbols([], catalog, example_id="ex1")
        assert not result.is_valid  # No valid symbols
