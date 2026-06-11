"""Tests for PLV-01..15 publication lifecycle validators (Wave 22)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.fixture_factory.publication_lifecycle_validators import (
    PlvResult,
    check_plv_01_wrong_stream_evidence,
    check_plv_02_pr_title_no_lowcode,
    check_plv_03_branch_naming,
    check_plv_04_example_readme_exists,
    check_plv_05_readme_quality,
    check_plv_06_root_readme_index,
    check_plv_07_pr_state_not_inflated,
    check_plv_08_branch_cleanup,
    check_plv_09_post_merge_state,
    check_plv_10_manifest_exists,
    check_plv_11_expected_output_exists,
    check_plv_12_ov_not_only_contract,
    check_plv_13_central_package_management,
    check_plv_14_ci_workflow,
    check_plv_15_evidence_authority,
    run_all_plv_checks,
)


class TestPlv01WrongStreamEvidence:
    def test_fails_for_wrong_stream_name(self):
        r = PlvResult()
        check_plv_01_wrong_stream_evidence("declaration-review-package(140).zip", r)
        assert r.failed == 1

    def test_passes_for_correct_name(self):
        r = PlvResult()
        check_plv_01_wrong_stream_evidence("lowcode-plugin-canonical-package-wave22-20260608.zip", r)
        assert r.passed == 1


class TestPlv02PrTitleNoLowcode:
    def test_fails_when_nlc_title_says_lowcode(self):
        r = PlvResult()
        check_plv_02_pr_title_no_lowcode(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "pr_title": "feat(lowcode): add barcode examples"}, r
        )
        assert r.failed == 1

    def test_passes_when_nlc_title_says_plugins(self):
        r = PlvResult()
        check_plv_02_pr_title_no_lowcode(
            {"namespace_source": "NON_LOWCODE_PLUGIN", "pr_title": "feat(plugins): add barcode examples"}, r
        )
        assert r.passed == 1

    def test_passes_for_lowcode_family(self):
        r = PlvResult()
        check_plv_02_pr_title_no_lowcode(
            {"namespace_source": "LOWCODE", "pr_title": "feat(lowcode): add words examples"}, r
        )
        assert r.failed == 0


class TestPlv03BranchNaming:
    def test_fails_for_new_nlc_branch_with_lowcode_prefix(self):
        r = PlvResult()
        check_plv_03_branch_naming(
            {
                "namespace_source": "NON_LOWCODE_PLUGIN",
                "branch_name": "lowcode/wave22/barcode",
                "branch_legacy_grandfathered": False,
            },
            r,
        )
        assert r.failed == 1

    def test_warns_for_legacy_grandfathered_branch(self):
        r = PlvResult()
        check_plv_03_branch_naming(
            {
                "namespace_source": "NON_LOWCODE_PLUGIN",
                "branch_name": "lowcode/wave19/barcode-plugin-examples",
                "branch_legacy_grandfathered": True,
            },
            r,
        )
        assert r.warnings == 1
        assert r.failed == 0

    def test_passes_for_plugins_prefix(self):
        r = PlvResult()
        check_plv_03_branch_naming(
            {
                "namespace_source": "NON_LOWCODE_PLUGIN",
                "branch_name": "plugins/wave22/barcode",
                "branch_legacy_grandfathered": False,
            },
            r,
        )
        assert r.passed == 1


class TestPlv04ReadmeExists:
    def test_fails_when_readme_missing(self, tmp_path):
        r = PlvResult()
        check_plv_04_example_readme_exists(tmp_path, r)
        assert r.failed == 1

    def test_passes_when_readme_present(self, tmp_path):
        (tmp_path / "README.md").write_text("# test", encoding="utf-8")
        r = PlvResult()
        check_plv_04_example_readme_exists(tmp_path, r)
        assert r.passed == 1


class TestPlv05ReadmeQuality:
    def test_warns_for_minimal_readme(self, tmp_path):
        (tmp_path / "README.md").write_text("# title\nSome text.", encoding="utf-8")
        r = PlvResult()
        check_plv_05_readme_quality(tmp_path, r)
        assert r.warnings >= 1

    def test_passes_for_quality_readme(self, tmp_path):
        content = (
            "# family/slug\n\n## Purpose\nDoes X.\n\n" "## Prerequisites\n.NET 8\n\n" "## Expected Output\nPNG file.\n"
        )
        (tmp_path / "README.md").write_text(content, encoding="utf-8")
        r = PlvResult()
        check_plv_05_readme_quality(tmp_path, r)
        assert r.failed == 0


class TestPlv06RootReadmeIndex:
    def test_fails_when_slug_not_in_root_readme(self, tmp_path):
        (tmp_path / "README.md").write_text("# Repo\nNo slug here.", encoding="utf-8")
        r = PlvResult()
        check_plv_06_root_readme_index(tmp_path, "barcode", ["1d-barcode-reader"], r)
        assert r.failed == 1

    def test_passes_when_all_slugs_indexed(self, tmp_path):
        (tmp_path / "README.md").write_text("# Repo\n| 1d-barcode-reader | ...", encoding="utf-8")
        r = PlvResult()
        check_plv_06_root_readme_index(tmp_path, "barcode", ["1d-barcode-reader"], r)
        assert r.passed == 1


class TestPlv07PrStateNotInflated:
    def test_fails_pr_created_without_url(self):
        r = PlvResult()
        check_plv_07_pr_state_not_inflated({"registry_status": "PR_CREATED", "slug": "test"}, r)
        assert r.failed == 1

    def test_fails_merged_without_timestamp(self):
        r = PlvResult()
        check_plv_07_pr_state_not_inflated({"registry_status": "MERGED", "slug": "test"}, r)
        assert r.failed == 1

    def test_passes_pr_created_with_url(self):
        r = PlvResult()
        check_plv_07_pr_state_not_inflated(
            {
                "registry_status": "PR_CREATED",
                "slug": "test",
                "pr_url": "https://github.com/x/y/pull/1",
            },
            r,
        )
        assert r.passed == 1


class TestPlv08BranchCleanup:
    def test_fails_merged_branch_not_deleted_no_reason(self):
        r = PlvResult()
        check_plv_08_branch_cleanup("plugins/wave22/barcode", False, True, "", r)
        assert r.failed == 1

    def test_warns_merged_branch_retained_with_reason(self):
        r = PlvResult()
        check_plv_08_branch_cleanup("plugins/wave22/barcode", False, True, "LTS branch", r)
        assert r.warnings == 1

    def test_passes_merged_branch_deleted(self):
        r = PlvResult()
        check_plv_08_branch_cleanup("plugins/wave22/barcode", True, True, "", r)
        assert r.passed == 1

    def test_passes_unmerged_branch(self):
        r = PlvResult()
        check_plv_08_branch_cleanup("plugins/wave22/barcode", False, False, "", r)
        assert r.passed == 1


class TestPlv09PostMergeState:
    def test_fails_merged_but_status_not_updated(self):
        r = PlvResult()
        check_plv_09_post_merge_state(
            {
                "merged_at": "2026-06-02T12:00:00Z",
                "registry_status": "PR_CREATED",
                "slug": "test",
            },
            r,
        )
        assert r.failed == 1

    def test_passes_merged_and_status_updated(self):
        r = PlvResult()
        check_plv_09_post_merge_state(
            {
                "merged_at": "2026-06-02T12:00:00Z",
                "registry_status": "MERGED",
                "slug": "test",
            },
            r,
        )
        assert r.passed == 1


class TestPlv10ManifestExists:
    def test_fails_when_missing(self, tmp_path):
        r = PlvResult()
        check_plv_10_manifest_exists(tmp_path, r)
        assert r.failed == 1

    def test_passes_when_present(self, tmp_path):
        (tmp_path / "example.manifest.json").write_text("{}", encoding="utf-8")
        r = PlvResult()
        check_plv_10_manifest_exists(tmp_path, r)
        assert r.passed == 1


class TestPlv11ExpectedOutputExists:
    def test_fails_when_missing(self, tmp_path):
        r = PlvResult()
        check_plv_11_expected_output_exists(tmp_path, r)
        assert r.failed == 1

    def test_passes_when_present(self, tmp_path):
        (tmp_path / "expected-output.json").write_text("{}", encoding="utf-8")
        r = PlvResult()
        check_plv_11_expected_output_exists(tmp_path, r)
        assert r.passed == 1


class TestPlv12OvNotOnlyContract:
    def test_fails_when_ov_without_eo(self, tmp_path):
        (tmp_path / "output-validation.json").write_text("{}", encoding="utf-8")
        r = PlvResult()
        check_plv_12_ov_not_only_contract(tmp_path, r)
        assert r.failed == 1

    def test_passes_when_both_present(self, tmp_path):
        (tmp_path / "output-validation.json").write_text("{}", encoding="utf-8")
        (tmp_path / "expected-output.json").write_text("{}", encoding="utf-8")
        r = PlvResult()
        check_plv_12_ov_not_only_contract(tmp_path, r)
        assert r.failed == 0


class TestPlv13CentralPackageManagement:
    def test_fails_when_missing(self, tmp_path):
        r = PlvResult()
        check_plv_13_central_package_management(tmp_path, r)
        assert r.failed == 1

    def test_passes_when_present_with_central_flag(self, tmp_path):
        content = (
            "<Project><PropertyGroup>"
            "<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>"
            "</PropertyGroup></Project>"
        )
        (tmp_path / "Directory.Packages.props").write_text(content, encoding="utf-8")
        r = PlvResult()
        check_plv_13_central_package_management(tmp_path, r)
        assert r.failed == 0


class TestPlv14CiWorkflow:
    def test_fails_when_workflow_missing(self, tmp_path):
        r = PlvResult()
        check_plv_14_ci_workflow(tmp_path, r)
        assert r.failed == 1

    def test_passes_when_workflow_with_build_present(self, tmp_path):
        wf = tmp_path / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "build.yml").write_text("name: CI\nsteps:\n  - run: dotnet build\n", encoding="utf-8")
        r = PlvResult()
        check_plv_14_ci_workflow(tmp_path, r)
        assert r.failed == 0


class TestPlv15EvidenceAuthority:
    def test_fails_when_bundle_missing(self, tmp_path):
        r = PlvResult()
        check_plv_15_evidence_authority(
            str(tmp_path / "bundle.zip"),
            str(tmp_path / "bundle.sha256"),
            str(tmp_path / "attestation.json"),
            r,
        )
        assert r.failed == 1

    def test_passes_when_all_present(self, tmp_path):
        (tmp_path / "bundle.zip").write_bytes(b"data")
        (tmp_path / "bundle.sha256").write_text("abc123  bundle.zip", encoding="utf-8")
        (tmp_path / "attestation.json").write_text("{}", encoding="utf-8")
        r = PlvResult()
        check_plv_15_evidence_authority(
            str(tmp_path / "bundle.zip"),
            str(tmp_path / "bundle.sha256"),
            str(tmp_path / "attestation.json"),
            r,
        )
        assert r.passed == 1


class TestRunAllPlvChecks:
    def test_full_passing_scenario(self, tmp_path):
        repo = tmp_path / "repo"
        ex = repo / "examples" / "barcode" / "1d-barcode-reader"
        ex.mkdir(parents=True)
        (repo / "Directory.Packages.props").write_text(
            "<Project><PropertyGroup>"
            "<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>"
            "</PropertyGroup></Project>",
            encoding="utf-8",
        )
        wf = repo / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "build.yml").write_text("name: CI\nsteps:\n  - run: dotnet build\n", encoding="utf-8")
        (repo / "README.md").write_text("# Barcode\n| 1d-barcode-reader | read | ...\n", encoding="utf-8")
        ex_readme = (
            "# barcode/1d-barcode-reader\n\n## Purpose\nReads barcodes.\n\n"
            "## Prerequisites\n.NET 8\n\n## Expected Output\nText.\n"
        )
        (ex / "README.md").write_text(ex_readme, encoding="utf-8")
        (ex / "example.manifest.json").write_text(json.dumps({"scenario_id": "test"}), encoding="utf-8")
        (ex / "expected-output.json").write_text("{}", encoding="utf-8")
        bundle = tmp_path / "lowcode-plugin-canonical-package-wave22-20260608.zip"
        bundle.write_bytes(b"data")
        sidecar = tmp_path / "lowcode-plugin-canonical-package-wave22-20260608.sha256"
        sidecar.write_text("abc  lowcode-plugin-canonical-package-wave22-20260608.zip", encoding="utf-8")
        attest = tmp_path / "attestation.json"
        attest.write_text("{}", encoding="utf-8")

        result = run_all_plv_checks(
            evidence_bundle_name="lowcode-plugin-canonical-package-wave22-20260608.zip",
            pr_packet={
                "namespace_source": "NON_LOWCODE_PLUGIN",
                "pr_title": "feat(plugins): add barcode examples",
                "branch_name": "plugins/wave22/barcode",
                "branch_legacy_grandfathered": False,
            },
            example_dirs=[ex],
            repo_root=repo,
            family="barcode",
            slugs=["1d-barcode-reader"],
            registry_entries=[
                {
                    "registry_status": "PR_CREATED",
                    "slug": "1d-barcode-reader",
                    "pr_url": "https://github.com/x/y/pull/1",
                }
            ],
            branch_cleanup_records=[
                {
                    "branch": "plugins/wave22/barcode",
                    "deleted": False,
                    "merged": False,
                    "retention_reason": "",
                }
            ],
            bundle_path=str(bundle),
            sha_file=str(sidecar),
            attestation_file=str(attest),
        )
        assert result.failed == 0, [c for c in result.checks if c["status"] == "FAIL"]
