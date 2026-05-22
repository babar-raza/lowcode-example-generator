"""Pipeline integration tests for EvidenceValidator wiring — Sprint 61 Phase 3.

Verifies that:
1. EvidenceValidator is importable from __main__.py (source scan passes)
2. `release-status --validate-bundle` calls EvidenceValidator and returns 0 on valid bundle
3. `release-status --validate-bundle` returns 1 on invalid bundle
4. The evidence_validator_wired_in_pipeline rule passes when source_root points to real pipeline
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.evidence_validator import EvidenceValidator


def _make_valid_bundle(tmpdir: str) -> Path:
    """Create a minimal valid bundle (passes all 22 rules)."""
    b = Path(tmpdir)

    (b / "git").mkdir(parents=True)
    (b / "git" / "final-clean-proof.txt").write_text(
        "On branch main\nnothing to commit, working tree clean\n", encoding="utf-8"
    )

    (b / "destination").mkdir(parents=True)
    (b / "destination" / "content-audit-repaired.json").write_text(
        json.dumps({
            "authority_mapped": "42/42",
            "present_no_authority": 0,
            "total_examples": 42,
            "examples": [
                {
                    "scenario_id": f"s-{i}",
                    "content_match": "MATCH",
                    "input_format_in_programcs": ".docx",
                    "input_classification": "AddInput",
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    (b / "readme").mkdir(parents=True)
    (b / "readme" / "example-readme-content-audit.json").write_text(
        json.dumps({"records": [{"scenario_id": "s-0", "family_in_readme": True, "workflow_type_in_readme": True, "package_id_in_readme": True}]}),
        encoding="utf-8",
    )
    (b / "readme" / "readme-gate-implementation.md").write_text("# Gate wired\n", encoding="utf-8")
    (b / "readme" / "readme-gate-test-results.txt").write_text("13 passed, 0 failed\n", encoding="utf-8")
    (b / "readme" / "readme-gate-source-proof.patch").write_text("diff --git a/src ...\n", encoding="utf-8")
    (b / "readme" / "readme-gate-flow-integration.md").write_text(
        "# README Gate Flow Integration\nGate is called in publish-pr live mode.\n", encoding="utf-8"
    )

    (b / "evidence").mkdir(parents=True)
    (b / "evidence" / "validator-test-results.txt").write_text("20 passed, 0 failed in 0.45s\n", encoding="utf-8")
    (b / "evidence" / "sprint61-bundle-validation-result.json").write_text(
        json.dumps({"sprint_id": "sprint61-test", "overall_valid": True, "passed": 21, "failed": 0, "warnings": 0, "total_rules": 21, "rules": []}),
        encoding="utf-8",
    )
    (b / "evidence" / "pipeline-integration-proof.md").write_text(
        "# Pipeline Integration\nEvidenceValidator is called in release-status command.\n", encoding="utf-8"
    )
    (b / "evidence" / "evidence-contract-computed.json").write_text(
        json.dumps({
            "contract_id": "sprint-test",
            "computed_at": "2026-05-22T07:30:00Z",
            "total_categories": 36,
            "present": 36,
            "missing": 0,
            "zero_bytes": 0,
            "semantic_failed": 0,
            "pending": 0,
            "blocking_failures": 0,
            "closure_valid": True,
            "categories": [],
        }),
        encoding="utf-8",
    )

    (b / "todo.md").write_text("- [x] Phase 0 complete\n- [x] Phase 10 complete\n", encoding="utf-8")
    (b / "commands.log").write_text("phase0: done\nphase10: done\n", encoding="utf-8")

    (b / "lanes" / "lane-I").mkdir(parents=True)
    (b / "lanes" / "lane-I" / "test-run.log").write_text("2889 passed, 0 failed, 3 skipped\n", encoding="utf-8")

    (b / "sprint-state.json").write_text(json.dumps({"sprint_id": "sprint61-test"}), encoding="utf-8")

    # Sprint 65: destination/content-audit-final.json with all required fields
    (b / "destination" / "content-audit-final.json").write_text(
        json.dumps({
            "total_publication_artifacts": 42,
            "standard_package_artifacts": 40,
            "special_case_artifacts": 2,
            "records_ready": 42,
            "records": [
                {
                    "scenario_id": f"s-{i}",
                    "family": "cells",
                    "package_version": "26.5.1",
                    "output_format": ".xlsx",
                    "readme_status": "IO_DOC",
                    "root_readme_status": "INCLUDED",
                    "final_readiness": "READY",
                    "special_case": False,
                }
                for i in range(42)
            ],
        }),
        encoding="utf-8",
    )

    # Sprint 65: root-readme/per-family artifacts
    (b / "root-readme" / "per-family").mkdir(parents=True)
    for family in ["cells", "diagram", "email", "pdf", "slides", "words"]:
        (b / "root-readme" / "per-family" / f"{family}-root-readme.md").write_text(
            f"# {family} README\n", encoding="utf-8"
        )

    # Sprint 65: special-cases/special-case-publication-map.json
    (b / "special-cases").mkdir(parents=True)
    (b / "special-cases" / "special-case-publication-map.json").write_text(
        json.dumps({"special_cases": [
            {"scenario_id": "pdf-pdfa-converter", "destination_path": "examples/pdf/lowcode/pdfa-converter"},
            {"scenario_id": "pdf-text-extractor", "destination_path": "examples/pdf/lowcode/text-extractor"},
        ]}),
        encoding="utf-8",
    )

    # Sprint 65: version/version-policy-final.json
    (b / "version").mkdir(parents=True)
    (b / "version" / "version-policy-final.json").write_text(
        json.dumps({"summary": {"total_drift_unresolved": 0}, "families": {}}),
        encoding="utf-8",
    )

    # Sprint 65: final-verdict.md + publication/remote-proof-index.json
    (b / "final-verdict.md").write_text("Verdict: TEST_DRY_RUN_APPROVAL_BLOCKED\n", encoding="utf-8")
    (b / "publication").mkdir(parents=True)
    (b / "publication" / "remote-proof-index.json").write_text(
        json.dumps({"families": ["cells"]}), encoding="utf-8"
    )

    # Sprint 65: evidence/*revalidation*.json — overall_valid=false
    (b / "evidence" / "sprint64-revalidation-result.json").write_text(
        json.dumps({"sprint_id": "sprint64-test", "overall_valid": False, "failed": 3}),
        encoding="utf-8",
    )

    for i in range(40):
        (b / f"pad-{i:02d}.txt").write_text(f"pad {i}\n", encoding="utf-8")

    return b


class TestEvidenceValidatorSourceScan(unittest.TestCase):
    """Verify EvidenceValidator is imported by real pipeline source (SD60-04 fix)."""

    def test_evidence_validator_imported_by_main(self):
        """_scan_source_for_import must find evidence_validator in __main__.py."""
        real_source_root = Path(__file__).resolve().parents[2] / "src" / "plugin_examples"
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            validator = EvidenceValidator(bundle_dir=b, source_root=real_source_root)
            result = validator.validate()

        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertTrue(rule.passed, f"Expected PASS but got FAIL: {rule.failure_detail}")
        self.assertIn("evidence_validator", rule.evidence)

    def test_sprint60_bundle_fails_evidence_validator_wired_rule(self):
        """Sprint 60 source did NOT wire evidence_validator — confirmed by isolation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            # Simulate a source tree WITHOUT evidence_validator import
            fake_src = Path(tmpdir) / "fake_src"
            fake_src.mkdir()
            (fake_src / "evidence_validator.py").write_text("class EvidenceValidator: pass\n", encoding="utf-8")
            (fake_src / "__main__.py").write_text("# standalone module, not wired\n", encoding="utf-8")

            validator = EvidenceValidator(bundle_dir=b, source_root=fake_src)
            result = validator.validate()

        rule = next(r for r in result.rule_results if r.rule_id == "evidence_validator_wired_in_pipeline")
        self.assertFalse(rule.passed)
        self.assertIn("not imported", rule.failure_detail.lower())


