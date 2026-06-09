"""Tests for fixture provenance sidecar format — Wave 25 Lane B."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from plugin_examples.fixture_registry.fixture_fetcher import _copy_with_provenance


REQUIRED_SIDECAR_FIELDS = [
    "filename",
    "source_repo",
    "source_ref",
    "source_commit_sha",
    "source_path",
    "file_sha256",
    "downloaded_at",
    "file_size_bytes",
    "license_note",
]


def _make_sidecar(tmp_path: Path) -> tuple[Path, dict]:
    """Create a fixture file and its provenance sidecar; return sidecar path + content."""
    content = b"fake fixture content"
    sha256 = hashlib.sha256(content).hexdigest()
    src = tmp_path / "src" / "test.dwg"
    src.parent.mkdir()
    src.write_bytes(content)

    dst = tmp_path / "dest" / "test.dwg"
    dst.parent.mkdir()

    file_entry = {"path": "Examples/Data/test.dwg", "sha": "abc", "size": len(content)}
    _copy_with_provenance(src, dst, file_entry, "aspose-cad", "Aspose.CAD-for-.NET", "master", sha256)

    sidecar_path = dst.with_suffix(".dwg.provenance.json")
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    return sidecar_path, sidecar


def test_provenance_sidecar_created(tmp_path):
    sidecar_path, _ = _make_sidecar(tmp_path)
    assert sidecar_path.exists()


def test_provenance_sidecar_has_all_required_fields(tmp_path):
    _, sidecar = _make_sidecar(tmp_path)
    for field in REQUIRED_SIDECAR_FIELDS:
        assert field in sidecar, f"Missing required field: {field}"


def test_provenance_sidecar_source_repo_format(tmp_path):
    _, sidecar = _make_sidecar(tmp_path)
    assert sidecar["source_repo"] == "aspose-cad/Aspose.CAD-for-.NET"


def test_provenance_sidecar_sha256_correct(tmp_path):
    content = b"fake fixture content"
    expected_sha = hashlib.sha256(content).hexdigest()
    _, sidecar = _make_sidecar(tmp_path)
    assert sidecar["file_sha256"] == expected_sha


def test_provenance_sidecar_filename_matches(tmp_path):
    _, sidecar = _make_sidecar(tmp_path)
    assert sidecar["filename"] == "test.dwg"


def test_provenance_sidecar_size_matches(tmp_path):
    content = b"fake fixture content"
    _, sidecar = _make_sidecar(tmp_path)
    assert sidecar["file_size_bytes"] == len(content)


def test_provenance_sidecar_source_path(tmp_path):
    _, sidecar = _make_sidecar(tmp_path)
    assert sidecar["source_path"] == "Examples/Data/test.dwg"


def test_provenance_sidecar_license_note_present(tmp_path):
    _, sidecar = _make_sidecar(tmp_path)
    assert "MIT" in sidecar["license_note"]


def test_provenance_sidecar_downloaded_at_is_iso8601(tmp_path):
    from datetime import datetime
    _, sidecar = _make_sidecar(tmp_path)
    ts = sidecar["downloaded_at"]
    # Should parse without error
    datetime.fromisoformat(ts)


def test_provenance_sidecar_source_commit_sha_is_none(tmp_path):
    """source_commit_sha starts as None; will be populated if the API provides it."""
    _, sidecar = _make_sidecar(tmp_path)
    assert sidecar["source_commit_sha"] is None
