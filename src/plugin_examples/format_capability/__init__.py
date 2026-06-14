"""Format capability manifest — single source of truth for type format metadata."""

from plugin_examples.format_capability.classifier import classify_operation_kind
from plugin_examples.format_capability.manifest import (
    FormatCapabilityManifest,
    TypeFormatCapability,
)
from plugin_examples.format_capability.populator import populate_manifest
from plugin_examples.format_capability.serializer import deserialize_manifest, serialize_manifest
from plugin_examples.format_capability.validator import validate_manifest

__all__ = [
    "FormatCapabilityManifest",
    "TypeFormatCapability",
    "classify_operation_kind",
    "populate_manifest",
    "validate_manifest",
    "serialize_manifest",
    "deserialize_manifest",
]
