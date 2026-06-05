"""Registry-driven example factory — generates dry-run packages from registry entries."""
from .generator import ExamplePackageGenerator
from .templates import FamilyTemplateRegistry

__all__ = ["ExamplePackageGenerator", "FamilyTemplateRegistry"]
