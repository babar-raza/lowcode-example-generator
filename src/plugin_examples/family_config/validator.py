"""Schema validation for family config YAML files."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "pipeline"
    / "schemas"
    / "family-config.schema.json"
)

_schema_cache: dict | None = None


def _load_schema() -> dict:
    global _schema_cache
    if _schema_cache is None:
        with open(_SCHEMA_PATH) as f:
            _schema_cache = json.load(f)
    return _schema_cache


def validate_family_config(data: dict) -> None:
    """Validate a raw dict against the family-config JSON schema.

    Raises jsonschema.ValidationError on failure.
    """
    schema = _load_schema()
    jsonschema.validate(instance=data, schema=schema)
