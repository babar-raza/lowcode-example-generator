"""Tests for EvidenceValidator — Sprint 60 Phase 5 + Sprint 61 Phase 2.

Covers all Sprint 59 false-complete failure modes (original 12 rules):
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

Sprint 61 new rules (8 additional semantic rules):
- TestFinalCleanProofNonzeroBytes — SD60-01: 0-byte file is not proof
- TestFinalCleanProofHasGitHeader — SD60-01: requires actual git output
- TestReadmeIOFormatNotFalselyComplete — SD60-02: MATCH without I/O docs = FAIL
- TestReadmeGateWiredInPipeline — SD60-03: standalone-only gate is not a gate
- TestEvidenceValidatorWiredInPipeline — SD60-04: standalone-only validator is not a gate
- TestDestinationProgramcsInputNotAllNull — SD60-05: null-for-all = audit not done
- TestNoPriOneItemsWithCompleteVerdict — SD60-08: P1 open + COMPLETE = contradiction
- TestRequiredFilesNonzeroSize — SD60-01 contributory: 0-byte required files
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
    """Create a minimal valid bundle directory structure (passes all 20 rules)."""
    b = Path(tmpdir)

    # git/final-clean-proof.txt — clean (nonzero, has git header)
    (b / "git").mkdir(parents=True)
    (b / "git" / "final-clean-proof.txt").write_text(
        "On branch main\nnothing to commit, working tree clean\n",
        encoding="utf-8",
    )

    # destination/content-audit-repaired.json — 42/42, with non-null input_format_in_programcs
    (b / "destination").mkdir(parents=True)
    (b / "destination" / "content-audit-repaired.json").write_text(
        json.dumps({
            "authority_mapped": "42/42",
            "present_no_authority": 0,
            "total_examples": 42,
            "examples": [
                {
                    "scenario_id": f"scenario-{i}",
                    "content_match": "MATCH",
                    "input_format_in_programcs": ".docx",
                    "input_classification": "AddInput",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # readme/example-readme-content-audit.json — content-based (no I/O fields = WARNING/pass)
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
    # readme-gate-flow-integration.md — confirms gate is wired (no "not wired"/"deferred"/"p1")
    (b / "readme" / "readme-gate-flow-integration.md").write_text(
        "# README Gate Flow Integration\nGate is called in publish-pr live mode.\n",
        encoding="utf-8",
    )

    # evidence/validator-test-results.txt + pipeline-integration-proof.md + bundle-validation-result.json
    (b / "evidence").mkdir(parents=True)
    (b / "evidence" / "validator-test-results.txt").write_text(
        "20 passed, 0 failed in 0.45s\n", encoding="utf-8"
    )
    (b / "evidence" / "pipeline-integration-proof.md").write_text(
        "# Pipeline Integration\nEvidenceValidator is called in release-status command.\n",
        encoding="utf-8",
    )
    (b / "evidence" / "sprint60-bundle-validation-result.json").write_text(
        json.dumps({
            "sprint_id": "sprint60-test",
            "overall_valid": True,
            "passed": 21,
            "failed": 0,
            "warnings": 0,
            "total_rules": 21,
            "rules": [],
        }),
        encoding="utf-8",
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
        self.assertEqual(result.total_rules, 21)

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

    def test_sprint60_style_bundle_detected_as_invalid(self):
        """A Sprint 60-style bundle (empty clean proof, null programcs, gate not wired,
        P1 items with COMPLETE verdict) must be detected as invalid."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # SD60-01: empty clean proof
            (b / "git" / "final-clean-proof.txt").write_text("", encoding="utf-8")
            # SD60-05: all-null programcs input
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "42/42",
                    "present_no_authority": 0,
                    "total_examples": 42,
                    "examples": [
                        {
                            "scenario_id": f"scenario-{i}",
                            "content_match": "MATCH",
                            "input_format_in_programcs": None,
                            "input_classification": None,
                        }
                        for i in range(42)
                    ],
                }),
                encoding="utf-8",
            )
            # SD60-03: gate not wired (remove flow integration proof, no source_root)
            (b / "readme" / "readme-gate-flow-integration.md").unlink()
            # SD60-04: validator not wired (remove pipeline integration proof)
            (b / "evidence" / "pipeline-integration-proof.md").unlink()
            # SD60-08: P1 items with complete verdict
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README gate CLI wiring | P1 | OPEN |\n",
                encoding="utf-8",
            )
            (b / "final-verdict.md").write_text(
                "Verdict: LOWCODE_IO_DESTINATION_README_CLOSURE_VERIFIED\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)
        # Should catch SD60-01 (x3 rules), SD60-03, SD60-04, SD60-05, SD60-08 = at least 7 failures
        self.assertGreaterEqual(result.failed, 5)

    def test_to_dict_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        d = result.to_dict()
        self.assertIn("bundle_dir", d)
        self.assertIn("sprint_id", d)
        self.assertIn("overall_valid", d)
        self.assertIn("rules", d)
        self.assertEqual(len(d["rules"]), 21)


# ===========================================================================
# Sprint 61 NEW semantic rule tests
# ===========================================================================


class TestFinalCleanProofNonzeroBytes(unittest.TestCase):
    """Rule: final_clean_proof_nonzero_bytes — closes SD60-01."""

    def test_fails_when_proof_is_zero_bytes(self):
        """SD60-01: git status --short produces no output when clean → 0-byte file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_nonzero_bytes")
        self.assertFalse(rule.passed)
        self.assertIn("0 bytes", rule.failure_detail)
        self.assertIn("--short", rule.failure_detail)

    def test_fails_when_proof_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_nonzero_bytes")
        self.assertFalse(rule.passed)
        self.assertIn("not found", rule.failure_detail.lower())

    def test_passes_when_proof_is_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_nonzero_bytes")
        self.assertTrue(rule.passed)
        self.assertIn("bytes", rule.evidence)


class TestFinalCleanProofHasGitHeader(unittest.TestCase):
    """Rule: final_clean_proof_has_git_header — closes SD60-01 (content check)."""

    def test_fails_when_no_git_header_present(self):
        """Nonzero file without git output is not valid clean proof."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "Sprint 61 clean proof captured.\nAll done.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertFalse(rule.passed)
        self.assertIn("git status header", rule.failure_detail.lower())

    def test_fails_when_proof_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertFalse(rule.passed)

    def test_passes_with_on_branch_header(self):
        """Standard git status output: 'On branch main\nnothing to commit...'"""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertTrue(rule.passed)

    def test_passes_with_nothing_to_commit_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "nothing to commit, working tree clean\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertTrue(rule.passed)

    def test_passes_with_head_detached_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "git" / "final-clean-proof.txt").write_text(
                "HEAD detached at abc1234\nnothing to commit, working tree clean\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "final_clean_proof_has_git_header")
        self.assertTrue(rule.passed)


class TestReadmeIOFormatNotFalselyComplete(unittest.TestCase):
    """Rule: readme_io_format_not_falsely_complete — closes SD60-02."""

    def test_fails_when_high_io_gap_with_complete_match_claimed(self):
        """SD60-02: 22/42 input false + 100% MATCH claimed = false completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            total = 42
            records = [
                {
                    "scenario_id": f"s-{i}",
                    "family_in_readme": True,
                    "workflow_type_in_readme": True,
                    "package_id_in_readme": True,
                    "content_audit": "MATCH",
                    "input_format_in_readme": i >= 20,   # 22 False (i<20 plus 2)
                    "output_format_in_readme": i >= 19,  # 23 False
                }
                for i in range(total)
            ]
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({"records": records, "match": total, "total": total}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertFalse(rule.passed)
        self.assertIn("input_format_in_readme=false", rule.failure_detail.lower())

    def test_passes_when_io_fields_not_tracked(self):
        """If I/O fields are not tracked, rule is WARNING/passed=True (basic audit scope)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # _make_bundle already has no I/O fields → should pass
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertTrue(rule.passed)

    def test_passes_when_io_gap_is_low(self):
        """≤30% I/O false = does not trigger false-completion check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            total = 42
            records = [
                {
                    "scenario_id": f"s-{i}",
                    "family_in_readme": True,
                    "workflow_type_in_readme": True,
                    "package_id_in_readme": True,
                    "content_audit": "MATCH",
                    "input_format_in_readme": True,    # all True
                    "output_format_in_readme": True,
                }
                for i in range(total)
            ]
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({"records": records, "match": total, "total": total}),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertTrue(rule.passed)

    def test_passes_when_match_not_100_percent(self):
        """High I/O gap is acceptable if match is not 100% (honest partial)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            total = 42
            records = [
                {
                    "scenario_id": f"s-{i}",
                    "family_in_readme": True,
                    "input_format_in_readme": False,
                    "output_format_in_readme": False,
                }
                for i in range(total)
            ]
            (b / "readme" / "example-readme-content-audit.json").write_text(
                json.dumps({"records": records, "match": 20, "total": total}),  # honest 20/42
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_io_format_not_falsely_complete")
        self.assertTrue(rule.passed)


class TestReadmeGateWiredInPipeline(unittest.TestCase):
    """Rule: readme_gate_wired_in_pipeline — closes SD60-03."""

    def test_fails_when_no_integration_proof_no_source_root(self):
        """No flow integration proof and no source_root = FAILURE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-flow-integration.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("readme-gate-flow-integration.md", rule.failure_detail)

    def test_fails_when_integration_proof_admits_deferred(self):
        """Integration proof that says 'deferred' is treated as not-wired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-flow-integration.md").write_text(
                "# README Gate\nWiring is deferred to Sprint 62 (P1 item).\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("deferred", rule.failure_detail.lower())

    def test_fails_when_integration_proof_admits_not_wired(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "readme" / "readme-gate-flow-integration.md").write_text(
                "# README Gate\nGate is not wired into publish-pr yet.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)

    def test_passes_when_integration_proof_exists_and_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertTrue(rule.passed)

    def test_passes_with_source_root_that_imports_gate(self):
        """source_root scan: file that imports readme_audit_gate → PASS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "readme_audit_gate.py").write_text("def check(): pass\n", encoding="utf-8")
            (src / "__main__.py").write_text(
                "from readme_audit_gate import check\ncheck()\n", encoding="utf-8"
            )
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertTrue(rule.passed)
        self.assertIn("readme_audit_gate", rule.evidence)

    def test_fails_with_source_root_that_does_not_import_gate(self):
        """source_root scan: no file imports readme_audit_gate → FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "readme_audit_gate.py").write_text("def check(): pass\n", encoding="utf-8")
            (src / "__main__.py").write_text("# no imports\n", encoding="utf-8")
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "readme_gate_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("not imported", rule.failure_detail.lower())


class TestEvidenceValidatorWiredInPipeline(unittest.TestCase):
    """Rule: evidence_validator_wired_in_pipeline — closes SD60-04."""

    def test_fails_when_no_pipeline_integration_proof_no_source_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "pipeline-integration-proof.md").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("pipeline-integration-proof.md", rule.failure_detail)

    def test_fails_when_integration_proof_admits_p1_open(self):
        """Integration proof mentioning P1 admits it is not actually wired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "pipeline-integration-proof.md").write_text(
                "# EvidenceValidator Pipeline Integration\nP1: wire into release-status.\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)

    def test_passes_when_integration_proof_exists_and_clean(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertTrue(rule.passed)

    def test_passes_with_source_root_that_imports_validator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "evidence_validator.py").write_text("class EvidenceValidator: pass\n", encoding="utf-8")
            (src / "__main__.py").write_text(
                "from evidence_validator import EvidenceValidator\n", encoding="utf-8"
            )
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertTrue(rule.passed)

    def test_fails_with_source_root_that_does_not_import_validator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            src = Path(tmpdir) / "src"
            src.mkdir()
            (src / "evidence_validator.py").write_text("class EvidenceValidator: pass\n", encoding="utf-8")
            (src / "__main__.py").write_text("# nothing imported\n", encoding="utf-8")
            result = EvidenceValidator(b, source_root=src).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)


class TestDestinationProgramcsInputNotAllNull(unittest.TestCase):
    """Rule: destination_programcs_input_not_all_null — closes SD60-05."""

    def test_fails_when_all_records_have_null_input(self):
        """SD60-05: input_format_in_programcs=null for all 42 records."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "42/42",
                    "present_no_authority": 0,
                    "total_examples": 42,
                    "examples": [
                        {
                            "scenario_id": f"s-{i}",
                            "content_match": "MATCH",
                            "input_format_in_programcs": None,
                            "input_classification": None,
                        }
                        for i in range(42)
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertFalse(rule.passed)
        self.assertIn("null", rule.failure_detail.lower())
        self.assertIn("42/42", rule.failure_detail)

    def test_fails_when_field_not_present_in_records(self):
        """Records without input_format_in_programcs = audit not performed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "content-audit-repaired.json").write_text(
                json.dumps({
                    "authority_mapped": "42/42",
                    "present_no_authority": 0,
                    "total_examples": 42,
                    "examples": [
                        {"scenario_id": f"s-{i}", "content_match": "MATCH"}
                        for i in range(42)
                    ],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertFalse(rule.passed)
        self.assertIn("input_format_in_programcs", rule.failure_detail)

    def test_passes_when_some_records_have_nonnull_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # _make_bundle already sets input_format_in_programcs = ".docx"
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertTrue(rule.passed)

    def test_passes_with_programcs_io_audit_file(self):
        """Dedicated programcs-io-audit-after.json with real data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "destination" / "programcs-io-audit-after.json").write_text(
                json.dumps({
                    "examples": [
                        {
                            "scenario_id": "cells-html-converter",
                            "input_format_in_programcs": ".xlsx",
                            "input_classification": "AddInput",
                            "output_format_in_programcs": ".html",
                        }
                    ]
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "destination_programcs_input_not_all_null")
        self.assertTrue(rule.passed)


class TestNoPriOneItemsWithCompleteVerdict(unittest.TestCase):
    """Rule: no_p1_items_with_complete_verdict — closes SD60-08."""

    def test_fails_when_p1_items_open_with_complete_verdict(self):
        """SD60-08: P1 items in register + COMPLETE verdict = contradiction."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README gate CLI wiring | P1 | OPEN |\n"
                "| EvidenceValidator CLI wiring | P1 | OPEN |\n",
                encoding="utf-8",
            )
            (b / "final-verdict.md").write_text(
                "Verdict: LOWCODE_IO_DESTINATION_README_CLOSURE_VERIFIED\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertFalse(rule.passed)
        self.assertIn("P1", rule.failure_detail)

    def test_passes_when_no_register_file(self):
        """No register file = no P1 items to check → WARNING/passed=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)

    def test_passes_when_register_has_no_p1_items(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README formatting | P2 | OPEN |\n",
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)

    def test_passes_when_p1_items_but_verdict_not_complete(self):
        """P1 items are allowed when verdict does not claim completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| Wiring | P1 | OPEN |\n", encoding="utf-8"
            )
            (b / "final-verdict.md").write_text(
                "Verdict: EVIDENCE_REPAIR_REQUIRED_NOT_CLOSED\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)

    def test_passes_when_p1_items_marked_done(self):
        """P1 lines marked DONE are not treated as open."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "process").mkdir(parents=True, exist_ok=True)
            (b / "process" / "next-work-register.md").write_text(
                "| README gate wiring | P1 | DONE |\n", encoding="utf-8"
            )
            (b / "final-verdict.md").write_text(
                "Verdict: LOWCODE_FALSE_CLOSURE_KILLED_PIPELINE_GATES_ACTIVE\n", encoding="utf-8"
            )
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "no_p1_items_with_complete_verdict")
        self.assertTrue(rule.passed)


class TestRequiredFilesNonzeroSize(unittest.TestCase):
    """Rule: required_files_nonzero_size — closes SD60-01 contributory."""

    def test_fails_when_commands_log_is_zero_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "commands.log").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertFalse(rule.passed)
        self.assertIn("commands.log", rule.failure_detail)

    def test_fails_when_todo_md_is_zero_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "todo.md").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertFalse(rule.passed)
        self.assertIn("todo.md", rule.failure_detail)

    def test_fails_when_test_run_log_is_zero_bytes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "lanes" / "lane-I" / "test-run.log").write_text("", encoding="utf-8")
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertFalse(rule.passed)
        self.assertIn("test-run.log", rule.failure_detail)

    def test_passes_when_all_required_files_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(r for r in result.rule_results if r.rule_id == "required_files_nonzero_size")
        self.assertTrue(rule.passed)


