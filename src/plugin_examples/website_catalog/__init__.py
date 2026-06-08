"""Website catalog module for discovering plugin pages on products.aspose.net.

This module provides discovery only — the catalog is NEVER used as API authority.
All PluginEntry objects carry marketing_only=True.
"""

from plugin_examples.website_catalog.crawler import WebsiteCatalog, normalize_url
from plugin_examples.website_catalog.drift_detector import DriftDetector, compute_page_hash
from plugin_examples.website_catalog.models import CatalogResult, PluginEntry

__all__ = [
    "CatalogResult",
    "DriftDetector",
    "PluginEntry",
    "WebsiteCatalog",
    "compute_page_hash",
    "normalize_url",
]
