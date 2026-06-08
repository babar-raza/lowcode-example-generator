"""Tests for plugin-capability-registry schema — TC-IMPL-002A."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

REGISTRY_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "pipeline"
    / "plugin-capability-registry"
    / "schema.json"
)


def _load_schema() -> dict:
    with open(REGISTRY_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _minimal_entry(**overrides) -> dict:
    base = {
        "family": "barcode",
        "package_id": "Aspose.BarCode",
        "type_name": "BarcodeGenerator",
        "namespace": "Aspose.BarCode.Generation",
        "method_name": "Save",
        "status": "WEBSITE_DISCOVERED",
        "confidence_score": 0.0,
    }
    base.update(overrides)
    return base


class TestRegistrySchemaAcceptsValid:
    def test_schema_accepts_website_discovered_entry(self):
        """Schema must accept a minimal WEBSITE_DISCOVERED entry."""
        schema = _load_schema()
        entry = _minimal_entry(status="WEBSITE_DISCOVERED")
        jsonschema.validate(instance=entry, schema=schema)

    def test_schema_accepts_probe_failed_with_taxonomy(self):
        """Schema must accept PROBE_FAILED when failure_taxonomy is present."""
        schema = _load_schema()
        entry = _minimal_entry(
            status="PROBE_FAILED",
            failure_taxonomy="PROBE_FAILED_LICENSE",
        )
        jsonschema.validate(instance=entry, schema=schema)

    def test_schema_accepts_all_twelve_status_values(self):
        """All 12 authoritative status values must be accepted."""
        schema = _load_schema()
        statuses = [
            "WEBSITE_DISCOVERED",
            "REFLECTION_CANDIDATE",
            "AI_DRAFT",
            "PROBE_CANDIDATE",
            "PROBE_CONFIRMED",
            "PROBE_FAILED",
            "VERIFIED_PUBLISHABLE",
            "STATIC_MAPPING_REQUIRED",
            "BLOCKED_PACKAGE_UNAVAILABLE",
            "BLOCKED_REFLECTION_FAILED",
            "BLOCKED_LICENSE_RESTRICTED",
            "REJECTED_BY_VALIDATOR",
        ]
        for status in statuses:
            entry = _minimal_entry(status=status)
            # Supply required fields for special statuses
            if status == "VERIFIED_PUBLISHABLE":
                entry["probe_evidence"] = "reports/prototypes/barcode/output-validation.json"
            if status == "PROBE_FAILED":
                entry["failure_taxonomy"] = "PROBE_FAILED_LICENSE"
            try:
                jsonschema.validate(instance=entry, schema=schema)
            except jsonschema.ValidationError as exc:
                pytest.fail(f"Status '{status}' failed validation: {exc.message}")


class TestRegistrySchemaRejectsInvalid:
    def test_schema_rejects_missing_required_field(self):
        """Schema must reject an entry missing a required field."""
        schema = _load_schema()
        entry = _minimal_entry()
        del entry["type_name"]
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=entry, schema=schema)

    def test_schema_rejects_invalid_status_value(self):
        """Schema must reject an unknown status value."""
        schema = _load_schema()
        entry = _minimal_entry(status="PROBE_UNKNOWN")
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=entry, schema=schema)

    def test_schema_rejects_verified_publishable_without_probe_evidence(self):
        """VERIFIED_PUBLISHABLE without probe_evidence must fail validation."""
        schema = _load_schema()
        entry = _minimal_entry(
            status="VERIFIED_PUBLISHABLE",
            probe_evidence=None,
        )
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=entry, schema=schema)

    def test_schema_rejects_probe_failed_without_taxonomy(self):
        """PROBE_FAILED without failure_taxonomy must fail validation."""
        schema = _load_schema()
        entry = _minimal_entry(
            status="PROBE_FAILED",
            failure_taxonomy=None,
        )
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=entry, schema=schema)

    def test_schema_rejects_confidence_score_above_maximum(self):
        """confidence_score > 1.05 must fail validation."""
        schema = _load_schema()
        entry = _minimal_entry(confidence_score=1.10)
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=entry, schema=schema)
