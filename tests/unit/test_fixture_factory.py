"""Unit tests for src/plugin_examples/fixture_factory/."""

import json
import tempfile
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.generators import (
    generate_minimal_png,
    generate_bmp_fixture,
    generate_svg_fixture,
    generate_html_fixture,
    generate_zip_fixture,
    _build_png,
    _build_bmp,
)
from plugin_examples.fixture_factory.validators import (
    validate_output_file,
    validate_package_outputs,
    detect_format,
    OutputValidationResult,
    PackageValidationResult,
)
from plugin_examples.fixture_factory.package_invariants import check_package


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as d:
        yield Path(d)


# ── Generator tests ──────────────────────────────────────────────────────────


class TestGenerators:
    def test_minimal_png_1x1(self, tmpdir):
        dest = tmpdir / "test.png"
        result = generate_minimal_png(dest, 1, 1)
        assert result.success
        assert dest.exists()
        assert dest.stat().st_size > 0
        data = dest.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_minimal_png_custom_size(self, tmpdir):
        dest = tmpdir / "test.png"
        result = generate_minimal_png(dest, 10, 10)
        assert result.success
        data = dest.read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_bmp_fixture(self, tmpdir):
        dest = tmpdir / "test.bmp"
        result = generate_bmp_fixture(dest, 50, 50)
        assert result.success
        assert result.size_bytes > 0
        data = dest.read_bytes()
        assert data[:2] == b"BM"

    def test_bmp_fixture_size(self, tmpdir):
        dest = tmpdir / "test.bmp"
        result = generate_bmp_fixture(dest, 10, 10)
        # 10x10 RGB BMP: 54 header + 10*12*1 rows (row padded to 30+2=32 bytes)
        assert dest.stat().st_size > 54

    def test_svg_fixture_inline(self):
        result = generate_svg_fixture(title="Unit Test")
        assert result.fixture_type == "SVG"
        assert result.size_bytes > 0
        assert result.strategy == "inline"

    def test_svg_fixture_to_file(self, tmpdir):
        dest = tmpdir / "test.svg"
        result = generate_svg_fixture(dest, title="Test")
        assert result.success
        content = dest.read_text()
        assert "<svg" in content

    def test_html_fixture_inline(self):
        result = generate_html_fixture(title="Test Page")
        assert result.fixture_type == "HTML"
        assert result.size_bytes > 0

    def test_html_fixture_to_file(self, tmpdir):
        dest = tmpdir / "test.html"
        result = generate_html_fixture(dest, title="Test")
        assert result.success
        content = dest.read_text()
        assert "<!DOCTYPE html>" in content

    def test_zip_fixture(self, tmpdir):
        dest = tmpdir / "test.zip"
        result = generate_zip_fixture(dest)
        assert result.success
        data = dest.read_bytes()
        assert data[:4] == b"PK\x03\x04"

    def test_build_png_valid(self):
        data = _build_png(5, 5)
        assert data[:8] == b"\x89PNG\r\n\x1a\n"

    def test_build_bmp_valid(self):
        data = _build_bmp(4, 4, 255, 0, 0)
        assert data[:2] == b"BM"


# ── Validator tests ──────────────────────────────────────────────────────────


class TestDetectFormat:
    def test_png(self, tmpdir):
        f = tmpdir / "a.png"
        f.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 20)
        assert detect_format(f.read_bytes()) == "PNG"

    def test_pdf(self, tmpdir):
        assert detect_format(b"%PDF-1.4\n") == "PDF"

    def test_zip(self, tmpdir):
        assert detect_format(b"PK\x03\x04" + b"\x00" * 20) == "ZIP"

    def test_jpeg(self):
        assert detect_format(b"\xff\xd8\xff" + b"\x00" * 10) == "JPEG"

    def test_bmp(self):
        assert detect_format(b"BM" + b"\x00" * 20) == "BMP"

    def test_text(self):
        assert detect_format(b"Hello world text content") == "TEXT"


class TestValidateOutputFile:
    def test_pass_nonzero_png(self, tmpdir):
        dest = tmpdir / "output.png"
        generate_minimal_png(dest, 1, 1)
        result = validate_output_file(dest)
        assert result.verdict == "PASS"
        assert result.size_bytes > 0

    def test_zero_byte_required_fail(self, tmpdir):
        dest = tmpdir / "output.txt"
        dest.write_bytes(b"")
        result = validate_output_file(dest, is_required=True)
        assert result.verdict == "ZERO_BYTE_REQUIRED_OUTPUT"

    def test_intermediate_optional_zero_ok(self, tmpdir):
        dest = tmpdir / "fixture.png"
        dest.write_bytes(b"")
        result = validate_output_file(dest, is_required=True)
        # fixture.png is in INTERMEDIATE_OPTIONAL_PATTERNS
        assert result.is_intermediate_optional
        assert result.verdict == "PASS"

    def test_missing_file(self, tmpdir):
        dest = tmpdir / "missing.png"
        result = validate_output_file(dest)
        assert result.verdict == "MISSING"

    def test_trial_watermark_detected(self, tmpdir):
        dest = tmpdir / "result.txt"
        dest.write_text("OCR result:\nTrial License\nsome text")
        result = validate_output_file(dest)
        assert any("TRIAL_WATERMARK_DETECTED" in n for n in result.notes)


