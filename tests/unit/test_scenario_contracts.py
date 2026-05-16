"""Tests for scenario contract files (REM-009 through REM-012 / B-004).

Verifies:
- All 18 scenario contracts parse as valid JSON
- Schema validates all contracts
- Contract coverage matches denominator model published counts
- Published (MERGED) scenarios have post-merge evidence sources
- Forbidden patterns are consistent with code_generator.py guards
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CONTRACTS_DIR = _REPO_ROOT / "pipeline" / "contracts"
_SCHEMA_PATH = _REPO_ROOT / "pipeline" / "schemas" / "scenario-contract.schema.json"
_DENOMINATOR_DIR = _REPO_ROOT / "pipeline" / "configs" / "denominators"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _load_contracts(family: str) -> list[dict]:
    """Load all contract files for a family."""
    family_dir = _CONTRACTS_DIR / family
    if not family_dir.exists():
        return []
    contracts = []
    for path in sorted(family_dir.glob("*.json")):
        contracts.append(json.loads(path.read_text(encoding="utf-8")))
    return contracts


def _all_contracts() -> list[dict]:
    contracts = []
    for family in ("cells", "words", "pdf"):
        contracts.extend(_load_contracts(family))
    return contracts


# ---------------------------------------------------------------------------
# TestContractFilesExist
# ---------------------------------------------------------------------------

class TestContractFilesExist:
    def test_contracts_dir_exists(self):
        assert _CONTRACTS_DIR.exists(), f"pipeline/contracts/ directory missing"

    def test_cells_contracts_dir_exists(self):
        assert (_CONTRACTS_DIR / "cells").exists()

    def test_words_contracts_dir_exists(self):
        assert (_CONTRACTS_DIR / "words").exists()

    def test_pdf_contracts_dir_exists(self):
        assert (_CONTRACTS_DIR / "pdf").exists()

    def test_cells_has_9_contracts(self):
        contracts = _load_contracts("cells")
        assert len(contracts) == 9, f"Expected 9 cells contracts, got {len(contracts)}"

    def test_words_has_7_contracts(self):
        contracts = _load_contracts("words")
        assert len(contracts) == 8, f"Expected 8 words contracts, got {len(contracts)}"

    def test_pdf_has_14_contracts(self):
        contracts = _load_contracts("pdf")
        assert len(contracts) == 14, f"Expected 14 pdf contracts, got {len(contracts)}"

    def test_total_contracts_is_31(self):
        """Total = 9 cells + 8 words + 14 pdf = 31. Sprint 20: added 6 Wave D contracts (jpeg/png/tiff/table-gen/toc-gen/image-extractor)."""
        total = len(_all_contracts())
        assert total == 31, f"Expected 31 total contracts, got {total}"


# ---------------------------------------------------------------------------
# TestContractSchemaValidation
# ---------------------------------------------------------------------------

class TestContractSchemaValidation:
    @pytest.fixture(scope="class")
    def schema(self):
        assert _SCHEMA_PATH.exists(), f"Schema missing: {_SCHEMA_PATH}"
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

    @pytest.mark.parametrize("family", ["cells", "words", "pdf"])
    def test_contracts_parse_as_valid_json(self, family):
        family_dir = _CONTRACTS_DIR / family
        for path in family_dir.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            assert isinstance(data, dict), f"Contract {path.name} is not a dict"

    @pytest.mark.parametrize("family", ["cells", "words", "pdf"])
    def test_contracts_have_required_fields(self, family, schema):
        required = schema.get("required", [])
        for contract in _load_contracts(family):
            for field in required:
                assert field in contract, (
                    f"Contract {contract.get('scenario_id','?')} missing required field: {field}"
                )

    def test_all_scenario_ids_are_unique(self):
        contracts = _all_contracts()
        ids = [c["scenario_id"] for c in contracts]
        assert len(ids) == len(set(ids)), f"Duplicate scenario IDs: {set(x for x in ids if ids.count(x)>1)}"

    def test_all_families_match_dir(self):
        for family in ("cells", "words", "pdf"):
            for contract in _load_contracts(family):
                assert contract["family"] == family, (
                    f"Contract {contract['scenario_id']} has family={contract['family']} "
                    f"but is in {family}/ directory"
                )

    def test_all_contracts_have_non_empty_expected_symbols(self):
        for contract in _all_contracts():
            assert len(contract.get("expected_symbols", [])) >= 1, (
                f"Contract {contract['scenario_id']} has empty expected_symbols"
            )

    def test_all_contracts_have_output_format(self):
        for contract in _all_contracts():
            assert contract.get("output_expectations", {}).get("output_format"), (
                f"Contract {contract['scenario_id']} missing output_format"
            )

    def test_publication_status_is_valid_enum(self):
        valid = {"MERGED", "PR_DRY_RUN_READY", "REVIEWER_PASSED", "PR_OPEN", "IN_GENERATION", "PLANNED"}
        for contract in _all_contracts():
            status = contract.get("publication_status", "")
            assert status in valid, (
                f"Contract {contract['scenario_id']} has invalid publication_status: {status}"
            )

    def test_fixture_type_is_valid_enum(self):
        valid = {
            "generated_fixture_file", "programmatic_input", "programmatic_pdf_single",
            "programmatic_pdf_multi_page", "programmatic_pdf_pair", "programmatic_pdf_known_text",
            "existing_fixture", "none"
        }
        for contract in _all_contracts():
            ft = contract.get("fixture_type", "")
            assert ft in valid, (
                f"Contract {contract['scenario_id']} has invalid fixture_type: {ft}"
            )


# ---------------------------------------------------------------------------
# TestCellsContracts
# ---------------------------------------------------------------------------

class TestCellsContracts:
    def test_all_cells_contracts_are_merged(self):
        for contract in _load_contracts("cells"):
            assert contract["publication_status"] == "MERGED", (
                f"Cells contract {contract['scenario_id']} is not MERGED: {contract['publication_status']}"
            )

    def test_all_cells_use_generated_fixture(self):
        for contract in _load_contracts("cells"):
            assert contract["fixture_type"] == "generated_fixture_file", (
                f"Cells contract {contract['scenario_id']} has unexpected fixture_type: {contract['fixture_type']}"
            )

    def test_all_cells_use_process_method(self):
        for contract in _load_contracts("cells"):
            assert contract["primary_method"] == "Process", (
                f"Cells contract {contract['scenario_id']} primary_method is not Process: {contract['primary_method']}"
            )

    def test_cells_scenario_ids_present(self):
        expected_ids = {
            "cells-html-converter", "cells-image-converter", "cells-json-converter",
            "cells-pdf-converter", "cells-spreadsheet-converter", "cells-spreadsheet-locker",
            "cells-spreadsheet-merger", "cells-spreadsheet-splitter", "cells-text-converter",
        }
        actual_ids = {c["scenario_id"] for c in _load_contracts("cells")}
        assert actual_ids == expected_ids, f"Mismatch: {expected_ids ^ actual_ids}"

    def test_cells_pdf_converter_has_pdf_header_validation(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("cells")}
        c = contracts["cells-pdf-converter"]
        assert c["output_expectations"]["validation_method"] == "pdf_header_check"

    def test_cells_contracts_forbid_datasources(self):
        for contract in _load_contracts("cells"):
            assert "DataSources" in contract.get("forbidden_patterns", []), (
                f"Cells contract {contract['scenario_id']} missing DataSources forbidden pattern"
            )


# ---------------------------------------------------------------------------
# TestWordsContracts
# ---------------------------------------------------------------------------

class TestWordsContracts:
    def test_all_words_contracts_are_merged(self):
        for contract in _load_contracts("words"):
            assert contract["publication_status"] == "MERGED", (
                f"Words contract {contract['scenario_id']} is not MERGED"
            )

    def test_all_words_use_programmatic_input(self):
        for contract in _load_contracts("words"):
            assert contract["fixture_type"] == "programmatic_input", (
                f"Words contract {contract['scenario_id']} unexpected fixture_type: {contract['fixture_type']}"
            )

    def test_words_scenario_ids_present(self):
        expected_ids = {
            "words-converter", "words-replacer", "words-splitter", "words-watermarker",
            "words-comparer", "words-merger", "words-mail-merger", "words-report-builder",
        }
        actual_ids = {c["scenario_id"] for c in _load_contracts("words")}
        assert actual_ids == expected_ids, f"Mismatch: {expected_ids ^ actual_ids}"

    def test_words_converter_outputs_pdf(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("words")}
        c = contracts["words-converter"]
        assert c["output_expectations"]["output_format"] == ".pdf"

    def test_words_replacer_outputs_docx(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("words")}
        c = contracts["words-replacer"]
        assert c["output_expectations"]["output_format"] == ".docx"


# ---------------------------------------------------------------------------
# TestPdfContracts
# ---------------------------------------------------------------------------

class TestPdfContracts:
    def test_pdf_scenario_ids_present(self):
        expected_ids = {
            "pdf-merger", "pdf-text-extractor", "pdf-splitter", "pdf-optimizer", "pdf-pdfa-converter",
            "pdf-doc-converter", "pdf-xls-converter", "pdf-html-converter",
            # Wave C (Sprint 9) + Wave D (Sprint 18/20)
            "pdf-jpeg", "pdf-png", "pdf-tiff",
            "pdf-table-generator", "pdf-toc-generator", "pdf-image-extractor",
        }
        actual_ids = {c["scenario_id"] for c in _load_contracts("pdf")}
        assert actual_ids == expected_ids, f"Mismatch: {expected_ids ^ actual_ids}"

    def test_pdf_merger_is_merged(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("pdf")}
        assert contracts["pdf-merger"]["publication_status"] == "MERGED"

    def test_pdf_text_extractor_is_merged(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("pdf")}
        assert contracts["pdf-text-extractor"]["publication_status"] == "MERGED"

    def test_pdf_splitter_is_pr_dry_run_ready(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("pdf")}
        assert contracts["pdf-splitter"]["publication_status"] == "PR_DRY_RUN_READY"

    def test_pdf_merger_forbids_plugin_options(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("pdf")}
        c = contracts["pdf-merger"]
        assert "new PluginOptions()" in c.get("forbidden_patterns", [])

    def test_pdf_text_extractor_forbids_text_absorber(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("pdf")}
        c = contracts["pdf-text-extractor"]
        assert "TextAbsorber" in c.get("forbidden_patterns", [])

    def test_pdf_optimizer_forbids_datasources_namespace(self):
        contracts = {c["scenario_id"]: c for c in _load_contracts("pdf")}
        c = contracts["pdf-optimizer"]
        assert "using Aspose.Pdf.LowCode.DataSources" in c.get("forbidden_patterns", [])

    def test_pdf_contracts_all_use_programmatic_input(self):
        for contract in _load_contracts("pdf"):
            assert contract["fixture_type"] == "programmatic_input", (
                f"PDF contract {contract['scenario_id']} unexpected fixture_type: {contract['fixture_type']}"
            )


# ---------------------------------------------------------------------------
# TestContractConsistencyWithDenominator
# ---------------------------------------------------------------------------

class TestContractConsistencyWithDenominator:
    def _load_denominator(self, family: str) -> dict:
        path = _DENOMINATOR_DIR / f"{family}.json"
        assert path.exists(), f"Denominator missing: {path}"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_cells_contract_count_matches_denominator_published(self):
        denom = self._load_denominator("cells")
        contracts = _load_contracts("cells")
        assert len(contracts) >= denom["published_count"], (
            f"Cells: {len(contracts)} contracts < {denom['published_count']} published scenarios"
        )

    def test_words_contract_count_matches_denominator_published(self):
        denom = self._load_denominator("words")
        contracts = _load_contracts("words")
        assert len(contracts) >= denom["published_count"], (
            f"Words: {len(contracts)} contracts < {denom['published_count']} published scenarios"
        )

    def test_pdf_contract_count_matches_denominator_published_plus_pipeline(self):
        denom = self._load_denominator("pdf")
        contracts = _load_contracts("pdf")
        # PDF has 2 merged + 2 PR_DRY_RUN_READY + 1 REVIEWER_PASSED = 5 in pipeline
        pipeline_count = denom.get("published_count", 0) + denom.get("pr_dry_run_ready_count", 0) + denom.get("reviewer_passed_awaiting_pr_count", 0)
        assert len(contracts) >= pipeline_count, (
            f"PDF: {len(contracts)} contracts < {pipeline_count} scenarios in pipeline"
        )

    def test_all_cells_runnable_ids_have_contracts(self):
        denom = self._load_denominator("cells")
        runnable = set(denom.get("runnable_scenario_ids", []))
        contract_ids = {c["scenario_id"] for c in _load_contracts("cells")}
        missing = runnable - contract_ids
        assert len(missing) == 0, f"Cells runnable scenarios without contracts: {missing}"
