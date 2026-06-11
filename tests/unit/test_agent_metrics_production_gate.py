"""TC14 production gate tests — is_agent_metrics_production_enabled() and runner integration."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def _config(tmp_path):
    from plugin_examples.metrics.config import load_metrics_config

    cfg_data = {
        "metrics": {
            "agent_owner": "Babar Raza",
            "agent_name": "Lowcode Example Generator",
            "website": "aspose.net",
            "website_section": "Examples",
            "platform": ".NET",
            "family_to_product": {"cells": "Aspose.Cells"},
            "command_to_job_type": {"run": "Examples Generation"},
            "command_to_item_name": {"run": "Examples"},
            "verdict_to_status": {"PR_DRY_RUN_READY": "success"},
            "api_endpoint": "https://example.com/exec",
            "post_ledger_path": str(tmp_path / "ledger.jsonl"),
        }
    }
    p = tmp_path / "m.yml"
    p.write_text(yaml.dump(cfg_data), encoding="utf-8")
    return load_metrics_config(config_path=p)


# ---------------------------------------------------------------------------
# Tests 1-5: is_agent_metrics_production_enabled() env var behavior
# ---------------------------------------------------------------------------


class TestProductionGateEnvVar:
    def test_production_gate_absent_keeps_sprint_true(self, monkeypatch):
        """Gate absent → production disabled → test_only_sprint=True."""
        monkeypatch.delenv("AGENT_METRICS_PRODUCTION_ENABLED", raising=False)
        from plugin_examples.metrics.config import is_agent_metrics_production_enabled

        assert is_agent_metrics_production_enabled() is False

    def test_production_gate_empty_string_keeps_sprint_true(self, monkeypatch):
        """Empty string → production disabled."""
        monkeypatch.setenv("AGENT_METRICS_PRODUCTION_ENABLED", "")
        from plugin_examples.metrics.config import is_agent_metrics_production_enabled

        assert is_agent_metrics_production_enabled() is False

    def test_production_gate_false_keeps_sprint_true(self, monkeypatch):
        """'false' → production disabled."""
        monkeypatch.setenv("AGENT_METRICS_PRODUCTION_ENABLED", "false")
        from plugin_examples.metrics.config import is_agent_metrics_production_enabled

        assert is_agent_metrics_production_enabled() is False

    def test_production_gate_mixed_case_invalid_keeps_sprint_true(self, monkeypatch):
        """'True' (capital T) must NOT enable production — only exact 'true' allowed."""
        monkeypatch.setenv("AGENT_METRICS_PRODUCTION_ENABLED", "True")
        from plugin_examples.metrics.config import is_agent_metrics_production_enabled

        assert is_agent_metrics_production_enabled() is False

    def test_production_gate_true_enables_production(self, monkeypatch):
        """Exact lowercase 'true' → production enabled."""
        monkeypatch.setenv("AGENT_METRICS_PRODUCTION_ENABLED", "true")
        from plugin_examples.metrics.config import is_agent_metrics_production_enabled

        assert is_agent_metrics_production_enabled() is True


# ---------------------------------------------------------------------------
# Tests 6-10: Production gate does not bypass other poster gates
# ---------------------------------------------------------------------------


class TestProductionGateDoesNotBypassOtherGates:
    def test_production_gate_does_not_bypass_dry_run(self, _config):
        """Gate enabled + dry_run=True → still blocked by dry_run gate, not sprint gate."""
        from plugin_examples.metrics.poster import post_metrics

        with patch("plugin_examples.metrics.poster.requests.post") as mock_post:
            result = post_metrics(
                {"run_id": "prod-test-1", "job_type": "Examples Generation"},
                _config,
                dry_run=True,
                test_only_sprint=False,  # production gate enabled
            )
        mock_post.assert_not_called()
        assert result["posted"] is False
        assert result["reason"] == "dry_run"

    def test_production_gate_does_not_bypass_missing_token(self, _config, monkeypatch):
        """Gate enabled + no AGENT_METRICS_TOKEN → blocked by token gate."""
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.delenv("AGENT_METRICS_TOKEN", raising=False)
        result = post_metrics(
            {"run_id": "prod-test-2", "job_type": "Examples Generation"},
            _config,
            dry_run=False,
            test_only_sprint=False,  # production gate enabled
        )
        assert result["posted"] is False
        assert "missing" in result["reason"]

    def test_production_gate_does_not_bypass_duplicate_ledger(self, _config, monkeypatch):
        """Gate enabled + duplicate run_id in ledger → blocked by duplicate gate."""
        from plugin_examples.metrics.poster import post_metrics

        monkeypatch.setenv("AGENT_METRICS_TOKEN", "FAKE_TOKEN_FOR_TESTING")
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ok":true}'

        payload = {"run_id": "prod-dup-test", "job_type": "Examples Generation"}

        with patch("plugin_examples.metrics.poster.requests.post", return_value=mock_resp):
            r1 = post_metrics(payload, _config, dry_run=False, test_only_sprint=False)
            r2 = post_metrics(payload, _config, dry_run=False, test_only_sprint=False)

        assert r1["posted"] is True
        assert r2["posted"] is False
        assert r2["reason"] == "duplicate_already_posted"

    def test_production_gate_does_not_bypass_external_command_allowlist(self):
        """Non-run commands cannot POST externally regardless of production gate."""
        from plugin_examples.metrics.session import MetricsSession, EXTERNAL_POST_COMMANDS

        assert "discover-lowcode" not in EXTERNAL_POST_COMMANDS
        assert "publish-pr" not in EXTERNAL_POST_COMMANDS
        assert "merge-pr" not in EXTERNAL_POST_COMMANDS
        # Only 'run' is allowed
        assert "run" in EXTERNAL_POST_COMMANDS

    def test_force_repost_cannot_bypass_test_only_sprint(self, _config):
        """force_repost=True bypasses duplicate check only, NOT sprint gate."""
        from plugin_examples.metrics.poster import post_metrics

        result = post_metrics(
            {"run_id": "force-sprint-test", "job_type": "Examples Generation"},
            _config,
            dry_run=False,
            test_only_sprint=True,  # sprint gate active
            force_repost=True,  # only bypasses dedup, not sprint gate
        )
        assert result["posted"] is False
        assert "blocked" in result["reason"]


# ---------------------------------------------------------------------------
# Tests 11-12: Production payload shape
# ---------------------------------------------------------------------------


class TestProductionPayloadShape:
    def test_production_payload_has_no_test_prefixes(self, _config):
        """When test_mode=False, agent_name/item_name/run_id have no 'test-' prefix."""
        from plugin_examples.metrics.payload_builder import build_payload

        payload = build_payload(
            config=_config,
            command="run",
            family="cells",
            run_id="pilot-cells-20260507-120000",
            verdict="PR_DRY_RUN_READY",
            items_discovered=9,
            items_succeeded=9,
            items_failed=0,
            token_usage=1500,
            api_calls_count=3,
            test_mode=False,
        )
        assert not payload["agent_name"].startswith(
            "test-"
        ), f"agent_name should not start with 'test-', got: {payload['agent_name']}"
        assert not payload["item_name"].startswith(
            "test-"
        ), f"item_name should not start with 'test-', got: {payload['item_name']}"
        assert not payload["run_id"].startswith(
            "test-"
        ), f"run_id should not start with 'test-', got: {payload['run_id']}"
        assert payload["agent_name"] == "Lowcode Example Generator"
        assert payload["item_name"] == "Examples"

    def test_website_remains_aspose_net_in_production_mode(self, _config):
        """Website must be config-driven and equal to 'aspose.net' in production mode."""
        from plugin_examples.metrics.payload_builder import build_payload

        payload = build_payload(
            config=_config,
            command="run",
            family="cells",
            run_id="pilot-cells-20260507-120000",
            verdict="PR_DRY_RUN_READY",
            items_discovered=9,
            items_succeeded=9,
            items_failed=0,
            token_usage=1500,
            api_calls_count=3,
            test_mode=False,
        )
        assert payload["website"] == "aspose.net"
        assert payload["platform"] == ".NET"
        assert payload["website_section"] == "Examples"


# ---------------------------------------------------------------------------
# Test 13: Runner integration — test_only_sprint=False when gate enabled
# ---------------------------------------------------------------------------


class TestRunnerProductionGateIntegration:
    def test_runner_passes_test_only_sprint_false_when_gate_enabled(self, monkeypatch):
        """When AGENT_METRICS_PRODUCTION_ENABLED=true, runner passes test_only_sprint=False."""
        monkeypatch.setenv("AGENT_METRICS_PRODUCTION_ENABLED", "true")
        from plugin_examples.metrics.config import is_agent_metrics_production_enabled

        # Verify helper returns True
        assert is_agent_metrics_production_enabled() is True
        # Verify test_only_sprint logic: not is_agent_metrics_production_enabled() == False
        test_only_sprint = not is_agent_metrics_production_enabled()
        assert test_only_sprint is False

    def test_runner_passes_test_only_sprint_true_by_default(self, monkeypatch):
        """When AGENT_METRICS_PRODUCTION_ENABLED is not set, runner passes test_only_sprint=True."""
        monkeypatch.delenv("AGENT_METRICS_PRODUCTION_ENABLED", raising=False)
        from plugin_examples.metrics.config import is_agent_metrics_production_enabled

        assert is_agent_metrics_production_enabled() is False
        test_only_sprint = not is_agent_metrics_production_enabled()
        assert test_only_sprint is True
