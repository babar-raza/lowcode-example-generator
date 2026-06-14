"""Tests for SharedContext — get/set/snapshot state management."""

from __future__ import annotations

from pathlib import Path

from plugin_examples.agents.context import SharedContext


class TestSharedContext:
    def test_get_set(self, tmp_path: Path):
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path / "ev")
        assert ctx.get("key") is None
        assert ctx.get("key", "default") == "default"
        ctx.set("key", 42)
        assert ctx.get("key") == 42

    def test_snapshot_returns_copy(self, tmp_path: Path):
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path / "ev")
        ctx.set("a", 1)
        ctx.set("b", 2)
        snap = ctx.snapshot()
        assert snap == {"a": 1, "b": 2}
        ctx.set("c", 3)
        assert "c" not in snap

    def test_snapshot_empty(self, tmp_path: Path):
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path / "ev")
        assert ctx.snapshot() == {}

    def test_defaults(self, tmp_path: Path):
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path / "ev")
        assert ctx.dry_run_remote is True
        assert ctx.gate_policy is None
        assert ctx.slo_defs == []
        assert ctx.history is None
        assert ctx.audit is None

    def test_overwrite_value(self, tmp_path: Path):
        ctx = SharedContext(repo_root=tmp_path, evidence_dir=tmp_path / "ev")
        ctx.set("x", "old")
        ctx.set("x", "new")
        assert ctx.get("x") == "new"
