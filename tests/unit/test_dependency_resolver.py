"""Unit tests for nuget_fetcher.dependency_resolver."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from plugin_examples.nuget_fetcher.dependency_resolver import (
    _clean_version,
    _find_nuspec,
    _parse_dependencies,
    resolve_dependencies,
    update_package_lock,
    write_dependency_manifest,
)


# --- Helpers ---


def _make_nupkg(nuspec_xml: str, tmp_path: Path, name: str = "test.nupkg") -> Path:
    """Create a fake .nupkg zip containing the given .nuspec XML."""
    nupkg_path = tmp_path / name
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("test.nuspec", nuspec_xml)
    nupkg_path.write_bytes(buf.getvalue())
    return nupkg_path


_NUSPEC_WITH_DEPS = """\
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>TestPackage</id>
    <version>1.0.0</version>
    <dependencies>
      <group targetFramework=".NETStandard2.0">
        <dependency id="Dep.One" version="[2.0.0, )" />
        <dependency id="Dep.Two" version="3.1.0" />
      </group>
      <group targetFramework="net6.0">
        <dependency id="Dep.Three" version="1.0.0" />
      </group>
    </dependencies>
  </metadata>
</package>
"""

_NUSPEC_NO_DEPS = """\
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>NoDeps</id>
    <version>1.0.0</version>
  </metadata>
</package>
"""

_NUSPEC_FLAT_DEPS = """\
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>FlatDeps</id>
    <version>1.0.0</version>
    <dependencies>
      <dependency id="Flat.Dep" version="1.0.0" />
    </dependencies>
  </metadata>
</package>
"""


# --- Tests: _parse_dependencies ---


class TestParseDependencies:
    def test_parses_netstandard20_group(self):
        deps = _parse_dependencies(
            _NUSPEC_WITH_DEPS,
            ["netstandard2.0", "net6.0"],
        )
        assert len(deps) == 2
        assert deps[0]["id"] == "Dep.One"
        assert deps[1]["id"] == "Dep.Two"

    def test_parses_net60_group(self):
        deps = _parse_dependencies(
            _NUSPEC_WITH_DEPS,
            ["net6.0"],
        )
        assert len(deps) == 1
        assert deps[0]["id"] == "Dep.Three"

    def test_no_deps_returns_empty(self):
        deps = _parse_dependencies(_NUSPEC_NO_DEPS, ["netstandard2.0"])
        assert deps == []

    def test_flat_deps_parsed(self):
        deps = _parse_dependencies(_NUSPEC_FLAT_DEPS, ["netstandard2.0"])
        assert len(deps) == 1
        assert deps[0]["id"] == "Flat.Dep"


# --- Tests: _clean_version ---


class TestCleanVersion:
    def test_plain_version(self):
        assert _clean_version("4.0.0") == "4.0.0"

    def test_bracket_range(self):
        assert _clean_version("[4.0.0, )") == "4.0.0"

    def test_paren_range(self):
        assert _clean_version("(1.0.0, 2.0.0)") == "1.0.0"


# --- Tests: _find_nuspec ---


class TestFindNuspec:
    def test_extracts_nuspec(self, tmp_path):
        nupkg = _make_nupkg("<package/>", tmp_path)
        xml = _find_nuspec(nupkg)
        assert "<package/>" in xml

    def test_missing_nuspec_raises(self, tmp_path):
        # Create zip without .nuspec
        nupkg = tmp_path / "bad.nupkg"
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("readme.txt", "hello")
        nupkg.write_bytes(buf.getvalue())

        from plugin_examples.nuget_fetcher.fetcher import NuGetFetchError
        with pytest.raises(NuGetFetchError, match="No .nuspec found"):
            _find_nuspec(nupkg)


# --- Tests: resolve_dependencies ---


class TestResolveDependencies:
    @patch("plugin_examples.nuget_fetcher.dependency_resolver._download_nupkg")
    def test_dependency_manifest_written(self, mock_dl, tmp_path):
        """Dependencies are resolved and a manifest is written."""
        nupkg = _make_nupkg(_NUSPEC_WITH_DEPS, tmp_path)
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        # Make fake dep nupkgs (with their own empty nuspec for recursion)
        def fake_download(pkg_id, version, target_path):
            target_path.parent.mkdir(parents=True, exist_ok=True)
            dep_nupkg = _make_nupkg(_NUSPEC_NO_DEPS, target_path.parent, target_path.name)
            return f"https://example.com/{pkg_id}"

        mock_dl.side_effect = fake_download

        deps = resolve_dependencies(
            nupkg,
            target_frameworks=["netstandard2.0"],
            max_depth=1,
            run_dir=run_dir,
            family="test",
        )

        assert len(deps) == 2
        assert deps[0]["package_id"] == "Dep.One"
        assert deps[0]["depth"] == 1
        assert deps[0]["status"] == "ok"
        assert deps[1]["package_id"] == "Dep.Two"

        # Write manifest
        manifest_path = write_dependency_manifest(deps, run_dir, "test")
        assert manifest_path.exists()
        with open(manifest_path) as f:
            data = json.load(f)
        assert len(data["dependencies"]) == 2

    @patch("plugin_examples.nuget_fetcher.dependency_resolver._download_nupkg")
    def test_max_depth_respected(self, mock_dl, tmp_path):
        """max_depth=1 prevents transitive resolution."""
        # Primary has deps, each dep also has deps
        dep_nuspec = """\
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>DepWithTransitive</id>
    <version>1.0.0</version>
    <dependencies>
      <group targetFramework=".NETStandard2.0">
        <dependency id="Transitive.Dep" version="1.0.0" />
      </group>
    </dependencies>
  </metadata>
