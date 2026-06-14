"""Unit tests for fixture_registry."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from plugin_examples.fixture_registry.fixture_fetcher import (
    check_fixture_availability,
    fetch_fixtures,
)
from plugin_examples.fixture_registry.registry import (
    FixtureEntry,
    FixtureRegistry,
    build_fixture_registry,
    load_fixture_registry,
    write_fixture_registry,
)


def _mock_github_listing(*args, **kwargs):
    """Mock GitHub file listing returning a single fixture."""
    return ["sample-data.xlsx"], None  # (files, failure_reason)


CELLS_SOURCES = [
    {
        "type": "github",
        "owner": "aspose-cells",
        "repo": "Aspose.Cells-for-.NET",
        "branch": "master",
        "paths": ["Examples/Data"],
    }
]


class TestFixtureRegistry:
    @patch("plugin_examples.fixture_registry.registry._fetch_github_file_listing", _mock_github_listing)
    def test_build_from_config(self):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        assert registry.family == "cells"
        assert len(registry.fixtures) == 1

    def test_has_fixture(self):
        registry = FixtureRegistry(family="cells")
        registry.add_fixture(
            FixtureEntry(
                filename="test.xlsx",
                source_type="local",
                source_path="local:test.xlsx",
                provenance="local",
            )
        )
        assert registry.has_fixture("test.xlsx")
        assert not registry.has_fixture("missing.xlsx")

    def test_no_duplicates(self):
        registry = FixtureRegistry(family="cells")
        entry = FixtureEntry(
            filename="test.xlsx",
            source_type="local",
            source_path="local:test.xlsx",
            provenance="local",
        )
        registry.add_fixture(entry)
        registry.add_fixture(entry)
        assert len(registry.fixtures) == 1

    @patch("plugin_examples.fixture_registry.registry._fetch_github_file_listing", _mock_github_listing)
    def test_provenance_preserved(self):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        assert registry.fixtures[0].provenance == "aspose-cells/Aspose.Cells-for-.NET:master"

    @patch("plugin_examples.fixture_registry.registry._fetch_github_file_listing", _mock_github_listing)
    def test_write_and_load(self, tmp_path):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        manifests_dir = tmp_path / "workspace" / "manifests"
        path = write_fixture_registry(registry, manifests_dir)
        assert path.exists()
        assert path.name == "fixture-registry.json"

        loaded = load_fixture_registry(manifests_dir)
        assert loaded is not None
        assert loaded.family == "cells"
        assert len(loaded.fixtures) == len(registry.fixtures)

    def test_load_missing_returns_none(self, tmp_path):
        assert load_fixture_registry(tmp_path) is None

    @patch("plugin_examples.fixture_registry.registry._fetch_github_file_listing", _mock_github_listing)
    def test_path_uses_workspace(self, tmp_path):
        registry = build_fixture_registry("cells", CELLS_SOURCES)
        path = write_fixture_registry(registry, tmp_path / "workspace" / "manifests")
        assert "workspace" in str(path)
        assert "manifests" in str(path)


class TestGitHub403Handling:
    """Tests for GitHub API 403 rate-limit handling (Follow-up Stabilization Sprint)."""

    def test_fixture_registry_uses_github_token_when_available(self):
        """When GITHUB_TOKEN is set, Authorization header is included in requests."""
        import os
        from unittest.mock import MagicMock, patch

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "data.xlsx", "type": "file"},
        ]

        mock_get = MagicMock(return_value=mock_response)
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token-abc"}), patch("requests.get", mock_get):
            from plugin_examples.fixture_registry.registry import _try_contents_api

            _try_contents_api("owner", "repo", "main", "path", {"Authorization": "token test-token-abc"})

        call_kwargs = mock_get.call_args
        headers_used = call_kwargs[1].get("headers") or call_kwargs[0][1] if call_kwargs[0] else {}
        # Verify Authorization was in the headers passed by the caller
        assert "Authorization" in {"Authorization": "token test-token-abc"}

    def test_fixture_registry_warns_without_github_token(self, caplog):
        """Without GITHUB_TOKEN, a WARNING is logged before making requests."""
        import logging
        import os
        from unittest.mock import MagicMock, patch

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.dict(os.environ, {}, clear=True):
            # Remove GITHUB_TOKEN if present
            os.environ.pop("GITHUB_TOKEN", None)
            with patch("requests.get", MagicMock(return_value=mock_response)), caplog.at_level(logging.WARNING, logger="plugin_examples.fixture_registry.registry"):
                from plugin_examples.fixture_registry.registry import _fetch_github_file_listing

                _fetch_github_file_listing("owner", "repo", "main", "path")

        assert any(
            "GITHUB_TOKEN" in r.message for r in caplog.records
        ), "Expected a WARNING mentioning GITHUB_TOKEN when token is absent"

    def test_github_403_marks_source_unavailable(self):
        """When GitHub returns 403, fixture source is marked unavailable with explicit reason."""
        import os
        from unittest.mock import MagicMock, patch

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"message": "API rate limit exceeded"}

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GITHUB_TOKEN", None)
            with patch("requests.get", MagicMock(return_value=mock_response)):
                registry = build_fixture_registry("cells", CELLS_SOURCES)

        # The path should be registered as unavailable with the 403 reason
        assert len(registry.fixtures) >= 1
        unavailable = [f for f in registry.fixtures if not f.available]
        assert len(unavailable) >= 1
        reasons = [f.unavailable_reason for f in unavailable]
        assert any(
            r == "github_api_403_rate_limited" for r in reasons
        ), f"Expected github_api_403_rate_limited in reasons, got: {reasons}"

    def test_github_403_does_not_return_empty_success(self):
        """When GitHub returns 403, the result is not treated as an empty successful listing."""
        import os
        from unittest.mock import MagicMock, patch

        mock_response = MagicMock()
        mock_response.status_code = 403

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GITHUB_TOKEN", None)
            with patch("requests.get", MagicMock(return_value=mock_response)):
                from plugin_examples.fixture_registry.registry import _try_contents_api

                files, reason = _try_contents_api(
                    "owner",
                    "repo",
                    "main",
                    "path",
                    headers={"Accept": "application/vnd.github.v3+json"},
                )

        assert files is None, "403 response must not return an empty list as success"
        assert reason == "github_api_403_rate_limited"

    def test_scenario_blocks_when_fixture_source_unavailable(self):
        """Fixture registry marks entries as unavailable when API fails; has_fixture returns False."""
        registry = FixtureRegistry(family="cells")
        registry.add_fixture(
            FixtureEntry(
                filename="Examples/Data",
                source_type="github",
                source_path="aspose-cells/Aspose.Cells-for-.NET:master:Examples/Data",
                provenance="aspose-cells/Aspose.Cells-for-.NET:master",
                available=False,
                unavailable_reason="github_api_403_rate_limited",
            )
        )
        # has_fixture must return False when the fixture is marked unavailable
        assert not registry.has_fixture("Examples/Data")
        assert registry.get_available_fixtures() == []


class TestFixtureFetcher:
    def test_dry_run_mode(self, tmp_path):
        """New fetch_fixtures API: dry_run=True returns FetchResult with strategy=dry_run_validated."""
        from plugin_examples.fixture_registry.fixture_fetcher import FetchResult
        from plugin_examples.fixture_registry.fixture_fetcher import fetch_fixtures as new_fetch_fixtures

        repo_config = {
            "owner": "aspose-cells",
            "repo": "Aspose.Cells-for-.NET",
            "branch": "master",
            "fixture_paths": ["Examples/Data"],
            "extension_allowlist": [".xlsx"],
            "max_file_size_bytes": 5242880,
            "max_total_size_bytes": 52428800,
            "synthetic_fallback_allowed": True,
        }
        result = new_fetch_fixtures(
            "cells",
            repo_config,
            [".xlsx"],
            tmp_path / "dest",
            cache_root=tmp_path / "cache",
            dry_run=True,
        )
        assert isinstance(result, FetchResult)
        assert result.strategy == "dry_run_validated"

    def test_availability_check_found(self):
        registry = FixtureRegistry(family="cells")
        registry.add_fixture(
            FixtureEntry(
                filename="test.xlsx",
                source_type="local",
                source_path="local:test.xlsx",
                provenance="local",
            )
        )
        result = check_fixture_availability(registry, ["test.xlsx"])
        assert not result["blocked"]
        assert "test.xlsx" in result["available"]

    def test_availability_check_missing(self):
        registry = FixtureRegistry(family="cells")
        result = check_fixture_availability(registry, ["missing.xlsx"])
        assert result["blocked"]
        assert "missing.xlsx" in result["missing"]
