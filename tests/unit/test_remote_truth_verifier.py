"""Unit tests for remote truth verifier — TC-REMOTE-001."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.publisher.remote_truth_verifier import (
    RemoteTruthResult,
    run_remote_truth_check,
    verify_branch_exists,
    verify_file_on_branch,
    verify_pr_state,
    write_remote_truth_report,
)


class TestVerifyPrState:
    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_merged_pr(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"state": "closed", "merged_at": "2026-06-01T00:00:00Z"},
        )
        mock_get.return_value.raise_for_status = MagicMock()
        result = verify_pr_state("owner", "repo", 42, "token")
        assert result.pr_exists is True
        assert result.pr_merged is True
        assert result.pr_state == "closed"

    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_open_pr(self, mock_get):
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"state": "open", "merged_at": None},
        )
        mock_get.return_value.raise_for_status = MagicMock()
        result = verify_pr_state("owner", "repo", 42, "token")
        assert result.pr_exists is True
        assert result.pr_merged is False
        assert result.pr_state == "open"

    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_pr_not_found(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)
        result = verify_pr_state("owner", "repo", 999)
        assert result.pr_exists is False
        assert "404" in result.error


class TestVerifyBranchExists:
    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_branch_exists(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        assert verify_branch_exists("owner", "repo", "main") is True

    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_branch_missing(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)
        assert verify_branch_exists("owner", "repo", "deleted-branch") is False


class TestVerifyFileOnBranch:
    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_file_exists(self, mock_get):
        mock_get.return_value = MagicMock(status_code=200)
        assert verify_file_on_branch("owner", "repo", "main", "README.md") is True

    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_file_missing(self, mock_get):
        mock_get.return_value = MagicMock(status_code=404)
        assert verify_file_on_branch("owner", "repo", "main", "nope.txt") is False


class TestRunRemoteTruthCheck:
    @patch("plugin_examples.publisher.remote_truth_verifier.requests.get")
    def test_full_check_merged(self, mock_get):
        def side_effect(url, **kwargs):
            resp = MagicMock()
            if "/pulls/" in url:
                resp.status_code = 200
                resp.json = lambda: {"state": "closed", "merged_at": "2026-06-01T00:00:00Z"}
                resp.raise_for_status = MagicMock()
            elif "/branches/" in url:
                resp.status_code = 200
            elif "/contents/" in url:
                resp.status_code = 200
            return resp

        mock_get.side_effect = side_effect

        records = [{
            "owner": "aspose-cells",
            "repo": "Aspose.Cells-for-.NET",
            "pr_number": 42,
            "branch": "lowcode/wave20/cells-examples",
            "expected_file_path": "examples/cells/converter/Program.cs",
        }]
        results = run_remote_truth_check(records, "token")
        assert len(results) == 1
        assert results[0].pr_merged is True
        assert results[0].branch_exists is True
        assert results[0].file_exists is True


class TestWriteRemoteTruthReport:
    def test_writes_valid_json(self, tmp_path):
        results = [
            RemoteTruthResult(owner="o", repo="r", pr_number=1, pr_exists=True, pr_merged=True),
        ]
        output = tmp_path / "report.json"
        write_remote_truth_report(results, output)
        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["total_checked"] == 1
        assert data["total_merged"] == 1
