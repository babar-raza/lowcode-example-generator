"""Tests for payload builder and config-driven validator."""

from pathlib import Path

import pytest
import yaml


@pytest.fixture
def _config(tmp_path):
    from plugin_examples.metrics.config import load_metrics_config

    cfg_data = {
        "metrics": {
            "agent_owner": "Test Owner",
            "agent_name": "test-gen",
            "website": "aspose.net",
            "website_section": "Examples",
            "platform": ".NET",
            "family_to_product": {"cells": "Aspose.Cells", "words": "Aspose.Words"},
            "command_to_job_type": {"run": "Examples Generation"},
            "command_to_item_name": {"run": "Examples"},
            "verdict_to_status": {
                "PR_READY": "success",
                "BLOCKED_GENERATION": "failure",
                "PARTIAL_PR_READY": "partial_success",
            },
            "api_endpoint": "https://example.com",
        }
    }
    p = tmp_path / "m.yml"
    p.write_text(yaml.dump(cfg_data), encoding="utf-8")
    return load_metrics_config(config_path=p)


class TestPayloadBuilder:
    def test_website_from_config(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        payload = build_payload(
            _config, command="run", family="cells", run_id="test-001",
        )
        assert payload["website"] == "aspose.net"

    def test_custom_website_override(self, tmp_path):
        from plugin_examples.metrics.config import load_metrics_config
        from plugin_examples.metrics.payload_builder import build_payload

        cfg_data = {
            "metrics": {
                "agent_owner": "X", "agent_name": "x-gen",
                "website": "custom.example.org", "family_to_product": {"a": "A"},
                "command_to_job_type": {"run": "gen"}, "verdict_to_status": {},
                "api_endpoint": "https://x.com",
            }
        }
        p = tmp_path / "m.yml"
        p.write_text(yaml.dump(cfg_data), encoding="utf-8")
        cfg = load_metrics_config(config_path=p)
        payload = build_payload(cfg, command="run", family="a", run_id="t-1")
        assert payload["website"] == "custom.example.org"

    def test_no_aspose_com_hardcoding(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        payload = build_payload(_config, command="run", family="cells", run_id="t-1")
        # Check no field contains aspose.com
        for k, v in payload.items():
            if isinstance(v, str):
                assert "aspose.com" not in v, f"Field {k} contains aspose.com"

    def test_verdict_maps_correctly(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        p = build_payload(_config, command="run", family="cells", run_id="t", verdict="PR_READY")
        assert p["status"] == "success"
        p = build_payload(_config, command="run", family="cells", run_id="t", verdict="BLOCKED_GENERATION")
        assert p["status"] == "failure"
        p = build_payload(_config, command="run", family="cells", run_id="t", verdict="PARTIAL_PR_READY")
        assert p["status"] == "partial_success"

    def test_unknown_verdict_maps_to_failure(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        p = build_payload(_config, command="run", family="cells", run_id="t", verdict="TOTALLY_UNKNOWN")
        assert p["status"] == "failure"

    def test_missing_family_empty_product(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        p = build_payload(_config, command="run", family="nonexistent", run_id="t")
        assert p["product"] == ""

    def test_job_type_test_override(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        p = build_payload(_config, command="run", family="cells", run_id="t",
                          job_type_override="Test")
        assert p["job_type"] == "Test"

    def test_test_mode_markers(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload

        p = build_payload(_config, command="run", family="cells", run_id="myrun",
                          test_mode=True, job_type_override="Test")
        assert p["agent_name"].startswith("test-")
        assert p["run_id"].startswith("test-")
        assert "test" in p["item_name"].lower()

    def test_all_production_verdicts_mapped(self):
        """Verify all 18 verdicts are in production config."""
        from plugin_examples.metrics.config import load_metrics_config

        repo_root = Path(__file__).resolve().parents[2]
        cfg_path = repo_root / "pipeline" / "configs" / "metrics.yml"
        if not cfg_path.exists():
            pytest.skip("metrics.yml not found")
        cfg = load_metrics_config(config_path=cfg_path)

        from plugin_examples.gates.models import VERDICTS
        for v in VERDICTS:
            status, unknown = cfg.resolve_status(v)
            assert not unknown, f"Verdict {v} is not in verdict_to_status mapping"
            if "BLOCKED" in v:
                assert status == "failure", f"{v} should map to failure"


class TestPayloadValidator:
    def test_valid_payload(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload
        from plugin_examples.metrics.validator import validate_payload

        payload = build_payload(
            _config, command="run", family="cells", run_id="test-001",
            items_discovered=5, items_succeeded=3, items_failed=2,
            run_duration_ms=1000, token_usage=500, api_calls_count=2,
        )
        result = validate_payload(payload, _config)
        assert result["valid"], f"Errors: {result['errors']}"

    def test_missing_field_invalid(self, _config):
        from plugin_examples.metrics.validator import validate_payload

        payload = {"timestamp": "2026-01-01T00:00:00Z"}  # Missing everything
        result = validate_payload(payload, _config)
        assert not result["valid"]
        assert len(result["errors"]) > 5

    def test_negative_integer_invalid(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload
        from plugin_examples.metrics.validator import validate_payload

        payload = build_payload(_config, command="run", family="cells", run_id="t")
        payload["items_discovered"] = -1
        result = validate_payload(payload, _config)
        assert not result["valid"]

    def test_missing_product_invalid(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload
        from plugin_examples.metrics.validator import validate_payload

        payload = build_payload(_config, command="run", family="missing", run_id="t")
        result = validate_payload(payload, _config)
        assert not result["valid"]
        assert any("product" in e for e in result["errors"])

    def test_status_validated_against_config(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload
        from plugin_examples.metrics.validator import validate_payload

        payload = build_payload(_config, command="run", family="cells", run_id="t")
        payload["status"] = "bogus_status"
        result = validate_payload(payload, _config)
        assert not result["valid"]
        assert any("allowed_statuses" in e for e in result["errors"])

    def test_website_validated_against_config(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload
        from plugin_examples.metrics.validator import validate_payload

        payload = build_payload(_config, command="run", family="cells", run_id="t")
        payload["website"] = "aspose.com"  # wrong!
        result = validate_payload(payload, _config)
        # This produces a warning, not an error (payload from external source)
        assert len(result["warnings"]) > 0
        assert any("aspose.com" in w for w in result["warnings"])

    def test_missing_command_empty_job_type(self, _config):
        from plugin_examples.metrics.payload_builder import build_payload
        from plugin_examples.metrics.validator import validate_payload

        payload = build_payload(_config, command="unknown_cmd", family="cells", run_id="t")
        result = validate_payload(payload, _config)
        # job_type will be empty → invalid
        assert not result["valid"]
