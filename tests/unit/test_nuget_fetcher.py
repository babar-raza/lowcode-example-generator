"""Unit tests for nuget_fetcher.fetcher and nuget_fetcher.cache."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.nuget_fetcher.cache import (
    check_cache,
    compute_sha256,
    read_manifest,
    write_manifest,
)
from plugin_examples.nuget_fetcher.fetcher import (
    NuGetFetchError,
    PackageNotFoundError,
    fetch_package,
    resolve_latest_stable,
)


# --- Fixtures ---


@pytest.fixture
def tmp_run_dir(tmp_path):
    run_dir = tmp_path / "workspace" / "runs" / "test-run"
    run_dir.mkdir(parents=True)
    return run_dir


@pytest.fixture
def fake_nupkg(tmp_path):
    """Create a fake .nupkg file for cache testing."""
    p = tmp_path / "fake.nupkg"
    p.write_bytes(b"fake nupkg content")
    return p


# --- Version list response mock ---


def _mock_service_index():
    """Return a mock service index response."""
    return {
        "resources": [
            {
                "@id": "https://api.nuget.org/v3-flatcontainer/",
                "@type": "PackageBaseAddress/3.0.0",
            }
        ]
    }


def _mock_versions(versions: list[str]):
    """Return a mock versions response."""
    return {"versions": versions}


# --- Tests: resolve_latest_stable ---


class TestResolveLatestStable:
    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_excludes_prerelease(self, mock_get):
        # Service index + versions endpoint
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_versions = MagicMock()
        resp_versions.status_code = 200
        resp_versions.json.return_value = _mock_versions([
            "1.0.0",
            "2.0.0-beta1",
            "2.0.0",
            "3.0.0-rc.1",
        ])
        resp_versions.raise_for_status = MagicMock()

        mock_get.side_effect = [resp_index, resp_versions]

        version = resolve_latest_stable("TestPackage", allow_prerelease=False)
        assert version == "2.0.0"

    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_includes_prerelease_when_allowed(self, mock_get):
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_versions = MagicMock()
        resp_versions.status_code = 200
        resp_versions.json.return_value = _mock_versions([
            "1.0.0",
            "2.0.0-beta1",
            "3.0.0-rc.1",
        ])
        resp_versions.raise_for_status = MagicMock()

        mock_get.side_effect = [resp_index, resp_versions]

        version = resolve_latest_stable("TestPackage", allow_prerelease=True)
        assert version == "3.0.0-rc.1"

    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_pinned_version_honored(self, mock_get, tmp_run_dir):
        """fetch_package with pinned version skips resolution."""
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_download = MagicMock()
        resp_download.status_code = 200
        resp_download.iter_content.return_value = [b"nupkg data"]
        resp_download.raise_for_status = MagicMock()

        mock_get.side_effect = [resp_index, resp_download]

        result = fetch_package(
            "TestPackage",
            "pinned",
            pinned_version="1.2.3",
            run_dir=tmp_run_dir,
            family="test",
        )
        assert result["version"] == "1.2.3"

    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_missing_package_raises(self, mock_get):
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_versions = MagicMock()
        resp_versions.status_code = 404
        resp_versions.raise_for_status.side_effect = Exception("404")

        import requests as req
        resp_versions.raise_for_status.side_effect = req.HTTPError(
            response=resp_versions
        )

        mock_get.side_effect = [resp_index, resp_versions]

        with pytest.raises(PackageNotFoundError):
            resolve_latest_stable("NonExistentPackage")


# --- Tests: fetch_package ---


class TestFetchPackage:
    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_download_writes_file(self, mock_get, tmp_run_dir):
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_versions = MagicMock()
        resp_versions.status_code = 200
        resp_versions.json.return_value = _mock_versions(["1.0.0"])
        resp_versions.raise_for_status = MagicMock()

        resp_download = MagicMock()
        resp_download.status_code = 200
        resp_download.iter_content.return_value = [b"nupkg content"]
        resp_download.raise_for_status = MagicMock()

        mock_get.side_effect = [resp_index, resp_versions, resp_index, resp_download]

        result = fetch_package(
            "TestPkg",
            "latest-stable",
            run_dir=tmp_run_dir,
            family="test",
        )

        nupkg_path = Path(result["cached_path"])
        assert nupkg_path.exists()
        assert nupkg_path.name == "TestPkg.1.0.0.nupkg"

    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_sha256_recorded(self, mock_get, tmp_run_dir):
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_versions = MagicMock()
        resp_versions.status_code = 200
        resp_versions.json.return_value = _mock_versions(["1.0.0"])
        resp_versions.raise_for_status = MagicMock()

        content = b"test nupkg content for hash"
        resp_download = MagicMock()
        resp_download.status_code = 200
        resp_download.iter_content.return_value = [content]
        resp_download.raise_for_status = MagicMock()

        mock_get.side_effect = [resp_index, resp_versions, resp_index, resp_download]

        result = fetch_package(
            "TestPkg",
            "latest-stable",
            run_dir=tmp_run_dir,
            family="test",
        )

        expected_hash = hashlib.sha256(content).hexdigest()
        assert result["sha256"] == expected_hash

    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_cache_hit_avoids_redownload(self, mock_get, tmp_run_dir):
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_versions = MagicMock()
        resp_versions.status_code = 200
        resp_versions.json.return_value = _mock_versions(["1.0.0"])
        resp_versions.raise_for_status = MagicMock()

        content = b"cached nupkg"
        resp_download = MagicMock()
        resp_download.status_code = 200
        resp_download.iter_content.return_value = [content]
        resp_download.raise_for_status = MagicMock()

        # First call: resolve + download
        mock_get.side_effect = [resp_index, resp_versions, resp_index, resp_download]
        result1 = fetch_package(
            "CachePkg",
            "latest-stable",
            run_dir=tmp_run_dir,
            family="test",
        )

        # Reset mock — second call should use cache
        mock_get.reset_mock()
        mock_get.side_effect = [resp_index, resp_versions]

        result2 = fetch_package(
            "CachePkg",
            "latest-stable",
            run_dir=tmp_run_dir,
            family="test",
        )

        assert result2["version"] == "1.0.0"
        assert result2["sha256"] == result1["sha256"]
        # Only 2 calls (service index + version list), no download call
        assert mock_get.call_count == 2


# --- Tests: cache module ---


class TestCache:
    def test_compute_sha256(self, fake_nupkg):
        expected = hashlib.sha256(b"fake nupkg content").hexdigest()
        assert compute_sha256(fake_nupkg) == expected

    def test_check_cache_miss(self, tmp_path):
        assert check_cache(tmp_path / "nonexistent.nupkg") is False

    def test_check_cache_hit(self, fake_nupkg):
        assert check_cache(fake_nupkg) is True

    def test_check_cache_hash_match(self, fake_nupkg):
        expected = hashlib.sha256(b"fake nupkg content").hexdigest()
        assert check_cache(fake_nupkg, expected) is True

    def test_check_cache_hash_mismatch(self, fake_nupkg):
        assert check_cache(fake_nupkg, "wrong_hash") is False

    def test_write_and_read_manifest(self, tmp_path):
        manifest_path = tmp_path / "sub" / "manifest.json"
        data = {"package_id": "Test", "version": "1.0.0"}
        write_manifest(manifest_path, data)

        loaded = read_manifest(manifest_path)
        assert loaded == data

    def test_read_missing_manifest(self, tmp_path):
        assert read_manifest(tmp_path / "missing.json") is None


# --- Tests: path correctness ---


class TestPathCorrectness:
    @patch("plugin_examples.nuget_fetcher.fetcher.requests.get")
    def test_paths_use_workspace(self, mock_get, tmp_run_dir):
        """Verify output paths use workspace/runs, not old root paths."""
        resp_index = MagicMock()
        resp_index.status_code = 200
        resp_index.json.return_value = _mock_service_index()
        resp_index.raise_for_status = MagicMock()

        resp_versions = MagicMock()
        resp_versions.status_code = 200
        resp_versions.json.return_value = _mock_versions(["1.0.0"])
        resp_versions.raise_for_status = MagicMock()

        resp_download = MagicMock()
        resp_download.status_code = 200
        resp_download.iter_content.return_value = [b"data"]
        resp_download.raise_for_status = MagicMock()

        mock_get.side_effect = [resp_index, resp_versions, resp_index, resp_download]

        result = fetch_package(
            "TestPkg",
            "latest-stable",
            run_dir=tmp_run_dir,
            family="test",
        )

        cached_path = result["cached_path"]
        # Must be under the run dir, not under a root-level runs/ or manifests/
        assert str(tmp_run_dir) in cached_path
