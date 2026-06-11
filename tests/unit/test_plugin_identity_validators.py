"""
Unit tests for plugin identity invariant validators (PIV-01..PIV-14).
Sprint: lowcode-plugin-canonical-identity-wave7-20260605
"""

import json
import pytest
from pathlib import Path

from plugin_examples.fixture_factory.plugin_identity_validators import (
    run_plugin_identity_validators,
    PivResult,
    GENERIC_BARCODE_SLUGS,
    CANONICAL_BARCODE_SLUGS,
)


def _make_canonical_package(tmp_path: Path, slug: str = "1d-barcode-writer", family: str = "barcode") -> Path:
    """Create a minimal canonical-identity-verified package."""
    pkg = tmp_path / family / slug
    pkg.mkdir(parents=True)
    (pkg / "output").mkdir()

    sp = {
        "canonical_plugin_slug": slug,
        "canonical_url": f"https://products.aspose.net/{family}/{slug}/",
        "display_plugin_name": f"Test Plugin {slug}",
        "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        "legacy_example_slug": "",
    }
    (pkg / "source-provenance.json").write_text(json.dumps(sp))

    pm = {
        "canonical_plugin_slug": slug,
        "canonical_url": f"https://products.aspose.net/{family}/{slug}/",
    }
    (pkg / "package-manifest.json").write_text(json.dumps(pm))

    ov = {
        "verdict": "PASS",
        "publication_classification": "",
    }
    (pkg / "output-validation.json").write_text(json.dumps(ov))

    (pkg / "README.md").write_text(f"# Test Plugin {slug}\n\nSome description.")
    (pkg / "output" / "result.txt").write_text("OK")

    return pkg


class TestPiv01MissingProvenance:
    def test_missing_source_provenance_triggers_piv01(self, tmp_path):
        pkg = tmp_path / "barcode" / "1d-barcode-writer"
        pkg.mkdir(parents=True)
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        codes = [v.rule for v in r.violations]
        assert "PIV-01" in codes
        assert not r.passes


class TestPiv02MissingCanonicalUrl:
    def test_missing_canonical_url_triggers_piv02(self, tmp_path):
        pkg = _make_canonical_package(tmp_path)
        sp = json.loads((pkg / "source-provenance.json").read_text())
        sp["canonical_url"] = ""
        (pkg / "source-provenance.json").write_text(json.dumps(sp))
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        codes = [v.rule for v in r.violations]
        assert "PIV-02" in codes


class TestPiv03MissingCanonicalSlug:
    def test_missing_canonical_plugin_slug_triggers_piv03(self, tmp_path):
        pkg = _make_canonical_package(tmp_path)
        sp = json.loads((pkg / "source-provenance.json").read_text())
        del sp["canonical_plugin_slug"]
        (pkg / "source-provenance.json").write_text(json.dumps(sp))
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        codes = [v.rule for v in r.violations]
        assert "PIV-03" in codes


class TestPiv04CanonicalUrlSlugMismatch:
    def test_url_slug_mismatch_triggers_piv04(self, tmp_path):
        pkg = _make_canonical_package(tmp_path, slug="1d-barcode-writer")
        sp = json.loads((pkg / "source-provenance.json").read_text())
        # URL says 2d-barcode-writer but canonical_plugin_slug says 1d-barcode-writer
        sp["canonical_url"] = "https://products.aspose.net/barcode/2d-barcode-writer/"
        (pkg / "source-provenance.json").write_text(json.dumps(sp))
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        codes = [v.rule for v in r.violations]
        assert "PIV-04" in codes


