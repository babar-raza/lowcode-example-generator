"""Tests for fixture synthetic fallback logic — Wave 25 Lane B."""
from __future__ import annotations

import pytest

from plugin_examples.fixture_registry.fixture_fetcher import (
    FetchResult,
    FixtureBlockedError,
    _synthetic_fallback,
    fetch_fixtures,
)


def test_synthetic_fallback_strategy_name():
    result = _synthetic_fallback("html")
    assert result.strategy == "synthetic_fallback"


def test_synthetic_fallback_has_empty_fetched():
    result = _synthetic_fallback("html")
    assert result.fetched == []


def test_synthetic_fallback_count_is_one():
    result = _synthetic_fallback("html")
    assert result.synthetic_count == 1


def test_no_owner_triggers_synthetic_fallback(tmp_path):
    result = fetch_fixtures("html", {}, [".html"], tmp_path, cache_root=tmp_path / "c")
    assert result.strategy == "synthetic_fallback"


def test_no_repo_triggers_synthetic_fallback(tmp_path):
    result = fetch_fixtures("html", {"owner": "aspose-html"}, [".html"], tmp_path, cache_root=tmp_path / "c")
    assert result.strategy == "synthetic_fallback"


def test_no_token_with_synthetic_allowed_triggers_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    config = {
        "owner": "aspose-html",
        "repo": "Aspose.HTML-for-.NET",
        "branch": "master",
        "synthetic_fallback_allowed": True,
    }
    result = fetch_fixtures("html", config, [".html"], tmp_path, cache_root=tmp_path / "c")
    assert result.strategy == "synthetic_fallback"


def test_no_token_with_synthetic_not_allowed_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    config = {
        "owner": "aspose-html",
        "repo": "Aspose.HTML-for-.NET",
        "branch": "master",
        "synthetic_fallback_allowed": False,
    }
    with pytest.raises(FixtureBlockedError):
        fetch_fixtures("html", config, [".html"], tmp_path, cache_root=tmp_path / "c")
