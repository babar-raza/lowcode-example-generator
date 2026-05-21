"""Tests for EvidenceValidator — Sprint 60 Phase 5.

Covers all Sprint 59 false-complete failure modes:
- test_fails_when_final_clean_proof_missing
- test_fails_when_final_clean_proof_shows_dirty_state
- test_fails_when_present_no_authority_exists
- test_fails_when_readme_audit_is_shallow
- test_fails_when_readme_gate_evidence_missing
- test_fails_when_todo_has_unchecked_items
- test_fails_when_validator_output_missing
- test_fails_when_commands_log_in_progress
- test_fails_when_test_log_missing
- test_fails_when_unknown_input_formats_nonzero
- test_passes_with_complete_valid_bundle
- test_overall_valid_false_on_any_failure
- test_sprint59_style_bundle_detected_as_invalid
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.evidence_validator import EvidenceValidator


def _make_bundle(tmpdir: str) -> Path:
    """Create a minimal valid bundle directory structure."""
    b = Path(tmpdir)

    # git/final-clean-proof.txt — clean
    (b / "git").mkdir(parents=True)
    (b / "git" / "final-clean-proof.txt").write_text(
        "On branch main\nnothing to commit, working tree clean\n",
        encoding="utf-8",
    )

    # destination/content-audit-repaired.json — 42/42
    (b / "destination").mkdir(parents=True)
    (b / "destination" / "content-audit-repaired.json").write_text(
        json.dumps({
            "authority_mapped": "42/42",
            "present_no_authority": 0,
            "total_examples": 42,
            "examples": [
                {"scenario_id": f"scenario-{i}", "content_match": "MATCH"}
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # readme/example-readme-content-audit.json — content-based
    (b / "readme").mkdir(parents=True)
    (b / "readme" / "example-readme-content-audit.json").write_text(
        json.dumps({
            "records": [
                {
                    "scenario_id": "cells-html-converter",
                    "family_in_readme": True,
                    "workflow_type_in_readme": True,
                    "package_id_in_readme": True,
                    "content_audit": "MATCH",
                }
            ]
        }),
        encoding="utf-8",
    )
    (b / "readme" / "readme-gate-implementation.md").write_text("# Gate\n", encoding="utf-8")
    (b / "readme" / "readme-gate-test-results.txt").write_text("13 passed, 0 failed\n", encoding="utf-8")
    (b / "readme" / "readme-gate-source-proof.patch").write_text("diff --git a/src ...\n", encoding="utf-8")

    # evidence/validator-test-results.txt
    (b / "evidence").mkdir(parents=True)
    (b / "evidence" / "validator-test-results.txt").write_text(
        "12 passed, 0 failed in 0.23s\n", encoding="utf-8"
    )

    # todo.md — all checked
    (b / "todo.md").write_text(
        "- [x] Phase 0 complete\n- [x] Phase 1 complete\n",
        encoding="utf-8",
    )

    # commands.log — complete (no IN_PROGRESS)
    (b / "commands.log").write_text("phase0: done\nphase1: done\n", encoding="utf-8")

    # lanes/lane-I/test-run.log
    (b / "lanes" / "lane-I").mkdir(parents=True)
    (b / "lanes" / "lane-I" / "test-run.log").write_text(
        "2826 passed, 0 failed, 3 skipped\n", encoding="utf-8"
    )

    # sprint-state.json
    (b / "sprint-state.json").write_text(
        json.dumps({"sprint_id": "sprint60-test"}), encoding="utf-8"
    )

    # Pad to >=35 files
    for i in range(40):
        (b / f"pad-{i:02d}.txt").write_text(f"pad {i}\n", encoding="utf-8")

    return b


class TestFinalCleanProof(unittest.TestCase):
    def test_fails_when_final_clean_proof_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_after_final_commit")
        self.assertFalse(rule.passed)
        self.assertIn("not found", rule.failure_detail.lower())

    def test_fails_when_final_clean_proof_shows_dirty_state(self):
        """Sprint 59 defect SD59-01: git-status.txt captured before final commit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "On branch main\nmodified: workspace/verification/latest/release-status.json\n"
                "?? reports/sprint59/\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_after_final_commit")
        self.assertFalse(rule.passed)
        self.assertIn("dirty", rule.failure_detail.lower())

    def test_passes_when_clean_proof_is_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_after_final_commit")
        self.assertTrue(rule.passed)


