"""Fixture factory: programmatic test fixture generation for dry-run packages."""
from .generators import (
    generate_barcode_png,
    generate_minimal_png,
    generate_bmp_fixture,
    generate_svg_fixture,
    generate_html_fixture,
    generate_zip_fixture,
    FixtureResult,
)
from .validators import (
    validate_output_file,
    validate_package_outputs,
    OutputValidationResult,
    PackageValidationResult,
)

__all__ = [
    "generate_barcode_png",
    "generate_minimal_png",
    "generate_bmp_fixture",
    "generate_svg_fixture",
    "generate_html_fixture",
    "generate_zip_fixture",
    "FixtureResult",
    "validate_output_file",
    "validate_package_outputs",
    "OutputValidationResult",
    "PackageValidationResult",
]