</package>
"""
        nupkg = _make_nupkg(_NUSPEC_WITH_DEPS, tmp_path)
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        def fake_download(pkg_id, version, target_path):
            target_path.parent.mkdir(parents=True, exist_ok=True)
            # Each dep also has transitive deps
            _make_nupkg(dep_nuspec, target_path.parent, target_path.name)
            return f"https://example.com/{pkg_id}"

        mock_dl.side_effect = fake_download

        # max_depth=1: only direct deps, no transitive
        deps = resolve_dependencies(
            nupkg,
            target_frameworks=["netstandard2.0"],
            max_depth=1,
            run_dir=run_dir,
            family="test",
        )

        dep_ids = [d["package_id"] for d in deps]
        assert "Dep.One" in dep_ids
        assert "Dep.Two" in dep_ids
        # Transitive dep should NOT be present at depth 1
        assert "Transitive.Dep" not in dep_ids

    @patch("plugin_examples.nuget_fetcher.dependency_resolver._download_nupkg")
    def test_max_depth_2_includes_transitive(self, mock_dl, tmp_path):
        """max_depth=2 resolves transitive dependencies."""
        dep_nuspec = """\
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
  <metadata>
    <id>DepWithTransitive</id>
    <version>1.0.0</version>
    <dependencies>
      <group targetFramework=".NETStandard2.0">
        <dependency id="Transitive.Dep" version="1.0.0" />
      </group>
    </dependencies>
  </metadata>
</package>
"""
        nupkg = _make_nupkg(_NUSPEC_WITH_DEPS, tmp_path)
        run_dir = tmp_path / "run"
        run_dir.mkdir()

        call_count = 0

        def fake_download(pkg_id, version, target_path):
            nonlocal call_count
            call_count += 1
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if pkg_id == "Transitive.Dep":
                _make_nupkg(_NUSPEC_NO_DEPS, target_path.parent, target_path.name)
            else:
                _make_nupkg(dep_nuspec, target_path.parent, target_path.name)
            return f"https://example.com/{pkg_id}"

        mock_dl.side_effect = fake_download

        deps = resolve_dependencies(
            nupkg,
            target_frameworks=["netstandard2.0"],
            max_depth=2,
            run_dir=run_dir,
            family="test",
        )

        dep_ids = [d["package_id"] for d in deps]
        assert "Dep.One" in dep_ids
        assert "Dep.Two" in dep_ids
        assert "Transitive.Dep" in dep_ids

        # Verify transitive deps are at depth 2
        transitive = [d for d in deps if d["package_id"] == "Transitive.Dep"]
        assert transitive[0]["depth"] == 2


# --- Tests: update_package_lock ---


class TestUpdatePackageLock:
    def test_creates_package_lock(self, tmp_path):
        download = {
            "package_id": "TestPkg",
            "version": "1.0.0",
            "sha256": "abc123",
            "source_url": "https://example.com/test",
        }
        deps = [
            {
                "package_id": "Dep.One",
                "version": "2.0.0",
                "sha256": "def456",
                "source_url": "https://example.com/dep",
                "status": "ok",
            }
        ]

        lock_path = update_package_lock(download, deps, tmp_path)
        assert lock_path.exists()

        with open(lock_path) as f:
            lock = json.load(f)

        assert "TestPkg" in lock["packages"]
        assert lock["packages"]["TestPkg"]["version"] == "1.0.0"
        assert "Dep.One" in lock["packages"]
        assert lock["packages"]["Dep.One"]["is_dependency"] is True

    def test_updates_existing_package_lock(self, tmp_path):
        """Subsequent calls merge into existing package-lock."""
        lock_path = tmp_path / "package-lock.json"
        lock_path.write_text(json.dumps({
            "packages": {
                "Existing": {"version": "0.1.0", "sha256": "aaa", "source_url": ""}
            }
        }))

        download = {
            "package_id": "NewPkg",
            "version": "2.0.0",
            "sha256": "bbb",
            "source_url": "https://example.com/new",
        }

        update_package_lock(download, [], tmp_path)

        with open(lock_path) as f:
            lock = json.load(f)

        assert "Existing" in lock["packages"]
        assert "NewPkg" in lock["packages"]

    def test_paths_use_workspace_manifests(self, tmp_path):
        """package-lock.json goes to manifests dir, not old root."""
        manifests_dir = tmp_path / "workspace" / "manifests"
        manifests_dir.mkdir(parents=True)

        download = {
            "package_id": "Test",
            "version": "1.0.0",
            "sha256": "x",
            "source_url": "",
        }
        lock_path = update_package_lock(download, [], manifests_dir)
        assert "workspace" in str(lock_path)
        assert "manifests" in str(lock_path)
