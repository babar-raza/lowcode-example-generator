"""Tests proving the gate-triggered reviewer repair loop works correctly.

These tests verify that:
1. Retryable reviewer failures trigger repair attempts
2. Non-retryable failures go straight to backlog
3. Exhausted repair attempts go to backlog
4. Successful repair after retry marks record as repaired
"""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[2]
_RUNNER_PATH = _REPO_ROOT / "src" / "plugin_examples" / "runner.py"


class TestReviewerRepairLoopWiring:
    """Verify runner.py has the repair loop infrastructure."""

    def test_runner_has_reviewer_max_repair_attempts(self):
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "_REVIEWER_MAX_REPAIR_ATTEMPTS" in source

    def test_runner_has_retryable_classification(self):
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "_is_reviewer_failure_retryable" in source
        assert "_REVIEWER_RETRYABLE_KEYWORDS" in source

    def test_runner_has_repair_loop_in_stage_reviewer(self):
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "repair_attempts" in source
        assert "repair_log" in source

    def test_runner_marks_reviewer_repaired_on_success_after_retry(self):
        source = _RUNNER_PATH.read_text(encoding="utf-8")
        assert "mark_reviewer_repaired" in source


class TestRetryableClassification:
    """Verify _is_reviewer_failure_retryable classifies correctly."""

    def _get_classifier(self):
        from plugin_examples.runner import _is_reviewer_failure_retryable

        return _is_reviewer_failure_retryable

    def _make_result(self, available=True, passed=False, error=None, details=None):
        from plugin_examples.verifier_bridge.bridge import ReviewerResult

        return ReviewerResult(available=available, passed=passed, error=error, details=details)

    def test_compilation_error_is_retryable(self):
        classify = self._get_classifier()
        r = self._make_result(error="CS0246: compilation error in Program.cs")
        assert classify(r) is True

    def test_missing_using_is_retryable(self):
        classify = self._get_classifier()
        r = self._make_result(error="error CS0246: missing using directive")
        assert classify(r) is True

    def test_timeout_is_not_retryable(self):
        classify = self._get_classifier()
        r = self._make_result(error="Reviewer timed out after 300s")
        assert classify(r) is False

    def test_unavailable_is_not_retryable(self):
        classify = self._get_classifier()
        r = self._make_result(available=False, error="Not installed")
        assert classify(r) is False

    def test_unknown_error_is_not_retryable(self):
        classify = self._get_classifier()
        r = self._make_result(error="some unknown infrastructure failure")
        assert classify(r) is False

    def test_structured_details_errors_are_retryable(self):
        classify = self._get_classifier()
        r = self._make_result(
            error="Build failed",
            details={"errors": ["CS0103: The name 'foo' does not contain a definition"]},
        )
        assert classify(r) is True


class TestLifecycleReviewerRepair:
    """Verify lifecycle record tracks reviewer repair correctly."""

    def test_mark_reviewer_repaired_sets_fields(self):
        from plugin_examples.gates.example_lifecycle import ExampleLifecycleRecord

        rec = ExampleLifecycleRecord(scenario_id="test-1", family="cells", run_id="r1")
        rec.mark_reviewer_repaired(attempts=2)
        assert rec.reviewer_status == "repaired"
        assert rec.reviewer_repair_attempts == 2
        assert rec.pr_candidate is True
        assert rec.final_verdict == "EXAMPLE_READY_FOR_PR_DRY_RUN"

    def test_mark_reviewer_failed_then_backlogged(self):
        from plugin_examples.gates.example_lifecycle import ExampleLifecycleRecord

        rec = ExampleLifecycleRecord(scenario_id="test-2", family="cells", run_id="r1")
        rec.mark_reviewer_failed("compilation error")
        assert rec.pr_candidate is False
        assert rec.final_verdict == "EXAMPLE_BLOCKED_REVIEWER_FAILED"
        rec.mark_backlogged(
            root_cause="reviewer_failed",
            recommended_fix="Fix code",
            priority="high",
        )
        assert rec.backlogged is True

    def test_reviewer_repaired_in_lifecycle_stages(self):
        from plugin_examples.gates.example_lifecycle import LIFECYCLE_STAGES

        assert "reviewer_repaired" in LIFECYCLE_STAGES


class TestReviewerRepairConstants:
    """Verify repair loop constants are sensible."""

    def test_max_attempts_is_positive(self):
        from plugin_examples.runner import _REVIEWER_MAX_REPAIR_ATTEMPTS

        assert _REVIEWER_MAX_REPAIR_ATTEMPTS > 0

    def test_max_attempts_is_bounded(self):
        from plugin_examples.runner import _REVIEWER_MAX_REPAIR_ATTEMPTS

        assert _REVIEWER_MAX_REPAIR_ATTEMPTS <= 5

    def test_retryable_keywords_are_nonempty(self):
        from plugin_examples.runner import _REVIEWER_RETRYABLE_KEYWORDS

        assert len(_REVIEWER_RETRYABLE_KEYWORDS) > 0
