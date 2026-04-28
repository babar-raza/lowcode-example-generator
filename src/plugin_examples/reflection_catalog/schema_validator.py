"""Validate API catalogs against the api-catalog JSON schema."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path

import jsonschema

logger = logging.getLogger(__name__)

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3]
    / "pipeline"
    / "schemas"
    / "api-catalog.schema.json"
)


@lru_cache(maxsize=1)
def _load_schema(schema_path: Path | None = None) -> dict:
    """Load and cache the api-catalog JSON schema."""
    path = schema_path or _SCHEMA_PATH
    with open(path) as f:
        return json.load(f)


def validate_catalog(
    catalog: dict,
    *,
    schema_path: Path | None = None,
) -> list[str]:
    """Validate a catalog dict against the api-catalog schema.

    Args:
        catalog: The catalog dict to validate.
        schema_path: Override path to the schema file.

    Returns:
        List of validation error messages. Empty list means valid.
    """
    schema = _load_schema(schema_path)

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(catalog), key=lambda e: list(e.path))

    error_messages = []
    for error in errors:
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        error_messages.append(f"{path}: {error.message}")

    if error_messages:
        logger.warning(
            "Catalog validation: %d error(s) found", len(error_messages)
        )
    else:
        logger.info("Catalog validation: passed")

    return error_messages
