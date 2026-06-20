"""Tests for catalog-discover --static-manifest flag (TC-SRHP-01).

Verifies that a pre-built JSON manifest can be loaded instead of crawling
products.aspose.net — the WAF workaround path.
"""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from plugin_examples.commands.catalog_discover import _handle_static_manifest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_args(**kwargs) -> object:
    """Create a simple namespace object for args."""
    ns = types.SimpleNamespace()
    ns.all_families = kwargs.get("all_families", False)
    ns.enrich_registry = kwargs.get("enrich_registry", False)
    ns.expand_registry = kwargs.get("expand_registry", False)
    return ns


def _write_manifest(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_static_manifest_loads_families(tmp_path: Path) -> None:
    """Happy path: manifest with one family is loaded into catalog."""
    manifest = tmp_path / "manifest.json"
    _write_manifest(
        manifest,
        {
            "families": {
                "imaging": [
                    {"slug": "image-converter", "url": "https://products.aspose.net/imaging/image-converter/"},
                    {"slug": "image-resizer", "url": "https://products.aspose.net/imaging/image-resizer/"},
                ]
            }
        },
    )
    output = tmp_path / "catalog.json"
    rc = _handle_static_manifest(
        manifest_path=manifest,
        families=["imaging"],
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(),
    )
    assert rc == 0
    assert output.exists()
    data = json.loads(output.read_text())
    assert data["source"] == "static_manifest"
    assert "imaging" in data["families"]
    assert len(data["families"]["imaging"]) == 2
    assert data["total_entries"] == 2
    assert data["errors"] == []


def test_static_manifest_missing_family_records_error(tmp_path: Path) -> None:
    """Family requested but not in manifest records an error entry."""
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, {"families": {"barcode": [{"slug": "barcode-gen"}]}})
    output = tmp_path / "catalog.json"
    rc = _handle_static_manifest(
        manifest_path=manifest,
        families=["barcode", "imaging"],  # imaging not in manifest
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(),
    )
    assert rc == 0
    data = json.loads(output.read_text())
    assert "barcode" in data["families"]
    assert "imaging" not in data["families"]
    assert any("imaging" in e for e in data["errors"])


def test_static_manifest_file_not_found(tmp_path: Path) -> None:
    """Returns error code 1 when manifest path does not exist."""
    output = tmp_path / "catalog.json"
    rc = _handle_static_manifest(
        manifest_path=tmp_path / "nonexistent.json",
        families=["imaging"],
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(),
    )
    assert rc == 1
    assert not output.exists()


def test_static_manifest_invalid_json(tmp_path: Path) -> None:
    """Returns error code 1 when manifest contains invalid JSON."""
    manifest = tmp_path / "bad.json"
    manifest.write_text("not json {{{", encoding="utf-8")
    output = tmp_path / "catalog.json"
    rc = _handle_static_manifest(
        manifest_path=manifest,
        families=["imaging"],
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(),
    )
    assert rc == 1


def test_static_manifest_flat_list_input(tmp_path: Path) -> None:
    """Flat list format (no 'families' key) is grouped by family_slug field."""
    manifest = tmp_path / "flat.json"
    _write_manifest(
        manifest,
        [
            {"family_slug": "ocr", "slug": "ocr-scan"},
            {"family_slug": "ocr", "slug": "ocr-read"},
        ],
    )
    output = tmp_path / "catalog.json"
    rc = _handle_static_manifest(
        manifest_path=manifest,
        families=["ocr"],
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(),
    )
    assert rc == 0
    data = json.loads(output.read_text())
    assert "ocr" in data["families"]
    assert len(data["families"]["ocr"]) == 2


def test_static_manifest_unsupported_structure(tmp_path: Path) -> None:
    """Returns error code 1 when manifest is neither a dict with 'families' nor a list."""
    manifest = tmp_path / "weird.json"
    manifest.write_text('"just a string"', encoding="utf-8")
    output = tmp_path / "catalog.json"
    rc = _handle_static_manifest(
        manifest_path=manifest,
        families=["imaging"],
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(),
    )
    assert rc == 1


def test_static_manifest_all_families_flag(tmp_path: Path) -> None:
    """--all-families uses all families in the manifest regardless of --family filter."""
    manifest = tmp_path / "manifest.json"
    _write_manifest(
        manifest,
        {
            "families": {
                "imaging": [{"slug": "convert"}],
                "barcode": [{"slug": "generate"}],
            }
        },
    )
    output = tmp_path / "catalog.json"
    rc = _handle_static_manifest(
        manifest_path=manifest,
        families=[],  # empty — all_families overrides
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(all_families=True),
    )
    assert rc == 0
    data = json.loads(output.read_text())
    assert "imaging" in data["families"]
    assert "barcode" in data["families"]
    assert data["total_entries"] == 2


def test_static_manifest_catalog_source_field(tmp_path: Path) -> None:
    """Output catalog records source=static_manifest and manifest_path."""
    manifest = tmp_path / "manifest.json"
    _write_manifest(manifest, {"families": {"svg": [{"slug": "convert-svg"}]}})
    output = tmp_path / "catalog.json"
    _handle_static_manifest(
        manifest_path=manifest,
        families=["svg"],
        output_path=output,
        timestamp="2026-06-20T00:00:00",
        repo_root=tmp_path,
        args=_make_args(),
    )
    data = json.loads(output.read_text())
    assert data["source"] == "static_manifest"
    assert "manifest_path" in data
    assert "manifest.json" in data["manifest_path"]
