"""Tests for README audit gate — Sprint 60 Phase 4.

Covers:
- Gate blocks when no audit artifact exists
- Gate blocks when audit is shallow (size/presence only)
- Gate blocks when audit has failed records
- Gate passes when audit is content-based and all records pass
- Gate approval token bypass

Test names:
    test_gate_blocks_when_no_audit_artifact
    test_gate_blocks_when_audit_is_shallow
    test_gate_blocks_when_audit_has_failed_records
    test_gate_passes_with_content_based_audit
    test_gate_passes_with_partial_content_audit_and_approval
    test_approval_token_from_env_var
    test_gate_passes_for_family_with_content_audit
    test_shallow_audit_detection_size_only
    test_content_audit_detection_with_fields
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.publisher.readme_audit_gate import (
    BLOCKED_README_AUDIT_FAILED,
    BLOCKED_README_AUDIT_MISSING,
    BLOCKED_README_AUDIT_SHALLOW,
    README_AUDIT_ENV_VAR,
    README_AUDIT_EXPECTED_VALUE,
    _is_content_based_audit,
    check_readme_audit_gate,
)


def _make_content_audit(records: list[dict]) -> dict:
    return {"generated": "2026-05-21", "records": records}


def _content_record(scenario_id: str, audit_status: str = "MATCH") -> dict:
    return {
        "scenario_id": scenario_id,
        "family_in_readme": True,
        "workflow_type_in_readme": True,
        "package_id_in_readme": True,
        "content_audit": audit_status,
    }


def _shallow_record(scenario_id: str) -> dict:
    """Shallow (size/presence only) audit record — no content fields."""
    return {
        "scenario_id": scenario_id,
        "readme_present": True,
        "readme_size": 350,
    }


class TestGateBlocksWhenNoAuditArtifact(unittest.TestCase):
    """test_gate_blocks_when_no_audit_artifact"""

    def test_gate_blocks_when_no_audit_artifact(self):
        """Gate must block if no audit file exists for the family."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            (vdir / "latest").mkdir(parents=True)
            result = check_readme_audit_gate("cells", vdir)
        self.assertFalse(result["gate_passed"])
        self.assertEqual(result["blocked_reason"], BLOCKED_README_AUDIT_MISSING)

    def test_gate_reports_family_in_result(self):
        """Result must include the family name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            (vdir / "latest").mkdir(parents=True)
            result = check_readme_audit_gate("words", vdir)
        self.assertEqual(result["family"], "words")


class TestGateBlocksWhenAuditIsShallow(unittest.TestCase):
    """test_gate_blocks_when_audit_is_shallow"""

    def _write_shallow_audit(self, vdir: Path, family: str, records: list[dict]) -> Path:
        audit_dir = vdir / "latest" / "families" / family
        audit_dir.mkdir(parents=True)
        path = audit_dir / "readme-audit.json"
        path.write_text(json.dumps({"records": records}), encoding="utf-8")
        return path

    def test_gate_blocks_when_audit_is_shallow(self):
        """Gate must block if audit has only size/presence fields (no content checks)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            self._write_shallow_audit(vdir, "cells", [
                _shallow_record("cells-html-converter"),
                _shallow_record("cells-image-converter"),
            ])
            result = check_readme_audit_gate("cells", vdir)
        self.assertFalse(result["gate_passed"])
        self.assertEqual(result["blocked_reason"], BLOCKED_README_AUDIT_SHALLOW)
        self.assertFalse(result["audit_is_content_based"])


