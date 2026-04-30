"""Minimal fixture file factory for generated examples.

Creates valid input files for Aspose plugin examples. Format generators
are adapted from example-reviewer's test_data_generator.py (stdlib only).
"""

from __future__ import annotations

import json as _json
import logging
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class GeneratedFixture:
    """Record of a generated fixture file."""
    path: str
    format: str
    created_by: str
    validity_check: str
    size_bytes: int
    ready: bool


# ---------------------------------------------------------------------------
# Format generators (adapted from example-reviewer test_data_generator.py)
# ---------------------------------------------------------------------------

def generate_xlsx(dest: Path) -> bool:
    """Generate a minimal valid .xlsx file (OOXML via stdlib zipfile)."""
    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/sharedStrings.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Data" sheetId="1" r:id="rId1"/></sheets>'
        '</workbook>'
    )
    xl_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
        'Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" '
        'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" '
        'Target="sharedStrings.xml"/>'
        '</Relationships>'
    )
    shared_strings = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="5" uniqueCount="5">'
        '<si><t>Name</t></si>'
        '<si><t>Value</t></si>'
        '<si><t>Aspose</t></si>'
        '<si><t>LowCode</t></si>'
        '<si><t>Fixture</t></si>'
        '</sst>'
    )
    sheet1 = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<sheetData>'
        '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c></row>'
        '<row r="2"><c r="A2" t="s"><v>2</v></c><c r="B2"><v>10</v></c></row>'
        '<row r="3"><c r="A3" t="s"><v>3</v></c><c r="B3"><v>20</v></c></row>'
        '<row r="4"><c r="A4" t="s"><v>4</v></c><c r="B4"><v>30</v></c></row>'
        '</sheetData>'
        '</worksheet>'
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_STORED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', rels)
        zf.writestr('xl/workbook.xml', workbook)
        zf.writestr('xl/_rels/workbook.xml.rels', xl_rels)
        zf.writestr('xl/sharedStrings.xml', shared_strings)
        zf.writestr('xl/worksheets/sheet1.xml', sheet1)
    return True


def generate_csv(dest: Path) -> bool:
    """Generate a minimal CSV file with deterministic known values."""
    content = "Name,Value,Category\nAspose,10,LowCode\nFixture,20,Data\nSample,30,Test\n"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return True


def generate_txt(dest: Path) -> bool:
    """Generate a text file with deterministic known values."""
    content = (
        "Name\tValue\tCategory\n"
        "Aspose\t10\tLowCode\n"
        "Fixture\t20\tData\n"
        "Sample\t30\tTest\n"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return True


def generate_json(dest: Path) -> bool:
    """Generate a minimal JSON file with deterministic known values."""
    data = [
        {"Name": "Aspose", "Value": 10, "Category": "LowCode"},
        {"Name": "Fixture", "Value": 20, "Category": "Data"},
        {"Name": "Sample", "Value": 30, "Category": "Test"},
    ]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_json.dumps(data, indent=2), encoding="utf-8")
    return True


def generate_html(dest: Path) -> bool:
    """Generate a minimal valid HTML file with deterministic known values."""
    content = (
        "<!DOCTYPE html>\n<html>\n<head><title>Aspose LowCode Fixture</title></head>\n"
        "<body>\n<h1>Aspose LowCode Fixture</h1>\n"
        "<table><tr><th>Name</th><th>Value</th><th>Category</th></tr>"
        "<tr><td>Aspose</td><td>10</td><td>LowCode</td></tr>"
        "<tr><td>Fixture</td><td>20</td><td>Data</td></tr>"
        "<tr><td>Sample</td><td>30</td><td>Test</td></tr></table>\n"
        "</body>\n</html>\n"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Dispatch table and public API
# ---------------------------------------------------------------------------

_FORMAT_GENERATORS: dict[str, callable] = {
    ".xlsx": generate_xlsx,
    ".csv": generate_csv,
    ".txt": generate_txt,
    ".json": generate_json,
    ".html": generate_html,
    ".htm": generate_html,
}

SUPPORTED_FORMATS = frozenset(_FORMAT_GENERATORS.keys())


def generate_fixture(
    filename: str,
    dest_dir: Path,
) -> GeneratedFixture | None:
    """Generate a fixture file for the given filename.

    Args:
        filename: Target filename (e.g., 'input.xlsx').
        dest_dir: Directory to write the file into.

    Returns:
        GeneratedFixture if successful, None if format not supported.
    """
    ext = Path(filename).suffix.lower()
    generator = _FORMAT_GENERATORS.get(ext)
    if generator is None:
        logger.warning("No fixture generator for format: %s", ext)
        return None

    dest = dest_dir / filename
    try:
        success = generator(dest)
    except Exception as e:
        logger.error("Fixture generation failed for %s: %s", filename, e)
        return None

    if not success or not dest.exists():
        return None

    size = dest.stat().st_size
    return GeneratedFixture(
        path=str(dest),
        format=ext,
        created_by="fixture_factory",
        validity_check=f"file_exists_and_size_{size}",
        size_bytes=size,
        ready=True,
    )


def generate_fixtures_for_scenario(
    input_files: list[str],
    dest_dir: Path,
) -> list[GeneratedFixture]:
    """Generate all fixture files needed for a scenario.

    Args:
        input_files: List of filenames to generate.
        dest_dir: Project directory to write files into.

    Returns:
        List of GeneratedFixture records.
    """
    results = []
    for filename in input_files:
        fixture = generate_fixture(filename, dest_dir)
        if fixture:
            results.append(fixture)
            logger.info("Generated fixture: %s (%d bytes)", filename, fixture.size_bytes)
        else:
            logger.warning("Could not generate fixture: %s", filename)
    return results


def write_generated_fixtures_evidence(
    fixtures: list[GeneratedFixture],
    evidence_dir: Path,
) -> Path:
    """Write generated-fixtures.json evidence."""
    out = evidence_dir / "latest" / "generated-fixtures.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "total_generated": len(fixtures),
        "total_ready": sum(1 for f in fixtures if f.ready),
        "fixtures": [
            {
                "path": f.path,
                "format": f.format,
                "created_by": f.created_by,
                "validity_check": f.validity_check,
                "size_bytes": f.size_bytes,
                "ready": f.ready,
            }
            for f in fixtures
        ],
    }
    out.write_text(_json.dumps(data, indent=2))
    return out