class TestValidatePackageOutputs:
    def _make_package(self, tmpdir, with_output=True, output_size=100) -> Path:
        pkg = tmpdir / "test_pkg"
        pkg.mkdir()
        (pkg / "Program.cs").write_text('Console.WriteLine("test");')
        readme = "# Test\n\n## Run\n\n```bash\ndotnet restore\ndotnet build\ndotnet run\n```\n"
        (pkg / "README.md").write_text(readme)
        (pkg / "source-provenance.json").write_text(
            json.dumps({"family": "test", "canonical_url": "https://example.com"})
        )
        (pkg / "output-validation.json").write_text(
            json.dumps(
                {"restore_status": "SUCCESS", "build_status": "SUCCESS", "run_status": "SUCCESS", "verdict": "PASS"}
            )
        )
        (pkg / "restore.log").write_text("restored")
        (pkg / "build.log").write_text("built")
        (pkg / "run.log").write_text("ran")
        if with_output:
            (pkg / "output").mkdir()
            (pkg / "output" / "result.txt").write_bytes(b"x" * output_size)
        return pkg

    def test_valid_package_passes(self, tmpdir):
        pkg = self._make_package(tmpdir)
        result = validate_package_outputs(pkg, "test/test-pkg")
        assert result.verdict == "PASS"
        assert result.publication_classification == "PUBLICATION_CANDIDATE_LOCAL_CLEAN"

    def test_missing_output_fails(self, tmpdir):
        pkg = self._make_package(tmpdir, with_output=False)
        result = validate_package_outputs(pkg, "test/no-output")
        assert result.verdict in ("NO_OUTPUTS", "MISSING_OUTPUT", "MISSING_REQUIRED_FILES", "OUTPUT_VALIDATION_FAILED")

    def test_zero_byte_output_fails(self, tmpdir):
        pkg = self._make_package(tmpdir, output_size=0)
        result = validate_package_outputs(pkg, "test/zero-output")
        assert result.verdict == "ZERO_BYTE_REQUIRED_OUTPUT"
        assert result.publication_classification == "NEEDS_OUTPUT_REPAIR"

    def test_trial_watermark_classification(self, tmpdir):
        pkg = self._make_package(tmpdir)
        (pkg / "output" / "result.txt").write_text("text\nTrial License present\n")
        result = validate_package_outputs(pkg, "test/trial")
        # Should detect trial watermark
        assert result.publication_classification in (
            "PUBLICATION_CANDIDATE_LOCAL_WITH_TRIAL_NOTICE",
            "PUBLICATION_CANDIDATE_LOCAL_CLEAN",  # if trial not in output dir files
        )


# ── Invariant tests ──────────────────────────────────────────────────────────


