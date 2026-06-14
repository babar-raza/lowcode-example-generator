"""Tests for non-LowCode source-of-truth proof and gate (TC-P1-05).

Validates:
- write_nonlowcode_source_of_truth_proof writes correct JSON
- assert_nonlowcode_source_of_truth_eligible gate passes/fails correctly
- Warns (not fails) when plugin_page_hash is not populated
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.plugin_detector.proof_reporter import (
    SourceOfTruthGateError,
    write_nonlowcode_source_of_truth_proof,
    assert_nonlowcode_source_of_truth_eligible,
)


def _probe_confirmed_entry(slug: str = "generate-barcode") -> dict:
    return {
        "plugin_slug": slug,
        "status": "PROBE_CONFIRMED",
        "type_name": "BarcodeGenerator",
        "namespace": "Aspose.BarCode.Generation",
        "method_name": "Save",
        "confidence_score": 0.95,
        "probe_evidence": "path/to/proof.json",
        "assembly_fingerprint": "abc123",
        "plugin_page_hash": None,
    }


def _reflection_candidate_entry(slug: str = "recognize-barcode") -> dict:
    return {
        "plugin_slug": slug,
        "status": "REFLECTION_CANDIDATE",
        "type_name": "BarCodeReader",
        "namespace": "Aspose.BarCode.BarCodeRecognition",
        "method_name": "ReadBarCodes",
        "confidence_score": 0.88,
    }


class TestWriteProof:
    def test_write_proof_with_probe_confirmed(self, tmp_path: Path) -> None:
        entry = _probe_confirmed_entry()
        path = write_nonlowcode_source_of_truth_proof(
            family="barcode",
            registry_entries=[entry],
            verification_dir=tmp_path,
        )

        assert path.exists()
        proof = json.loads(path.read_text())
        assert proof["proof_type"] == "nonlowcode_registry"
        assert proof["family"] == "barcode"
        assert proof["registry_entry_count"] == 1
        assert proof["eligibility_status"] == "eligible"
        assert "generate-barcode" in proof["eligibility_reason"]
        assert proof["page_hash_source"] == "NOT_POPULATED"

    def test_write_proof_with_no_ready_entries(self, tmp_path: Path) -> None:
        entry = _reflection_candidate_entry()
        path = write_nonlowcode_source_of_truth_proof(
            family="barcode",
            registry_entries=[entry],
            verification_dir=tmp_path,
        )

        proof = json.loads(path.read_text())
        assert proof["eligibility_status"] == "not_eligible"
        assert proof["registry_entry_count"] == 0

    def test_write_proof_with_page_hash_populated(self, tmp_path: Path) -> None:
        entry = _probe_confirmed_entry()
        entry["plugin_page_hash"] = "sha256abc123"
        path = write_nonlowcode_source_of_truth_proof(
            family="barcode",
            registry_entries=[entry],
            verification_dir=tmp_path,
        )

        proof = json.loads(path.read_text())
        assert proof["page_hash_source"] == "website_catalog"
        assert proof["plugin_page_hash_count"] == 1


class TestAssertEligible:
    def test_assert_eligible_passes(self, tmp_path: Path) -> None:
        path = write_nonlowcode_source_of_truth_proof(
            family="barcode",
            registry_entries=[_probe_confirmed_entry()],
            verification_dir=tmp_path,
        )
        # Should not raise
        assert_nonlowcode_source_of_truth_eligible(str(path))

    def test_assert_fails_on_missing_file(self) -> None:
        with pytest.raises(SourceOfTruthGateError, match="not found"):
            assert_nonlowcode_source_of_truth_eligible("/nonexistent/proof.json")

    def test_assert_fails_on_invalid_json(self, tmp_path: Path) -> None:
        bad_path = tmp_path / "latest" / "barcode-nonlowcode-source-of-truth-proof.json"
        bad_path.parent.mkdir(parents=True)
        bad_path.write_text("{invalid json")

        with pytest.raises(SourceOfTruthGateError, match="invalid JSON"):
            assert_nonlowcode_source_of_truth_eligible(str(bad_path))

    def test_assert_fails_on_wrong_proof_type(self, tmp_path: Path) -> None:
        proof_path = tmp_path / "latest" / "test-proof.json"
        proof_path.parent.mkdir(parents=True)
        proof_path.write_text(json.dumps({
            "proof_type": "dll_reflection",
            "eligibility_status": "eligible",
            "registry_entry_count": 1,
        }))

        with pytest.raises(SourceOfTruthGateError, match="wrong proof_type"):
            assert_nonlowcode_source_of_truth_eligible(str(proof_path))

    def test_assert_fails_on_no_entries(self, tmp_path: Path) -> None:
        path = write_nonlowcode_source_of_truth_proof(
            family="barcode",
            registry_entries=[_reflection_candidate_entry()],
            verification_dir=tmp_path,
        )
        with pytest.raises(SourceOfTruthGateError, match="eligibility_status='not_eligible'"):
            assert_nonlowcode_source_of_truth_eligible(str(path))

    def test_assert_warns_on_missing_page_hash(self, tmp_path: Path, caplog) -> None:
        import logging

        path = write_nonlowcode_source_of_truth_proof(
            family="barcode",
            registry_entries=[_probe_confirmed_entry()],
            verification_dir=tmp_path,
        )
        with caplog.at_level(logging.WARNING):
            assert_nonlowcode_source_of_truth_eligible(str(path))

        assert any("plugin_page_hash not populated" in r.message for r in caplog.records)
