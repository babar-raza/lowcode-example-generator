"""Unit tests for plugin_detector: detector, proof_reporter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.plugin_detector.detector import (
    DetectionResult,
    detect_plugin_namespaces,
)
from plugin_examples.plugin_detector.proof_reporter import (
    SourceOfTruthGateError,
    assert_source_of_truth_eligible,
    write_product_inventory,
    write_source_of_truth_proof,
)


# --- Fixtures ---


def _make_catalog(namespaces: list[dict] | None = None) -> dict:
    """Create a test API catalog with given namespaces."""
    if namespaces is None:
        namespaces = [
            {
                "namespace": "Aspose.Cells.LowCode",
                "types": [
                    {
                        "name": "SpreadsheetLocker",
                        "full_name": "Aspose.Cells.LowCode.SpreadsheetLocker",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [
                            {
                                "name": "Process",
                                "return_type": "System.Void",
                                "is_static": True,
                                "is_obsolete": False,
                                "parameters": [],
                            },
                            {
                                "name": "Process",
                                "return_type": "System.Void",
                                "is_static": True,
                                "is_obsolete": False,
                                "parameters": [
                                    {"name": "options", "type": "LockOptions", "is_optional": False}
                                ],
                            },
                        ],
                        "constructors": [],
                        "properties": [],
                    },
                    {
                        "name": "LockOptions",
                        "full_name": "Aspose.Cells.LowCode.LockOptions",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [],
                        "constructors": [{"parameters": [], "is_obsolete": False}],
                        "properties": [
                            {
                                "name": "Password",
                                "type": "System.String",
                                "can_read": True,
                                "can_write": True,
                                "is_obsolete": False,
                            }
                        ],
                    },
                ],
            },
            {
                "namespace": "Aspose.Cells.LowCode.Converters",
                "types": [
                    {
                        "name": "PdfConverter",
                        "full_name": "Aspose.Cells.LowCode.Converters.PdfConverter",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [
                            {
                                "name": "Convert",
                                "return_type": "System.Void",
                                "is_static": True,
                                "is_obsolete": False,
                                "parameters": [],
                            }
                        ],
                        "constructors": [],
                        "properties": [],
                    }
                ],
            },
            {
                "namespace": "Aspose.Cells",
                "types": [
                    {
                        "name": "Workbook",
                        "full_name": "Aspose.Cells.Workbook",
                        "kind": "class",
                        "is_obsolete": False,
                        "methods": [
                            {
                                "name": "Save",
                                "return_type": "System.Void",
                                "is_static": False,
                                "is_obsolete": False,
                                "parameters": [],
                            }
                        ],
                        "constructors": [],
                        "properties": [],
                    }
                ],
            },
        ]

    return {
        "assembly_name": "Aspose.Cells",
        "assembly_version": "25.4.0.0",
        "target_framework": ".NETStandard,Version=v2.0",
        "namespaces": namespaces,
        "diagnostics": {
            "xml_documentation_loaded": True,
            "metadata_only": True,
        },
    }


CELLS_PATTERNS = [
    "Aspose.Cells.LowCode",
    "Aspose.Cells.LowCode.*",
    "Aspose.Cells.Plugins",
    "Aspose.Cells.Plugins.*",
]


def _run_detection_and_write(
    tmp_path: Path,
    catalog: dict | None = None,
    patterns: list[str] | None = None,
) -> tuple[DetectionResult, Path, Path]:
    """Helper: run detection and write both artifacts."""
    cat = catalog or _make_catalog()
    pats = patterns or CELLS_PATTERNS
    result = detect_plugin_namespaces(cat, pats)

    inv_path = write_product_inventory(
        family="cells",
        package_id="Aspose.Cells",
        resolved_version="25.4.0",
        detection_result=result,
        manifests_dir=tmp_path / "workspace" / "manifests",
    )

    proof_path = write_source_of_truth_proof(
        family="cells",
        package_id="Aspose.Cells",
        resolved_version="25.4.0",
        nupkg_sha256="abc123",
        selected_target_framework="netstandard2.0",
        dll_path="workspace/runs/test/extracted/cells/primary/Aspose.Cells.dll",
        xml_path="workspace/runs/test/extracted/cells/primary/Aspose.Cells.xml",
        xml_warning=None,
        dependency_count=2,
        dependency_paths=["dep1.dll", "dep2.dll"],
        api_catalog_path="workspace/manifests/api-catalogs/cells/25.4.0.json",
        detection_result=result,
        verification_dir=tmp_path / "workspace" / "verification",
    )

    return result, inv_path, proof_path


# --- Tests: detector ---


class TestDetector:
    def test_exact_namespace_match_marks_eligible(self):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, ["Aspose.Cells.LowCode"])
        assert result.is_eligible
        assert any(m.namespace == "Aspose.Cells.LowCode" for m in result.matched_namespaces)

    def test_glob_namespace_match_marks_eligible(self):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, ["Aspose.Cells.LowCode.*"])
        assert result.is_eligible
        assert any(
            m.namespace == "Aspose.Cells.LowCode.Converters"
            for m in result.matched_namespaces
        )

    def test_no_namespace_match_marks_not_eligible(self):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, ["Aspose.Words.LowCode"])
        assert not result.is_eligible

    def test_matched_namespace_list_is_correct(self):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, CELLS_PATTERNS)
        matched_ns = {m.namespace for m in result.matched_namespaces}
        assert "Aspose.Cells.LowCode" in matched_ns
        assert "Aspose.Cells.LowCode.Converters" in matched_ns
        # Aspose.Cells (root) should NOT match
        assert "Aspose.Cells" not in matched_ns

    def test_unmatched_patterns_recorded_with_reason(self):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, CELLS_PATTERNS)
        # Plugins and Plugins.* don't exist in this catalog
        unmatched_pats = [u["pattern"] for u in result.unmatched_patterns]
        assert "Aspose.Cells.Plugins" in unmatched_pats
        assert "Aspose.Cells.Plugins.*" in unmatched_pats
        for u in result.unmatched_patterns:
            assert "reason" in u

    def test_public_plugin_type_count_only_matched(self):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, CELLS_PATTERNS)
        # LowCode has 2 types, LowCode.Converters has 1 = 3 total
        assert result.public_plugin_type_count == 3

    def test_public_plugin_method_count_only_matched(self):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, CELLS_PATTERNS)
        # LowCode has 2 methods, Converters has 1 = 3 total
        assert result.public_plugin_method_count == 3


# --- Tests: proof_reporter writing ---


class TestProofReporterWriting:
    def test_product_inventory_written_to_workspace_manifests(self, tmp_path):
        _, inv_path, _ = _run_detection_and_write(tmp_path)
        assert inv_path.exists()
        assert "workspace" in str(inv_path)
        assert "manifests" in str(inv_path)
        assert inv_path.name == "product-inventory.json"

    def test_source_of_truth_proof_written_to_workspace_verification(self, tmp_path):
        _, _, proof_path = _run_detection_and_write(tmp_path)
        assert proof_path.exists()
        assert "workspace" in str(proof_path)
        assert "verification" in str(proof_path)
        assert "latest" in str(proof_path)
        assert proof_path.name == "cells-source-of-truth-proof.json"

    def test_proof_contains_required_fields(self, tmp_path):
        _, _, proof_path = _run_detection_and_write(tmp_path)
        with open(proof_path) as f:
            proof = json.load(f)
        required = [
            "package_id", "resolved_version", "nupkg_sha256",
            "selected_target_framework", "dll_path", "xml_path",
            "xml_warning", "dependency_count", "dependency_paths",
            "api_catalog_path", "namespace_count",
            "matched_plugin_namespaces", "public_plugin_type_count",
            "public_plugin_method_count", "eligibility_status",
            "eligibility_reason",
        ]
        for field in required:
            assert field in proof, f"Missing field: {field}"

    def test_eligible_proof_status(self, tmp_path):
        _, _, proof_path = _run_detection_and_write(tmp_path)
        with open(proof_path) as f:
            proof = json.load(f)
        assert proof["eligibility_status"] == "eligible"

    def test_not_eligible_proof_status(self, tmp_path):
        catalog = _make_catalog()
        result = detect_plugin_namespaces(catalog, ["Aspose.Words.LowCode"])
        proof_path = write_source_of_truth_proof(
            family="words",
            package_id="Aspose.Words",
            resolved_version="25.4.0",
            nupkg_sha256="def456",
            selected_target_framework="netstandard2.0",
            dll_path=None,
            xml_path=None,
            xml_warning=None,
            dependency_count=0,
            dependency_paths=[],
            api_catalog_path=None,
            detection_result=result,
            verification_dir=tmp_path / "workspace" / "verification",
        )
        with open(proof_path) as f:
            proof = json.load(f)
        assert proof["eligibility_status"] == "not_eligible"
        assert "reason" in proof["eligibility_reason"].lower() or len(proof["eligibility_reason"]) > 0


# --- Tests: downstream gate ---


class TestDownstreamGate:
    def test_missing_proof_file_fails_gate(self, tmp_path):
        with pytest.raises(SourceOfTruthGateError, match="not found"):
            assert_source_of_truth_eligible(str(tmp_path / "nonexistent.json"))

    def test_not_eligible_proof_fails_gate(self, tmp_path):
        proof_path = tmp_path / "proof.json"
        proof_path.write_text(json.dumps({
            "eligibility_status": "not_eligible",
            "eligibility_reason": "No plugin namespaces matched",
        }))
        with pytest.raises(SourceOfTruthGateError, match="not_eligible"):
            assert_source_of_truth_eligible(str(proof_path))

    def test_eligible_proof_passes_gate(self, tmp_path):
        _, _, proof_path = _run_detection_and_write(tmp_path)
        # Should not raise
        assert_source_of_truth_eligible(str(proof_path))

    def test_invalid_json_fails_gate(self, tmp_path):
        proof_path = tmp_path / "proof.json"
        proof_path.write_text("not valid json {{{")
        with pytest.raises(SourceOfTruthGateError, match="invalid JSON"):
            assert_source_of_truth_eligible(str(proof_path))

    def test_missing_eligibility_status_fails_gate(self, tmp_path):
        proof_path = tmp_path / "proof.json"
        proof_path.write_text(json.dumps({"some_field": "value"}))
        with pytest.raises(SourceOfTruthGateError, match="missing"):
            assert_source_of_truth_eligible(str(proof_path))


# --- Tests: path correctness ---


class TestPathCorrectness:
    def test_old_root_paths_not_created(self, tmp_path):
        _run_detection_and_write(tmp_path)
        for old_dir in ["configs", "schemas", "prompts", "runs", "manifests", "verification"]:
            assert not (tmp_path / old_dir).exists(), f"Old root path created: {old_dir}"
