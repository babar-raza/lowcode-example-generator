"""Tests for PPV-01..16 non-LowCode parity validators."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.nonlowcode_parity_validators import (
    PpvResult,
    check_ppv_01_pr_title_no_lowcode,
    check_ppv_02_pr_body_no_lowcode,
    check_ppv_03_branch_naming_warn,
    check_ppv_04_manifest_exists,
    check_ppv_05_expected_output_exists,
    check_ppv_06_output_validation_not_only_contract,
    check_ppv_07_dir_packages_props,
    check_ppv_08_csproj_no_version,
    check_ppv_09_root_readme,
    check_ppv_10_ci_workflow,
    check_ppv_11_folder_layout,
    check_ppv_12_fixture_provenance,
    check_ppv_13_manifest_namespace_source,
    check_ppv_14_status_not_inflated,
    check_ppv_15_gitignore,
    check_ppv_16_shared_downstream_path,
    run_all_ppv_checks,
)


class TestPpv01PrTitle:
    def test_fails_when_nlc_family_has_lowcode_title(self):
        result = PpvResult()
        check_ppv_01_pr_title_no_lowcode(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "pr_title": "feat(lowcode): add barcode examples"},
            result,
        )
        assert result.failed == 1
        assert result.checks[0]["code"] == "PPV-01"

    def test_passes_when_nlc_family_has_correct_title(self):
        result = PpvResult()
        check_ppv_01_pr_title_no_lowcode(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "pr_title": "feat(plugins): add barcode examples"},
            result,
        )
        assert result.failed == 0
        assert result.passed == 1

    def test_passes_for_lowcode_family_with_lowcode_title(self):
        result = PpvResult()
        check_ppv_01_pr_title_no_lowcode(
            {"namespace_source": "LOWCODE", "pr_title": "feat(lowcode): add words examples"},
            result,
        )
        assert result.failed == 0


class TestPpv02PrBody:
    def test_fails_when_nlc_body_says_low_code(self):
        result = PpvResult()
        check_ppv_02_pr_body_no_lowcode(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "pr_body": "Adds canonical low-code C# examples"},
            result,
        )
        assert result.failed == 1

    def test_passes_when_nlc_body_says_plugin(self):
        result = PpvResult()
        check_ppv_02_pr_body_no_lowcode(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "pr_body": "Adds canonical plugin API examples"},
            result,
        )
        assert result.failed == 0


class TestPpv03BranchNaming:
    def test_warns_when_nlc_branch_uses_lowcode_prefix(self):
        result = PpvResult()
        check_ppv_03_branch_naming_warn(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "branch_name": "lowcode/wave19/barcode"},
            result,
        )
        assert result.warnings == 1
        assert result.failed == 0  # only a warning, not a failure

    def test_passes_when_branch_uses_plugins_prefix(self):
        result = PpvResult()
        check_ppv_03_branch_naming_warn(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "branch_name": "plugins/wave21/barcode"},
            result,
        )
        assert result.warnings == 0
        assert result.passed == 1


class TestPpv04ManifestExists:
    def test_fails_when_manifest_missing(self, tmp_path):
        result = PpvResult()
        check_ppv_04_manifest_exists(tmp_path, result)
        assert result.failed == 1

    def test_passes_when_manifest_present(self, tmp_path):
        (tmp_path / "example.manifest.json").write_text("{}", encoding="utf-8")
        result = PpvResult()
        check_ppv_04_manifest_exists(tmp_path, result)
        assert result.passed == 1


class TestPpv05ExpectedOutput:
    def test_fails_when_expected_output_missing(self, tmp_path):
        result = PpvResult()
        check_ppv_05_expected_output_exists(tmp_path, result)
        assert result.failed == 1

    def test_passes_when_expected_output_present(self, tmp_path):
        (tmp_path / "expected-output.json").write_text("{}", encoding="utf-8")
        result = PpvResult()
        check_ppv_05_expected_output_exists(tmp_path, result)
        assert result.passed == 1


class TestPpv06OutputValidationNotSubstitute:
    def test_fails_when_only_output_validation_present(self, tmp_path):
        (tmp_path / "output-validation.json").write_text("{}", encoding="utf-8")
        result = PpvResult()
        check_ppv_06_output_validation_not_only_contract(tmp_path, result)
        assert result.failed == 1

    def test_passes_when_both_present(self, tmp_path):
        (tmp_path / "output-validation.json").write_text("{}", encoding="utf-8")
        (tmp_path / "expected-output.json").write_text("{}", encoding="utf-8")
        result = PpvResult()
        check_ppv_06_output_validation_not_only_contract(tmp_path, result)
        assert result.failed == 0


class TestPpv07DirPackagesProps:
    def test_fails_when_missing(self, tmp_path):
        result = PpvResult()
        check_ppv_07_dir_packages_props(tmp_path, result)
        assert result.failed == 1

    def test_passes_when_present(self, tmp_path):
        (tmp_path / "Directory.Packages.props").write_text("<Project/>", encoding="utf-8")
        result = PpvResult()
        check_ppv_07_dir_packages_props(tmp_path, result)
        assert result.passed == 1


class TestPpv08CsprojNoVersion:
    def test_fails_when_csproj_has_version(self, tmp_path):
        p = tmp_path / "test.csproj"
        p.write_text('<PackageReference Include="Aspose.BarCode" Version="24.12.0" />', encoding="utf-8")
        result = PpvResult()
        check_ppv_08_csproj_no_version(p, result)
        assert result.failed == 1

    def test_passes_when_no_version_in_csproj(self, tmp_path):
        p = tmp_path / "test.csproj"
        p.write_text('<PackageReference Include="Aspose.BarCode" />', encoding="utf-8")
        result = PpvResult()
        check_ppv_08_csproj_no_version(p, result)
        assert result.passed == 1


class TestPpv11FolderLayout:
    def test_fails_for_lowcode_at_wrong_path(self, tmp_path):
        wrong = tmp_path / "examples" / "words" / "converter"
        wrong.mkdir(parents=True)
        result = PpvResult()
        check_ppv_11_folder_layout(wrong, "words", "converter", "LOWCODE", result)
        assert result.failed == 1

    def test_passes_for_lowcode_at_correct_path(self, tmp_path):
        correct = tmp_path / "examples" / "words" / "lowcode" / "converter"
        correct.mkdir(parents=True)
        result = PpvResult()
        check_ppv_11_folder_layout(correct, "words", "converter", "LOWCODE", result)
        assert result.passed == 1

    def test_passes_for_nlc_at_correct_path(self, tmp_path):
        correct = tmp_path / "examples" / "barcode" / "1d-barcode-reader"
        correct.mkdir(parents=True)
        result = PpvResult()
        check_ppv_11_folder_layout(correct, "barcode", "1d-barcode-reader", "NON_LOWCODE_PLUGIN", result)
        assert result.passed == 1


class TestPpv14StatusNotInflated:
    def test_fails_pr_created_without_url(self):
        result = PpvResult()
        check_ppv_14_status_not_inflated({"registry_status": "PR_CREATED", "slug": "test"}, result)
        assert result.failed == 1

    def test_passes_pr_created_with_url(self):
        result = PpvResult()
        check_ppv_14_status_not_inflated(
            {"registry_status": "PR_CREATED", "slug": "test", "pr_url": "https://github.com/x/y/pull/1"},
            result,
        )
        assert result.passed == 1


class TestPpv16SharedDownstreamPath:
    def test_fails_when_stages_missing(self):
        result = PpvResult()
        check_ppv_16_shared_downstream_path(["restore", "build"], result)
        assert result.failed == 1

    def test_passes_when_all_stages_present(self):
        result = PpvResult()
        check_ppv_16_shared_downstream_path(
            ["manifest_generation", "expected_output_generation", "pr_packet_generation"],
            result,
        )
        assert result.passed == 1


class TestRunAllPpvChecks:
    def test_full_passing_scenario(self, tmp_path):
        # Scaffold a valid example directory
        repo = tmp_path / "repo"
        ex = repo / "examples" / "barcode" / "1d-barcode-reader"
        ex.mkdir(parents=True)
        (repo / "Directory.Packages.props").write_text("<Project/>", encoding="utf-8")
        (repo / "Directory.Build.props").write_text("<Project/>", encoding="utf-8")
        (repo / "README.md").write_text("# readme", encoding="utf-8")
        (repo / ".gitignore").write_text("bin/\n", encoding="utf-8")
        wf = repo / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "build.yml").write_text("name: CI\n", encoding="utf-8")
        manifest = {
            "scenario_id": "barcode-1d-barcode-reader",
            "namespace_source": "NON_LOWCODE_PLUGIN",
            "canonical_url": "https://products.aspose.net/barcode/1d-barcode-reader/",
            "input_strategy": "programmatic",
            "input_files": [],
        }
        (ex / "example.manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (ex / "expected-output.json").write_text("{}", encoding="utf-8")
        csproj = ex / "barcode-1d-barcode-reader.csproj"
        csproj.write_text('<PackageReference Include="Aspose.BarCode" />', encoding="utf-8")

        result = run_all_ppv_checks(
            pr_packet={
                "namespace_source": "NON_LOWCODE_PLUGIN",
                "pr_title": "feat(plugins): add barcode",
                "pr_body": "plugin examples",
                "branch_name": "plugins/wave21/barcode",
            },
            example_dirs=[ex],
            repo_root=repo,
            family="barcode",
            namespace_source="NON_LOWCODE_PLUGIN",
            registry_entries=[{"registry_status": "CANONICAL_PACKAGE_PROVEN", "slug": "1d-barcode-reader"}],
            pipeline_stages=["manifest_generation", "expected_output_generation", "pr_packet_generation"],
        )
        assert result.failed == 0, [c for c in result.checks if c["status"] == "FAIL"]
