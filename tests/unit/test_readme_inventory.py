"""Tests for the cumulative README example inventory."""

import json
from pathlib import Path

import pytest

from plugin_examples.publisher.readme_inventory import (
    InventoryEntry,
    InventoryAuditTrail,
    discover_family_inventory,
    build_cumulative_examples_meta,
    build_package_path_map,
    inventory_to_json,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_package(tmp_path: Path, family: str, pkg_name: str, examples: list[str]) -> Path:
    """Create a minimal PR dry-run package directory."""
    pkg = tmp_path / "workspace" / "pr-dry-run" / pkg_name
    lowcode = pkg / "examples" / family / "lowcode"
    for ex in examples:
        ex_dir = lowcode / ex
        ex_dir.mkdir(parents=True, exist_ok=True)
        (ex_dir / "Program.cs").write_text("// placeholder", encoding="utf-8")
    return pkg


def _make_post_merge(tmp_path: Path, family: str, examples: list[dict]) -> None:
    """Create a post-merge validation JSON."""
    pm_dir = tmp_path / "workspace" / "verification" / "latest"
    pm_dir.mkdir(parents=True, exist_ok=True)
    data = {"examples": examples}
    (pm_dir / f"{family}-post-merge-clean-checkout-validation.json").write_text(
        json.dumps(data), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestDiscoverFamilyInventory:

    def test_single_package_discovery(self, tmp_path):
        _make_package(tmp_path, "cells", "cells-controlled-pilot", ["converter", "merger"])
        entries, trail = discover_family_inventory(
            "cells", tmp_path, inventory_mode="repo_actual"
        )
        names = [e.name for e in entries]
        assert "converter" in names
        assert "merger" in names
        assert len(entries) == 2
        assert trail.inventory_mode == "repo_actual"

    def test_multiple_packages_deduplicated(self, tmp_path):
        _make_package(tmp_path, "pdf", "pdf-controlled-pilot", ["doc-converter", "html"])
        _make_package(tmp_path, "pdf", "pdf-controlled-pilot-pr5", ["jpeg", "png"])
        entries, trail = discover_family_inventory(
            "pdf", tmp_path, inventory_mode="repo_actual"
        )
        names = [e.name for e in entries]
        assert sorted(names) == ["doc-converter", "html", "jpeg", "png"]

    def test_post_merge_evidence_used_as_base(self, tmp_path):
        _make_post_merge(tmp_path, "cells", [
            {"name": "converter", "output_format": "pdf"},
            {"name": "merger", "output_format": "xlsx"},
        ])
        _make_package(tmp_path, "cells", "cells-controlled-pilot", ["converter"])
        entries, trail = discover_family_inventory(
            "cells", tmp_path, inventory_mode="repo_actual"
        )
        # Both from post-merge, plus package enriches package_path
        assert len(entries) == 2
        converter = next(e for e in entries if e.name == "converter")
        assert converter.output_format == "pdf"  # from post-merge

    def test_repo_actual_explicit_examples(self, tmp_path):
        _make_package(tmp_path, "pdf", "pdf-controlled-pilot", ["doc-converter"])
        entries, trail = discover_family_inventory(
            "pdf", tmp_path,
            inventory_mode="repo_actual",
            repo_actual_examples=["merger", "splitter"],
        )
        names = [e.name for e in entries]
        assert "merger" in names
        assert "splitter" in names
        assert "doc-converter" in names  # from package scan
        assert len(entries) == 3

    def test_current_package_overlay(self, tmp_path):
        _make_post_merge(tmp_path, "pdf", [
            {"name": "merger"},
            {"name": "splitter"},
        ])
        pkg = _make_package(tmp_path, "pdf", "pdf-pr5", ["jpeg", "png"])
        entries, trail = discover_family_inventory(
            "pdf", tmp_path,
            inventory_mode="current_package_overlay",
            current_package_path=pkg,
        )
        names = [e.name for e in entries]
        assert sorted(names) == ["jpeg", "merger", "png", "splitter"]
        assert trail.inventory_mode == "current_package_overlay"

    def test_batch_overlay(self, tmp_path):
        _make_post_merge(tmp_path, "pdf", [{"name": "merger"}])
        pkg1 = _make_package(tmp_path, "pdf", "pdf-pr5", ["jpeg"])
        pkg2 = _make_package(tmp_path, "pdf", "pdf-pr6", ["toc-gen"])
        entries, trail = discover_family_inventory(
            "pdf", tmp_path,
            inventory_mode="batch_overlay",
            batch_package_paths=[pkg1, pkg2],
        )
        names = [e.name for e in entries]
        assert sorted(names) == ["jpeg", "merger", "toc-gen"]

    def test_invalid_mode_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Invalid inventory_mode"):
            discover_family_inventory("cells", tmp_path, inventory_mode="bogus")

    def test_current_package_overlay_requires_path(self, tmp_path):
        with pytest.raises(ValueError, match="current_package_path required"):
            discover_family_inventory(
                "cells", tmp_path, inventory_mode="current_package_overlay"
            )

    def test_empty_family_returns_empty(self, tmp_path):
        (tmp_path / "workspace" / "pr-dry-run").mkdir(parents=True)
        entries, trail = discover_family_inventory("empty", tmp_path)
        assert entries == []

    def test_audit_trail_records_sources(self, tmp_path):
        _make_package(tmp_path, "cells", "cells-controlled-pilot", ["converter"])
        _make_package(tmp_path, "cells", "cells-extra", ["merger"])
        _, trail = discover_family_inventory("cells", tmp_path)
        assert len(trail.sources_scanned) >= 2

    def test_dedup_preserves_package_path(self, tmp_path):
        _make_post_merge(tmp_path, "cells", [{"name": "converter"}])
        pkg = _make_package(tmp_path, "cells", "cells-controlled-pilot", ["converter"])
        entries, _ = discover_family_inventory("cells", tmp_path)
        conv = next(e for e in entries if e.name == "converter")
        assert conv.package_path  # enriched from pr_package
        assert conv.has_program_cs


class TestBuildHelpers:

    def test_build_cumulative_examples_meta(self):
        entries = [
            InventoryEntry(name="conv", source_package="p1", source_type="pr_package", output_format="pdf"),
            InventoryEntry(name="merge", source_package="p1", source_type="pr_package"),
        ]
        meta = build_cumulative_examples_meta(entries)
        assert meta == [
            {"name": "conv", "output_format": "pdf"},
            {"name": "merge", "output_format": ""},
        ]

    def test_build_package_path_map(self, tmp_path):
        entries = [
            InventoryEntry(name="a", source_package="p1", source_type="pr_package",
                           package_path=str(tmp_path / "p1")),
            InventoryEntry(name="b", source_package="p2", source_type="pr_package",
                           package_path=str(tmp_path / "p2")),
            InventoryEntry(name="c", source_package="pm", source_type="post_merge"),
        ]
        pmap = build_package_path_map(entries)
        assert pmap["a"] == tmp_path / "p1"
        assert pmap["b"] == tmp_path / "p2"
        assert "c" not in pmap


class TestInventoryJson:

    def test_serialization(self):
        entries = [InventoryEntry(name="x", source_package="p", source_type="pr_package")]
        trail = InventoryAuditTrail(family="test", inventory_mode="repo_actual")
        result = json.loads(inventory_to_json(entries, trail))
        assert len(result["inventory"]) == 1
        assert result["audit_trail"]["family"] == "test"
