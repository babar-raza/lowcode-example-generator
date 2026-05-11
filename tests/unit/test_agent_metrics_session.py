"""Tests for MetricsSession — command-agnostic metrics runtime."""

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
            "agent_name": "Lowcode Example Generator",
            "agent_name_test_prefix": "test-",
            "website": "aspose.net",
            "family_to_product": {"cells": "Aspose.Cells"},
            "command_to_job_type": {"run": "Examples Generation", "discover-lowcode": "Discovery"},
            "command_to_item_name": {"run": "Examples", "discover-lowcode": "API Types"},
            "verdict_to_status": {"PR_READY": "success"},
            "api_endpoint": "https://example.com/exec",
            "post_ledger_path": str(tmp_path / "ledger.jsonl"),
        }
    }
    p = tmp_path / "m.yml"
    p.write_text(yaml.dump(cfg_data), encoding="utf-8")
    return load_metrics_config(config_path=p)


class TestSessionLifecycle:
    def test_session_starts_active(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        session = MetricsSession(
            command="run", family="cells", config=_config,
            collector=MetricsCollector(), evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-session-1",
        )
        session.start()
        assert session.active is True

    def test_excluded_command_not_active(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        session = MetricsSession(
            command="status", family="", config=_config,
            collector=MetricsCollector(), evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-status-1",
        )
        session.start()
        assert session.active is False

    def test_inactive_session_finalize_noop(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession

        session = MetricsSession(
            command="status", family="", config=_config,
            evidence_dir=tmp_path, repo_root=tmp_path,
        )
        result = session.finalize()
        assert result["metrics_enabled"] is False


class TestCountSourcePolicy:
    def test_run_command_external_allowed(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession

        session = MetricsSession(command="run", config=_config,
                                  evidence_dir=tmp_path, repo_root=tmp_path)
        assert session.external_post_allowed is True
        assert session.count_source_policy == "SUPPORTED_EXTERNAL_METRICS"

    def test_discover_command_local_only(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession

        session = MetricsSession(command="discover-lowcode", config=_config,
                                  evidence_dir=tmp_path, repo_root=tmp_path)
        assert session.external_post_allowed is False
        assert session.count_source_policy == "LOCAL_ONLY_LLM_METRICS"

    def test_status_command_excluded(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession

        session = MetricsSession(command="status", config=_config,
                                  evidence_dir=tmp_path, repo_root=tmp_path)
        assert session.count_source_policy == "EXCLUDED_INFO_ONLY"

    def test_check_command_excluded(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession

        session = MetricsSession(command="check", config=_config,
                                  evidence_dir=tmp_path, repo_root=tmp_path)
        assert session.count_source_policy == "EXCLUDED_INFO_ONLY"


class TestLocalOnlyBlocking:
    def test_local_only_command_blocks_external_post(self, _config, tmp_path):
        """Commands with unverified count formulas write evidence but block POST."""
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        collector = MetricsCollector()
        collector.record_call(provider="llm_professionalize", total_tokens=100)

        session = MetricsSession(
            command="discover-lowcode", family="cells", config=_config,
            collector=collector, evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-discover-1",
            post=True, dry_run=False,
        )
        session.start()

        with patch("plugin_examples.metrics.poster.requests.post") as mock_post:
            result = session.finalize(items_discovered=3, items_succeeded=2, items_failed=1)

        # No HTTP POST should have been made
        mock_post.assert_not_called()
        assert result["post_result"]["posted"] is False
        assert "count_source_unverified" in result["post_result"]["reason"]

        # But local evidence must exist
        files = [f.name for f in tmp_path.iterdir() if f.is_file()]
        assert "agent-metrics-run-summary.json" in files
        assert "agent-metrics-payload.json" in files

    def test_local_only_command_records_llm_metrics(self, _config, tmp_path):
        """LLM calls are captured even for local-only commands."""
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        collector = MetricsCollector()
        collector.record_call(provider="llm_professionalize", total_tokens=500,
                              token_usage_available=True)

        session = MetricsSession(
            command="discover-lowcode", family="cells", config=_config,
            collector=collector, evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-local-llm-1",
        )
        session.start()
        result = session.finalize(items_discovered=1)

        payload = result["payload"]
        assert payload["token_usage"] == 500
        assert payload["api_calls_count"] == 1

    def test_test_job_type_bypasses_local_only(self, _config, tmp_path):
        """Test job_type is allowed even for local-only commands."""
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        session = MetricsSession(
            command="discover-lowcode", family="cells", config=_config,
            collector=MetricsCollector(), evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-bypass-1",
            post=True, dry_run=False, job_type_override="Test",
        )
        session.start()

        # The post should attempt (test mode bypasses local-only block)
        # It will fail due to missing token, but that's expected
        result = session.finalize(items_discovered=1, items_succeeded=1)
        # Should NOT be blocked by count_source_unverified
        assert result["post_result"].get("reason") != "count_source_unverified_for_discover-lowcode"


class TestEvidenceWriting:
    def test_session_writes_all_evidence(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        collector = MetricsCollector()
        collector.record_call(provider="llm_professionalize", total_tokens=200)

        session = MetricsSession(
            command="run", family="cells", config=_config,
            collector=collector, evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-ev-1",
        )
        session.start()
        result = session.finalize(items_discovered=5, items_succeeded=3, items_failed=2)

        files = [f.name for f in tmp_path.iterdir() if f.is_file()]
        assert "agent-metrics-llm-calls.jsonl" in files
        assert "agent-metrics-run-summary.json" in files
        assert "agent-metrics-payload.json" in files
        assert "agent-metrics-validation.json" in files
        assert "agent-metrics-post-result.json" in files

    def test_summary_includes_count_policy(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        session = MetricsSession(
            command="discover-lowcode", family="cells", config=_config,
            collector=MetricsCollector(), evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-policy-1",
        )
        session.start()
        session.finalize()

        summary = json.loads((tmp_path / "agent-metrics-run-summary.json").read_text())
        assert summary["count_source_policy"] == "LOCAL_ONLY_LLM_METRICS"
        assert summary["external_post_allowed"] is False


class TestAgentName:
    def test_production_agent_name_is_stable(self, _config):
        """Production agent_name must be Lowcode Example Generator, not command-specific."""
        from plugin_examples.metrics.payload_builder import build_payload

        payload = build_payload(_config, command="run", family="cells", run_id="prod-1")
        assert payload["agent_name"] == "Lowcode Example Generator"

    def test_production_agent_name_same_for_all_commands(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        p1 = build_payload(_config, command="run", family="cells", run_id="t1")
        p2 = build_payload(_config, command="discover-lowcode", family="cells", run_id="t2")
        assert p1["agent_name"] == p2["agent_name"] == "Lowcode Example Generator"

    def test_test_mode_prefixes_agent_name(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        payload = build_payload(
            _config, command="run", family="cells", run_id="myrun",
            test_mode=True, job_type_override="Test",
        )
        assert payload["agent_name"] == "test-Lowcode Example Generator"

    def test_command_in_job_type_not_agent_name(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        p = build_payload(_config, command="run", family="cells", run_id="t")
        assert "run" not in p["agent_name"]
        assert p["job_type"] == "Examples Generation"  # command identity in job_type

    def test_production_config_agent_name(self):
        """Verify actual metrics.yml has stable agent_name."""
        from plugin_examples.metrics.config import load_metrics_config

        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / "pipeline" / "configs" / "metrics.yml"
        if not cfg_path.exists():
            pytest.skip("metrics.yml not found")
        cfg = load_metrics_config(config_path=cfg_path)
        assert cfg.agent_name == "Lowcode Example Generator"
        assert "run" not in cfg.agent_name
        assert "{" not in cfg.agent_name  # no template syntax


class TestAutomaticLLMCapture:
    def test_router_with_collector_records_calls(self):
        """Any LLMRouter with metrics_collector records all LLM calls."""
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.llm_router.router import LLMRouter

        collector = MetricsCollector()
        router = LLMRouter(
            provider_order=["llm_professionalize"],
            metrics_collector=collector,
        )
        assert router.metrics_collector is collector

    def test_non_run_command_with_router_records_metrics(self, _config, tmp_path):
        """Simulated non-run command using LLMRouter still records LLM metrics."""
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        collector = MetricsCollector()
        # Simulate a hypothetical command making 3 LLM calls via router
        collector.record_call(provider="llm_professionalize", total_tokens=100)
        collector.record_call(provider="llm_professionalize", total_tokens=200)
        collector.record_call(provider="llm_professionalize", total_tokens=300)

        session = MetricsSession(
            command="discover-lowcode", family="cells", config=_config,
            collector=collector, evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-nonrun-llm-1",
        )
        session.start()
        result = session.finalize(items_discovered=1)

        assert result["payload"]["token_usage"] == 600
        assert result["payload"]["api_calls_count"] == 3

        # LLM calls evidence should be written
        assert (tmp_path / "agent-metrics-llm-calls.jsonl").exists()
        lines = (tmp_path / "agent-metrics-llm-calls.jsonl").read_text().strip().split("\n")
        assert len(lines) == 3

    def test_disabled_metrics_no_side_effects(self):
        """Metrics disabled = no collector, no evidence, no overhead."""
        from plugin_examples.metrics.models import MetricsCollector

        collector = MetricsCollector(enabled=False)
        collector.record_call(provider="test", total_tokens=999)
        assert collector.api_calls_count == 0
        assert collector.token_usage == 0


class TestSafetyGates:
    def test_dry_run_session_never_posts(self, _config, tmp_path):
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        session = MetricsSession(
            command="run", family="cells", config=_config,
            collector=MetricsCollector(), evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-dry-1",
            dry_run=True, post=False,
        )
        session.start()

        with patch("plugin_examples.metrics.poster.requests.post") as mock_post:
            result = session.finalize(items_discovered=1)

        mock_post.assert_not_called()
        assert result["post_result"]["posted"] is False

    def test_force_repost_cannot_bypass_production_safety(self, _config, tmp_path):
        """--metrics-force-repost does not bypass test_only_sprint."""
        from plugin_examples.metrics.session import MetricsSession
        from plugin_examples.metrics.models import MetricsCollector

        session = MetricsSession(
            command="run", family="cells", config=_config,
            collector=MetricsCollector(), evidence_dir=tmp_path,
            repo_root=tmp_path, run_id="test-force-prod-1",
            dry_run=False, post=True, force_repost=True,
            # No job_type_override → production job_type
        )
        session.start()

        with patch("plugin_examples.metrics.poster.requests.post") as mock_post:
            result = session.finalize(items_discovered=1)

        # test_only_sprint should block production job_type
        mock_post.assert_not_called()
        assert result["post_result"]["posted"] is False
        assert "blocked" in result["post_result"]["reason"]
