"""JSON serialization for format capability manifests."""

from __future__ import annotations

import json
from dataclasses import asdict

from plugin_examples.format_capability.manifest import (
    FormatCapabilityManifest,
    TypeFormatCapability,
)


def serialize_manifest(manifest: FormatCapabilityManifest) -> str:
    """Serialize a FormatCapabilityManifest to JSON string."""
    data = asdict(manifest)
    return json.dumps(data, indent=2, sort_keys=False)


def deserialize_manifest(json_str: str) -> FormatCapabilityManifest:
    """Deserialize a FormatCapabilityManifest from JSON string."""
    data = json.loads(json_str)
    types = {}
    for type_name, type_data in data.get("types", {}).items():
        types[type_name] = TypeFormatCapability(**type_data)
    return FormatCapabilityManifest(
        family=data["family"],
        generation_date=data.get("generation_date", ""),
        types=types,
    )
