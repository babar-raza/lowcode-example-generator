"""Tests for API delta auto-steering — removed symbols added as CANDIDATE only.

Wave 25 Lane D: auto-promote is explicitly forbidden.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.api_delta.delta_engine import (
    DeltaResult,
    TypeDelta,
    apply_auto_steering_candidates,
)


def _make_delta(removed_type_names: list[str], family: str = "barcode") -> DeltaResult:
    delta = DeltaResult(initial_run=False, old_version="25.0.0", new_version="26.0.0")
    for name in removed_type_names:
        delta.removed_types.append(TypeDelta(
            full_name=name, namespace="Aspose.BarCode", change_type="removed",
        ))
    return delta


# ── Candidates are added ──────────────────────────────────────────────────────

def test_removed_type_added_as_candidate():
    delta = _make_delta(["Aspose.BarCode.OldClass"])
    result = apply_auto_steering_candidates(delta, "barcode")
    forbidden = result.get("forbidden_symbols", [])
    assert len(forbidden) == 1
    entry = forbidden[0]
    assert entry["symbol"] == "Aspose.BarCode.OldClass"
    assert entry["status"] == "CANDIDATE"


def test_multiple_removed_types_all_become_candidates():
    delta = _make_delta(["TypeA", "TypeB", "TypeC"])
    result = apply_auto_steering_candidates(delta, "barcode")
    symbols = {e["symbol"] for e in result["forbidden_symbols"]}
    assert {"TypeA", "TypeB", "TypeC"}.issubset(symbols)
    for e in result["forbidden_symbols"]:
        assert e["status"] == "CANDIDATE"


# ── Status is never auto-promoted to CONFIRMED ───────────────────────────────

def test_candidates_never_auto_confirmed():
    delta = _make_delta(["TypeA", "TypeB"])
    result = apply_auto_steering_candidates(delta, "barcode")
    for entry in result["forbidden_symbols"]:
        assert entry["status"] != "CONFIRMED", (
            f"Auto-promotion forbidden: {entry['symbol']} has status CONFIRMED"
        )


def test_existing_confirmed_entries_not_mutated():
    """CONFIRMED entries in existing steering must not be changed by auto-learn."""
    existing = {
        "forbidden_symbols": [
            {"symbol": "SomeType", "status": "CONFIRMED", "reason": "manually confirmed", "occurrence_count": 5},
        ]
    }
    delta = _make_delta(["NewRemovedType"])
    result = apply_auto_steering_candidates(delta, "barcode", existing_steering=existing)

    confirmed_entries = [e for e in result["forbidden_symbols"] if e["symbol"] == "SomeType"]
    assert len(confirmed_entries) == 1
    assert confirmed_entries[0]["status"] == "CONFIRMED"
    assert confirmed_entries[0]["reason"] == "manually confirmed"


# ── Deduplication ─────────────────────────────────────────────────────────────

def test_existing_candidate_not_duplicated():
    existing = {
        "forbidden_symbols": [
            {"symbol": "DuplicateType", "status": "CANDIDATE", "occurrence_count": 2},
        ]
    }
    delta = _make_delta(["DuplicateType"])
    result = apply_auto_steering_candidates(delta, "barcode", existing_steering=existing)

    entries = [e for e in result["forbidden_symbols"] if e["symbol"] == "DuplicateType"]
    assert len(entries) == 1  # not duplicated


def test_existing_candidate_occurrence_count_incremented():
    existing = {
        "forbidden_symbols": [
            {"symbol": "DuplicateType", "status": "CANDIDATE", "occurrence_count": 2},
        ]
    }
    delta = _make_delta(["DuplicateType"])
    result = apply_auto_steering_candidates(delta, "barcode", existing_steering=existing)

    entry = next(e for e in result["forbidden_symbols"] if e["symbol"] == "DuplicateType")
    assert entry["occurrence_count"] == 3


# ── No removed types → no changes ────────────────────────────────────────────

def test_no_removed_types_leaves_steering_unchanged():
    existing = {"forbidden_symbols": [{"symbol": "X", "status": "CONFIRMED"}]}
    delta = DeltaResult(initial_run=False, old_version="1.0", new_version="2.0")
    result = apply_auto_steering_candidates(delta, "barcode", existing_steering=existing)
    assert result["forbidden_symbols"] == existing["forbidden_symbols"]


# ── Output file written when path provided ────────────────────────────────────

def test_output_file_written(tmp_path):
    delta = _make_delta(["TypeToRemove"])
    out = tmp_path / "auto-steering-update.json"
    apply_auto_steering_candidates(delta, "barcode", output_path=out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["added_candidates"] == 1
    assert data["policy"] == "CANDIDATE status only — never auto-promoted to CONFIRMED"
    assert data["candidates"][0]["status"] == "CANDIDATE"


# ── Source field ──────────────────────────────────────────────────────────────

def test_candidate_source_is_auto_delta():
    delta = _make_delta(["Aspose.BarCode.SomeType"])
    result = apply_auto_steering_candidates(delta, "barcode")
    entry = result["forbidden_symbols"][0]
    assert entry["source"] == "auto_delta"
