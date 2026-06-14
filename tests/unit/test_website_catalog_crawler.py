"""Tests for the website catalog crawler — TC-IMPL-003.

All HTTP is mocked. No real network calls.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.website_catalog.crawler import WebsiteCatalog, normalize_url
from plugin_examples.website_catalog.drift_detector import DriftDetector, compute_page_hash
from plugin_examples.website_catalog.models import PluginEntry

# ---------------------------------------------------------------------------
# TC-IMPL-003 Tests
# ---------------------------------------------------------------------------


class TestNormalizeUrl:
    def test_normalize_url_removes_en_locale(self):
        url = "https://products.aspose.net/en/barcode/generate-barcode"
        assert normalize_url(url) == "https://products.aspose.net/barcode/generate-barcode"

    def test_normalize_url_removes_de_locale(self):
        url = "https://products.aspose.net/de/barcode/generate-barcode"
        assert normalize_url(url) == "https://products.aspose.net/barcode/generate-barcode"

    def test_normalize_url_removes_all_locale_patterns(self):
        locales = ["fr", "es", "zh", "ja", "ru", "pt", "it"]
        base = "https://products.aspose.net/{locale}/barcode/generate"
        for locale in locales:
            result = normalize_url(base.format(locale=locale))
            assert f"/{locale}/" not in result, f"Locale /{locale}/ not stripped"


class TestDriftDetection:
    def test_drift_detected_on_hash_change(self):
        detector = DriftDetector()
        old_hash = compute_page_hash("page content v1")
        new_hash = compute_page_hash("page content v2")
        assert detector.detect_drift("https://example.com", new_hash, old_hash) is True

    def test_no_drift_when_hash_unchanged(self):
        detector = DriftDetector()
        content_hash = compute_page_hash("page content v1")
        assert detector.detect_drift("https://example.com", content_hash, content_hash) is False


class TestCachedReplay:
    def test_cached_replay_does_not_make_http_calls(self, tmp_path, monkeypatch):
        """In replay mode, no HTTP calls are made — only the cache is read."""
        family = "barcode"
        url = "https://products.aspose.net/barcode/generate"
        slug = "barcode_generate"

        # Pre-populate cache
        cache_file = tmp_path / family / f"{slug}.html"
        cache_file.parent.mkdir(parents=True)
        cache_file.write_text("<h1>BarCode Generator</h1>", encoding="utf-8")

        # Patch the cache base path
        import plugin_examples.website_catalog.crawler as crawler_mod

        monkeypatch.setattr(crawler_mod, "_CACHE_BASE", tmp_path)

        # Ensure no HTTP calls are made
        with patch("urllib.request.urlopen") as mock_urlopen:
            catalog = WebsiteCatalog(replay=True)
            result = catalog.crawl_family(family, [url])

        mock_urlopen.assert_not_called()
        assert result.from_cache is True
        assert len(result.entries) == 1


class TestMissingPage:
    def test_missing_page_classified_not_raises(self, tmp_path, monkeypatch):
        """A fetch failure returns an entry with empty hash — does not raise."""
        import plugin_examples.website_catalog.crawler as crawler_mod

        monkeypatch.setattr(crawler_mod, "_CACHE_BASE", tmp_path)
        monkeypatch.setattr(crawler_mod, "_DEFAULT_DELAY_MS", 0)

        with patch("plugin_examples.website_catalog.crawler._fetch_url", return_value=None):
            catalog = WebsiteCatalog(replay=False)
            result = catalog.crawl_family("barcode", ["https://products.aspose.net/barcode/missing"])

        # Should not raise; error is recorded
        assert len(result.errors) >= 1 or len(result.entries) >= 1


class TestPluginEntries:
    def test_crawl_family_returns_plugin_entries_with_marketing_only_true(self, tmp_path, monkeypatch):
        """All returned PluginEntry objects must have marketing_only=True."""
        import plugin_examples.website_catalog.crawler as crawler_mod

        monkeypatch.setattr(crawler_mod, "_CACHE_BASE", tmp_path)
        monkeypatch.setattr(crawler_mod, "_DEFAULT_DELAY_MS", 0)

        html_content = "<h1>BarCode Generator</h1><p>Generate barcodes easily.</p>"

        with patch("plugin_examples.website_catalog.crawler._fetch_url", return_value=html_content):
            catalog = WebsiteCatalog(replay=False)
            result = catalog.crawl_family(
                "barcode",
                ["https://products.aspose.net/barcode/generate-barcode"],
            )

        assert len(result.entries) >= 1
        for entry in result.entries:
            assert isinstance(entry, PluginEntry)
            assert entry.marketing_only is True
