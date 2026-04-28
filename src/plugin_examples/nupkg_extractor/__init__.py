"""NuGet package extraction with framework selection and dependency DLL resolution."""

from plugin_examples.nupkg_extractor.extractor import extract_package
from plugin_examples.nupkg_extractor.framework_selector import select_framework

__all__ = ["extract_package", "select_framework"]
