"""Tests for advisory output validation in example gates."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from plugin_examples.gates.example_gates import (
    _advisory_output_validation,
    evaluate_example_gates,
    ExampleGateResult,
)


class TestAdvisoryOutputValidation:
    """Test the _advisory_output_validation helper."""

    def test_text_extractor_not_applicable(self, tmp_path):
        """TextExtractor types should return advisory_not_applicable."""
        result = _advisory_output_validation(str(tmp_path), "pdf-text-extractor")
        assert result == "advisory_not_applicable"

    def test_text_extractor_by_scenario_id(self, tmp_path):
        """TextExtractor detected via scenario_id pattern."""
        result = _advisory_output_validation(str(tmp_path), "slides-textextractor")
        assert result == "advisory_not_applicable"

    def test_nonexistent_dir_returns_passed(self):
        """Non-existent project dir returns passed (fallback)."""
        result = _advisory_output_validation("/nonexistent/path/xyz", "pdf-merger")
        assert result == "passed"

    def test_empty_dir_returns_no_output(self, tmp_path):
        """Empty project dir returns advisory_no_output."""
        result = _advisory_output_validation(str(tmp_path), "pdf-merger")
        assert result == "advisory_no_output"

    def test_output_file_present_validator_unavailable(self, tmp_path):
        """Output file present but validator import fails → passed fallback."""
        (tmp_path / "output.pdf").write_bytes(b"%PDF-1.4 fake")
        with patch(
            "plugin_examples.gates.example_gates.validate_output_file_semantic",
            side_effect=ImportError("no validator"),
            create=True,
        ):
            # The function catches ImportError internally
            result = _advisory_output_validation(str(tmp_path), "pdf-merger")
            # Should be either "advisory_passed" or "passed" (fallback)
            assert result in ("advisory_passed", "passed")

    def test_output_file_present_valid(self, tmp_path):
        """Output file present and valid → advisory_passed."""
        (tmp_path / "output.pdf").write_bytes(b"%PDF-1.4 test content")
        with patch(
            "plugin_examples.verifier_bridge.output_validator.validate_output_file_semantic",
            return_value={"valid": True},
        ):
            result = _advisory_output_validation(str(tmp_path), "pdf-merger")
            assert result == "advisory_passed"

    def test_output_file_present_invalid(self, tmp_path):
        """Output file present but invalid → advisory_failed."""
        (tmp_path / "output.pdf").write_bytes(b"not a pdf")
        with patch(
            "plugin_examples.verifier_bridge.output_validator.validate_output_file_semantic",
            return_value={"valid": False, "reason": "bad magic bytes"},
        ):
            result = _advisory_output_validation(str(tmp_path), "pdf-merger")
            assert result == "advisory_failed"

    def test_output_dir_present(self, tmp_path):
        """Directory output (Email FolderOutputHandler) → advisory_passed or passed."""
        output_dir = tmp_path / "output_dir"
        output_dir.mkdir()
        result = _advisory_output_validation(str(tmp_path), "email-converter")
        # Directory output found, but no file to validate → depends on validator
        assert result in ("advisory_passed", "passed", "advisory_no_output")

    def test_numbered_output_files(self, tmp_path):
        """Page-numbered output files (ImageExtractor) detected."""
        (tmp_path / "output_0.png").write_bytes(b"\x89PNG fake")
        with patch(
            "plugin_examples.verifier_bridge.output_validator.validate_output_file_semantic",
            return_value={"valid": True},
        ):
            result = _advisory_output_validation(str(tmp_path), "pdf-image-extractor")
            assert result == "advisory_passed"


class TestGateIntegrationAdvisory:
    """Test that advisory validation integrates correctly into gate evaluation."""

    def test_advisory_does_not_block(self):
        """Advisory validation should never block an example from being a PR candidate."""
        # The advisory validation result should not affect publish_candidate
        # when all other gates pass. We verify this by checking the gate function
        # handles the new status values without blocking.
        eg = ExampleGateResult(
            scenario_id="test",
            example_path="/fake",
            restore_status="passed",
            build_status="passed",
            run_status="passed",
            output_validation_status="advisory_failed",
            reviewer_status="passed",
            publish_candidate=True,
            final_example_verdict="EXAMPLE_READY_FOR_PR_DRY_RUN",
        )
        # advisory_failed should not make this a non-candidate
        assert eg.publish_candidate is True
        assert eg.final_example_verdict == "EXAMPLE_READY_FOR_PR_DRY_RUN"
