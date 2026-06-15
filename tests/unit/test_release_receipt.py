"""Tests for compliance/release_receipt.py — TC-RH03."""

from __future__ import annotations

from pathlib import Path

from plugin_examples.compliance.release_receipt import (
    ReleaseReceipt,
    save_release_receipt,
)


class TestReleaseReceipt:
    def test_to_dict_contains_all_fields(self):
        receipt = ReleaseReceipt(version="0.31.0", git_sha="abc123")
        d = receipt.to_dict()
        assert d["version"] == "0.31.0"
        assert d["git_sha"] == "abc123"
        assert "doctor_total" in d
        assert "slo_compliant" in d
        assert "coverage_percent" in d

    def test_save_creates_file(self, tmp_path: Path):
        receipt = ReleaseReceipt(version="1.0.0", doctor_total=10, doctor_passed=9)
        path = save_release_receipt(receipt, tmp_path / "receipts")
        assert path.exists()
        assert "1.0.0" in path.name

    def test_save_creates_directory(self, tmp_path: Path):
        out = tmp_path / "nested" / "receipts"
        receipt = ReleaseReceipt(version="2.0.0")
        path = save_release_receipt(receipt, out)
        assert path.exists()
        assert out.exists()

    def test_save_is_valid_json(self, tmp_path: Path):
        import json
        receipt = ReleaseReceipt(version="0.31.0", test_count=4545)
        path = save_release_receipt(receipt, tmp_path)
        data = json.loads(path.read_text())
        assert data["test_count"] == 4545

    def test_default_receipt_values(self):
        receipt = ReleaseReceipt()
        assert receipt.version == ""
        assert receipt.slo_compliant is True
        assert receipt.gate_policy_loaded is False
        assert receipt.extra == {}

    def test_unknown_version_filename(self, tmp_path: Path):
        receipt = ReleaseReceipt()
        path = save_release_receipt(receipt, tmp_path)
        assert "unknown" in path.name