class TestReleaseStatusValidateBundleFlag(unittest.TestCase):
    """Integration tests for release-status --validate-bundle CLI wiring."""

    def _run_validate_bundle(self, bundle_dir: Path) -> int:
        """Call the release-status --validate-bundle path in __main__.main() directly."""
        from plugin_examples.__main__ import main
        argv_backup = sys.argv[:]
        try:
            sys.argv = [
                "plugin_examples",
                "release-status",
                "--validate-bundle", str(bundle_dir),
            ]
            # Mock the heavy release-status computation so we only test the EV wiring
            with patch("plugin_examples.publisher.release_status.compute_release_status") as mock_compute, \
                 patch("plugin_examples.publisher.release_status.write_release_status_report") as mock_write, \
                 patch("plugin_examples.publisher.release_status.ALL_RELEASE_FAMILIES", ["cells"]):
                mock_compute.return_value = {
                    "families": [
                        {
                            "family": "cells",
                            "last_merge_sha": None,
                            "last_post_merge_validation_status": "UNKNOWN",
                            "published_examples_count": 0,
                            "release_scope_status": "UNKNOWN",
                            "next_required_action": "none",
                        }
                    ],
                    "all_merged": False,
                    "all_post_merge_validated": False,
                }
                mock_write.return_value = Path("/tmp/fake-report.json")
                return main()
        finally:
            sys.argv = argv_backup

    def test_returns_0_on_valid_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            exit_code = self._run_validate_bundle(b)
        self.assertEqual(exit_code, 0)

    def test_returns_1_on_invalid_bundle(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            b = _make_valid_bundle(tmpdir)
            # Introduce a failure: empty clean proof
            (b / "git" / "final-clean-proof.txt").write_text("", encoding="utf-8")
            exit_code = self._run_validate_bundle(b)
        self.assertEqual(exit_code, 1)

    def test_validate_bundle_not_called_without_flag(self):
        """Without --validate-bundle, EvidenceValidator is NOT called."""
        from plugin_examples.__main__ import main
        argv_backup = sys.argv[:]
        called = []
        original_ev = EvidenceValidator.__init__

        def spy_init(self_ev, *args, **kwargs):
            called.append(True)
            return original_ev(self_ev, *args, **kwargs)

        try:
            sys.argv = ["plugin_examples", "release-status"]
            with patch("plugin_examples.publisher.release_status.compute_release_status") as mock_compute, \
                 patch("plugin_examples.publisher.release_status.write_release_status_report") as mock_write, \
                 patch("plugin_examples.publisher.release_status.ALL_RELEASE_FAMILIES", ["cells"]), \
                 patch.object(EvidenceValidator, "__init__", spy_init):
                mock_compute.return_value = {
                    "families": [
                        {
                            "family": "cells",
                            "last_merge_sha": None,
                            "last_post_merge_validation_status": "UNKNOWN",
                            "published_examples_count": 0,
                            "release_scope_status": "UNKNOWN",
                            "next_required_action": "none",
                        }
                    ],
                    "all_merged": False,
                    "all_post_merge_validated": False,
                }
                mock_write.return_value = Path("/tmp/fake-report.json")
                main()
        finally:
            sys.argv = argv_backup

        self.assertEqual(called, [], "EvidenceValidator should NOT be called without --validate-bundle")


if __name__ == "__main__":
    unittest.main()
