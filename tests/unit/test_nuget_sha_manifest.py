"""Tests for NuGet SHA-256 manifest revalidation — Wave 25 Lane D."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from plugin_examples.nuget_fetcher.fetcher import (
    _load_sha_manifest,
    _record_sha_manifest,
    _revalidate_sha_manifest,
    _save_sha_manifest,
    _SHA_MANIFEST_PATH,
)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _patch_sha_path(tmp_path: Path):
    """Redirect SHA manifest to a temp path for isolation."""
    import plugin_examples.nuget_fetcher.fetcher as mod
    return patch.object(mod, "_SHA_MANIFEST_PATH", tmp_path / "sha-manifest.json")


# ── _record_sha_manifest ──────────────────────────────────────────────────────

def test_record_creates_manifest(tmp_path):
    with _patch_sha_path(tmp_path):
        _record_sha_manifest("Aspose.BarCode", "26.5.0", "abc123", "https://example.com/pkg")
        manifest = _load_sha_manifest()
        # monkey-patch the global path for load as well
        manifest_file = tmp_path / "sha-manifest.json"
        data = json.loads(manifest_file.read_text())
        assert "Aspose.BarCode/26.5.0" in data
        entry = data["Aspose.BarCode/26.5.0"]
        assert entry["sha256"] == "abc123"
        assert "downloaded_at" in entry
        assert "last_revalidated" in entry


# ── _revalidate_sha_manifest — file missing ───────────────────────────────────

def test_revalidate_returns_none_when_file_missing(tmp_path):
    with _patch_sha_path(tmp_path):
        result = _revalidate_sha_manifest("Aspose.BarCode", "26.5.0", tmp_path / "nonexistent.nupkg")
    assert result is None


# ── _revalidate_sha_manifest — SHA mismatch deletes file ─────────────────────

def test_revalidate_deletes_corrupted_file(tmp_path):
    nupkg = tmp_path / "Aspose.BarCode.26.5.0.nupkg"
    nupkg.write_bytes(b"real content")
    real_sha = hashlib.sha256(b"real content").hexdigest()

    manifest_path = tmp_path / "sha-manifest.json"
    manifest_data = {
        "Aspose.BarCode/26.5.0": {
            "sha256": "wrong_sha_that_doesnt_match",
            "downloaded_at": "2026-01-01T00:00:00+00:00",
            "last_revalidated": "2020-01-01T00:00:00+00:00",  # old — will revalidate
        }
    }
    manifest_path.write_text(json.dumps(manifest_data))

    import plugin_examples.nuget_fetcher.fetcher as mod
    with patch.object(mod, "_SHA_MANIFEST_PATH", manifest_path):
        result = _revalidate_sha_manifest("Aspose.BarCode", "26.5.0", nupkg)

    assert result is None
    assert not nupkg.exists(), "Corrupted file should have been deleted"


# ── _revalidate_sha_manifest — SHA matches ────────────────────────────────────

def test_revalidate_returns_sha_when_file_matches(tmp_path):
    content = b"valid nupkg content"
    sha = hashlib.sha256(content).hexdigest()
    nupkg = tmp_path / "Aspose.BarCode.26.5.0.nupkg"
    nupkg.write_bytes(content)

    manifest_path = tmp_path / "sha-manifest.json"
    manifest_data = {
        "Aspose.BarCode/26.5.0": {
            "sha256": sha,
            "downloaded_at": "2026-01-01T00:00:00+00:00",
            "last_revalidated": "2020-01-01T00:00:00+00:00",  # old — will revalidate
        }
    }
    manifest_path.write_text(json.dumps(manifest_data))

    import plugin_examples.nuget_fetcher.fetcher as mod
    with patch.object(mod, "_SHA_MANIFEST_PATH", manifest_path):
        result = _revalidate_sha_manifest("Aspose.BarCode", "26.5.0", nupkg)

    assert result == sha


# ── _revalidate_sha_manifest — TTL skips revalidation ────────────────────────

def test_revalidate_skips_within_ttl(tmp_path):
    content = b"some bytes"
    nupkg = tmp_path / "pkg.nupkg"
    nupkg.write_bytes(content)

    from datetime import datetime, timezone
    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    manifest_path = tmp_path / "sha-manifest.json"
    manifest_data = {
        "Aspose.BarCode/26.5.0": {
            "sha256": "stored_sha",
            "downloaded_at": now_iso,
            "last_revalidated": now_iso,  # just revalidated — within TTL
        }
    }
    manifest_path.write_text(json.dumps(manifest_data))

    import plugin_examples.nuget_fetcher.fetcher as mod
    with patch.object(mod, "_SHA_MANIFEST_PATH", manifest_path):
        result = _revalidate_sha_manifest("Aspose.BarCode", "26.5.0", nupkg)

    # Should return stored SHA without computing actual hash (within TTL)
    assert result == "stored_sha"
    # File should still exist (not deleted)
    assert nupkg.exists()
