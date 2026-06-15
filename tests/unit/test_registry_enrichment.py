"""Tests for registry enrichment — _expand_registry_entries."""

from __future__ import annotations

import pytest
import yaml

from plugin_examples.commands.catalog_discover import (
    _expand_registry_entries,
    _guess_operation_kind,
)


@pytest.fixture
def registry_dir(tmp_path):
    """Create a capability registry directory with a single-entry YAML."""
    reg_dir = tmp_path / "pipeline" / "plugin-capability-registry"
    reg_dir.mkdir(parents=True)

    imaging_data = {
        "entries": [
            {
                "family": "imaging",
                "plugin_slug": None,
                "type_name": "Image",
                "method_name": "Save",
                "status": "PROBE_CONFIRMED",
                "confidence_score": 0.80,
            }
        ]
    }
    (reg_dir / "imaging.yaml").write_text(yaml.dump(imaging_data), encoding="utf-8")

    zip_data = {
        "entries": [
            {
                "family": "zip",
                "plugin_slug": None,
                "type_name": "Archive",
                "method_name": "Save",
                "status": "PROBE_CONFIRMED",
                "confidence_score": 0.90,
            }
        ]
    }
    (reg_dir / "zip.yaml").write_text(yaml.dump(zip_data), encoding="utf-8")

    return reg_dir


class TestExpandRegistryEntries:
    def test_creates_new_entries_from_static_fallback(self, tmp_path, registry_dir):
        """Static fallback creates WEBSITE_DISCOVERED entries for imaging."""
        families_map = {"imaging": []}  # No discovery data, triggers static fallback

        added = _expand_registry_entries(tmp_path, families_map)

        assert added >= 9  # imaging has 10 known slugs, 1 already in registry (image.save)

        data = yaml.safe_load((registry_dir / "imaging.yaml").read_text(encoding="utf-8"))
        entries = data["entries"]
        assert len(entries) >= 10

        # Original entry preserved
        original = [e for e in entries if e.get("type_name") == "Image"]
        assert len(original) == 1
        assert original[0]["status"] == "PROBE_CONFIRMED"

        # New entries are WEBSITE_DISCOVERED
        new_entries = [e for e in entries if e.get("status") == "WEBSITE_DISCOVERED"]
        assert len(new_entries) >= 9
        assert all(e["bootstrap_status"] == "WEBSITE_DISCOVERED" for e in new_entries)
        assert all(e["next_action"] == "PROBE_PENDING" for e in new_entries)

    def test_preserves_existing_entries(self, tmp_path, registry_dir):
        """Existing PROBE_CONFIRMED entries must not be overwritten."""
        families_map = {"imaging": []}

        _expand_registry_entries(tmp_path, families_map)

        data = yaml.safe_load((registry_dir / "imaging.yaml").read_text(encoding="utf-8"))
        confirmed = [e for e in data["entries"] if e.get("status") == "PROBE_CONFIRMED"]
        assert len(confirmed) == 1

    def test_deduplicates_slugs(self, tmp_path, registry_dir):
        """Same slug from discovery + static fallback should not create duplicates."""
        families_map = {
            "imaging": [
                {"plugin_slug": "image-converter", "slug": "image-converter"},
            ]
        }

        _expand_registry_entries(tmp_path, families_map)

        data = yaml.safe_load((registry_dir / "imaging.yaml").read_text(encoding="utf-8"))
        converter_entries = [
            e for e in data["entries"]
            if e.get("plugin_slug") == "image-converter"
        ]
        assert len(converter_entries) == 1

    def test_zip_gets_three_entries(self, tmp_path, registry_dir):
        """ZIP should get 3 entries total (1 existing + 3 new from static)."""
        families_map = {"zip": []}

        added = _expand_registry_entries(tmp_path, families_map)

        data = yaml.safe_load((registry_dir / "zip.yaml").read_text(encoding="utf-8"))
        assert len(data["entries"]) >= 4  # 1 original + 3 new

    def test_no_expansion_when_no_new_slugs(self, tmp_path, registry_dir):
        """If all slugs already exist, no new entries are created for that family."""
        # Add all known imaging slugs to the existing registry
        data = yaml.safe_load((registry_dir / "imaging.yaml").read_text(encoding="utf-8"))
        for slug_info in [
            "animation-maker", "image-converter", "image-compressor",
            "image-merger", "image-resizer", "photo-album-maker",
            "image-cropper", "image-effect-creator", "image-deskew",
            "image-rotate-flip",
        ]:
            data["entries"].append({
                "family": "imaging",
                "plugin_slug": slug_info,
                "status": "WEBSITE_DISCOVERED",
            })
        (registry_dir / "imaging.yaml").write_text(yaml.dump(data), encoding="utf-8")

        # Also add all known zip slugs to prevent zip from expanding
        zip_data = yaml.safe_load((registry_dir / "zip.yaml").read_text(encoding="utf-8"))
        for slug_info in ["universal-compressor", "universal-extractor", "rar-extractor"]:
            zip_data["entries"].append({
                "family": "zip",
                "plugin_slug": slug_info,
                "status": "WEBSITE_DISCOVERED",
            })
        (registry_dir / "zip.yaml").write_text(yaml.dump(zip_data), encoding="utf-8")

        families_map = {"imaging": []}
        added = _expand_registry_entries(tmp_path, families_map)

        assert added == 0


class TestGuessOperationKind:
    def test_converter(self):
        assert _guess_operation_kind("image-converter", "imaging") == "IMAGING_CONVERSION"

    def test_compressor(self):
        assert _guess_operation_kind("image-compressor", "imaging") == "IMAGING_COMPRESSION"

    def test_extractor(self):
        assert _guess_operation_kind("universal-extractor", "zip") == "ZIP_EXTRACT"

    def test_unknown_slug(self):
        assert _guess_operation_kind("mystery-plugin", "barcode") == "BARCODE_UNKNOWN"
