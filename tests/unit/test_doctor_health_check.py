"""Unit tests for doctor health check — TC-DOCTOR-001."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from plugin_examples.health.doctor import (
    HealthCheck,
    check_python_version,
    check_required_packages,
    check_dotnet_sdk,
    check_github_token,
    check_llm_endpoint,
    check_family_configs,
    check_format_authority,
    run_all_checks,
    format_results_text,
    format_results_json,
)


class TestCheckPythonVersion:
    def test_passes_on_current_python(self):
        result = check_python_version()
        assert result.status == "PASS"
        assert result.required is True


class TestCheckRequiredPackages:
    def test_passes_when_all_present(self):
        result = check_required_packages()
        # jsonschema, jinja2 (as jinja2), yaml, requests should all be installed
        assert result.status == "PASS"

    @patch("importlib.import_module", side_effect=ImportError("not found"))
    def test_fails_when_missing(self, mock_import):
        result = check_required_packages()
        assert result.status == "FAIL"


class TestCheckDotnetSdk:
    @patch("subprocess.run")
    def test_passes_when_dotnet_available(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="9.0.200\n")
        result = check_dotnet_sdk()
        assert result.status == "PASS"
        assert "9.0.200" in result.detail

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_warns_when_missing(self, mock_run):
        result = check_dotnet_sdk()
        assert result.status == "WARN"
        assert result.required is False


class TestCheckGithubToken:
    def test_passes_when_set(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "ghp_test123"}):
            result = check_github_token()
        assert result.status == "PASS"

    def test_warns_when_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            env = os.environ.copy()
            env.pop("GITHUB_TOKEN", None)
            env.pop("GH_TOKEN", None)
            with patch.dict(os.environ, env, clear=True):
                result = check_github_token()
        assert result.status == "WARN"


class TestCheckLlmEndpoint:
    def test_passes_with_professionalize(self):
        with patch.dict(os.environ, {"GPT_OSS_ENDPOINT": "https://llm.professionalize.com/v1/"}):
            result = check_llm_endpoint()
        assert result.status == "PASS"

    def test_warns_when_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            env = os.environ.copy()
            env.pop("GPT_OSS_ENDPOINT", None)
            with patch.dict(os.environ, env, clear=True):
                result = check_llm_endpoint()
        assert result.status == "WARN"


class TestCheckFamilyConfigs:
    def test_passes_with_valid_configs(self, tmp_path):
        families_dir = tmp_path / "pipeline" / "configs" / "families"
        families_dir.mkdir(parents=True)
        (families_dir / "cells.yml").write_text("family: cells\nstatus: active\n", encoding="utf-8")
        result = check_family_configs(tmp_path)
        assert result.status == "PASS"
        assert "1 configs" in result.detail

    def test_fails_when_dir_missing(self, tmp_path):
        result = check_family_configs(tmp_path)
        assert result.status == "FAIL"


class TestCheckFormatAuthority:
    def test_passes_when_manifest_exists(self, tmp_path):
        manifest_dir = tmp_path / "pipeline" / "format-authority"
        manifest_dir.mkdir(parents=True)
        (manifest_dir / "manifest.json").write_text("{}", encoding="utf-8")
        result = check_format_authority(tmp_path)
        assert result.status == "PASS"

    def test_fails_when_missing(self, tmp_path):
        result = check_format_authority(tmp_path)
        assert result.status == "FAIL"


class TestRunAllChecks:
    def test_returns_list_of_health_checks(self, tmp_path):
        results = run_all_checks(tmp_path)
        assert isinstance(results, list)
        assert len(results) >= 5
        assert all(isinstance(r, HealthCheck) for r in results)


class TestFormatResults:
    def test_text_format(self):
        checks = [HealthCheck("test", "PASS", "ok", True)]
        text = format_results_text(checks)
        assert "test" in text
        assert "[OK]" in text

    def test_json_format(self):
        import json
        checks = [HealthCheck("test", "PASS", "ok", True)]
        output = format_results_json(checks)
        data = json.loads(output)
        assert data["summary"]["total"] == 1
        assert data["summary"]["passed"] == 1
