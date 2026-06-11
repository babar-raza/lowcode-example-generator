"""Tests for metrics poster — dry-run safety, ledger, mocked HTTP."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml


@pytest.fixture
def _config(tmp_path):
    from plugin_examples.metrics.config import load_metrics_config

    cfg_data = {
        "metrics": {
            "agent_owner": "Test",
            "agent_name": "test-gen",
            "website": "aspose.net",
            "family_to_product": {"cells": "Aspose.Cells"},
            "command_to_job_type": {"run": "Examples Generation"},
            "verdict_to_status": {"PR_READY": "success"},
            "api_endpoint": "https://example.com/exec",
            "post_ledger_path": str(tmp_path / "ledger.jsonl"),
        }
    }
    p = tmp_path / "m.yml"
    p.write_text(yaml.dump(cfg_data), encoding="utf-8")
    return load_metrics_config(config_path=p)


class TestDryRun:
    def test_dry_run_never_posts(self, _config):
        from plugin_examples.metrics.poster import post_metrics

        with patch("plugin_examples.metrics.poster.requests.post") as mock_post:
            result = post_metrics(
                {"run_id": "t-1", "job_type": "Test"},
                _config,
                dry_run=True,
            )
        mock_post.assert_not_called()
        assert result["posted"] is False
        assert result["reason"] == "dry_run"

    def test_dry_run_does_not_append_ledger(self, _config, tmp_path):
        from plugin_examples.metrics.poster import post_metrics

        ledger_path = Path(_config.post_ledger_path)
        post_metrics({"run_id": "t-1", "job_type": "Test"}, _config, dry_run=True)
        assert not ledger_path.exists() or ledger_path.stat().st_size == 0


class TestTestOnlySprint:
    def test_production_job_type_blocked(self, _config):
        from plugin_examples.metrics.poster import post_metrics

        result = post_metrics(
            {"run_id": "t-1", "job_type": "Examples Generation"},
            _config,
            dry_run=False,
            test_only_sprint=True,
        )
        assert result["posted"] is False
        assert "blocked" in result["reason"]

    def test_test_job_type_allowed(self, _config, monkeypatch):
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.setenv("AGENT_METRICS_TOKEN", "FAKE_TOKEN_FOR_TESTING")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"status":"ok"}'

        with patch("plugin_examples.metrics.poster.requests.post", return_value=mock_resp):
            result = post_metrics(
                {"run_id": "test-1", "job_type": "Test"},
                _config,
                dry_run=False,
                test_only_sprint=True,
            )
        assert result["posted"] is True


class TestDuplicatePrevention:
    def test_duplicate_blocked(self, _config, monkeypatch):
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.setenv("AGENT_METRICS_TOKEN", "FAKE_TOKEN_FOR_TESTING")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok":true}'

        payload = {"run_id": "test-dup", "job_type": "Test"}

        with patch("plugin_examples.metrics.poster.requests.post", return_value=mock_resp):
            r1 = post_metrics(payload, _config, dry_run=False, test_only_sprint=True)
            r2 = post_metrics(payload, _config, dry_run=False, test_only_sprint=True)

        assert r1["posted"] is True
        assert r2["posted"] is False
        assert r2["reason"] == "duplicate_already_posted"

    def test_force_repost_bypasses_duplicate(self, _config, monkeypatch):
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.setenv("AGENT_METRICS_TOKEN", "FAKE_TOKEN_FOR_TESTING")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok":true}'

        payload = {"run_id": "test-force", "job_type": "Test"}

        with patch("plugin_examples.metrics.poster.requests.post", return_value=mock_resp):
            r1 = post_metrics(payload, _config, dry_run=False, test_only_sprint=True)
            r2 = post_metrics(payload, _config, dry_run=False, test_only_sprint=True, force_repost=True)

        assert r1["posted"] is True
        assert r2["posted"] is True


class TestNetworkFailure:
    def test_network_error_graceful(self, _config, monkeypatch):
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.setenv("AGENT_METRICS_TOKEN", "FAKE_TOKEN_FOR_TESTING")

        with patch("plugin_examples.metrics.poster.requests.post", side_effect=Exception("timeout")):
            result = post_metrics(
                {"run_id": "test-net", "job_type": "Test"},
                _config,
                dry_run=False,
                test_only_sprint=True,
            )
        assert result["posted"] is False
        assert result["reason"] == "network_error"


class TestTokenSecurity:
    def test_missing_token_blocks_post(self, _config, monkeypatch):
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.delenv("AGENT_METRICS_TOKEN", raising=False)
        result = post_metrics(
            {"run_id": "test-notoken", "job_type": "Test"},
            _config,
            dry_run=False,
            test_only_sprint=True,
        )
        assert result["posted"] is False
        assert "missing" in result["reason"]

    def test_token_not_in_result(self, _config, monkeypatch):
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.setenv("AGENT_METRICS_TOKEN", "sk-SUPERSECRET99")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok":true}'

        with patch("plugin_examples.metrics.poster.requests.post", return_value=mock_resp):
            result = post_metrics(
                {"run_id": "test-sec", "job_type": "Test"},
                _config,
                dry_run=False,
                test_only_sprint=True,
            )

        result_str = json.dumps(result)
        assert "SUPERSECRET" not in result_str


class TestLedger:
    def test_ledger_created_on_success(self, _config, monkeypatch):
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.setenv("AGENT_METRICS_TOKEN", "FAKE")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok":true}'

        with patch("plugin_examples.metrics.poster.requests.post", return_value=mock_resp):
            post_metrics(
                {"run_id": "test-ledger", "job_type": "Test"},
                _config,
                dry_run=False,
                test_only_sprint=True,
            )

        ledger = Path(_config.post_ledger_path)
        assert ledger.exists()
        entries = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(entries) == 1
        assert entries[0]["run_id"] == "test-ledger"
        assert entries[0]["dry_run"] is False
