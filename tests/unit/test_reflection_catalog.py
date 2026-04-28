"""Unit tests for reflection_catalog: reflector, catalog_builder, schema_validator."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.reflection_catalog.catalog_builder import (
    CatalogBuildError,
    build_catalog,
    _normalize,
    _normalize_type,
)
from plugin_examples.reflection_catalog.reflector import (
    ReflectorError,
    find_reflector_executable,
    run_reflector,
)
from plugin_examples.reflection_catalog.schema_validator import (
    validate_catalog,
)


# --- Fixtures ---


def _make_valid_catalog(**overrides) -> dict:
    """Create a minimal valid catalog dict."""
    catalog = {
        "assembly_name": "TestAssembly",
        "assembly_version": "1.0.0.0",
        "target_framework": ".NETStandard,Version=v2.0",
        "namespaces": [
            {
                "namespace": "TestNamespace",
                "types": [
                    {
                        "name": "TestClass",
                        "full_name": "TestNamespace.TestClass",
                        "kind": "class",
                        "is_obsolete": False,
                        "constructors": [
                            {
                                "parameters": [],
                                "is_obsolete": False,
                            }
                        ],
                        "methods": [
                            {
                                "name": "DoWork",
                                "return_type": "System.Void",
                                "is_static": False,
                                "is_obsolete": False,
                                "parameters": [
                                    {
                                        "name": "input",
                                        "type": "System.String",
                                        "is_optional": False,
                                    }
                                ],
                            }
                        ],
                        "properties": [
                            {
                                "name": "Value",
                                "type": "System.Int32",
                                "can_read": True,
                                "can_write": True,
                                "is_obsolete": False,
                            }
                        ],
                    }
                ],
            }
        ],
        "diagnostics": {
            "xml_documentation_loaded": False,
            "xml_warning": "No XML documentation path provided",
            "dependency_paths_provided": 0,
            "metadata_only": True,
        },
    }
    catalog.update(overrides)
    return catalog


def _make_enum_catalog() -> dict:
    """Create a catalog with an enum type."""
    return {
        "assembly_name": "TestAssembly",
        "assembly_version": "1.0.0.0",
        "target_framework": None,
        "namespaces": [
            {
                "namespace": "TestNamespace",
                "types": [
                    {
                        "name": "Color",
                        "full_name": "TestNamespace.Color",
                        "kind": "enum",
                        "is_obsolete": False,
                        "enum_values": [
                            {"name": "Red", "is_obsolete": False},
                            {"name": "Green", "is_obsolete": False},
                            {"name": "Blue", "is_obsolete": True},
                        ],
                    }
                ],
            }
        ],
        "diagnostics": {
            "xml_documentation_loaded": False,
            "metadata_only": True,
        },
    }


# --- Tests: schema_validator ---


class TestSchemaValidator:
    def test_valid_catalog_passes(self):
        errors = validate_catalog(_make_valid_catalog())
        assert errors == []

    def test_enum_catalog_passes(self):
        errors = validate_catalog(_make_enum_catalog())
        assert errors == []

    def test_missing_assembly_name_fails(self):
        catalog = _make_valid_catalog()
        del catalog["assembly_name"]
        errors = validate_catalog(catalog)
        assert len(errors) > 0
        assert any("assembly_name" in e for e in errors)

    def test_missing_diagnostics_fails(self):
        catalog = _make_valid_catalog()
        del catalog["diagnostics"]
        errors = validate_catalog(catalog)
        assert len(errors) > 0

    def test_invalid_type_kind_fails(self):
        catalog = _make_valid_catalog()
        catalog["namespaces"][0]["types"][0]["kind"] = "module"
        errors = validate_catalog(catalog)
        assert len(errors) > 0

    def test_metadata_only_must_be_true(self):
        catalog = _make_valid_catalog()
        catalog["diagnostics"]["metadata_only"] = False
        errors = validate_catalog(catalog)
        assert len(errors) > 0

    def test_missing_method_fields_fails(self):
        catalog = _make_valid_catalog()
        del catalog["namespaces"][0]["types"][0]["methods"][0]["return_type"]
        errors = validate_catalog(catalog)
        assert len(errors) > 0

    def test_extra_root_field_fails(self):
        catalog = _make_valid_catalog()
        catalog["extra_field"] = "not allowed"
        errors = validate_catalog(catalog)
        assert len(errors) > 0


# --- Tests: reflector ---


class TestFindReflectorExecutable:
    def test_finds_release_build(self, tmp_path):
        release = tmp_path / "bin" / "Release" / "net8.0" / "DllReflector.dll"
        release.parent.mkdir(parents=True)
        release.write_text("fake")
        result = find_reflector_executable(tmp_path)
        assert result == release

    def test_falls_back_to_debug(self, tmp_path):
        debug = tmp_path / "bin" / "Debug" / "net8.0" / "DllReflector.dll"
        debug.parent.mkdir(parents=True)
        debug.write_text("fake")
        result = find_reflector_executable(tmp_path)
        assert result == debug

    def test_release_preferred_over_debug(self, tmp_path):
        for config in ("Release", "Debug"):
            p = tmp_path / "bin" / config / "net8.0" / "DllReflector.dll"
            p.parent.mkdir(parents=True)
            p.write_text("fake")
        result = find_reflector_executable(tmp_path)
        assert "Release" in str(result)

    def test_raises_when_not_built(self, tmp_path):
        with pytest.raises(ReflectorError, match="not built"):
            find_reflector_executable(tmp_path)


class TestRunReflector:
    def test_success(self, tmp_path):
        catalog = _make_valid_catalog()
        output = tmp_path / "catalog.json"
        exe = tmp_path / "bin" / "Release" / "net8.0" / "DllReflector.dll"
        exe.parent.mkdir(parents=True)
        exe.write_text("fake")
        dll = tmp_path / "test.dll"
        dll.write_text("fake")

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        def side_effect(cmd, **kwargs):
            output.write_text(json.dumps(catalog))
            return mock_result

        with patch("plugin_examples.reflection_catalog.reflector.subprocess.run", side_effect=side_effect):
            result = run_reflector(
                dll_path=dll,
                output_path=output,
                reflector_dir=tmp_path,
            )

        assert result["assembly_name"] == "TestAssembly"
        assert len(result["namespaces"]) == 1

    def test_nonzero_exit_raises(self, tmp_path):
        exe = tmp_path / "bin" / "Release" / "net8.0" / "DllReflector.dll"
        exe.parent.mkdir(parents=True)
        exe.write_text("fake")
        dll = tmp_path / "test.dll"
        dll.write_text("fake")

        mock_result = MagicMock()
        mock_result.returncode = 2
        mock_result.stdout = ""
        mock_result.stderr = "DLL not found"

        with patch("plugin_examples.reflection_catalog.reflector.subprocess.run", return_value=mock_result):
            with pytest.raises(ReflectorError, match="exited with code 2"):
                run_reflector(
                    dll_path=dll,
                    output_path=tmp_path / "out.json",
                    reflector_dir=tmp_path,
                )

    def test_timeout_raises(self, tmp_path):
        exe = tmp_path / "bin" / "Release" / "net8.0" / "DllReflector.dll"
        exe.parent.mkdir(parents=True)
        exe.write_text("fake")
        dll = tmp_path / "test.dll"
        dll.write_text("fake")

        with patch(
            "plugin_examples.reflection_catalog.reflector.subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="dotnet", timeout=120),
        ):
            with pytest.raises(ReflectorError, match="timed out"):
                run_reflector(
                    dll_path=dll,
                    output_path=tmp_path / "out.json",
                    reflector_dir=tmp_path,
                )

    def test_xml_and_deps_passed_to_cli(self, tmp_path):
        exe = tmp_path / "bin" / "Release" / "net8.0" / "DllReflector.dll"
        exe.parent.mkdir(parents=True)
        exe.write_text("fake")
        dll = tmp_path / "test.dll"
        dll.write_text("fake")
        xml = tmp_path / "test.xml"
        xml.write_text("<doc></doc>")
        dep1 = tmp_path / "dep1.dll"
        dep1.write_text("fake")
        output = tmp_path / "out.json"

        captured_cmd = []
        mock_result = MagicMock()
        mock_result.returncode = 0

        def side_effect(cmd, **kwargs):
            captured_cmd.extend(cmd)
            output.write_text(json.dumps(_make_valid_catalog()))
            return mock_result

        with patch("plugin_examples.reflection_catalog.reflector.subprocess.run", side_effect=side_effect):
            run_reflector(
                dll_path=dll,
                output_path=output,
                xml_path=xml,
                dependency_paths=[dep1],
                reflector_dir=tmp_path,
            )

        assert "--xml" in captured_cmd
        assert "--deps" in captured_cmd
        assert str(xml) in captured_cmd
        assert str(dep1) in captured_cmd


# --- Tests: catalog_builder normalize ---


class TestNormalize:
    def test_passthrough_preserves_fields(self):
        raw = _make_valid_catalog()
        result = _normalize(raw)
        assert result["assembly_name"] == "TestAssembly"
        assert len(result["namespaces"]) == 1
        assert result["namespaces"][0]["types"][0]["name"] == "TestClass"

    def test_namespace_filter(self):
        raw = _make_valid_catalog()
        raw["namespaces"].append({
            "namespace": "OtherNamespace",
            "types": [],
        })
        result = _normalize(raw, namespace_filter=["TestNamespace"])
        assert len(result["namespaces"]) == 1
        assert result["namespaces"][0]["namespace"] == "TestNamespace"

    def test_namespace_filter_case_insensitive(self):
        raw = _make_valid_catalog()
        result = _normalize(raw, namespace_filter=["testnamespace"])
        assert len(result["namespaces"]) == 1

    def test_no_filter_keeps_all(self):
        raw = _make_valid_catalog()
        raw["namespaces"].append({
            "namespace": "Other",
            "types": [],
        })
        result = _normalize(raw)
        assert len(result["namespaces"]) == 2

    def test_enum_type_normalized(self):
        raw = _make_enum_catalog()
        result = _normalize(raw)
        enum_type = result["namespaces"][0]["types"][0]
        assert enum_type["kind"] == "enum"
        assert "enum_values" in enum_type
        assert "constructors" not in enum_type
        assert "methods" not in enum_type

    def test_class_type_has_members(self):
        raw = _make_valid_catalog()
        result = _normalize(raw)
        class_type = result["namespaces"][0]["types"][0]
        assert "constructors" in class_type
        assert "methods" in class_type
        assert "properties" in class_type
        assert "enum_values" not in class_type


# --- Tests: catalog_builder build ---


class TestBuildCatalog:
    def test_build_writes_output(self, tmp_path):
        catalog = _make_valid_catalog()
        output = tmp_path / "catalog.json"
        dll = tmp_path / "test.dll"
        dll.write_text("fake")

        with patch(
            "plugin_examples.reflection_catalog.catalog_builder.run_reflector",
            return_value=catalog,
        ):
            result = build_catalog(
                dll_path=dll,
                output_path=output,
            )

        assert output.exists()
        assert result["assembly_name"] == "TestAssembly"
        with open(output) as f:
            written = json.load(f)
        assert written["assembly_name"] == "TestAssembly"

    def test_build_with_namespace_filter(self, tmp_path):
        catalog = _make_valid_catalog()
        catalog["namespaces"].append({"namespace": "Unrelated", "types": []})
        output = tmp_path / "catalog.json"
        dll = tmp_path / "test.dll"
        dll.write_text("fake")

        with patch(
            "plugin_examples.reflection_catalog.catalog_builder.run_reflector",
            return_value=catalog,
        ):
            result = build_catalog(
                dll_path=dll,
                output_path=output,
                namespace_filter=["TestNamespace"],
            )

        assert len(result["namespaces"]) == 1

    def test_build_validation_failure_raises(self, tmp_path):
        bad_catalog = {"assembly_name": "Test"}  # Missing required fields
        output = tmp_path / "catalog.json"
        dll = tmp_path / "test.dll"
        dll.write_text("fake")

        with patch(
            "plugin_examples.reflection_catalog.catalog_builder.run_reflector",
            return_value=bad_catalog,
        ):
            with pytest.raises(CatalogBuildError, match="validation failed"):
                build_catalog(dll_path=dll, output_path=output)