class TestGateBlocksWhenAuditHasFailedRecords(unittest.TestCase):
    """test_gate_blocks_when_audit_has_failed_records"""

    def _write_audit(self, vdir: Path, family: str, records: list[dict]) -> Path:
        audit_dir = vdir / "latest" / "families" / family
        audit_dir.mkdir(parents=True)
        path = audit_dir / "readme-audit.json"
        path.write_text(json.dumps({"records": records}), encoding="utf-8")
        return path

    def test_gate_blocks_when_audit_has_failed_records(self):
        """Gate must block if any record has content_audit=FAIL or NEEDS_REVIEW."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            self._write_audit(vdir, "pdf", [
                _content_record("pdf-doc-converter", "MATCH"),
                _content_record("pdf-image-extractor", "NEEDS_REVIEW"),
            ])
            result = check_readme_audit_gate("pdf", vdir)
        self.assertFalse(result["gate_passed"])
        self.assertEqual(result["blocked_reason"], BLOCKED_README_AUDIT_FAILED)


class TestGatePassesWithContentAudit(unittest.TestCase):
    """test_gate_passes_with_content_based_audit"""

    def _write_audit(self, vdir: Path, family: str, records: list[dict]) -> Path:
        audit_dir = vdir / "latest" / "families" / family
        audit_dir.mkdir(parents=True)
        path = audit_dir / "readme-audit.json"
        path.write_text(json.dumps({"records": records}), encoding="utf-8")
        return path

    def test_gate_passes_with_content_based_audit(self):
        """Gate must pass if audit is content-based and all records are MATCH."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            self._write_audit(vdir, "cells", [
                _content_record("cells-html-converter"),
                _content_record("cells-pdf-converter"),
                _content_record("cells-image-converter"),
            ])
            result = check_readme_audit_gate("cells", vdir)
        self.assertTrue(result["gate_passed"])
        self.assertIsNone(result["blocked_reason"])
        self.assertTrue(result["audit_is_content_based"])

    def test_gate_passes_for_family_with_content_audit(self):
        """Gate passes when audit covers expected records with content checks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            self._write_audit(vdir, "diagram", [
                _content_record("diagram-diagram-converter"),
                _content_record("diagram-pdf-converter"),
            ])
            result = check_readme_audit_gate("diagram", vdir)
        self.assertTrue(result["gate_passed"])
        self.assertEqual(result["audit_record_count"], 2)

    def test_gate_passes_with_partial_content_audit_and_approval(self):
        """Gate passes for NEEDS_REVIEW records if explicit approval provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            self._write_audit(vdir, "pdf", [
                _content_record("pdf-image-extractor", "NEEDS_REVIEW"),
            ])
            result = check_readme_audit_gate(
                "pdf", vdir,
                readme_push_approval=README_AUDIT_EXPECTED_VALUE,
            )
        self.assertTrue(result["gate_passed"])

    def test_approval_token_from_env_var(self):
        """Gate reads approval token from env var as fallback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir)
            audit_dir = vdir / "latest" / "families" / "slides"
            audit_dir.mkdir(parents=True)
            (audit_dir / "readme-audit.json").write_text(
                json.dumps({"records": [_content_record("slides-compress", "NEEDS_REVIEW")]}),
                encoding="utf-8",
            )
            with patch.dict(os.environ, {README_AUDIT_ENV_VAR: README_AUDIT_EXPECTED_VALUE}):
                result = check_readme_audit_gate("slides", vdir)
        self.assertTrue(result["gate_passed"])


class TestShallowAuditDetection(unittest.TestCase):
    """test_shallow_audit_detection_size_only"""

    def test_shallow_audit_detection_size_only(self):
        """Size/presence-only records are detected as shallow."""
        records = [_shallow_record("cells-html-converter")]
        self.assertFalse(_is_content_based_audit(records))

    def test_content_audit_detection_with_fields(self):
        """Records with content fields are detected as content-based."""
        records = [_content_record("cells-html-converter")]
        self.assertTrue(_is_content_based_audit(records))

    def test_mixed_records_detected_as_content_based(self):
        """If even one record has content fields, audit is considered content-based."""
        records = [
            _shallow_record("cells-html-converter"),
            _content_record("cells-pdf-converter"),
        ]
        self.assertTrue(_is_content_based_audit(records))

    def test_empty_records_not_content_based(self):
        """Empty records list is not content-based."""
        self.assertFalse(_is_content_based_audit([]))

    def test_sprint59_readme_audit_detected_as_shallow(self):
        """Sprint 59 readme-vs-authority.json format (presence+size only) = shallow."""
        sprint59_style_records = [
            {"scenario_id": "cells-html-converter", "readme_present": True, "readme_size": 350},
            {"scenario_id": "cells-pdf-converter", "readme_present": True, "readme_size": 300},
        ]
        self.assertFalse(
            _is_content_based_audit(sprint59_style_records),
            "Sprint 59 presence/size-only audit must be detected as shallow",
        )
