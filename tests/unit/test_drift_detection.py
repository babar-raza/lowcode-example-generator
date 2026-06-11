"""Tests for catalog-level drift detection — Wave 25 Lane C."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.website_catalog.drift_detector import (
    DriftReport,
    compute_page_hash,
    detect_catalog_drift,
    is_discovery_stale,
    make_discovery_metadata,
)


# ── detect_catalog_drift ───────────────────────────────────────────────────────


def test_no_prior_evidence_all_added(tmp_path):
    current = [
        {"url": "https://example.com/plugin/a", "page_hash": "aaa"},
        {"url": "https://example.com/plugin/b", "page_hash": "bbb"},
    ]
    report = detect_catalog_drift(None, current)
    assert set(report.added) == {"https://example.com/plugin/a", "https://example.com/plugin/b"}
    assert report.removed == []
    assert report.changed == []
    assert report.has_drift is True
    assert report.compared_against == "NONE"


def test_empty_current_all_removed(tmp_path):
    prior_path = tmp_path / "prior.json"
    prior_data = {
        "discovery_metadata": {"run_id": "run-prior-001"},
        "plugins": [
            {"url": "https://example.com/plugin/a", "page_hash": "aaa"},
        ],
    }
    prior_path.write_text(json.dumps(prior_data), encoding="utf-8")
    report = detect_catalog_drift(prior_path, [])
    assert report.removed == ["https://example.com/plugin/a"]
    assert report.added == []
    assert report.has_drift is True
    assert report.compared_against == "run-prior-001"


def test_hash_change_detected(tmp_path):
    prior_path = tmp_path / "prior.json"
    prior_data = {
        "discovery_metadata": {"run_id": "run-prior-002"},
        "plugins": [
            {"url": "https://example.com/plugin/a", "page_hash": "old-hash"},
        ],
    }
    prior_path.write_text(json.dumps(prior_data), encoding="utf-8")
    current = [{"url": "https://example.com/plugin/a", "page_hash": "new-hash"}]
    report = detect_catalog_drift(prior_path, current)
    assert "https://example.com/plugin/a" in report.changed
    assert report.has_drift is True


def test_unchanged_plugins_identified(tmp_path):
    prior_path = tmp_path / "prior.json"
    prior_data = {
        "discovery_metadata": {"run_id": "run-prior-003"},
        "plugins": [
            {"url": "https://example.com/plugin/a", "page_hash": "same-hash"},
        ],
    }
    prior_path.write_text(json.dumps(prior_data), encoding="utf-8")
    current = [{"url": "https://example.com/plugin/a", "page_hash": "same-hash"}]
    report = detect_catalog_drift(prior_path, current)
    assert "https://example.com/plugin/a" in report.unchanged
    assert report.has_drift is False


def test_mixed_drift_classified_correctly(tmp_path):
    prior_path = tmp_path / "prior.json"
    prior_data = {
        "discovery_metadata": {"run_id": "run-prior-004"},
        "plugins": [
            {"url": "https://example.com/plugin/a", "page_hash": "hash-a"},  # unchanged
            {"url": "https://example.com/plugin/b", "page_hash": "hash-b"},  # changed
            {"url": "https://example.com/plugin/c", "page_hash": "hash-c"},  # removed
        ],
    }
    prior_path.write_text(json.dumps(prior_data), encoding="utf-8")
    current = [
        {"url": "https://example.com/plugin/a", "page_hash": "hash-a"},  # unchanged
        {"url": "https://example.com/plugin/b", "page_hash": "hash-b-new"},  # changed
        {"url": "https://example.com/plugin/d", "page_hash": "hash-d"},  # added
    ]
    report = detect_catalog_drift(prior_path, current)
    assert "https://example.com/plugin/a" in report.unchanged
    assert "https://example.com/plugin/b" in report.changed
    assert "https://example.com/plugin/c" in report.removed
    assert "https://example.com/plugin/d" in report.added
    assert report.has_drift is True


def test_missing_prior_file_treated_as_no_prior(tmp_path):
    prior_path = tmp_path / "nonexistent.json"
    current = [{"url": "https://example.com/plugin/a", "page_hash": "aaa"}]
    report = detect_catalog_drift(prior_path, current)
    assert report.compared_against == "NONE"
    assert "https://example.com/plugin/a" in report.added


def test_drift_report_to_dict_has_required_keys():
    report = DriftReport(
        added=["a"],
        removed=[],
        changed=[],
        unchanged=["b"],
        has_drift=True,
        run_id="run-test",
        compared_against="NONE",
    )
    d = report.to_dict()
    for key in [
        "run_id",
        "generated_at",
        "compared_against",
        "has_drift",
        "added_count",
        "removed_count",
        "changed_count",
        "unchanged_count",
        "added",
        "removed",
        "changed",
        "unchanged",
    ]:
        assert key in d, f"Missing key: {key}"


# ── make_discovery_metadata ────────────────────────────────────────────────────


def test_discovery_metadata_has_required_fields():
    meta = make_discovery_metadata()
    for field in ["validated_at", "run_id", "catalog_version", "ttl_seconds", "expires_at"]:
        assert field in meta, f"Missing field: {field}"


def test_discovery_metadata_expires_after_ttl():
    from datetime import datetime, timezone

    meta = make_discovery_metadata(ttl_seconds=3600)
    validated = datetime.fromisoformat(meta["validated_at"])
    expires = datetime.fromisoformat(meta["expires_at"])
    delta = (expires - validated).total_seconds()
    assert abs(delta - 3600) < 5  # within 5 seconds tolerance


def test_discovery_metadata_not_stale_immediately():
    meta = make_discovery_metadata(ttl_seconds=3600)
    assert is_discovery_stale(meta) is False


def test_discovery_metadata_stale_when_expired():
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    past = (now - timedelta(hours=2)).isoformat(timespec="seconds")
    meta = {
        "validated_at": past,
        "run_id": "old",
        "ttl_seconds": 3600,
        "expires_at": (now - timedelta(hours=1)).isoformat(timespec="seconds"),
    }
    assert is_discovery_stale(meta) is True


def test_discovery_metadata_stale_when_no_expires_at():
    meta = {"validated_at": "2026-01-01T00:00:00+00:00", "run_id": "old"}
    assert is_discovery_stale(meta) is True


# ── backward compat: compute_page_hash ────────────────────────────────────────


def test_compute_page_hash_string_and_bytes_equal():
    content = "hello world"
    assert compute_page_hash(content) == compute_page_hash(content.encode("utf-8"))