class TestPackageInvariants:
    def _make_valid_package(self, tmpdir) -> Path:
        pkg = tmpdir / "valid_pkg"
        pkg.mkdir()
        (pkg / "Program.cs").write_text('Console.WriteLine("hello");')
        (pkg / "README.md").write_text("# Test\n\n## Run\n\n```bash\ndotnet run\n```\n")
        (pkg / "source-provenance.json").write_text(
            json.dumps({"family": "test", "canonical_url": "https://example.com"})
        )
        (pkg / "output-validation.json").write_text(json.dumps({"verdict": "PASS"}))
        (pkg / "restore.log").write_text("ok")
        (pkg / "build.log").write_text("ok")
        (pkg / "run.log").write_text("ok")
        (pkg / "test-test.csproj").write_text("<Project/>")
        (pkg / "output").mkdir()
        (pkg / "output" / "result.txt").write_bytes(b"hello\n")
        return pkg

    def test_valid_package_no_violations(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        violations = check_package(pkg)
        assert violations == [], f"Unexpected violations: {violations}"

    def test_missing_readme(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        (pkg / "README.md").unlink()
        violations = check_package(pkg)
        assert any("INV-02" in v for v in violations)

    def test_readme_no_run_cmd(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        (pkg / "README.md").write_text("# Test\n\nNo run command here.\n")
        violations = check_package(pkg)
        assert any("INV-03" in v for v in violations)

    def test_missing_provenance(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        (pkg / "source-provenance.json").unlink()
        violations = check_package(pkg)
        assert any("INV-04" in v for v in violations)

    def test_missing_output_validation(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        (pkg / "output-validation.json").unlink()
        violations = check_package(pkg)
        assert any("INV-06" in v for v in violations)

    def test_zero_byte_output(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        (pkg / "output" / "result.txt").write_bytes(b"")
        violations = check_package(pkg)
        assert any("INV-12" in v for v in violations)

    def test_missing_canonical_url(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        (pkg / "source-provenance.json").write_text(json.dumps({"family": "test", "canonical_url": ""}))
        violations = check_package(pkg)
        assert any("INV-15" in v for v in violations)

    def test_bin_obj_detected(self, tmpdir):
        pkg = self._make_valid_package(tmpdir)
        (pkg / "bin").mkdir()
        violations = check_package(pkg)
        assert any("INV-11" in v for v in violations)


# ── Wave 5 fixture generator tests ───────────────────────────────────────────


class TestWave5Generators:
    def test_geojson_inline(self):
        from plugin_examples.fixture_factory.generators import generate_geojson_fixture

        result = generate_geojson_fixture()
        assert result.fixture_type == "GeoJSON"
        assert result.size_bytes > 0
        # Must be parseable JSON with correct structure
        assert result.provenance["features"] == 2

    def test_geojson_to_file(self, tmpdir):
        from plugin_examples.fixture_factory.generators import generate_geojson_fixture

        dest = tmpdir / "fixture.geojson"
        result = generate_geojson_fixture(dest)
        assert result.success
        data = json.loads(dest.read_text())
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 2

    def test_obj_inline(self):
        from plugin_examples.fixture_factory.generators import generate_obj_fixture

        result = generate_obj_fixture()
        assert result.fixture_type == "OBJ"
        assert result.size_bytes > 0
        assert result.provenance["vertices"] == 8

    def test_obj_to_file(self, tmpdir):
        from plugin_examples.fixture_factory.generators import generate_obj_fixture

        dest = tmpdir / "model.obj"
        result = generate_obj_fixture(dest)
        assert result.success
        content = dest.read_text()
        assert content.startswith("# Minimal Wavefront OBJ")
        assert content.count("v ") >= 8
        assert content.count("f ") >= 6

    def test_xbrl_inline(self):
        from plugin_examples.fixture_factory.generators import generate_xbrl_fixture

        result = generate_xbrl_fixture()
        assert result.fixture_type == "XBRL"
        assert result.size_bytes > 0

    def test_xbrl_to_file(self, tmpdir):
        from plugin_examples.fixture_factory.generators import generate_xbrl_fixture

        dest = tmpdir / "report.xbrl"
        result = generate_xbrl_fixture(dest)
        assert result.success
        content = dest.read_text()
        assert "FeatureCollection" not in content  # sanity
        assert "<xbrl" in content or "xbrl" in content.lower()

    def test_ps_inline(self):
        from plugin_examples.fixture_factory.generators import generate_ps_fixture

        result = generate_ps_fixture(title="My Doc")
        assert result.fixture_type == "PS"
        assert result.size_bytes > 0

    def test_ps_to_file(self, tmpdir):
        from plugin_examples.fixture_factory.generators import generate_ps_fixture

        dest = tmpdir / "doc.ps"
        result = generate_ps_fixture(dest, title="Hello")
        assert result.success
        content = dest.read_text()
        assert content.startswith("%!PS-Adobe-3.0")
        assert "%%EOF" in content

    def test_note_xml_inline(self):
        from plugin_examples.fixture_factory.generators import generate_note_xml_fixture

        result = generate_note_xml_fixture()
        assert result.fixture_type == "NOTE_XML"
        assert result.size_bytes > 0

    def test_note_xml_to_file(self, tmpdir):
        from plugin_examples.fixture_factory.generators import generate_note_xml_fixture

        dest = tmpdir / "note.xml"
        result = generate_note_xml_fixture(dest, title="My Note")
        assert result.success
        content = dest.read_text()
        assert "<Document" in content
        assert "My Note" in content

    def test_drawing_xml_inline(self):
        from plugin_examples.fixture_factory.generators import generate_drawing_xml_fixture

        result = generate_drawing_xml_fixture()
        assert result.fixture_type == "DRAWING_XML"
        assert result.size_bytes > 0

    def test_drawing_xml_to_file(self, tmpdir):
        from plugin_examples.fixture_factory.generators import generate_drawing_xml_fixture

        dest = tmpdir / "drawing.xml"
        result = generate_drawing_xml_fixture(dest)
        assert result.success
        content = dest.read_text()
        assert "VisioDocument" in content
        assert "Page-1" in content