class TestPresentNoAuthority(unittest.TestCase):
    def test_fails_when_present_no_authority_exists(self):
        """Sprint 59 defect SD59-02: 3 PRESENT_NO_AUTHORITY entries in destination audit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "39/42",
                    "present_no_authority": 3,
                    "total_examples": 42,
                    "examples": [
                        {"scenario_id": "diagram-diagram-diagram-converter",
                         "content_match": "PRESENT_NO_AUTHORITY"},
                        {"scenario_id": "pdf-pdfa-converter",
                         "content_match": "PRESENT_NO_AUTHORITY"},
                        {"scenario_id": "diagram-diagram-pdf-converter",
                         "content_match": "PRESENT_NO_AUTHORITY"},
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_present_no_authority")
        self.assertFalse(rule.passed)
        self.assertIn("3", rule.failure_detail)

    def test_passes_when_no_present_no_authority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_present_no_authority")
        self.assertTrue(rule.passed)


class TestReadmeAuditContentBased(unittest.TestCase):
    def test_fails_when_readme_audit_is_shallow(self):
        """Sprint 59 defect SD59-03: README audit was presence/size only, not content-based."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Write shallow (Sprint 59-style) audit records
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({
                    "records": [
                        {
                            "scenario_id": "cells-html-converter",
                            "readme_present": True,
                            "readme_size": 350,
                        },
                        {
                            "scenario_id": "cells-pdf-converter",
                            "readme_present": True,
                            "readme_size": 300,
                        },
                    ]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_audit_content_based")
        self.assertFalse(rule.passed)
        self.assertIn("size/presence", rule.failure_detail)

    def test_fails_when_readme_audit_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "example-readme-content-audit.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_audit_content_based")
        self.assertFalse(rule.passed)
        self.assertIn("not found", rule.failure_detail.lower())

    def test_passes_when_content_audit_has_content_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_audit_content_based")
        self.assertTrue(rule.passed)


class TestReadmeGateImplemented(unittest.TestCase):
    def test_fails_when_readme_gate_evidence_missing(self):
        """Sprint 59 defect SD59-04: README gate was documented but not wired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-source-proof.patch").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_implemented_and_tested")
        self.assertFalse(rule.passed)
        self.assertIn("readme-gate-source-proof.patch", rule.failure_detail)

    def test_fails_when_gate_test_results_show_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-test-results.txt").write_text(
                "3 passed, 2 failed\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_implemented_and_tested")
        self.assertFalse(rule.passed)

    def test_passes_when_all_gate_evidence_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_implemented_and_tested")
        self.assertTrue(rule.passed)


class TestTodoAllChecked(unittest.TestCase):
    def test_fails_when_todo_has_unchecked_items(self):
        """Sprint 59 defect SD59-06: todo.md had unchecked [ ] items despite work done."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "todo.md").write_text(
                "- [x] Phase 0 complete\n"
                "- [ ] Phase 1 README gate wiring\n"
                "- [ ] Phase 2 bundle commit\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "todo_all_items_checked_or_carried")
        self.assertFalse(rule.passed)
        self.assertIn("2", rule.failure_detail)

    def test_fails_when_todo_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "todo.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "todo_all_items_checked_or_carried")
        self.assertFalse(rule.passed)

    def test_passes_when_all_items_checked(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "todo_all_items_checked_or_carried")
        self.assertTrue(rule.passed)


class TestEvidenceValidatorActuallyRan(unittest.TestCase):
    def test_fails_when_validator_output_missing(self):
        """Sprint 59 defect SD59-07: validation_rules_passed was hardcoded, not run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "validator-test-results.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_actually_ran")
        self.assertFalse(rule.passed)

    def test_fails_when_output_not_test_output(self):
        """Validator output that looks like a hardcoded list, not test output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "validator-test-results.txt").write_text(
                "validation_rules_passed:\n- final_clean_proof_after_final_commit\n- bundle_min_files\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_actually_ran")
        self.assertFalse(rule.passed)

    def test_passes_when_real_test_output_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_actually_ran")
        self.assertTrue(rule.passed)


class TestCommandsLog(unittest.TestCase):
    def test_fails_when_commands_log_in_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").write_text(
                "phase0: done\nphase1: IN_PROGRESS\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_complete")
        self.assertFalse(rule.passed)

    def test_fails_when_commands_log_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "commands_log_complete")
        self.assertFalse(rule.passed)


class TestTestLog(unittest.TestCase):
    def test_fails_when_test_log_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "lanes" / "lane-I" / "test-run.log").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "test_log_zero_failed")
        self.assertFalse(rule.passed)

    def test_fails_when_test_log_shows_failures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "lanes" / "lane-I" / "test-run.log").write_text(
                "2800 passed, 26 failed, 3 skipped\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "test_log_zero_failed")
        self.assertFalse(rule.passed)


class TestUnknownInputFormats(unittest.TestCase):
    def test_fails_when_unknown_input_formats_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "io-authority").mkdir(parents=True)
            (b / "io-authority" / "input-format-authority-matrix.json").write_text(
                json.dumps({"unknown_input_formats": 42, "total_types": 42}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "zero_unknown_input_formats")
        self.assertFalse(rule.passed)

    def test_passes_when_all_formats_known(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "io-authority").mkdir(parents=True)
            (b / "io-authority" / "input-format-authority-matrix.json").write_text(
                json.dumps({"unknown_input_formats": 0, "total_types": 42}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "zero_unknown_input_formats")
        self.assertTrue(rule.passed)


class TestCompleteBundle(unittest.TestCase):
    def test_passes_with_complete_valid_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        self.assertTrue(result.overall_valid)
        self.assertEqual(result.failed, 0)
        self.assertEqual(result.total_rules, 12)

    def test_overall_valid_false_on_any_failure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Introduce a single failure
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)
        self.assertGreater(result.failed, 0)

    def test_sprint59_style_bundle_detected_as_invalid(self):
        """A Sprint 59-style bundle (documented but not implemented gate, shallow audit, dirty proof)
        must be detected as invalid by EvidenceValidator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Sprint 59 defect SD59-01: dirty proof
            (b / "git" / "final-clean-proof.txt").write_text(
                "modified: workspace/verification/latest/release-status.json\n",
                encoding="utf-8",
            )
            # Sprint 59 defect SD59-03: shallow README audit
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({
                    "records": [
                        {"scenario_id": "cells-html-converter", "readme_present": True, "readme_size": 350}
                    ]
                }),
                encoding="utf-8",
            )
            # Sprint 59 defect SD59-04: gate not wired (no source proof)
            (b / "readme" / "readme-gate-source-proof.patch").unlink()
            # Sprint 59 defect SD59-06: unchecked items in todo
            (b / "todo.md").write_text("- [ ] Phase 4 README gate wiring\n", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)
        # Should catch at least 4 failures
        self.assertGreaterEqual(result.failed, 4)

    def test_to_dict_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        d = result.to_dict()
        self.assertIn("bundle_dir", d)
        self.assertIn("sprint_id", d)
        self.assertIn("overall_valid", d)
        self.assertIn("rules", d)
        self.assertEqual(len(d["rules"]), 12)
