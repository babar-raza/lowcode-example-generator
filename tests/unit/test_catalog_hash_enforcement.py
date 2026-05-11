"""Tests for catalog hash enforcement (B-013)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.scenario_planner.planner import (
    CatalogHashMismatchError,
    CatalogHashResult,
    compute_catalog_hash,
    validate_catalog_hash,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SAMPLE_CATALOG = {
    "namespaces": [
        {
            "namespace": "Aspose.Cells.LowCode",
            "types": [
                {"full_name": "Aspose.Cells.LowCode.Converter", "name": "Converter", "methods": []},
            ],
        }
    ]
}


def _write_denominator(tmp_path: Path, family: str, sha256: str) -> Path:
    """Write a minimal denominator file."""
    denom_dir = tmp_path / "pipeline" / "configs" / "denominators"
    denom_dir.mkdir(parents=True, exist_ok=True)
    denom = {"family": family, "api_catalog_sha256": sha256}
    path = denom_dir / f"{family}.json"
    path.write_text(json.dumps(denom), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------


class TestCatalogHashComputation:

    def test_hash_is_deterministic(self):
        h1 = compute_catalog_hash(SAMPLE_CATALOG)
        h2 = compute_catalog_hash(SAMPLE_CATALOG)
        assert h1 == h2

    def test_hash_is_hex_string_64_chars(self):
        h = compute_catalog_hash(SAMPLE_CATALOG)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_hash_differs_on_catalog_change(self):
        modified = {**SAMPLE_CATALOG, "extra_key": "extra_value"}
        h1 = compute_catalog_hash(SAMPLE_CATALOG)
        h2 = compute_catalog_hash(modified)
        assert h1 != h2

    def test_hash_ignores_key_order(self):
        ordered = {"a": 1, "b": 2}
        reversed_order = {"b": 2, "a": 1}
        assert compute_catalog_hash(ordered) == compute_catalog_hash(reversed_order)


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------


class TestCatalogHashValidation:

    def test_match_passes(self, tmp_path):
        expected_hash = compute_catalog_hash(SAMPLE_CATALOG)
        _write_denominator(tmp_path, "cells", expected_hash)

        result = validate_catalog_hash("cells", SAMPLE_CATALOG, tmp_path)

        assert result.match is True
        assert result.current_hash == expected_hash
        assert result.denominator_hash == expected_hash

    def test_mismatch_detected(self, tmp_path):
        _write_denominator(tmp_path, "cells", "0000000000000000000000000000000000000000000000000000000000000000")

        result = validate_catalog_hash("cells", SAMPLE_CATALOG, tmp_path)

        assert result.match is False
        assert result.denominator_hash == "0000000000000000000000000000000000000000000000000000000000000000"

    def test_missing_denominator_graceful(self, tmp_path):
        result = validate_catalog_hash("cells", SAMPLE_CATALOG, tmp_path)

        assert result.match is None
        assert result.denominator_hash is None
        assert result.denominator_path is None

    def test_denominator_without_sha256_field(self, tmp_path):
        denom_dir = tmp_path / "pipeline" / "configs" / "denominators"
        denom_dir.mkdir(parents=True, exist_ok=True)
        (denom_dir / "cells.json").write_text(json.dumps({"family": "cells"}))

        result = validate_catalog_hash("cells", SAMPLE_CATALOG, tmp_path)

        assert result.match is None

    def test_strict_mode_raises_on_mismatch(self, tmp_path):
        _write_denominator(tmp_path, "cells", "bad_hash")

        with pytest.raises(CatalogHashMismatchError):
            validate_catalog_hash("cells", SAMPLE_CATALOG, tmp_path, strict=True)

    def test_strict_mode_passes_on_match(self, tmp_path):
        expected_hash = compute_catalog_hash(SAMPLE_CATALOG)
        _write_denominator(tmp_path, "cells", expected_hash)

        result = validate_catalog_hash("cells", SAMPLE_CATALOG, tmp_path, strict=True)
        assert result.match is True

    def test_result_to_dict(self, tmp_path):
        expected_hash = compute_catalog_hash(SAMPLE_CATALOG)
        _write_denominator(tmp_path, "cells", expected_hash)

        result = validate_catalog_hash("cells", SAMPLE_CATALOG, tmp_path)
        d = result.to_dict()

        assert d["family"] == "cells"
        assert d["match"] is True
        assert d["current_hash"] == expected_hash
        assert d["denominator_hash"] == expected_hash
        assert d["denominator_path"] is not None


# ---------------------------------------------------------------------------
# Integration with plan_scenarios
# ---------------------------------------------------------------------------


class TestPlanScenariosWithRepoRoot:

    def test_plan_scenarios_accepts_repo_root(self, tmp_path):
        """plan_scenarios with repo_root does not crash even without denominator."""
        from plugin_examples.scenario_planner.planner import plan_scenarios

        result = plan_scenarios(
            family="cells",
            catalog=SAMPLE_CATALOG,
            plugin_namespaces=["Aspose.Cells.LowCode"],
            repo_root=tmp_path,
        )
        assert result.family == "cells"

    def test_plan_scenarios_without_repo_root_skips_check(self):
        """plan_scenarios without repo_root skips catalog hash check (backward compat)."""
        from plugin_examples.scenario_planner.planner import plan_scenarios

        result = plan_scenarios(
            family="cells",
            catalog=SAMPLE_CATALOG,
            plugin_namespaces=["Aspose.Cells.LowCode"],
        )
        assert result.family == "cells"
