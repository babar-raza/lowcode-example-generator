"""Tests for the version drift checker module (Sprint 36 SYS-1)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.publisher.version_drift_checker import (
    FamilyDriftResult,
    VersionDriftReport,
    _compare_versions,
    _drift_severity,
    run_version_drift_check,
    LOWCODE_FAMILIES,
)


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------


class TestCompareVersions:
    def test_equal_versions(self):
        assert _compare_versions("26.5.0", "26.5.0") == 0

    def test_older_major(self):
        assert _compare_versions("25.0.0", "26.0.0") == -1

    def test_newer_minor(self):
        assert _compare_versions("26.6.0", "26.5.0") == 1

    def test_patch_increment(self):
        assert _compare_versions("26.4.0", "26.4.1") == -1

    def test_multi_digit(self):
        assert _compare_versions("26.10.0", "26.9.0") == 1

    def test_two_part_version(self):
        assert _compare_versions("5.9", "5.10") == -1


class TestDriftSeverity:
    def test_no_drift(self):
        assert _drift_severity("26.5.0", "26.5.0") == "NONE"

    def test_patch_drift(self):
        assert _drift_severity("26.4.0", "26.4.1") == "PATCH"

    def test_month_bump_is_major(self):
        # Aspose calendar versioning: Year.Month.Patch — month change = full monthly release = MAJOR
        assert _drift_severity("26.4.0", "26.5.0") == "MAJOR"

    def test_year_bump_is_major(self):
        assert _drift_severity("25.0.0", "26.0.0") == "MAJOR"

    def test_cells_drift(self):
        # Cells 26.4.0 -> 26.5.1: month component changed -> MAJOR (Aspose monthly release)
        result = _drift_severity("26.4.0", "26.5.1")
        assert result == "MAJOR"

    def test_invalid_input_returns_unknown(self):
        assert _drift_severity("abc", "xyz") == "UNKNOWN"


# ---------------------------------------------------------------------------
# Tests for run_version_drift_check with mocked NuGet
# ---------------------------------------------------------------------------


def _make_nuget_response(versions: list[str]) -> MagicMock:
    """Create a mock urllib response with a versions list."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"versions": versions}).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def _write_denominator(tmp_path: Path, family: str, version: str) -> None:
    denom_dir = tmp_path / "pipeline" / "configs" / "denominators"
    denom_dir.mkdir(parents=True, exist_ok=True)
    (denom_dir / f"{family}.json").write_text(
        json.dumps({"family": family, "source_version": version}), encoding="utf-8"
    )


class TestRunVersionDriftCheck:
    def test_all_current(self, tmp_path):
        _write_denominator(tmp_path, "cells", "26.5.0")
        _write_denominator(tmp_path, "words", "26.5.0")

        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value = _make_nuget_response(["26.4.0", "26.5.0"])
            report = run_version_drift_check(families=["cells", "words"], repo_root=tmp_path)

        assert report.overall_verdict == "ALL_CURRENT"
        assert report.drifted_count == 0
        assert report.current_count == 2

    def test_drift_detected_cells(self, tmp_path):
        _write_denominator(tmp_path, "cells", "26.4.0")

        def side_effect(url, timeout=15):
            return _make_nuget_response(["26.4.0", "26.5.0", "26.5.1"])

        with patch("urllib.request.urlopen", side_effect=side_effect):
            report = run_version_drift_check(families=["cells"], repo_root=tmp_path)

        assert report.overall_verdict == "DRIFT_DETECTED"
        assert report.drifted_count == 1
        assert report.families[0].latest_nuget_version == "26.5.1"
        assert report.families[0].drift is True
        assert report.families[0].drift_severity == "MAJOR"

    def test_not_on_nuget_returns_error(self, tmp_path):
        _write_denominator(tmp_path, "cells", "26.4.0")

        import urllib.error
        with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(None, 404, "Not Found", {}, None)):
            report = run_version_drift_check(families=["cells"], repo_root=tmp_path)

        assert report.error_count == 1
        assert report.families[0].on_nuget is False
        assert report.families[0].status == "ERROR"

    def test_missing_denominator(self, tmp_path):
        # No denominator file for 'cells'
        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value = _make_nuget_response(["26.5.0"])
            report = run_version_drift_check(families=["cells"], repo_root=tmp_path)

        assert report.error_count == 1
        assert report.families[0].status == "NO_DENOMINATOR"

    def test_unknown_family_skipped(self, tmp_path):
        report = run_version_drift_check(families=["nonexistent_family"], repo_root=tmp_path)
        assert len(report.families) == 0

    def test_to_dict_structure(self, tmp_path):
        _write_denominator(tmp_path, "pdf", "26.5.0")

        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value = _make_nuget_response(["26.5.0"])
            report = run_version_drift_check(families=["pdf"], repo_root=tmp_path)

        d = report.to_dict()
        assert "generated_at" in d
        assert "families" in d
        assert d["families"][0]["family"] == "pdf"
        assert d["families"][0]["status"] == "CURRENT"
        assert d["overall_verdict"] == "ALL_CURRENT"

    def test_drift_severity_cells_26_4_to_26_5_1(self, tmp_path):
        """Cells drifted from 26.4.0 -> 26.5.1: month component changed -> MAJOR."""
        _write_denominator(tmp_path, "cells", "26.4.0")

        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value = _make_nuget_response(["26.4.0", "26.5.0", "26.5.1"])
            report = run_version_drift_check(families=["cells"], repo_root=tmp_path)

        r = report.families[0]
        assert r.denominator_version == "26.4.0"
        assert r.latest_nuget_version == "26.5.1"
        assert r.drift is True
        assert r.drift_severity == "MAJOR"

    def test_drift_severity_diagram_26_4_to_26_5(self, tmp_path):
        """Diagram drifted from 26.4.0 -> 26.5.0: month component changed -> MAJOR."""
        _write_denominator(tmp_path, "diagram", "26.4.0")

        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value = _make_nuget_response(["26.4.0", "26.5.0"])
            report = run_version_drift_check(families=["diagram"], repo_root=tmp_path)

        r = report.families[0]
        assert r.drift is True
        assert r.drift_severity == "MAJOR"

    def test_slides_uses_correct_package_id(self):
        """Slides must use 'Aspose.Slides.NET' not 'Aspose.Slides'."""
        assert LOWCODE_FAMILIES["slides"] == "Aspose.Slides.NET"

    def test_all_six_lowcode_families_present(self):
        expected = {"cells", "words", "pdf", "diagram", "email", "slides"}
        assert expected == set(LOWCODE_FAMILIES.keys())
