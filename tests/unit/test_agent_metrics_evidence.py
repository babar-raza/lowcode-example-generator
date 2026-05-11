"""Tests for metrics evidence writer."""

import json
from pathlib import Path

import pytest


class TestEvidenceWriter:
    def test_write_llm_calls_jsonl(self, tmp_path):
        from plugin_examples.metrics.models import MetricsCollector
        from plugin_examples.metrics.evidence import write_llm_calls_jsonl

        mc = MetricsCollector()
        mc.record_call(provider="test", total_tokens=10, token_usage_available=True)
        mc.record_call(provider="test", total_tokens=20, token_usage_available=False)

        path = write_llm_calls_jsonl(tmp_path, mc.calls)
        assert path.exists()
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2
        rec = json.loads(lines[0])
        assert rec["provider"] == "test"
        assert rec["total_tokens"] == 10

    def test_write_payload(self, tmp_path):
        from plugin_examples.metrics.evidence import write_payload

        payload = {"agent_name": "test", "website": "aspose.net"}
        path = write_payload(tmp_path, payload)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["website"] == "aspose.net"

    def test_write_validation_result(self, tmp_path):
        from plugin_examples.metrics.evidence import write_validation_result

        result = {"valid": True, "errors": [], "warnings": []}
        path = write_validation_result(tmp_path, result)
        assert path.exists()

    def test_write_post_result(self, tmp_path):
        from plugin_examples.metrics.evidence import write_post_result

        result = {"posted": False, "reason": "dry_run"}
        path = write_post_result(tmp_path, result)
        assert path.exists()

    def test_no_secrets_in_evidence(self, tmp_path, monkeypatch):
        """Evidence must never contain tokens or API keys."""
        from plugin_examples.metrics.evidence import write_payload, write_post_result

        fake_token = "sk-SUPERSECRET12345"
        monkeypatch.setenv("AGENT_METRICS_TOKEN", fake_token)

        payload = {"agent_name": "test", "website": "aspose.net", "run_id": "t-1"}
        write_payload(tmp_path, payload)
        write_post_result(tmp_path, {"posted": False, "reason": "dry_run"})

        for f in tmp_path.iterdir():
            content = f.read_text(encoding="utf-8")
            assert fake_token not in content, f"Secret found in {f.name}"

    def test_run_summary(self, tmp_path):
        from plugin_examples.metrics.evidence import write_run_summary

        summary = {"token_usage": 100, "api_calls_count": 3}
        path = write_run_summary(tmp_path, summary)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["token_usage"] == 100