class TestPiv05FolderSlugMismatch:
    def test_folder_mismatch_without_alias_triggers_piv05_error(self, tmp_path):
        # Package is in folder "my-custom-name" but canonical slug is "1d-barcode-writer"
        pkg = tmp_path / "barcode" / "my-custom-name"
        pkg.mkdir(parents=True)
        (pkg / "output").mkdir()
        sp = {
            "canonical_plugin_slug": "1d-barcode-writer",
            "canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
            "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        }
        (pkg / "source-provenance.json").write_text(json.dumps(sp))
        (pkg / "output-validation.json").write_text(json.dumps({"verdict": "PASS"}))
        (pkg / "package-manifest.json").write_text(
            json.dumps({"canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/"})
        )
        (pkg / "README.md").write_text("# Test")
        (pkg / "output" / "r.txt").write_text("ok")
        r = run_plugin_identity_validators(pkg, "barcode/my-custom-name")
        codes = [v.rule for v in r.violations]
        assert "PIV-05" in codes
        piv5 = next(v for v in r.violations if v.rule == "PIV-05")
        assert piv5.severity == "ERROR"

    def test_folder_mismatch_with_alias_triggers_piv05_warning_only(self, tmp_path):
        pkg = tmp_path / "barcode" / "generate-barcode"
        pkg.mkdir(parents=True)
        (pkg / "output").mkdir()
        sp = {
            "canonical_plugin_slug": "1d-barcode-writer",
            "canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/",
            "legacy_example_slug": "generate-barcode",
            "identity_status": "CANONICAL_IDENTITY_VERIFIED",
        }
        (pkg / "source-provenance.json").write_text(json.dumps(sp))
        (pkg / "output-validation.json").write_text(json.dumps({"verdict": "PASS"}))
        (pkg / "package-manifest.json").write_text(
            json.dumps({"canonical_url": "https://products.aspose.net/barcode/1d-barcode-writer/"})
        )
        (pkg / "README.md").write_text("# 1D Barcode Writer")
        (pkg / "output" / "r.txt").write_text("ok")
        r = run_plugin_identity_validators(pkg, "barcode/generate-barcode")
        error_codes = [v.rule for v in r.violations if v.severity == "ERROR"]
        assert "PIV-05" not in error_codes  # alias documented → warning only


class TestPiv08BarcodeGenericName:
    def test_generic_barcode_slug_triggers_piv08(self, tmp_path):
        for slug in GENERIC_BARCODE_SLUGS:
            pkg = _make_canonical_package(tmp_path, slug=slug)
            r = run_plugin_identity_validators(pkg, f"barcode/{slug}")
            codes = [v.rule for v in r.violations]
            assert "PIV-08" in codes, f"PIV-08 not raised for generic slug '{slug}'"

    def test_canonical_barcode_slug_does_not_trigger_piv08(self, tmp_path):
        for slug in CANONICAL_BARCODE_SLUGS:
            pkg = _make_canonical_package(tmp_path, slug=slug)
            r = run_plugin_identity_validators(pkg, f"barcode/{slug}")
            codes = [v.rule for v in r.violations]
            assert "PIV-08" not in codes, f"PIV-08 wrongly raised for canonical slug '{slug}'"


class TestPiv12PassWithNoOutputs:
    def test_pass_verdict_with_empty_output_triggers_piv12(self, tmp_path):
        pkg = _make_canonical_package(tmp_path)
        # Remove all output files
        for f in (pkg / "output").iterdir():
            f.unlink()
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        codes = [v.rule for v in r.violations]
        assert "PIV-12" in codes


class TestPiv13ProvenanceManifestMismatch:
    def test_canonical_url_mismatch_triggers_piv13(self, tmp_path):
        pkg = _make_canonical_package(tmp_path)
        pm = json.loads((pkg / "package-manifest.json").read_text())
        pm["canonical_url"] = "https://products.aspose.net/barcode/different-url/"
        (pkg / "package-manifest.json").write_text(json.dumps(pm))
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        codes = [v.rule for v in r.violations]
        assert "PIV-13" in codes


class TestPiv14PublicationCleanWithoutIdentity:
    def test_clean_pub_without_verified_identity_triggers_piv14(self, tmp_path):
        pkg = _make_canonical_package(tmp_path)
        ov = json.loads((pkg / "output-validation.json").read_text())
        ov["publication_classification"] = "PUBLICATION_CANDIDATE_LOCAL_CLEAN"
        (pkg / "output-validation.json").write_text(json.dumps(ov))
        sp = json.loads((pkg / "source-provenance.json").read_text())
        sp["identity_status"] = "SLUG_ALIAS_REQUIRED"
        (pkg / "source-provenance.json").write_text(json.dumps(sp))
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        codes = [v.rule for v in r.violations]
        assert "PIV-14" in codes


class TestCleanPackagePasses:
    def test_clean_canonical_package_has_no_errors(self, tmp_path):
        pkg = _make_canonical_package(tmp_path, slug="1d-barcode-writer")
        r = run_plugin_identity_validators(pkg, "barcode/1d-barcode-writer")
        assert r.passes, f"Unexpected violations: {[v.message for v in r.violations if v.severity == 'ERROR']}"

    def test_canonical_identity_status_on_clean_package(self, tmp_path):
        pkg = _make_canonical_package(tmp_path, slug="2d-barcode-writer")
        r = run_plugin_identity_validators(pkg, "barcode/2d-barcode-writer")
        assert r.identity_status in ("CANONICAL_IDENTITY_VERIFIED", "IDENTITY_WARNING_ONLY")
