"""Tests for EvidenceContractComputer — Sprint 63 Phase 1 + Sprint 64 fixes.

Verifies that:
- PENDING blocking category fails closure
- Missing required file fails closure
- Zero-byte required file fails closure
- Present-but-semantically-invalid file fails closure
- All categories present and semantically valid passes closure
- Semantic: IN_PROGRESS detected
- Semantic: unchecked [ ] items detected
- Semantic: 0 failed test output required
- Semantic: overall_valid=false required
- Semantic: overall_valid=true + no internal contradiction required

Sprint 64 additions:
- Semantic "0 failed": accepts "N passed" with no failures (pytest format)
- Semantic "6 families": accepts dict-keyed index (family names as top-level keys)
- Contract format: supports both "contract_id"/"categories" and "sprint_id"/"required_evidence_categories"
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.evidence_contract_computer import (
    EvidenceContractComputer,
    CategoryResult,
)


def _make_contract(tmpdir: str, categories: list[dict]) -> Path:
    """Write a minimal evidence-contract.json to tmpdir."""
    contract = {
        "sprint_id": "test-sprint",
        "required_evidence_categories": categories,
    }
    p = Path(tmpdir) / "reports" / "test" / "evidence-contract.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(contract), encoding="utf-8")
    return p


class TestPendingBlocksClosure(unittest.TestCase):
    """PENDING blocking category must block closure."""

    def test_pending_category_is_blocking_failure(self):
        """A PENDING category (file does not exist) is a blocking failure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "test_file",
                        "blocking": True,
                        "file": "reports/test/nonexistent.md",
                        "status": "PENDING",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertFalse(result.closure_valid)
        self.assertEqual(result.blocking_failures, 1)
        self.assertEqual(result.categories[0].status, "MISSING")

    def test_non_blocking_pending_does_not_block_closure(self):
        """A PENDING non-blocking category does not prevent closure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid file for EC01
            p = Path(tmpdir) / "reports" / "test" / "existing.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# content\n", encoding="utf-8")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "existing",
                        "blocking": True,
                        "file": "reports/test/existing.md",
                        "status": "PENDING",
                    },
                    {
                        "id": "EC02",
                        "name": "missing_nonblocking",
                        "blocking": False,
                        "file": "reports/test/nonexistent.md",
                        "status": "PENDING",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertTrue(result.closure_valid)
        self.assertEqual(result.blocking_failures, 0)


class TestMissingFileBlocksClosure(unittest.TestCase):
    """Missing required file must fail closure."""

    def test_missing_file_is_missing_status(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "missing",
                        "blocking": True,
                        "file": "does/not/exist.json",
                        "status": "PENDING",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "MISSING")
        self.assertFalse(result.closure_valid)


class TestZeroBytesBlocksClosure(unittest.TestCase):
    """Zero-byte required file must fail closure."""

    def test_zero_byte_file_fails(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "reports" / "empty.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("", encoding="utf-8")  # 0 bytes
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "empty",
                        "blocking": True,
                        "file": "reports/empty.md",
                        "status": "PENDING",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "ZERO_BYTES")
        self.assertFalse(result.closure_valid)


class TestSemanticValidation(unittest.TestCase):
    """Semantic validation failures must produce SEMANTIC_FAILED status."""

    def _make_file(self, tmpdir: str, rel_path: str, content: str) -> str:
        p = Path(tmpdir) / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return rel_path

    def test_in_progress_marker_fails(self):
        """commands.log with IN_PROGRESS fails semantic validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/cmd.log", "phase 0: done\nphase 1: IN_PROGRESS\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "commands_log",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must not contain IN_PROGRESS at closure",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")
        self.assertFalse(result.closure_valid)

    def test_unchecked_todo_fails(self):
        """todo.md with unchecked [ ] items fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/todo.md", "- [x] Done\n- [ ] Not done\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "todo",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must have no unchecked [ ] items",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")

    def test_test_log_with_failures_fails(self):
        """Test log with failures fails '0 failed' semantic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/test.log", "10 passed, 3 failed in 5s\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "test_log",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show 0 failed",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")

    def test_test_log_zero_failed_passes(self):
        """Test log with 0 failed passes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/test.log", "2956 passed, 3 skipped, 0 failed in 111s\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "test_log",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show 0 failed",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "PRESENT")

    def test_overall_valid_false_required_passes(self):
        """overall_valid=false semantic passes when JSON has overall_valid=false."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/result.json", json.dumps({"overall_valid": False, "failed": 3}))
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "revalidation",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show overall_valid=false",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "PRESENT")

    def test_overall_valid_true_required_fails_when_false(self):
        """overall_valid=true semantic fails when JSON has overall_valid=false."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(
                tmpdir, "reports/result.json", json.dumps({"overall_valid": False, "failed": 1, "rules": []})
            )
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "result",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show overall_valid=true, no internal contradiction",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")

    def test_internal_contradiction_detected(self):
        """overall_valid=true with a FAILURE rule passed=false is contradictory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # This is the Sprint 62 defect pattern
            contradictory = {
                "overall_valid": True,
                "failed": 0,
                "passed": 21,
                "rules": [
                    {"rule_id": "good_rule", "severity": "FAILURE", "passed": True},
                    {"rule_id": "bad_rule", "severity": "FAILURE", "passed": False},
                ],
            }
            rel = self._make_file(tmpdir, "reports/result.json", json.dumps(contradictory))
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "result",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show overall_valid=true, no internal contradiction",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")
        self.assertIn("contradiction", result.categories[0].detail.lower())

    def test_no_contradiction_when_all_rules_pass(self):
        """overall_valid=true with all FAILURE rules passed=true is valid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            valid_result = {
                "overall_valid": True,
                "failed": 0,
                "passed": 2,
                "rules": [
                    {"rule_id": "rule_a", "severity": "FAILURE", "passed": True},
                    {"rule_id": "rule_b", "severity": "FAILURE", "passed": True},
                ],
            }
            rel = self._make_file(tmpdir, "reports/result.json", json.dumps(valid_result))
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "result",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show overall_valid=true, no internal contradiction",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "PRESENT")


class TestAllPresentPasses(unittest.TestCase):
    """All categories present and valid must report closure_valid=True."""

    def test_all_present_passes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            p1 = Path(tmpdir) / "reports" / "file1.md"
            p2 = Path(tmpdir) / "reports" / "file2.json"
            p1.parent.mkdir(parents=True, exist_ok=True)
            p1.write_text("# content\n", encoding="utf-8")
            p2.write_text('{"data": 1}', encoding="utf-8")
            contract_path = _make_contract(
                tmpdir,
                [
                    {"id": "EC01", "name": "file1", "blocking": True, "file": "reports/file1.md", "status": "PENDING"},
                    {
                        "id": "EC02",
                        "name": "file2",
                        "blocking": True,
                        "file": "reports/file2.json",
                        "status": "PENDING",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertTrue(result.closure_valid)
        self.assertEqual(result.blocking_failures, 0)
        self.assertEqual(result.present_count, 2)
        self.assertEqual(result.missing_count, 0)


def _make_contract_new_format(tmpdir: str, categories: list[dict]) -> Path:
    """Write a contract using the new sprint64 format (contract_id/categories)."""
    contract = {
        "contract_id": "test-sprint64",
        "sprint_id": "test-sprint64",
        "categories": categories,
    }
    p = Path(tmpdir) / "reports" / "test64" / "evidence-contract.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(contract), encoding="utf-8")
    return p


class TestSprint64PytestZeroFailedFix(unittest.TestCase):
    """Sprint 64: 'must show 0 failed' should accept pytest 'N passed' format.

    Pytest omits '0 failed' entirely when all tests pass — it outputs
    e.g. '2976 passed, 3 skipped in 96.19s'. The old regex only matched
    literal '0 failed', causing false SEMANTIC_FAILED for valid test logs.
    """

    def _make_file(self, tmpdir: str, rel_path: str, content: str) -> str:
        p = Path(tmpdir) / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return rel_path

    def test_pytest_passed_no_failed_line_is_passing(self):
        """'2976 passed, 3 skipped in 96.19s' with no 'failed' = passing test run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/test.log", "2976 passed, 3 skipped in 96.19s\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "test_log",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show 0 failed",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(
            result.categories[0].status,
            "PRESENT",
            f"Expected PRESENT, got SEMANTIC_FAILED: {result.categories[0].detail}",
        )

    def test_pytest_n_passed_in_Xs_passes(self):
        """'76 passed in 12.07s' (no skipped line) is a valid pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/test.log", "76 passed in 12.07s\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "test_log",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show 0 failed",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(
            result.categories[0].status, "PRESENT", f"Expected PRESENT, got: {result.categories[0].detail}"
        )

    def test_log_with_failures_still_fails(self):
        """'10 passed, 3 failed in 5s' must still fail semantic validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/test.log", "10 passed, 3 failed in 5s\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "test_log",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show 0 failed",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")

    def test_empty_log_no_passed_no_failed_fails(self):
        """A test log with neither 'passed' nor 'failed' fails semantic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/test.log", "Running tests...\nDone.\n")
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "test_log",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must show 0 failed",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")


class TestSprint64FamiliesDictKeyFix(unittest.TestCase):
    """Sprint 64: '6 families' check should work with dict-keyed package-artifact-index.json.

    Sprint 63 defect: data.get('families', []) returned [] because the JSON used
    family names as top-level keys, not a list under 'families'. The fix counts
    known family names as top-level keys.
    """

    def _make_file(self, tmpdir: str, rel_path: str, content: str) -> str:
        p = Path(tmpdir) / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return rel_path

    def test_dict_keyed_6_families_passes(self):
        """package-artifact-index.json with 6 top-level family keys passes."""
        pkg_index = {
            "cells": {"total_files": 9, "program_cs_count": 9},
            "diagram": {"total_files": 2, "program_cs_count": 2},
            "email": {"total_files": 1, "program_cs_count": 1},
            "pdf": {"total_files": 19, "program_cs_count": 17},
            "slides": {"total_files": 3, "program_cs_count": 3},
            "words": {"total_files": 8, "program_cs_count": 8},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/pkg-index.json", json.dumps(pkg_index))
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "pkg_index",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must list 6 families with file counts",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(
            result.categories[0].status, "PRESENT", f"Expected PRESENT, got: {result.categories[0].detail}"
        )

    def test_dict_keyed_only_4_families_fails(self):
        """Only 4 family keys fails the 6 families check."""
        pkg_index = {
            "cells": {"total_files": 9},
            "diagram": {"total_files": 2},
            "email": {"total_files": 1},
            "pdf": {"total_files": 19},
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/pkg-index.json", json.dumps(pkg_index))
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "pkg_index",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must list 6 families with file counts",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.categories[0].status, "SEMANTIC_FAILED")

    def test_legacy_families_list_key_still_works(self):
        """Legacy format with 'families' key (list of 6) still passes."""
        pkg_index = {
            "families": ["cells", "diagram", "email", "pdf", "slides", "words"],
            "total_files": 42,
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            rel = self._make_file(tmpdir, "reports/pkg-index.json", json.dumps(pkg_index))
            contract_path = _make_contract(
                tmpdir,
                [
                    {
                        "id": "EC01",
                        "name": "pkg_index",
                        "blocking": True,
                        "file": rel,
                        "status": "PENDING",
                        "semantic": "must list 6 families with file counts",
                    },
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(
            result.categories[0].status, "PRESENT", f"Expected PRESENT, got: {result.categories[0].detail}"
        )


class TestSprint64ContractFormatFix(unittest.TestCase):
    """Sprint 64: ECC should support both contract formats.

    - Legacy: "sprint_id" + "required_evidence_categories"
    - New: "contract_id" + "categories"
    """

    def test_new_format_contract_id_and_categories(self):
        """contract_id + categories format is read correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "reports" / "file.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# content\n", encoding="utf-8")
            contract_path = _make_contract_new_format(
                tmpdir,
                [
                    {"id": "EC01", "name": "file", "blocking": True, "file": "reports/file.md", "status": "PENDING"},
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.contract_id, "test-sprint64")
        self.assertTrue(result.closure_valid)
        self.assertEqual(result.total_categories, 1)

    def test_legacy_format_still_works(self):
        """sprint_id + required_evidence_categories format still works."""
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "reports" / "file.md"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# content\n", encoding="utf-8")
            contract_path = _make_contract(
                tmpdir,
                [
                    {"id": "EC01", "name": "file", "blocking": True, "file": "reports/file.md", "status": "PENDING"},
                ],
            )
            computer = EvidenceContractComputer(contract_path, Path(tmpdir))
            result = computer.compute()
        self.assertEqual(result.contract_id, "test-sprint")
        self.assertTrue(result.closure_valid)
