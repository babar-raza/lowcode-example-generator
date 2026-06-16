"""Tests for probe executor (TC-PSAL-24)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.probe_executor.executor import (
    _PROBEABLE_STATUSES,
    ProbeExecutor,
    ProbeOutcome,
    _load_registry_entries,
)
from plugin_examples.probe_generator.runner import ProbeResult

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_entry(family="drawing", slug="convert-drawing", status="REFLECTION_CANDIDATE", **kw):
    entry = {
        "family": family,
        "plugin_slug": slug,
        "type_name": "Bitmap",
        "namespace": "System.Drawing",
        "method_name": "Save",
        "package_id": "Aspose.Drawing",
        "last_reflected_package_version": "26.5.0",
        "selected_api_mapping": {},
        "status": status,
    }
    entry.update(kw)
    return entry


def _make_probe_result(*, success=True, taxonomy=None, build_ok=True, run_ok=True, output_size=100):
    return ProbeResult(
        restore_ok=True,
        build_ok=build_ok,
        run_ok=run_ok,
        output_validated=success,
        output_size_bytes=output_size,
        log_path=None,
        failure_taxonomy=taxonomy,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestProbeExecutor:
    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_dotnet_check_at_init(self, mock_run, tmp_path):
        mock_run.return_value = MagicMock(returncode=0, stdout="9.0.200", stderr="")
        executor = ProbeExecutor(repo_root=tmp_path, timeout=30)
        mock_run.assert_called_once()
        assert "dotnet" in mock_run.call_args[0][0]

    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_dotnet_missing_raises(self, mock_run, tmp_path):
        mock_run.side_effect = FileNotFoundError("dotnet not found")
        with pytest.raises(RuntimeError, match="dotnet SDK not found"):
            ProbeExecutor(repo_root=tmp_path)


class TestProbeEntry:
    @patch("plugin_examples.probe_executor.executor.ProbeRunner")
    @patch("plugin_examples.probe_executor.executor.generate_probe_from_registry")
    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_confirmed_on_success(self, mock_subprocess, mock_gen, mock_runner_cls, tmp_path):
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="9.0.200", stderr="")

        mock_gen.return_value = MagicMock(
            cs_path=tmp_path / "Program.cs",
            csproj_path=tmp_path / "Probe.csproj",
        )
        mock_runner = MagicMock()
        mock_runner.run.return_value = _make_probe_result(success=True)
        mock_runner_cls.return_value = mock_runner

        executor = ProbeExecutor(repo_root=tmp_path, timeout=30)
        entry = _make_entry()
        outcome = executor.probe_entry("drawing", entry)

        assert outcome.new_status == "PROBE_CONFIRMED"
        assert outcome.family == "drawing"
        assert outcome.plugin_slug == "convert-drawing"

    @patch("plugin_examples.probe_executor.executor.ProbeRunner")
    @patch("plugin_examples.probe_executor.executor.generate_probe_from_registry")
    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_failed_build(self, mock_subprocess, mock_gen, mock_runner_cls, tmp_path):
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="9.0.200", stderr="")

        mock_gen.return_value = MagicMock(
            cs_path=tmp_path / "Program.cs",
            csproj_path=tmp_path / "Probe.csproj",
        )
        mock_runner = MagicMock()
        mock_runner.run.return_value = _make_probe_result(
            success=False, taxonomy="PROBE_FAILED_BUILD", build_ok=False
        )
        mock_runner_cls.return_value = mock_runner

        executor = ProbeExecutor(repo_root=tmp_path, timeout=30)
        outcome = executor.probe_entry("drawing", _make_entry())

        assert outcome.new_status == "PROBE_FAILED_BUILD"

    @patch("plugin_examples.probe_executor.executor.ProbeRunner")
    @patch("plugin_examples.probe_executor.executor.generate_probe_from_registry")
    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_failed_license(self, mock_subprocess, mock_gen, mock_runner_cls, tmp_path):
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="9.0.200", stderr="")

        mock_gen.return_value = MagicMock(
            cs_path=tmp_path / "Program.cs",
            csproj_path=tmp_path / "Probe.csproj",
        )
        mock_runner = MagicMock()
        mock_runner.run.return_value = _make_probe_result(
            success=False, taxonomy="PROBE_FAILED_LICENSE", output_size=0
        )
        mock_runner_cls.return_value = mock_runner

        executor = ProbeExecutor(repo_root=tmp_path, timeout=30)
        outcome = executor.probe_entry("threed", _make_entry(family="threed", slug="convert-3d"))

        assert outcome.new_status == "PROBE_FAILED_LICENSE"

    @patch("plugin_examples.probe_executor.executor.generate_probe_from_registry")
    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_codegen_crash_handled(self, mock_subprocess, mock_gen, tmp_path):
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="9.0.200", stderr="")
        mock_gen.side_effect = ValueError("template render failed")

        executor = ProbeExecutor(repo_root=tmp_path, timeout=30)
        outcome = executor.probe_entry("drawing", _make_entry())

        assert outcome.new_status == "PROBE_FAILED_BUILD"
        assert "Code generation failed" in outcome.error


class TestProbeFamily:
    @patch("plugin_examples.probe_executor.executor.ProbeRunner")
    @patch("plugin_examples.probe_executor.executor.generate_probe_from_registry")
    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_filters_by_status(self, mock_subprocess, mock_gen, mock_runner_cls, tmp_path):
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="9.0.200", stderr="")
        mock_gen.return_value = MagicMock(cs_path=tmp_path / "P.cs", csproj_path=tmp_path / "P.csproj")
        mock_runner = MagicMock()
        mock_runner.run.return_value = _make_probe_result(success=True)
        mock_runner_cls.return_value = mock_runner

        # Write a registry with mixed statuses
        registry_path = tmp_path / "pipeline" / "plugin-capability-registry" / "drawing.yaml"
        registry_path.parent.mkdir(parents=True)
        import yaml
        registry_path.write_text(yaml.dump({"entries": [
            _make_entry(slug="eligible", status="REFLECTION_CANDIDATE"),
            _make_entry(slug="confirmed", status="PROBE_CONFIRMED"),  # should be skipped
            _make_entry(slug="also-eligible", status="WEBSITE_DISCOVERED"),
        ]}), encoding="utf-8")

        executor = ProbeExecutor(repo_root=tmp_path, timeout=30)
        outcomes = executor.probe_family("drawing", registry_path)

        # Only 2 eligible entries should be probed
        assert len(outcomes) == 2
        slugs = {o.plugin_slug for o in outcomes}
        assert "eligible" in slugs
        assert "also-eligible" in slugs
        assert "confirmed" not in slugs

    @patch("plugin_examples.probe_executor.executor.subprocess.run")
    def test_no_registry_returns_empty(self, mock_subprocess, tmp_path):
        mock_subprocess.return_value = MagicMock(returncode=0, stdout="9.0.200", stderr="")
        executor = ProbeExecutor(repo_root=tmp_path, timeout=30)
        outcomes = executor.probe_family("nonexistent")
        assert outcomes == []


class TestProbeableStatuses:
    def test_includes_expected(self):
        assert "REFLECTION_CANDIDATE" in _PROBEABLE_STATUSES
        assert "WEBSITE_DISCOVERED" in _PROBEABLE_STATUSES
        assert "PROBE_CANDIDATE" in _PROBEABLE_STATUSES

    def test_excludes_confirmed(self):
        assert "PROBE_CONFIRMED" not in _PROBEABLE_STATUSES
        assert "PROBE_FAILED" not in _PROBEABLE_STATUSES
