"""
Tests for CPV-01..CPV-12 canonical-primary invariant validators.
Sprint: lowcode-plugin-canonical-primary-wave8-20260605
"""

import json
import pytest
from pathlib import Path

from src.plugin_examples.fixture_factory.canonical_primary_validators import (
    run_canonical_primary_validators,
    CpvResult,
    CpvViolation,
)


def _make_pkg(key, verdict="PASS", canon_slug=None, legacy_slug=None, path=None, sprint="test"):
    family, slug = key.split("/", 1) if "/" in key else ("", key)
    return {
        "verdict": verdict,
        "canonical_plugin_slug": canon_slug or slug,
        "legacy_slug": legacy_slug,
        "classification": "PUBLICATION_CANDIDATE_LOCAL_CLEAN",
        "path": path or "",
        "sprint": sprint,
    }


def _make_entry(
    family, slug, canon_slug=None, identity_status="CANONICAL_IDENTITY_VERIFIED", display_name=None, canonical_url=None
):
    return {
        "family": family,
        "plugin_slug": slug,
        "canonical_plugin_slug": canon_slug or slug,
        "identity_status": identity_status,
        "display_plugin_name": display_name or f"{slug} plugin",
        "canonical_url": canonical_url or f"https://products.aspose.net/{family}/{slug}/",
        "legacy_aliases": [],
    }


# --- CPV-01: legacy slug as publication candidate ---


def test_cpv01_pass_canonical_slug_in_candidates():
    packages = {
        "barcode/1d-barcode-writer": _make_pkg("barcode/1d-barcode-writer", canon_slug="1d-barcode-writer"),
    }
    pub = {"canonical_candidates": ["barcode/1d-barcode-writer"]}
    result = run_canonical_primary_validators(packages, publication_matrix=pub)
    assert result.passes
    assert not any(v.rule == "CPV-01" for v in result.violations)


def test_cpv01_fail_generic_slug_in_candidates():
    packages = {
        "barcode/generate-barcode": _make_pkg("barcode/generate-barcode", canon_slug=None, legacy_slug=None),
    }
    pub = {"canonical_candidates": ["barcode/generate-barcode"]}
    result = run_canonical_primary_validators(packages, publication_matrix=pub)
    assert not result.passes
    rules = [v.rule for v in result.violations if v.severity == "ERROR"]
    assert "CPV-01" in rules or "CPV-08" in rules  # both CPV-01 and CPV-08 fire


def test_cpv01_fail_legacy_slug_no_canonical():
    packages = {
        "barcode/old-generator": {
            "verdict": "PASS",
            "canonical_plugin_slug": None,
            "legacy_slug": "old-generator",
            "path": "",
            "sprint": "test",
        }
    }
    pub = {"canonical_candidates": ["barcode/old-generator"]}
    result = run_canonical_primary_validators(packages, publication_matrix=pub)
    assert not result.passes
    assert any(v.rule == "CPV-01" for v in result.violations)


# --- CPV-02: canonical entry must have canonical_plugin_slug ---


def test_cpv02_pass_verified_has_canon_slug():
    entries = [_make_entry("barcode", "1d-barcode-writer")]
    result = run_canonical_primary_validators({}, registry_entries=entries)
    assert not any(v.rule == "CPV-02" for v in result.violations)


def test_cpv02_fail_verified_missing_canon_slug():
    entry = _make_entry("barcode", "1d-barcode-writer")
    entry["canonical_plugin_slug"] = None
    result = run_canonical_primary_validators({}, registry_entries=[entry])
    assert not result.passes
    assert any(v.rule == "CPV-02" for v in result.violations)


# --- CPV-03: canonical entry must have display_plugin_name ---


def test_cpv03_pass_verified_has_display_name():
    entries = [_make_entry("barcode", "1d-barcode-writer", display_name="1D Barcode Writer for .NET")]
    result = run_canonical_primary_validators({}, registry_entries=entries)
    assert not any(v.rule == "CPV-03" for v in result.violations)


def test_cpv03_warn_verified_missing_display_name():
    entry = _make_entry("barcode", "1d-barcode-writer")
    entry["display_plugin_name"] = None
    result = run_canonical_primary_validators({}, registry_entries=[entry])
    assert any(v.rule == "CPV-03" and v.severity == "WARNING" for v in result.violations)


# --- CPV-04: legacy alias must not be in canonical candidates ---


def test_cpv04_pass_no_overlap():
    packages = {}
    pub = {
        "canonical_candidates": ["barcode/1d-barcode-writer"],
        "legacy_aliases": ["barcode/generate-barcode"],
    }
    result = run_canonical_primary_validators(packages, publication_matrix=pub)
    assert not any(v.rule == "CPV-04" for v in result.violations)


def test_cpv04_fail_double_counted():
    packages = {}
    pub = {
        "canonical_candidates": ["barcode/1d-barcode-writer"],
        "legacy_aliases": ["barcode/1d-barcode-writer"],
    }
    result = run_canonical_primary_validators(packages, publication_matrix=pub)
    assert not result.passes
    assert any(v.rule == "CPV-04" for v in result.violations)


