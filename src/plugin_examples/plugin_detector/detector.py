"""Plugin namespace detection against reflected API catalogs."""

from __future__ import annotations

import fnmatch
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class NamespaceMatch:
    """A single matched namespace with counts."""
    namespace: str
    matched_by_pattern: str
    public_type_count: int
    public_method_count: int


@dataclass
class DetectionResult:
    """Result of plugin namespace detection."""
    matched_namespaces: list[NamespaceMatch] = field(default_factory=list)
    unmatched_patterns: list[dict] = field(default_factory=list)
    public_plugin_type_count: int = 0
    public_plugin_method_count: int = 0

    @property
    def is_eligible(self) -> bool:
        return len(self.matched_namespaces) > 0


def detect_plugin_namespaces(
    catalog: dict,
    namespace_patterns: list[str],
) -> DetectionResult:
    """Detect plugin namespaces in an API catalog.

    Args:
        catalog: Parsed API catalog dict (from DllReflector output).
        namespace_patterns: List of namespace patterns from family config.
            Supports exact match ("Aspose.Cells.LowCode") and glob suffix
            ("Aspose.Cells.LowCode.*").

    Returns:
        DetectionResult with matched namespaces, counts, and unmatched patterns.
    """
    catalog_namespaces = {
        ns["namespace"]: ns for ns in catalog.get("namespaces", [])
    }

    result = DetectionResult()
    matched_ns_names: set[str] = set()

    for pattern in namespace_patterns:
        pattern_matched = False
        for ns_name, ns_data in catalog_namespaces.items():
            if _matches_pattern(ns_name, pattern) and ns_name not in matched_ns_names:
                type_count = len(ns_data.get("types", []))
                method_count = _count_methods(ns_data)
                result.matched_namespaces.append(
                    NamespaceMatch(
                        namespace=ns_name,
                        matched_by_pattern=pattern,
                        public_type_count=type_count,
                        public_method_count=method_count,
                    )
                )
                matched_ns_names.add(ns_name)
                result.public_plugin_type_count += type_count
                result.public_plugin_method_count += method_count
                pattern_matched = True

        if not pattern_matched:
            result.unmatched_patterns.append({
                "pattern": pattern,
                "reason": f"No namespace in catalog matches pattern '{pattern}'",
            })

    logger.info(
        "Plugin detection: %d matched namespaces, %d unmatched patterns, "
        "%d plugin types, %d plugin methods",
        len(result.matched_namespaces),
        len(result.unmatched_patterns),
        result.public_plugin_type_count,
        result.public_plugin_method_count,
    )

    return result


def _matches_pattern(namespace: str, pattern: str) -> bool:
    """Check if a namespace matches a pattern.

    Supports:
        - Exact match: "Aspose.Cells.LowCode" matches "Aspose.Cells.LowCode"
        - Glob suffix: "Aspose.Cells.LowCode.*" matches "Aspose.Cells.LowCode.Foo"
    """
    if "*" in pattern or "?" in pattern:
        return fnmatch.fnmatch(namespace, pattern)
    return namespace == pattern


def _count_methods(ns_data: dict) -> int:
    """Count public methods across all types in a namespace."""
    count = 0
    for type_info in ns_data.get("types", []):
        count += len(type_info.get("methods", []))
    return count
