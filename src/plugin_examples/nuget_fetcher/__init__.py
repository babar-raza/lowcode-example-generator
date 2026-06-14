"""NuGet package fetching, caching, and dependency resolution."""

from plugin_examples.nuget_fetcher.dependency_resolver import resolve_dependencies
from plugin_examples.nuget_fetcher.fetcher import fetch_package

__all__ = ["fetch_package", "resolve_dependencies"]