# --- CPV-05: dryrun path must use canonical slug ---


def test_cpv05_pass_canonical_slug_no_alias_record():
    packages = {
        "barcode/1d-barcode-writer": _make_pkg("barcode/1d-barcode-writer", canon_slug="1d-barcode-writer"),
    }
    result = run_canonical_primary_validators(packages)
    assert not any(v.rule == "CPV-05" for v in result.violations)


def test_cpv05_fail_generic_slug_no_alias_record():
    packages = {
        "barcode/generate-barcode": {
            "verdict": "PASS",
            "canonical_plugin_slug": None,  # no alias record
            "legacy_slug": None,
            "path": "reports/test/barcode/generate-barcode",
            "sprint": "test",
        }
    }
    result = run_canonical_primary_validators(packages)
    assert not result.passes
    assert any(v.rule == "CPV-05" for v in result.violations)


# --- CPV-08: BarCode generic names must not be in publication candidate list ---


def test_cpv08_pass_no_generic_in_candidates():
    pub = {"canonical_candidates": ["barcode/1d-barcode-writer", "barcode/2d-barcode-reader"]}
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert not any(v.rule == "CPV-08" for v in result.violations)


def test_cpv08_fail_generic_in_candidates():
    pub = {"canonical_candidates": ["barcode/generate-barcode"]}
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert not result.passes
    assert any(v.rule == "CPV-08" for v in result.violations)


# --- CPV-09: identity_review_required must not overlap canonical candidates ---


def test_cpv09_pass_no_overlap():
    pub = {
        "canonical_candidates": ["barcode/1d-barcode-writer"],
        "identity_review_required": ["html/html-converter"],
    }
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert not any(v.rule == "CPV-09" for v in result.violations)


def test_cpv09_fail_contaminated_matrix():
    pub = {
        "canonical_candidates": ["html/html-converter"],
        "identity_review_required": ["html/html-converter"],
    }
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert not result.passes
    assert any(v.rule == "CPV-09" for v in result.violations)


# --- CPV-10: family-level probe detection ---


def test_cpv10_pass_plugin_level_coverage():
    pub = {"canonical_candidates": ["barcode/1d-barcode-writer"]}
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert not any(v.rule == "CPV-10" for v in result.violations)


def test_cpv10_warn_family_slug_equals_family():
    pub = {"canonical_candidates": ["barcode/barcode"]}
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert any(v.rule == "CPV-10" and v.severity == "WARNING" for v in result.violations)


# --- CPV-11: family plugin list required ---


def test_cpv11_pass_family_has_plugin_list():
    entries = [_make_entry("barcode", "1d-barcode-writer")]
    fpl = {"barcode": ["1d-barcode-writer"]}
    result = run_canonical_primary_validators({}, registry_entries=entries, family_plugin_lists=fpl)
    assert not any(v.rule == "CPV-11" for v in result.violations)


def test_cpv11_warn_family_missing_plugin_list():
    entries = [_make_entry("barcode", "1d-barcode-writer")]
    # No family_plugin_lists provided
    result = run_canonical_primary_validators({}, registry_entries=entries)
    assert any(v.rule == "CPV-11" and v.severity == "WARNING" for v in result.violations)


# --- CPV-12: summary counts canonical and legacy separately ---


def test_cpv12_pass_counts_match():
    pub = {
        "total": 3,
        "canonical_candidates": ["a/x"],
        "legacy_aliases": ["a/y"],
        "identity_review_required": ["a/z"],
    }
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert not any(v.rule == "CPV-12" for v in result.violations)


def test_cpv12_warn_counts_mismatch():
    pub = {
        "total": 5,  # declared 5 but buckets only sum to 3
        "canonical_candidates": ["a/x"],
        "legacy_aliases": ["a/y"],
        "identity_review_required": ["a/z"],
    }
    result = run_canonical_primary_validators({}, publication_matrix=pub)
    assert any(v.rule == "CPV-12" and v.severity == "WARNING" for v in result.violations)


# --- CpvResult properties ---


def test_cpv_result_passes_no_violations():
    result = CpvResult()
    assert result.passes
    assert result.error_count == 0
    assert result.warning_count == 0


def test_cpv_result_fails_on_error():
    result = CpvResult()
    result.violations.append(CpvViolation("CPV-01", "ERROR", "test error", "ctx"))
    assert not result.passes
    assert result.error_count == 1


def test_cpv_result_passes_with_warnings_only():
    result = CpvResult()
    result.violations.append(CpvViolation("CPV-03", "WARNING", "missing display name", "ctx"))
    assert result.passes
    assert result.warning_count == 1


def test_cpv_result_to_dict():
    result = CpvResult()
    result.violations.append(CpvViolation("CPV-01", "ERROR", "bad slug", "k1"))
    d = result.to_dict()
    assert d["passes"] is False
    assert d["error_count"] == 1
    assert len(d["violations"]) == 1
    assert d["violations"][0]["rule"] == "CPV-01"
