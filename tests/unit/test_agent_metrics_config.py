"""Tests for agent metrics config and models."""

import textwrap
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def _metrics_yml(tmp_path):
    """Create a minimal metrics.yml for testing."""
    cfg = {
        "metrics": {
            "enabled": True,
            "dry_run": True,
            "agent_owner": "Test Owner",
            "agent_name": "test-gen",
            "website": "aspose.net",
            "website_section": "Examples",
            "platform": ".NET",
            "family_to_product": {"cells": "Aspose.Cells"},
            "command_to_job_type": {"run": "Examples Generation"},
            "command_to_item_name": {"run": "Examples"},
            "verdict_to_status": {
                "PR_READY": "success",
                "BLOCKED_GENERATION": "failure",
            },
            "api_endpoint": "https://example.com/exec",
            "post_ledger_path": "workspace/verification/agent-metrics-post-ledger.jsonl",
        }
    }
    p = tmp_path / "metrics.yml"
    p.write_text(yaml.dump(cfg), encoding="utf-8")
    return p


class TestMetricsConfigLoading:
    def test_loads_from_yaml(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        assert cfg.enabled is True
        assert cfg.dry_run is True
        assert cfg.agent_owner == "Test Owner"
        assert cfg.website == "aspose.net"
        assert cfg.family_to_product == {"cells": "Aspose.Cells"}

    def test_website_comes_from_config_not_hardcoded(self, tmp_path):
        """Prove website is config-driven by loading a custom value."""
        from plugin_examples.metrics.config import load_metrics_config

        cfg_data = {
            "metrics": {
                "website": "custom.example.org",
                "agent_owner": "X",
                "agent_name": "x-gen",
                "family_to_product": {"a": "A"},
                "command_to_job_type": {"run": "gen"},
                "verdict_to_status": {"X": "failure"},
                "api_endpoint": "https://x.com",
            }
        }
        p = tmp_path / "m.yml"
        p.write_text(yaml.dump(cfg_data), encoding="utf-8")
        cfg = load_metrics_config(config_path=p)
        assert cfg.website == "custom.example.org"

    def test_default_website_is_aspose_net(self):
        """Default website must be aspose.net, not aspose.com."""
        from plugin_examples.metrics.config import load_metrics_config

        # Load from nonexistent path → defaults
        cfg = load_metrics_config(config_path=Path("/nonexistent/metrics.yml"))
        assert cfg.website == "aspose.net"

    def test_missing_file_returns_defaults(self):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=Path("/no/such/file.yml"))
        assert cfg.enabled is False
        assert cfg.dry_run is True

    def test_override_dict(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml, override={"website": "override.net"})
        assert cfg.website == "override.net"


