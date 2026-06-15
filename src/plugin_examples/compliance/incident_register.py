"""Incident register — structured incident tracking with schema validation.

Provides a typed IncidentEntry model and validation against a JSON Schema
so that post-incident records are machine-readable and auditable. The
doctor health check integration ensures incident register integrity is
continuously verified.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

INCIDENT_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["id", "severity", "timestamp", "title", "root_cause", "resolution"],
    "properties": {
        "id": {"type": "string", "pattern": "^INC-[0-9]+$"},
        "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
        "timestamp": {"type": "string"},
        "title": {"type": "string", "minLength": 1},
        "root_cause": {"type": "string", "minLength": 1},
        "resolution": {"type": "string", "minLength": 1},
        "duration_minutes": {"type": "integer", "minimum": 0},
        "affected_families": {"type": "array", "items": {"type": "string"}},
        "regression_test_added": {"type": "boolean"},
        "post_mortem_url": {"type": "string"},
    },
    "additionalProperties": False,
}


@dataclass
class IncidentEntry:
    """A single incident register entry."""

    id: str
    severity: str
    timestamp: str
    title: str
    root_cause: str
    resolution: str
    duration_minutes: int = 0
    affected_families: list[str] = field(default_factory=list)
    regression_test_added: bool = False
    post_mortem_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_incident_entry(entry: dict[str, Any]) -> list[str]:
    """Validate an incident entry dict against the schema. Returns list of errors."""
    import jsonschema

    validator = jsonschema.Draft202012Validator(INCIDENT_SCHEMA)
    return [e.message for e in validator.iter_errors(entry)]


def validate_incident_register(register_path: Path) -> tuple[int, int, list[str]]:
    """Validate all entries in an incident register JSON file.

    Returns (total_entries, valid_entries, error_messages).
    """
    if not register_path.exists():
        return 0, 0, ["Incident register file not found"]

    try:
        data = json.loads(register_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return 0, 0, [f"Failed to read register: {exc}"]

    entries = data if isinstance(data, list) else data.get("incidents", [])
    total = len(entries)
    errors: list[str] = []
    valid = 0

    for i, entry in enumerate(entries):
        entry_errors = validate_incident_entry(entry)
        if entry_errors:
            errors.extend(f"Entry {i}: {e}" for e in entry_errors)
        else:
            valid += 1

    return total, valid, errors