class TestBundleValidationResultPresentAndValid(unittest.TestCase):
    """Rule: bundle_validation_result_present_and_valid — Sprint 62 mandatory EV execution."""

    def test_fails_when_no_bundle_validation_result(self):
        """Missing evidence/*-bundle-validation-result.json = FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove the bundle-validation-result.json that _make_bundle creates
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertFalse(rule.passed)
        self.assertIn("bundle-validation-result.json", rule.failure_detail)

    def test_fails_when_bundle_validation_result_shows_failures(self):
        """overall_valid=false in bundle-validation-result.json = FAIL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint60-bundle-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint60-test",
                    "overall_valid": False,
                    "passed": 15,
                    "failed": 5,
                    "warnings": 0,
                    "total_rules": 20,
                    "rules": [],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertFalse(rule.passed)
        self.assertIn("overall_valid=false", rule.failure_detail)
        self.assertIn("5", rule.failure_detail)  # failed count

    def test_passes_when_bundle_validation_result_is_valid(self):
        """overall_valid=true in bundle-validation-result.json = PASS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertTrue(rule.passed)
        self.assertIn("overall_valid=true", rule.evidence)

    def test_uses_most_recent_file_when_multiple_exist(self):
        """When multiple *-bundle-validation-result.json exist, uses the most recent (alphabetically last)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Add a second, newer result file that passes
            (b / "evidence" / "sprint62-bundle-validation-result.json").write_text(
                json.dumps({
                    "sprint_id": "sprint62-test",
                    "overall_valid": True,
                    "passed": 21,
                    "failed": 0,
                    "warnings": 0,
                    "total_rules": 21,
                    "rules": [],
                }),
                encoding="utf-8",
            )
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        self.assertTrue(rule.passed)
        self.assertIn("sprint62", rule.evidence)

    def test_overall_valid_false_when_bundle_validation_missing(self):
        """overall_valid=False when bundle-validation-result.json is missing from evidence/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate()
        self.assertFalse(result.overall_valid)


class TestTwoPhaseValidation(unittest.TestCase):
    """Sprint 63 Phase 2: Two-phase validation eliminates self-referential bootstrap contradiction."""

    def test_validate_for_storage_excludes_self_reference_rule(self):
        """validate_for_storage() runs 20 rules (excludes rule 21 bundle_validation_result_present_and_valid)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove the validation result so rule 21 would fail if evaluated
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate_for_storage()
        # Rule 21 must not appear in results
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertNotIn(EvidenceValidator.SELF_REFERENCE_RULE_ID, rule_ids)
        # Should have exactly 20 rules evaluated
        self.assertEqual(len(result.rule_results), 20)

    def test_validate_for_storage_overall_valid_reflects_20_rules_only(self):
        """validate_for_storage() overall_valid=True means all 20 non-self-referential rules pass."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove the validation result so rule 21 would fail if included
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate_for_storage()
        # overall_valid should be True because rule 21 was excluded
        self.assertTrue(result.overall_valid)
        self.assertEqual(result.failed, 0)

    def test_full_validate_passes_after_storing_phase_a_result(self):
        """After storing phase A result, phase B (all 21 rules) passes."""
        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Remove old result
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            # Phase A: run without rule 21
            phase_a = EvidenceValidator(b).validate_for_storage()
            # Store the phase A result (simulating actual storage)
            result_data = {
                "sprint_id": "sprint63-test",
                "overall_valid": phase_a.overall_valid,
                "passed": phase_a.passed,
                "failed": phase_a.failed,
                "warnings": phase_a.warnings,
                "total_rules": len(phase_a.rule_results),
                "rules": [
                    {"rule_id": r.rule_id, "passed": r.passed}
                    for r in phase_a.rule_results
                ],
            }
            (b / "evidence" / "sprint63-bundle-validation-result.json").write_text(
                json.dumps(result_data), encoding="utf-8"
            )
            # Phase B: run all 21 rules — rule 21 should now pass
            phase_b = EvidenceValidator(b).validate()
        self.assertTrue(phase_b.overall_valid)
        self.assertEqual(phase_b.failed, 0)
        self.assertEqual(len(phase_b.rule_results), 21)

    def test_sprint62_style_contradiction_detected_by_rule_21(self):
        """Sprint 62 defect: overall_valid=true + failed=0 but embedded rule has passed=false is detected."""
        import json
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            # Write a contradictory result file: claims overall_valid=true but one rule is failed
            contradictory_result = {
                "sprint_id": "sprint62-test",
                "overall_valid": True,
                "passed": 21,
                "failed": 0,
                "warnings": 0,
                "total_rules": 21,
                "rules": [
                    {"rule_id": "bundle_validation_result_present_and_valid", "passed": False},
                ],
            }
            (b / "evidence" / "sprint62-bundle-validation-result.json").write_text(
                json.dumps(contradictory_result), encoding="utf-8"
            )
            # Remove the old result so only the contradictory one is used
            (b / "evidence" / "sprint60-bundle-validation-result.json").unlink()
            result = EvidenceValidator(b).validate()
        rule = next(
            r for r in result.rule_results
            if r.rule_id == "bundle_validation_result_present_and_valid"
        )
        # The contradiction (overall_valid=true but a rule has passed=false) must be detected
        self.assertFalse(rule.passed)
        detail_lower = rule.failure_detail.lower()
        self.assertTrue(
            "contradict" in detail_lower or "inconsistent" in detail_lower or "false" in detail_lower,
            f"Expected contradiction language in failure_detail, got: {rule.failure_detail}",
        )

    def test_validate_exclude_rule_ids_removes_specified_rule(self):
        """validate(exclude_rule_ids={'some_rule'}) removes that rule from results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate(
                exclude_rule_ids={"required_files_nonzero_size"}
            )
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertNotIn("required_files_nonzero_size", rule_ids)
        # All other rules still present
        self.assertIn("bundle_validation_result_present_and_valid", rule_ids)

    def test_validate_exclude_empty_set_runs_all_rules(self):
        """validate(exclude_rule_ids=set()) is identical to validate()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result_default = EvidenceValidator(b).validate()
            result_empty_exclude = EvidenceValidator(b).validate(exclude_rule_ids=set())
        self.assertEqual(len(result_default.rule_results), len(result_empty_exclude.rule_results))
        self.assertEqual(result_default.overall_valid, result_empty_exclude.overall_valid)

    def test_self_reference_rule_id_constant_matches_actual_rule(self):
        """SELF_REFERENCE_RULE_ID must match the actual rule ID used in validate()."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_bundle(tmpdir)
            result = EvidenceValidator(b).validate()
        rule_ids = {r.rule_id for r in result.rule_results}
        self.assertIn(
            EvidenceValidator.SELF_REFERENCE_RULE_ID,
            rule_ids,
            "SELF_REFERENCE_RULE_ID must match an actual rule in the validator",
        )


if __name__ == "__main__":
    unittest.main()
