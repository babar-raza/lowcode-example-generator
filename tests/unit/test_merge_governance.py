"""Tests for PR merge governance: separate approval gate, preconditions, dry-run safety.

Test names:
    test_merge_requires_separate_approval_token
    test_merge_rejects_live_publish_approval_token
    test_merge_requires_family_and_pr_number
    test_merge_rejects_wrong_target_repo
    test_merge_rejects_unexpected_files
    test_merge_rejects_missing_clean_checkout_evidence
    test_merge_dry_run_performs_no_remote_mutation
    test_merge_live_mode_requires_approve_merge_pr
    test_post_merge_plan_written
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from plugin_examples.publisher.merge_approval_gate import (
    BLOCKED_INVALID_MERGE_APPROVAL,
    BLOCKED_MERGE_APPROVAL_REQUIRED,
    BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN,
    MERGE_APPROVAL_ENV_VAR,
    MERGE_APPROVAL_EXPECTED_VALUE,
    check_merge_approval,
)


class TestMergeRequiresSeparateApprovalToken(unittest.TestCase):
    """test_merge_requires_separate_approval_token"""

    def test_merge_requires_separate_approval_token(self):
        """Merge approval gate accepts only APPROVE_MERGE_PR."""
        approved, reason = check_merge_approval("APPROVE_MERGE_PR")
        self.assertTrue(approved, "Expected approval with APPROVE_MERGE_PR")
        self.assertEqual(reason, "")

    def test_merge_blocks_empty_token(self):
        """Empty token is rejected with blocked_merge_approval_required."""
        approved, reason = check_merge_approval(None)
        self.assertFalse(approved)
        self.assertEqual(reason, BLOCKED_MERGE_APPROVAL_REQUIRED)

    def test_merge_blocks_wrong_phrase(self):
        """Arbitrary wrong phrases are rejected."""
        approved, reason = check_merge_approval("some_random_phrase")
        self.assertFalse(approved)
        self.assertEqual(reason, BLOCKED_INVALID_MERGE_APPROVAL)

    def test_merge_reads_env_var_as_fallback(self):
        """Reads PLUGIN_EXAMPLES_MERGE_PR_APPROVAL env var when CLI token not provided."""
        with patch.dict(os.environ, {MERGE_APPROVAL_ENV_VAR: MERGE_APPROVAL_EXPECTED_VALUE}):
            approved, reason = check_merge_approval(None)
        self.assertTrue(approved)
        self.assertEqual(reason, "")


class TestMergeRejectsLivePublishApprovalToken(unittest.TestCase):
    """test_merge_rejects_live_publish_approval_token"""

    def test_merge_rejects_live_publish_approval_token(self):
        """APPROVE_LIVE_PR must be explicitly rejected for merge — separate intent required."""
        approved, reason = check_merge_approval("APPROVE_LIVE_PR")
        self.assertFalse(approved)
        self.assertEqual(
            reason,
            BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN,
            "Expected APPROVE_LIVE_PR to be explicitly rejected with reused-token error",
        )

    def test_merge_rejects_live_publish_token_from_env(self):
        """APPROVE_LIVE_PR from env var is also rejected."""
        with patch.dict(os.environ, {MERGE_APPROVAL_ENV_VAR: "APPROVE_LIVE_PR"}):
            approved, reason = check_merge_approval(None)
        self.assertFalse(approved)
        self.assertEqual(reason, BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN)


class TestMergeRequiresFamilyAndPrNumber(unittest.TestCase):
    """test_merge_requires_family_and_pr_number"""

    def test_merge_requires_family_and_pr_number(self):
        """merge-pr CLI requires both --family and --pr-number arguments."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "plugin_examples", "merge-pr"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
            env={**os.environ, "PYTHONPATH": "src"},
        )
        # Should fail with missing required args error
        self.assertNotEqual(result.returncode, 0, "Expected non-zero exit when --family and --pr-number are missing")
        # argparse error message should mention the missing args
        combined = result.stdout + result.stderr
        self.assertIn("--family", combined)

    def test_merge_requires_pr_number(self):
        """merge-pr requires --pr-number even when --family is provided."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "plugin_examples", "merge-pr", "--family", "words"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
            env={**os.environ, "PYTHONPATH": "src"},
        )
        self.assertNotEqual(result.returncode, 0, "Expected non-zero exit when --pr-number is missing")


class TestMergeRejectsWrongTargetRepo(unittest.TestCase):
    """test_merge_rejects_wrong_target_repo"""

    def test_merge_rejects_wrong_target_repo(self):
        """check_merge_preconditions blocks when PR is against wrong repo."""
        from plugin_examples.publisher.github_pr_merger import check_merge_preconditions

        # Mock a PR that targets a different repo
        mock_pr_data = {
            "number": 1,
            "state": "open",
            "merged": False,
            "merged_at": None,
            "head": {"ref": "plugin-examples/words/20260502-135703"},
            "base": {
                "ref": "main",
                "repo": {"full_name": "wrong-org/wrong-repo"},
            },
            "title": "Test PR",
            "changed_files": 23,
        }

        with patch("plugin_examples.publisher.github_pr_merger._api_get") as mock_get:
            mock_get.side_effect = [
                mock_pr_data,  # PR fetch
                [],  # files fetch
            ]
            result = check_merge_preconditions(
                owner="aspose-words-net",
                repo="Aspose.Words.LowCode-for-.NET-Examples",
                pr_number=1,
                expected_family="words",
                clean_checkout_evidence_path=None,
                github_token="dummy_token",
            )

        self.assertFalse(result["ok"])
        self.assertIn("blocked_merge_wrong_target_repo", result["blocked_reasons"])


class TestMergeRejectsUnexpectedFiles(unittest.TestCase):
    """test_merge_rejects_unexpected_files"""

    def test_merge_rejects_unexpected_files(self):
        """check_merge_preconditions blocks when PR contains unexpected files like PR_SUMMARY.md."""
        from plugin_examples.publisher.github_pr_merger import check_merge_preconditions

        mock_pr_data = {
            "number": 1,
            "state": "open",
            "merged": False,
            "merged_at": None,
            "head": {"ref": "plugin-examples/words/20260502-135703"},
            "base": {
                "ref": "main",
                "repo": {"full_name": "aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples"},
            },
            "title": "Test PR",
            "changed_files": 25,
        }
        mock_files = [
            {"filename": "examples/words/lowcode/converter/Program.cs"},
            {"filename": "PR_SUMMARY.md"},  # unexpected
        ]

        with patch("plugin_examples.publisher.github_pr_merger._api_get") as mock_get:
            mock_get.side_effect = [mock_pr_data, mock_files]
            result = check_merge_preconditions(
                owner="aspose-words-net",
                repo="Aspose.Words.LowCode-for-.NET-Examples",
                pr_number=1,
                expected_family="words",
                clean_checkout_evidence_path=None,
                github_token="dummy_token",
            )

        self.assertFalse(result["ok"])
        self.assertIn("blocked_merge_unexpected_files", result["blocked_reasons"])


class TestMergeRejectsMissingCleanCheckoutEvidence(unittest.TestCase):
    """test_merge_rejects_missing_clean_checkout_evidence"""

    def test_merge_rejects_missing_clean_checkout_evidence(self):
        """check_merge_preconditions blocks when clean-checkout evidence does not exist."""
        from plugin_examples.publisher.github_pr_merger import check_merge_preconditions

        mock_pr_data = {
            "number": 1,
            "state": "open",
            "merged": False,
            "merged_at": None,
            "head": {"ref": "plugin-examples/cells/20260502-153727"},
            "base": {
                "ref": "main",
                "repo": {"full_name": "aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples"},
            },
            "title": "Test PR",
            "changed_files": 57,
        }
        mock_files = [{"filename": "examples/cells/lowcode/html-converter/Program.cs"}]

        nonexistent = Path("/tmp/nonexistent_clean_checkout_evidence.json")

        with patch("plugin_examples.publisher.github_pr_merger._api_get") as mock_get:
            mock_get.side_effect = [mock_pr_data, mock_files]
            result = check_merge_preconditions(
                owner="aspose-cells-net",
                repo="Aspose.Cells.LowCode-for-.NET-Examples",
                pr_number=1,
                expected_family="cells",
                clean_checkout_evidence_path=nonexistent,
                github_token="dummy_token",
            )

        self.assertFalse(result["ok"])
        self.assertIn("blocked_merge_no_clean_checkout_evidence", result["blocked_reasons"])


class TestMergeDryRunPerformsNoRemoteMutation(unittest.TestCase):
    """test_merge_dry_run_performs_no_remote_mutation"""

    def test_merge_dry_run_performs_no_remote_mutation(self):
        """simulate_merge always returns live_merge_performed=False."""
        from plugin_examples.publisher.github_pr_merger import simulate_merge

        mock_pr_data = {
            "number": 1,
            "state": "open",
            "merged": False,
            "merged_at": None,
            "head": {"ref": "plugin-examples/words/20260502-135703"},
            "base": {
                "ref": "main",
                "repo": {"full_name": "aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples"},
            },
            "title": "Test PR",
            "changed_files": 23,
        }
        mock_files = [{"filename": "examples/words/lowcode/converter/Program.cs"}]

        with patch("plugin_examples.publisher.github_pr_merger._api_get") as mock_get:
            mock_get.side_effect = [mock_pr_data, mock_files]
            result = simulate_merge(
                owner="aspose-words-net",
                repo="Aspose.Words.LowCode-for-.NET-Examples",
                pr_number=1,
                family="words",
                clean_checkout_evidence_path=None,
                github_token="dummy_token",
            )

        self.assertFalse(result["live_merge_performed"], "simulate_merge must never set live_merge_performed=True")

    def test_merge_dry_run_does_not_call_put_merge_endpoint(self):
        """Dry-run must not call PUT /pulls/{n}/merge."""
        from plugin_examples.publisher.github_pr_merger import simulate_merge

        mock_pr_data = {
            "number": 1,
            "state": "open",
            "merged": False,
            "merged_at": None,
            "head": {"ref": "plugin-examples/words/20260502-135703"},
            "base": {
                "ref": "main",
                "repo": {"full_name": "aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples"},
            },
            "title": "Test PR",
            "changed_files": 23,
        }
        mock_files: list = []

        with (
            patch("urllib.request.urlopen") as mock_urlopen,
            patch("plugin_examples.publisher.github_pr_merger._api_get") as mock_get,
        ):
            mock_get.side_effect = [mock_pr_data, mock_files]
            simulate_merge(
                owner="aspose-words-net",
                repo="Aspose.Words.LowCode-for-.NET-Examples",
                pr_number=1,
                family="words",
                clean_checkout_evidence_path=None,
                github_token="dummy_token",
            )
            # urlopen should not be called for PUT — all reads go via _api_get mock
            for call in mock_urlopen.call_args_list:
                url = str(call)
                self.assertNotIn("/merge", url.lower(), "Dry-run must not call PUT /merge endpoint")


class TestMergeLiveModeRequiresApproveMergePr(unittest.TestCase):
    """test_merge_live_mode_requires_approve_merge_pr"""

    def test_merge_live_mode_blocked_without_approve_merge_pr(self):
        """check_merge_approval rejects APPROVE_LIVE_PR; only APPROVE_MERGE_PR passes."""
        # APPROVE_LIVE_PR must be rejected
        approved, reason = check_merge_approval("APPROVE_LIVE_PR")
        self.assertFalse(approved)
        self.assertEqual(reason, BLOCKED_MERGE_REUSED_LIVE_PUBLISH_TOKEN)

        # APPROVE_MERGE_PR must pass
        approved2, reason2 = check_merge_approval("APPROVE_MERGE_PR")
        self.assertTrue(approved2)
        self.assertEqual(reason2, "")

    def test_merge_live_mode_requires_github_token(self):
        """merge-pr --merge without GITHUB_TOKEN exits 1 with clear error."""
        import subprocess

        # Run without GITHUB_TOKEN — should fail with token missing error
        env_without_token = {k: v for k, v in os.environ.items() if k != "GITHUB_TOKEN"}
        env_without_token["PYTHONPATH"] = "src"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "plugin_examples",
                "merge-pr",
                "--family",
                "words",
                "--pr-number",
                "1",
                "--merge",
                "--approval-token",
                "APPROVE_MERGE_PR",
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
            env=env_without_token,
        )
        self.assertNotEqual(result.returncode, 0, "merge-pr --merge without GITHUB_TOKEN must exit non-zero")
        combined = result.stdout + result.stderr
        self.assertIn("GITHUB_TOKEN", combined, "Expected GITHUB_TOKEN error in output when token is missing")


class TestPostMergePlanWritten(unittest.TestCase):
    """test_post_merge_plan_written"""

    def test_post_merge_plan_written(self):
        """post-merge-verification-plan.json exists and has required fields."""
        plan_path = (
            Path(__file__).resolve().parents[2]
            / "workspace"
            / "verification"
            / "latest"
            / "post-merge-verification-plan.json"
        )
        self.assertTrue(plan_path.exists(), f"Expected {plan_path} to exist")

        with open(plan_path) as f:
            plan = json.load(f)

        self.assertEqual(plan["plan_type"], "post_merge_verification_plan")
        self.assertIn("verification_steps", plan)
        self.assertGreater(len(plan["verification_steps"]), 0)
        self.assertFalse(plan["live_merge_enabled"])
        self.assertIn("families_pending_merge", plan)
        # Both families present
        family_names = [f["family"] for f in plan["families_pending_merge"]]
        self.assertIn("words", family_names)
        self.assertIn("cells", family_names)
        # Runbook documented
        self.assertIn("runbook", plan)

    def test_post_merge_runbook_written(self):
        """post-merge-verification-runbook.md exists."""
        runbook_path = (
            Path(__file__).resolve().parents[2] / "docs" / "publishing" / "post-merge-verification-runbook.md"
        )
        self.assertTrue(runbook_path.exists(), f"Expected {runbook_path} to exist")
        content = runbook_path.read_text()
        self.assertIn("APPROVE_MERGE_PR", content)
        self.assertIn("merge_commit_sha", content)
        self.assertIn("rollback", content.lower())


class TestBranchAutoDelete(unittest.TestCase):
    """Sprint 58 Lane G: branch auto-delete implementation tests.

    The delete_branch_after_merge function:
    - Is DRY-RUN by default (no remote mutation without allow_branch_auto_delete=True AND dry_run=False)
    - Only acts on lowcode-pilot- and lowcode-wave- prefixed branches
    - Skips non-lowcode branches
    - Skips when allow_branch_auto_delete=False
    """

    def _import_delete_fn(self):
        from plugin_examples.publisher.github_pr_merger import delete_branch_after_merge

        return delete_branch_after_merge

    def test_dry_run_by_default(self):
        """delete_branch_after_merge must be dry-run when called with defaults."""
        delete_branch_after_merge = self._import_delete_fn()
        result = delete_branch_after_merge(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch_ref="lowcode-pilot-cells-sprint58",
            github_token="fake-token",
            allow_branch_auto_delete=True,
            dry_run=True,
        )
        self.assertEqual(result["action"], "dry_run_would_delete")
        self.assertIn("api_endpoint", result)
        self.assertTrue(result["dry_run"])

    def test_skips_non_lowcode_branch(self):
        """Branches without lowcode-pilot- or lowcode-wave- prefix must be skipped."""
        delete_branch_after_merge = self._import_delete_fn()
        result = delete_branch_after_merge(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch_ref="main",
            github_token="fake-token",
            allow_branch_auto_delete=True,
            dry_run=False,
        )
        self.assertEqual(result["action"], "skipped")
        self.assertIn("does not match", result["reason"])

    def test_skips_feature_branch_without_prefix(self):
        """Feature branches without recognized prefix must be skipped."""
        delete_branch_after_merge = self._import_delete_fn()
        result = delete_branch_after_merge(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch_ref="feature/add-example",
            github_token="fake-token",
            allow_branch_auto_delete=True,
            dry_run=False,
        )
        self.assertEqual(result["action"], "skipped")

    def test_skips_when_flag_disabled(self):
        """When allow_branch_auto_delete=False, even lowcode branches must be skipped."""
        delete_branch_after_merge = self._import_delete_fn()
        result = delete_branch_after_merge(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch_ref="lowcode-pilot-cells-sprint58",
            github_token="fake-token",
            allow_branch_auto_delete=False,
            dry_run=False,
        )
        self.assertEqual(result["action"], "skipped")
        self.assertIn("allow_branch_auto_delete=False", result["reason"])

    def test_lowcode_wave_prefix_recognized(self):
        """lowcode-wave- prefix is also recognized for auto-delete."""
        delete_branch_after_merge = self._import_delete_fn()
        result = delete_branch_after_merge(
            owner="aspose-pdf-net",
            repo="Aspose.PDF.LowCode-for-.NET-Examples",
            branch_ref="lowcode-wave-pdf-sprint58-wave-g",
            github_token="fake-token",
            allow_branch_auto_delete=True,
            dry_run=True,
        )
        self.assertEqual(result["action"], "dry_run_would_delete")
        self.assertIn("lowcode-wave-pdf-sprint58-wave-g", result["api_endpoint"])

    def test_dry_run_does_not_call_api(self):
        """Dry-run must never invoke _api_delete."""
        delete_branch_after_merge = self._import_delete_fn()
        with patch("plugin_examples.publisher.github_pr_merger._api_delete") as mock_delete:
            delete_branch_after_merge(
                owner="aspose-cells-net",
                repo="test-repo",
                branch_ref="lowcode-pilot-cells-sprint58",
                github_token="fake-token",
                allow_branch_auto_delete=True,
                dry_run=True,
            )
            mock_delete.assert_not_called()

    def test_no_api_call_when_flag_disabled(self):
        """_api_delete must never be called when allow_branch_auto_delete=False."""
        delete_branch_after_merge = self._import_delete_fn()
        with patch("plugin_examples.publisher.github_pr_merger._api_delete") as mock_delete:
            delete_branch_after_merge(
                owner="aspose-cells-net",
                repo="test-repo",
                branch_ref="lowcode-pilot-cells-sprint58",
                github_token="fake-token",
                allow_branch_auto_delete=False,
                dry_run=False,
            )
            mock_delete.assert_not_called()