class TestMetricsConfigValidation:
    def test_valid_config_no_errors(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        assert cfg.validate() == []

    def test_missing_agent_owner(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml, override={"agent_owner": ""})
        errors = cfg.validate()
        assert any("agent_owner" in e for e in errors)

    def test_missing_family_mapping(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml, override={"family_to_product": {}})
        errors = cfg.validate()
        assert any("family_to_product" in e for e in errors)

    def test_invalid_verdict_status(self, tmp_path):
        from plugin_examples.metrics.config import load_metrics_config

        cfg_data = {
            "metrics": {
                "agent_owner": "X",
                "agent_name": "x-gen",
                "website": "aspose.net",
                "family_to_product": {"a": "A"},
                "command_to_job_type": {"run": "gen"},
                "verdict_to_status": {"BAD": "invalid_status"},
                "api_endpoint": "https://x.com",
            }
        }
        p = tmp_path / "m.yml"
        p.write_text(yaml.dump(cfg_data), encoding="utf-8")
        cfg = load_metrics_config(config_path=p)
        errors = cfg.validate()
        assert any("invalid status" in e for e in errors)

    def test_validate_family_missing(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        err = cfg.validate_family("unknown_family")
        assert err is not None
        assert "unknown_family" in err

    def test_validate_family_present(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        assert cfg.validate_family("cells") is None

    def test_validate_command_missing(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        err = cfg.validate_command("unknown_cmd")
        assert err is not None

    def test_validate_command_present(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        assert cfg.validate_command("run") is None


class TestVerdictResolution:
    def test_known_verdict(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        status, unknown = cfg.resolve_status("PR_READY")
        assert status == "success"
        assert unknown is False

    def test_unknown_verdict_maps_to_failure(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        status, unknown = cfg.resolve_status("NEVER_HEARD_OF_THIS")
        assert status == "failure"
        assert unknown is True

    def test_unknown_verdict_never_maps_to_success(self, _metrics_yml):
        from plugin_examples.metrics.config import load_metrics_config

        cfg = load_metrics_config(config_path=_metrics_yml)
        status, _ = cfg.resolve_status("TOTALLY_UNKNOWN")
        assert status != "success"


class TestMetricsCollector:
    def test_empty_collector(self):
        from plugin_examples.metrics.models import MetricsCollector

        mc = MetricsCollector()
        assert mc.token_usage == 0
        assert mc.api_calls_count == 0

    def test_record_call_increments(self):
        from plugin_examples.metrics.models import MetricsCollector

        mc = MetricsCollector()
        mc.record_call(provider="llm_professionalize", total_tokens=100, token_usage_available=True)
        mc.record_call(provider="llm_professionalize", total_tokens=200, token_usage_available=True)
        assert mc.api_calls_count == 2
        assert mc.token_usage == 300

    def test_disabled_collector_ignores_calls(self):
        from plugin_examples.metrics.models import MetricsCollector

        mc = MetricsCollector(enabled=False)
        mc.record_call(provider="test", total_tokens=999)
        assert mc.api_calls_count == 0
        assert mc.token_usage == 0

    def test_call_index_sequential(self):
        from plugin_examples.metrics.models import MetricsCollector

        mc = MetricsCollector()
        mc.record_call(provider="a")
        mc.record_call(provider="b")
        assert mc.calls[0].call_index == 1
        assert mc.calls[1].call_index == 2

    def test_two_collectors_independent(self):
        from plugin_examples.metrics.models import MetricsCollector

        mc1 = MetricsCollector()
        mc2 = MetricsCollector()
        mc1.record_call(provider="a", total_tokens=10)
        mc2.record_call(provider="b", total_tokens=20)
        mc2.record_call(provider="b", total_tokens=30)
        assert mc1.api_calls_count == 1
        assert mc1.token_usage == 10
        assert mc2.api_calls_count == 2
        assert mc2.token_usage == 50


class TestProductionConfig:
    def test_production_config_loads(self):
        """Verify the actual pipeline/configs/metrics.yml loads correctly."""
        from plugin_examples.metrics.config import load_metrics_config

        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / "pipeline" / "configs" / "metrics.yml"
        if not cfg_path.exists():
            pytest.skip("metrics.yml not found")
        cfg = load_metrics_config(config_path=cfg_path)
        assert cfg.website == "aspose.net"
        assert cfg.agent_owner == "Babar Raza"
        assert "cells" in cfg.family_to_product
        assert "words" in cfg.family_to_product
        assert "pdf" in cfg.family_to_product
        assert cfg.enabled is False  # default disabled
        assert cfg.dry_run is True
        errors = cfg.validate()
        # api_endpoint is intentionally empty in metrics.yml — supplied via AGENT_METRICS_ENDPOINT env var.
        # Filter it out before asserting; all other fields must be valid.
        non_endpoint_errors = [e for e in errors if "api_endpoint" not in e]
        assert non_endpoint_errors == [], f"Production config has non-endpoint errors: {non_endpoint_errors}"

    def test_production_config_has_all_verdicts(self):
        from plugin_examples.gates.models import VERDICTS
        from plugin_examples.metrics.config import load_metrics_config

        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / "pipeline" / "configs" / "metrics.yml"
        if not cfg_path.exists():
            pytest.skip("metrics.yml not found")
        cfg = load_metrics_config(config_path=cfg_path)
        # Config must cover every verdict in the canonical taxonomy
        assert len(cfg.verdict_to_status) == len(VERDICTS), (
            f"metrics.yml has {len(cfg.verdict_to_status)} verdicts mapped but "
            f"models.py defines {len(VERDICTS)}. Add missing verdicts to metrics.yml."
        )
        # No verdict maps to success that shouldn't
        for v, s in cfg.verdict_to_status.items():
            if "BLOCKED" in v:
                assert s == "failure", f"{v} should map to failure"

    def test_no_aspose_com_in_config_website(self):
        from plugin_examples.metrics.config import load_metrics_config

        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / "pipeline" / "configs" / "metrics.yml"
        if not cfg_path.exists():
            pytest.skip("metrics.yml not found")
        cfg = load_metrics_config(config_path=cfg_path)
        assert "aspose.com" not in cfg.website

    def test_metrics_yml_api_endpoint_is_empty(self):
        """metrics.yml must not contain a hardcoded endpoint URL."""
        from plugin_examples.metrics.config import load_metrics_config

        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / "pipeline" / "configs" / "metrics.yml"
        if not cfg_path.exists():
            pytest.skip("metrics.yml not found")
        import yaml

        raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        assert (
            raw["metrics"]["api_endpoint"] == ""
        ), "api_endpoint must be empty in metrics.yml — set AGENT_METRICS_ENDPOINT env var instead"


class TestAgentMetricsEndpointEnvVar:
    def test_agent_metrics_endpoint_overrides_empty_config(self, _metrics_yml, monkeypatch):
        """AGENT_METRICS_ENDPOINT env var populates api_endpoint when config is empty."""
        import yaml

        from plugin_examples.metrics.config import load_metrics_config

        data = yaml.safe_load(_metrics_yml.read_text(encoding="utf-8"))
        data["metrics"]["api_endpoint"] = ""
        _metrics_yml.write_text(yaml.dump(data), encoding="utf-8")

        monkeypatch.setenv("AGENT_METRICS_ENDPOINT", "https://script.google.com/macros/s/FAKE/exec")
        cfg = load_metrics_config(config_path=_metrics_yml)
        assert cfg.api_endpoint == "https://script.google.com/macros/s/FAKE/exec"

    def test_agent_metrics_endpoint_absent_leaves_empty(self, _metrics_yml, monkeypatch):
        """Without AGENT_METRICS_ENDPOINT, api_endpoint stays empty when config is empty."""
        import yaml

        from plugin_examples.metrics.config import load_metrics_config

        data = yaml.safe_load(_metrics_yml.read_text(encoding="utf-8"))
        data["metrics"]["api_endpoint"] = ""
        _metrics_yml.write_text(yaml.dump(data), encoding="utf-8")

        monkeypatch.delenv("AGENT_METRICS_ENDPOINT", raising=False)
        cfg = load_metrics_config(config_path=_metrics_yml)
        assert cfg.api_endpoint == ""

    def test_agent_metrics_endpoint_does_not_override_non_empty_config(self, _metrics_yml, monkeypatch):
        """AGENT_METRICS_ENDPOINT takes precedence over a non-empty config value."""
        from plugin_examples.metrics.config import load_metrics_config

        monkeypatch.setenv("AGENT_METRICS_ENDPOINT", "https://override.example.com/exec")
        cfg = load_metrics_config(config_path=_metrics_yml)
        assert cfg.api_endpoint == "https://override.example.com/exec"
