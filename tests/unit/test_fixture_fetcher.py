"""Tests for the production-safe fixture fetcher — Wave 25 Lane B."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.fixture_registry.fixture_fetcher import (
    FetchResult,
    FixtureBlockedError,
    _DEFAULT_EXTENSION_ALLOWLIST,
    _synthetic_fallback,
    fetch_fixtures,
)

# ── Helpers ────────────────────────────────────────────────────────────────────

_GOOD_REPO_CONFIG = {
    "owner": "aspose-cad",
    "repo": "Aspose.CAD-for-.NET",
    "branch": "master",
    "fixture_paths": ["Examples/Data"],
    "extension_allowlist": [".dwg", ".dxf", ".pdf"],
    "max_file_size_bytes": 5 * 1024 * 1024,
    "max_total_size_bytes": 50 * 1024 * 1024,
    "synthetic_fallback_allowed": True,
}


# ── No-token fallback ─────────────────────────────────────────────────────────

def test_no_github_token_falls_back_to_synthetic(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    result = fetch_fixtures("cad", _GOOD_REPO_CONFIG, [".dwg"], tmp_path, cache_root=tmp_path / "cache")
    assert result.strategy == "synthetic_fallback"
    assert result.fetched == []


def test_no_github_token_blocks_when_synthetic_not_allowed(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    config = {**_GOOD_REPO_CONFIG, "synthetic_fallback_allowed": False}
    with pytest.raises(FixtureBlockedError):
        fetch_fixtures("cad", config, [".dwg"], tmp_path, cache_root=tmp_path / "cache")


# ── Empty / missing repo config ───────────────────────────────────────────────

def test_missing_owner_falls_back_to_synthetic(tmp_path):
    result = fetch_fixtures("cad", {}, [".dwg"], tmp_path, cache_root=tmp_path / "cache")
    assert result.strategy == "synthetic_fallback"


def test_missing_repo_falls_back_to_synthetic(tmp_path):
    result = fetch_fixtures("cad", {"owner": "aspose-cad"}, [".dwg"], tmp_path, cache_root=tmp_path / "cache")
    assert result.strategy == "synthetic_fallback"


# ── Dry-run mode ──────────────────────────────────────────────────────────────

def test_dry_run_returns_without_download(tmp_path):
    result = fetch_fixtures(
        "cad", _GOOD_REPO_CONFIG, [".dwg"], tmp_path,
        cache_root=tmp_path / "cache", dry_run=True,
    )
    assert result.strategy == "dry_run_validated"
    assert result.fetched == []


# ── Extension filter ──────────────────────────────────────────────────────────

def test_extension_allowlist_applied(tmp_path, monkeypatch):
    """Files outside the allowlist should not appear in fetched list."""
    # We can test this via the listing filter logic directly
    from plugin_examples.fixture_registry.fixture_fetcher import _list_github_files

    listing_cache = tmp_path / "listings"
    listing_cache.mkdir()

    # Write a fake cached listing with mixed extensions
    safe_path = "Examples_Data"
    cache_file = listing_cache / f"{safe_path}.json"
    cache_file.write_text(json.dumps([
        {"path": "Examples/Data/test.dwg", "sha": "abc", "size": 100},
        {"path": "Examples/Data/test.exe", "sha": "def", "size": 200},  # not in allowlist
        {"path": "Examples/Data/test.dxf", "sha": "ghi", "size": 150},
    ]), encoding="utf-8")

    # Force cache to appear fresh (mtime is now, TTL is 24h)
    allowed = frozenset({".dwg", ".dxf"})
    files = _list_github_files("owner", "repo", "master", "Examples/Data", allowed, 1_000_000, listing_cache, "fake_token")
    assert len(files) == 2
    paths = {f["path"] for f in files}
    assert "Examples/Data/test.exe" not in paths
    assert "Examples/Data/test.dwg" in paths
    assert "Examples/Data/test.dxf" in paths


# ── Size limits ───────────────────────────────────────────────────────────────

def test_file_size_limit_filters_large_files(tmp_path, monkeypatch):
    from plugin_examples.fixture_registry.fixture_fetcher import _list_github_files

    listing_cache = tmp_path / "listings"
    listing_cache.mkdir()

    safe_path = "Examples_Data"
    cache_file = listing_cache / f"{safe_path}.json"
    cache_file.write_text(json.dumps([
        {"path": "Examples/Data/small.dwg", "sha": "abc", "size": 100},
        {"path": "Examples/Data/large.dwg", "sha": "def", "size": 10 * 1024 * 1024},  # 10 MB
    ]), encoding="utf-8")

    max_size = 5 * 1024 * 1024  # 5 MB limit
    files = _list_github_files("o", "r", "master", "Examples/Data", frozenset({".dwg"}), max_size, listing_cache, "tok")
    assert len(files) == 1
    assert files[0]["path"].endswith("small.dwg")


# ── Cache hit / miss ──────────────────────────────────────────────────────────

def test_cache_hit_skips_download(tmp_path):
    """If a cached file exists with matching SHA, no download should occur."""
    cache_dir = tmp_path / "cache" / "cad"
    cache_dir.mkdir(parents=True)
    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # Write a fake cached file
    fake_content = b"fake dwg content"
    import hashlib
    sha = hashlib.sha256(fake_content).hexdigest()
    (cache_dir / "test.dwg").write_bytes(fake_content)
    manifest = {"test.dwg": {"file_sha256": sha, "source_path": "Examples/Data/test.dwg"}}
    (cache_dir / "fixtures-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    # Patch _list_github_files to return the fake file
    from unittest.mock import patch
    from plugin_examples.fixture_registry import fixture_fetcher as ff

    fake_listing = [{"path": "Examples/Data/test.dwg", "sha": "abc", "size": len(fake_content)}]
    import os
    with patch.dict(os.environ, {"GITHUB_TOKEN": "fake_token"}):
        with patch.object(ff, "_list_github_files", return_value=fake_listing):
            result = fetch_fixtures(
                "cad", _GOOD_REPO_CONFIG, [".dwg"], dest_dir,
                cache_root=tmp_path / "cache",
            )

    assert result.cache_hits == 1
    assert result.cache_misses == 0
    assert (dest_dir / "test.dwg").exists()
    # Provenance sidecar should be written
    assert (dest_dir / "test.dwg.provenance.json").exists()


# ── Synthetic fallback ────────────────────────────────────────────────────────

def test_synthetic_fallback_returns_correct_strategy():
    result = _synthetic_fallback("cad")
    assert result.strategy == "synthetic_fallback"
    assert result.fetched == []
    assert result.synthetic_count == 1


# ── Default extension allowlist ───────────────────────────────────────────────

def test_default_extension_allowlist_covers_common_types():
    for ext in [".xlsx", ".docx", ".pdf", ".dwg", ".dxf", ".svg", ".ttf", ".png"]:
        assert ext in _DEFAULT_EXTENSION_ALLOWLIST, f"{ext} missing from default allowlist"


# ── check_fixture_availability backward compat ───────────────────────────────

def test_check_fixture_availability_backward_compat():
    from plugin_examples.fixture_registry.fixture_fetcher import check_fixture_availability

    class FakeRegistry:
        def has_fixture(self, name):
            return name == "present.dwg"

    r = check_fixture_availability(FakeRegistry(), ["present.dwg", "missing.dxf"])
    assert r["total_required"] == 2
    assert "present.dwg" in r["available"]
    assert "missing.dxf" in r["missing"]
    assert r["blocked"] is True
