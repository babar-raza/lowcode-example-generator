"""Data models for the website catalog module."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PluginEntry:
    """A plugin product page entry discovered from products.aspose.net."""

    family: str
    plugin_name: str
    url: str
    slug: str
    page_hash: str = ""
    marketing_only: bool = True  # Always True — catalog is discovery only, not API authority

    # Extended fields — populated by catalog_discover CLI; optional for basic crawler
    family_slug: str = ""
    plugin_slug: str = ""
    canonical_url: str = ""
    marketing_title: str = ""
    description: str = ""
    action_verbs: list = field(default_factory=list)
    input_formats: list = field(default_factory=list)
    output_formats: list = field(default_factory=list)
    nuget_hints: list = field(default_factory=list)
    content_hash: str = ""
    extraction_timestamp: str = ""


@dataclass
class CatalogResult:
    """Result of crawling a family's plugin pages."""

    family: str
    entries: list[PluginEntry] = field(default_factory=list)
    from_cache: bool = False
    errors: list[str] = field(default_factory=list)
