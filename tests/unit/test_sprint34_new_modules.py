"""Tests for Sprint 34 new modules.

Covers:
- FormImporter version-watch (formimporter_watch.py)
- Batch publication orchestrator (batch_publisher.py)
- Post-publication verifier (post_publication_verifier.py)
- Portfolio release dashboard (portfolio_dashboard.py)
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# FormImporter version-watch tests
# ---------------------------------------------------------------------------

class TestFormImporterVersionCompare:
    def test_compare_versions_advanced(self):
        from plugin_examples.package_watcher.formimporter_watch import _compare_versions
        assert _compare_versions("26.6.0", "26.5.0") == 1

    def test_compare_versions_same(self):
        from plugin_examples.package_watcher.formimporter_watch import _compare_versions
        assert _compare_versions("26.5.0", "26.5.0") == 0

    def test_compare_versions_older(self):
        from plugin_examples.package_watcher.formimporter_watch import _compare_versions
        assert _compare_versions("26.4.0", "26.5.0") == -1

    def test_compare_versions_major_change(self):
        from plugin_examples.package_watcher.formimporter_watch import _compare_versions
        assert _compare_versions("27.0.0", "26.5.0") == 1


class TestFormImporterWatch:
    def test_check_formimporter_no_network_graceful(self):
        """Watch completes without network — uses graceful degradation."""
        from plugin_examples.package_watcher.formimporter_watch import check_formimporter

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            # No network mock — should degrade gracefully
            with patch(
                "plugin_examples.package_watcher.formimporter_watch._get_latest_nuget_version",
                return_value=None,
            ):
                result = check_formimporter(repo_root, run_repro=False)

        assert result.defect_version == "26.5.0"
        assert result.retest_triggered is False
        assert result.verdict in ("STILL_BLOCKED", "CHECK_ONLY")

    def test_check_formimporter_version_not_advanced(self):
        from plugin_examples.package_watcher.formimporter_watch import check_formimporter

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            with patch(
                "plugin_examples.package_watcher.formimporter_watch._get_latest_nuget_version",
                return_value="26.5.0",  # same as defect version
            ):
                result = check_formimporter(repo_root, run_repro=False)

        assert result.version_advanced is False
        assert result.verdict == "STILL_BLOCKED"

    def test_check_formimporter_version_advanced_no_repro(self):
        from plugin_examples.package_watcher.formimporter_watch import check_formimporter

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            with patch(
                "plugin_examples.package_watcher.formimporter_watch._get_latest_nuget_version",
                return_value="26.6.0",  # beyond defect version
            ):
                result = check_formimporter(repo_root, run_repro=False)

        assert result.version_advanced is True
        assert result.retest_triggered is False
        assert result.verdict == "CHECK_ONLY"

    def test_write_watch_report(self):
        from plugin_examples.package_watcher.formimporter_watch import (
            FormImporterWatchResult, write_watch_report,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            result = FormImporterWatchResult(
                checked_at="2026-05-18T00:00:00+00:00",
                current_version="26.5.0",
                latest_nuget_version="26.5.0",
                defect_version="26.5.0",
                version_advanced=False,
                retest_triggered=False,
                retest_passed=None,
                retest_output=None,
                retest_exit_code=None,
                verdict="STILL_BLOCKED",
                notes=["test note"],
            )
            path = write_watch_report(result, Path(tmpdir) / "report.json")
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["verdict"] == "STILL_BLOCKED"
            assert data["defect_version"] == "26.5.0"
            assert "taskcard" in data


# ---------------------------------------------------------------------------
# Post-publication verifier tests
# ---------------------------------------------------------------------------

class TestPostPublicationVerifier:
    def _make_example_dir(self, base: Path, example_name: str, family: str = "pdf") -> Path:
        """Create a minimal example directory structure."""
        # Packages use examples/{family}/lowcode/{name}/Program.cs
        example_dir = base / "examples" / family / "lowcode" / example_name
        example_dir.mkdir(parents=True)

        lowcode_ns = f"Aspose.{family.capitalize()}.LowCode"
        (example_dir / "Program.cs").write_text(
            f"using {lowcode_ns};\n\nvar opts = new ConvertOptions();\n// Demo\n",
            encoding="utf-8",
        )
        csproj = example_dir / f"{example_name}.csproj"
        csproj.write_text("<Project Sdk=\"Microsoft.NET.Sdk\"></Project>", encoding="utf-8")
        (example_dir / "README.md").write_text(f"# {example_name}\n", encoding="utf-8")
        return example_dir

    def test_verify_package_all_verified(self):
        from plugin_examples.publisher.post_publication_verifier import verify_local_package

        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_path = Path(tmpdir)
            self._make_example_dir(pkg_path, "doc-converter", "pdf")
            self._make_example_dir(pkg_path, "html", "pdf")

            result = verify_local_package("pdf", 3, "pdf-controlled-pilot", pkg_path)

        assert result.total_examples == 2
        assert result.verified_examples == 2
        assert result.verdict == "ALL_VERIFIED"

    def test_verify_package_missing_path(self):
        from plugin_examples.publisher.post_publication_verifier import verify_local_package

        result = verify_local_package("pdf", 3, "missing-pkg", Path("/nonexistent/path"))
        assert result.verdict == "PACKAGE_PATH_MISSING"

    def test_verify_package_no_lowcode_api(self):
        from plugin_examples.publisher.post_publication_verifier import verify_local_package

        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_path = Path(tmpdir)
            ex_dir = pkg_path / "examples" / "pdf" / "lowcode" / "bad-example"
            ex_dir.mkdir(parents=True)
            (ex_dir / "Program.cs").write_text(
                "using System;\nvar x = 1;\n",  # No LowCode API
                encoding="utf-8",
            )
            (ex_dir / "bad-example.csproj").write_text("<Project/>", encoding="utf-8")

            result = verify_local_package("pdf", 3, "bad-pkg", pkg_path)

        assert result.total_examples == 1
        assert result.verified_examples == 0
        assert result.failed_examples == 1

    def test_run_post_publication_verification(self):
        from plugin_examples.publisher.post_publication_verifier import (
            run_post_publication_verification,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            pkg1 = base / "pdf-controlled-pilot"
            pkg1.mkdir()
            self._make_example_dir(pkg1, "doc-converter", "pdf")

            result = run_post_publication_verification(
                "pdf",
                [(3, "pdf-controlled-pilot")],
                base,
            )

        assert result.total_packages == 1
        assert result.all_verified is True
        assert result.verdict == "ALL_PACKAGES_VERIFIED"

    def test_write_verification_report(self):
        from plugin_examples.publisher.post_publication_verifier import (
            PostPublicationReport, write_verification_report,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            report = PostPublicationReport(
                verified_at="2026-05-18T00:00:00+00:00",
                family="pdf",
                mode="dry_run_local",
                total_packages=1,
                all_verified=True,
                verdict="ALL_PACKAGES_VERIFIED",
            )
            path = write_verification_report(report, Path(tmpdir) / "report.json")
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["verdict"] == "ALL_PACKAGES_VERIFIED"
            assert data["all_verified"] is True


# ---------------------------------------------------------------------------
# Portfolio dashboard tests
# ---------------------------------------------------------------------------

class TestPortfolioDashboard:
    def test_build_dashboard_smoke(self):
        from plugin_examples.publisher.portfolio_dashboard import build_portfolio_dashboard

        dashboard = build_portfolio_dashboard("sprint34")
        assert dashboard.sprint == "sprint34"
        assert dashboard.total_published == 28
        assert dashboard.total_pr_ready == 14
        assert dashboard.total_families == 6
        assert dashboard.families_complete_or_pilot_complete == 5
        assert dashboard.families_partial == 1  # pdf

    def test_dashboard_approval_gate_blocked(self):
        from plugin_examples.publisher.portfolio_dashboard import build_portfolio_dashboard

        with patch.dict(os.environ, {"PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL": ""}):
            dashboard = build_portfolio_dashboard("sprint34")

        assert dashboard.approval_gate_status == "NOT_SET"
        assert "APPROVAL_BLOCKED" in dashboard.verdict

    def test_dashboard_approval_gate_ready(self):
        from plugin_examples.publisher.portfolio_dashboard import build_portfolio_dashboard

        with patch.dict(os.environ, {"PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL": "APPROVE_LIVE_PR"}):
            dashboard = build_portfolio_dashboard("sprint34")

        assert dashboard.approval_gate_status == "READY"
        assert "READY" in dashboard.verdict

    def test_write_dashboard_json(self):
        from plugin_examples.publisher.portfolio_dashboard import (
            build_portfolio_dashboard, write_dashboard_json,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard = build_portfolio_dashboard("sprint34")
            path = write_dashboard_json(dashboard, Path(tmpdir) / "dashboard.json")
            assert path.exists()
            data = json.loads(path.read_text())
        assert "families" in data
        assert len(data["families"]) == 6
        assert data["summary"]["total_published"] == 28

    def test_write_dashboard_markdown(self):
        from plugin_examples.publisher.portfolio_dashboard import (
            build_portfolio_dashboard, write_dashboard_markdown,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard = build_portfolio_dashboard("sprint34")
            path = write_dashboard_markdown(dashboard, Path(tmpdir) / "dashboard.md")
            assert path.exists()
            content = path.read_text(encoding="utf-8")
        assert "# Portfolio Release Dashboard" in content
        assert "PORTFOLIO_RELEASE_CANDIDATE" in content
        assert "| Cells" in content or "| cells" in content.lower()

    def test_dashboard_all_families_present(self):
        from plugin_examples.publisher.portfolio_dashboard import (
            build_portfolio_dashboard, FAMILIES,
        )

        dashboard = build_portfolio_dashboard("sprint34")
        entry_families = {e.family for e in dashboard.entries}
        assert entry_families == set(FAMILIES)

    def test_dashboard_coverage_pct_cells(self):
        from plugin_examples.publisher.portfolio_dashboard import build_portfolio_dashboard

        dashboard = build_portfolio_dashboard("sprint34")
        cells_entry = next(e for e in dashboard.entries if e.family == "cells")
        assert cells_entry.coverage_pct == 100.0

    def test_dashboard_system_health_all_complete(self):
        from plugin_examples.publisher.portfolio_dashboard import build_portfolio_dashboard

        dashboard = build_portfolio_dashboard("sprint34")
        tc_sys = {k: v for k, v in dashboard.system_health.items() if k.startswith("TC-SYS")}
        assert all(v == "COMPLETE" for v in tc_sys.values())
        assert len(tc_sys) == 5  # TC-SYS-01 through TC-SYS-05


# ---------------------------------------------------------------------------
# Batch publisher tests
# ---------------------------------------------------------------------------

class TestBatchPublisher:
    def test_get_packages_for_pdf(self):
        from plugin_examples.publisher.batch_publisher import _get_packages_for_family, PDF_PR_PACKAGES

        result = _get_packages_for_family("pdf")
        assert result == PDF_PR_PACKAGES
        assert len(result) == 6

    def test_get_packages_unknown_family(self):
        from plugin_examples.publisher.batch_publisher import _get_packages_for_family

        result = _get_packages_for_family("unknown")
        assert result == []

    def test_batch_result_verdict_all_passed(self):
        from plugin_examples.publisher.batch_publisher import BatchPublishResult, PackagePublishResult

        results = [
            PackagePublishResult(3, "pkg3", 0, "ok", "", True),
            PackagePublishResult(5, "pkg5", 0, "ok", "", True),
        ]
        batch = BatchPublishResult(
            started_at="2026-05-18T00:00:00+00:00",
            finished_at="2026-05-18T00:01:00+00:00",
            family="pdf",
            live_mode=False,
            approval_gate_set=False,
            results=results,
            total=2,
            succeeded=2,
            failed=0,
            blocked=0,
        )
        assert batch.all_passed is True
        assert "PASSED" in batch.verdict or "DRY_RUN" in batch.verdict

    def test_batch_result_verdict_approval_blocked(self):
        from plugin_examples.publisher.batch_publisher import BatchPublishResult

        batch = BatchPublishResult(
            started_at="2026-05-18T00:00:00+00:00",
            finished_at="2026-05-18T00:01:00+00:00",
            family="pdf",
            live_mode=False,
            approval_gate_set=False,
            results=[],
            total=0,
            succeeded=0,
            failed=0,
            blocked=0,
        )
        assert "APPROVAL_BLOCKED" in batch.verdict

    def test_write_batch_report(self):
        from plugin_examples.publisher.batch_publisher import (
            BatchPublishResult, PackagePublishResult, write_batch_report,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            results = [PackagePublishResult(3, "pdf-pkg", 0, "sim ok", "", True)]
            batch = BatchPublishResult(
                started_at="2026-05-18T00:00:00+00:00",
                finished_at="2026-05-18T00:01:00+00:00",
                family="pdf",
                live_mode=False,
                approval_gate_set=False,
                results=results,
                total=1,
                succeeded=1,
                failed=0,
                blocked=0,
            )
            path = write_batch_report(batch, Path(tmpdir) / "batch.json")
            data = json.loads(path.read_text())
            assert data["total"] == 1
            assert data["succeeded"] == 1
            assert len(data["packages"]) == 1
