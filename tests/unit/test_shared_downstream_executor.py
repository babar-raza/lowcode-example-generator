"""Tests for SharedDownstreamExecutor — Wave 23 Lane C pipeline parity."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.shared_downstream_executor import (
    BatchResult,
    DownstreamResult,
    PluginCandidate,
    SharedDownstreamExecutor,
    discover_lowcode_candidates,
    discover_nonlowcode_candidates,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_quality_example(tmp_path: Path, slug: str, family: str = "barcode") -> Path:
    d = tmp_path / slug
    d.mkdir(parents=True)
    (d / "example.manifest.json").write_text(
        json.dumps({"scenario_id": slug}), encoding="utf-8"
    )
    (d / "expected-output.json").write_text("{}", encoding="utf-8")
    readme = (
        f"# {family}/{slug}\n\n## Purpose\nDoes X.\n\n"
        "## Prerequisites\n.NET 8\n\n## Expected Output\nPNG.\n"
    )
    (d / "README.md").write_text(readme, encoding="utf-8")
    return d


def make_minimal_example(tmp_path: Path, slug: str) -> Path:
    d = tmp_path / slug
    d.mkdir(parents=True)
    (d / "example.manifest.json").write_text("{}", encoding="utf-8")
    (d / "expected-output.json").write_text("{}", encoding="utf-8")
    (d / "README.md").write_text("# title\nMinimal content.", encoding="utf-8")
    return d


# ---------------------------------------------------------------------------
# PluginCandidate
# ---------------------------------------------------------------------------


class TestPluginCandidate:
    def test_lowcode_candidate(self, tmp_path):
        c = PluginCandidate(
            slug="convert-words-to-pdf",
            family="words",
            namespace_source="LOWCODE",
            discovery_method="namespace_scan",
            example_dir=tmp_path,
        )
        assert c.namespace_source == "LOWCODE"
        assert c.discovery_method == "namespace_scan"

    def test_nonlowcode_candidate(self, tmp_path):
        c = PluginCandidate(
            slug="1d-barcode-reader",
            family="barcode",
            namespace_source="NON_LOWCODE_PLUGIN",
            discovery_method="capability_registry_fallback",
            example_dir=tmp_path,
        )
        assert c.namespace_source == "NON_LOWCODE_PLUGIN"
        assert c.discovery_method == "capability_registry_fallback"


# ---------------------------------------------------------------------------
# SharedDownstreamExecutor — identical behavior for both sources
# ---------------------------------------------------------------------------


class TestSharedDownstreamExecutor:
    def test_lowcode_quality_example_passes(self, tmp_path):
        d = make_quality_example(tmp_path, "convert-words-to-pdf", "words")
        candidate = PluginCandidate(
            slug="convert-words-to-pdf",
            family="words",
            namespace_source="LOWCODE",
            discovery_method="namespace_scan",
            example_dir=d,
        )
        result = SharedDownstreamExecutor().execute(candidate)
        assert result.ok, result.errors
        assert result.artifact_contract["manifest"] == "PRESENT"
        assert result.artifact_contract["expected_output"] == "PRESENT"
        assert result.artifact_contract["readme"] == "QUALITY"
        assert result.publication_state == "READY_FOR_PR"

    def test_nonlowcode_quality_example_passes(self, tmp_path):
        d = make_quality_example(tmp_path, "1d-barcode-reader", "barcode")
        candidate = PluginCandidate(
            slug="1d-barcode-reader",
            family="barcode",
            namespace_source="NON_LOWCODE_PLUGIN",
            discovery_method="capability_registry_fallback",
            example_dir=d,
        )
        result = SharedDownstreamExecutor().execute(candidate)
        assert result.ok, result.errors
        assert result.artifact_contract["readme"] == "QUALITY"
        assert result.publication_state == "READY_FOR_PR"

    def test_both_sources_identical_behavior_for_same_content(self, tmp_path):
        """Core parity test: same dir content produces same downstream result for both sources."""
        lc_dir = make_quality_example(tmp_path / "lc", "slug-x", "family-x")
        nlc_dir = make_quality_example(tmp_path / "nlc", "slug-x", "family-x")

        lc = PluginCandidate("slug-x", "family-x", "LOWCODE", "namespace_scan", lc_dir)
        nlc = PluginCandidate("slug-x", "family-x", "NON_LOWCODE_PLUGIN", "capability_registry_fallback", nlc_dir)

        executor = SharedDownstreamExecutor()
        lc_result = executor.execute(lc)
        nlc_result = executor.execute(nlc)

        # Both pass/fail identically based on artifact content
        assert lc_result.ok == nlc_result.ok
        assert lc_result.artifact_contract["manifest"] == nlc_result.artifact_contract["manifest"]
        assert lc_result.artifact_contract["expected_output"] == nlc_result.artifact_contract["expected_output"]
        assert lc_result.artifact_contract["readme"] == nlc_result.artifact_contract["readme"]
        assert lc_result.publication_state == nlc_result.publication_state

    def test_missing_manifest_fails(self, tmp_path):
        d = tmp_path / "slug"
        d.mkdir()
        (d / "expected-output.json").write_text("{}", encoding="utf-8")
        (d / "README.md").write_text("# t\n## Purpose\nX\n## Prerequisites\n.NET\n## Expected Output\nY\n", encoding="utf-8")
        candidate = PluginCandidate("slug", "fam", "LOWCODE", "namespace_scan", d)
        result = SharedDownstreamExecutor().execute(candidate)
        assert not result.ok
        assert result.artifact_contract["manifest"] == "MISSING"
        assert result.publication_state == "NEEDS_REPAIR"

    def test_missing_expected_output_fails(self, tmp_path):
        d = tmp_path / "slug"
        d.mkdir()
        (d / "example.manifest.json").write_text("{}", encoding="utf-8")
        (d / "README.md").write_text("# t\n## Purpose\nX\n## Prerequisites\n.NET\n## Expected Output\nY\n", encoding="utf-8")
        candidate = PluginCandidate("slug", "fam", "NON_LOWCODE_PLUGIN", "capability_registry_fallback", d)
        result = SharedDownstreamExecutor().execute(candidate)
        assert not result.ok
        assert result.artifact_contract["expected_output"] == "MISSING"

    def test_minimal_readme_fails_in_strict_mode(self, tmp_path):
        d = make_minimal_example(tmp_path, "slug")
        candidate = PluginCandidate("slug", "fam", "LOWCODE", "namespace_scan", d)
        result = SharedDownstreamExecutor(strict=True).execute(candidate)
        assert not result.ok
        assert result.artifact_contract["readme"] == "MINIMAL"

    def test_no_example_dir_strict_fails(self):
        candidate = PluginCandidate("slug", "fam", "LOWCODE", "namespace_scan", None)
        result = SharedDownstreamExecutor(strict=True).execute(candidate)
        assert not result.ok

    def test_no_example_dir_nonstrict_passes_contract_as_not_provided(self):
        candidate = PluginCandidate("slug", "fam", "LOWCODE", "namespace_scan", None)
        result = SharedDownstreamExecutor(strict=False).execute(candidate)
        assert result.artifact_contract.get("example_dir") == "NOT_PROVIDED"

    def test_pr_packet_lowcode_uses_lowcode_prefix(self, tmp_path):
        d = make_quality_example(tmp_path, "my-slug", "words")
        candidate = PluginCandidate("my-slug", "words", "LOWCODE", "namespace_scan", d)
        result = SharedDownstreamExecutor().execute(candidate)
        assert result.pr_packet["branch_prefix"] == "lowcode-examples"
        assert result.pr_packet["pr_title_prefix"] == "feat(lowcode):"

    def test_pr_packet_nonlowcode_uses_plugins_prefix(self, tmp_path):
        d = make_quality_example(tmp_path, "my-slug", "barcode")
        candidate = PluginCandidate("my-slug", "barcode", "NON_LOWCODE_PLUGIN", "capability_registry_fallback", d)
        result = SharedDownstreamExecutor().execute(candidate)
        assert result.pr_packet["branch_prefix"] == "plugins"
        assert result.pr_packet["pr_title_prefix"] == "feat(plugins):"


# ---------------------------------------------------------------------------
# Batch execution
# ---------------------------------------------------------------------------


class TestBatchExecution:
    def test_batch_mixed_sources(self, tmp_path):
        lc_dir = make_quality_example(tmp_path / "lc", "words-slug", "words")
        nlc_dir = make_quality_example(tmp_path / "nlc", "barcode-slug", "barcode")

        candidates = [
            PluginCandidate("words-slug", "words", "LOWCODE", "namespace_scan", lc_dir),
            PluginCandidate("barcode-slug", "barcode", "NON_LOWCODE_PLUGIN", "capability_registry_fallback", nlc_dir),
        ]
        batch = SharedDownstreamExecutor().execute_batch(candidates)
        assert batch.candidates == 2
        assert batch.passed == 2
        assert batch.failed == 0

    def test_batch_counts_failures(self, tmp_path):
        good = make_quality_example(tmp_path / "good", "good-slug", "fam")
        bad = tmp_path / "bad"
        bad.mkdir()  # empty dir — missing all artifacts

        candidates = [
            PluginCandidate("good-slug", "fam", "LOWCODE", "namespace_scan", good),
            PluginCandidate("bad-slug", "fam", "NON_LOWCODE_PLUGIN", "capability_registry_fallback", bad),
        ]
        batch = SharedDownstreamExecutor().execute_batch(candidates)
        assert batch.passed == 1
        assert batch.failed == 1


# ---------------------------------------------------------------------------
# Discovery adapters
# ---------------------------------------------------------------------------


class TestDiscoveryAdapters:
    def test_lowcode_discovery_returns_lowcode_source(self, tmp_path):
        d = make_quality_example(tmp_path, "convert-words", "words")
        candidates = discover_lowcode_candidates(["convert"], "words", [d])
        assert len(candidates) == 1
        assert candidates[0].namespace_source == "LOWCODE"
        assert candidates[0].discovery_method == "namespace_scan"

    def test_lowcode_discovery_empty_patterns_matches_all(self, tmp_path):
        d1 = make_quality_example(tmp_path / "a", "slug-a", "words")
        d2 = make_quality_example(tmp_path / "b", "slug-b", "words")
        candidates = discover_lowcode_candidates([], "words", [d1, d2])
        assert len(candidates) == 2

    def test_nonlowcode_discovery_returns_nonlowcode_source(self, tmp_path):
        d = make_quality_example(tmp_path, "1d-barcode-reader", "barcode")
        entries = [{"slug": "1d-barcode-reader"}]
        candidates = discover_nonlowcode_candidates(entries, "barcode", [d])
        assert len(candidates) == 1
        assert candidates[0].namespace_source == "NON_LOWCODE_PLUGIN"
        assert candidates[0].discovery_method == "capability_registry_fallback"

    def test_nonlowcode_discovery_no_dir_match_still_returns_candidate(self):
        entries = [{"slug": "no-dir-slug"}]
        candidates = discover_nonlowcode_candidates(entries, "barcode", [])
        assert len(candidates) == 1
        assert candidates[0].example_dir is None

    def test_both_adapters_feed_same_executor(self, tmp_path):
        """Proves both discovery paths produce candidates consumable by shared executor."""
        lc_d = make_quality_example(tmp_path / "lc", "lc-slug", "words")
        nlc_d = make_quality_example(tmp_path / "nlc", "nlc-slug", "barcode")

        lc_candidates = discover_lowcode_candidates([], "words", [lc_d])
        nlc_candidates = discover_nonlowcode_candidates([{"slug": "nlc-slug"}], "barcode", [nlc_d])

        executor = SharedDownstreamExecutor()
        all_candidates = lc_candidates + nlc_candidates
        batch = executor.execute_batch(all_candidates)
        assert batch.passed == 2
        assert batch.failed == 0
