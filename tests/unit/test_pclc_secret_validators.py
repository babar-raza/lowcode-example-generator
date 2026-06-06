"""
Tests for PCLV (PCLC Consistency) and SHV (Secret Hygiene) validators — Wave 16
"""

import pytest

from src.plugin_examples.fixture_factory.pclc_consistency_validators import (
    pclv_01_state_count_matches_readiness_file,
    pclv_02_every_pclc_has_pr_packet_field,
    pclv_03_pr_packet_count_matches_ready_count,
    run_all_pclv,
)
from src.plugin_examples.fixture_factory.secret_hygiene_validators import (
    shv_01_no_pfx_untracked_or_staged,
    shv_02_no_pem_key_p12_untracked_or_staged,
    shv_03_no_credential_filenames_staged,
    run_all_shv,
)


# ============================================================
# PCLV-01
# ============================================================

def make_readiness(total, packages=None):
    if packages is None:
        packages = [{"family": f"fam{i}", "slug": f"slug{i}", "pr_packet_exists": True} for i in range(total)]
    return {"pclc_total": total, "packages": packages, "pr_packets_total": total, "pr_packets_wave16_count": 0}


def make_state(pclc_count):
    return {"pclc_count": pclc_count}


class TestPCLV01:
    def test_pass_counts_match(self):
        result = pclv_01_state_count_matches_readiness_file(make_state(16), make_readiness(16))
        assert result.passed

    def test_fail_wave15_pattern_16_vs_14(self):
        """Regression: Wave 15 state said 16 PCLC but readiness file only had 14."""
        state = {"pclc_count": 16}
        readiness = make_readiness(14)
        result = pclv_01_state_count_matches_readiness_file(state, readiness)
        assert not result.passed
        assert "16" in result.message
        assert "14" in result.message

    def test_pass_zeros(self):
        result = pclv_01_state_count_matches_readiness_file(make_state(0), make_readiness(0, packages=[]))
        assert result.passed

    def test_fail_state_missing_field(self):
        result = pclv_01_state_count_matches_readiness_file({}, make_readiness(16))
        assert not result.passed


# ============================================================
# PCLV-02
# ============================================================

class TestPCLV02:
    def test_pass_all_have_field(self):
        readiness = make_readiness(3)
        result = pclv_02_every_pclc_has_pr_packet_field(readiness)
        assert result.passed

    def test_fail_missing_pr_packet_field(self):
        packages = [
            {"family": "html", "slug": "xps", "pr_packet_exists": True},
            {"family": "psd", "slug": "png"},  # Missing pr_packet_exists
        ]
        readiness = {"pclc_total": 2, "packages": packages}
        result = pclv_02_every_pclc_has_pr_packet_field(readiness)
        assert not result.passed
        assert "psd/png" in result.detail["missing"]

    def test_fail_no_packages(self):
        result = pclv_02_every_pclc_has_pr_packet_field({"pclc_total": 5, "packages": []})
        assert not result.passed


# ============================================================
# PCLV-03
# ============================================================

class TestPCLV03:
    def test_pass_all_pr_packets_accounted(self):
        packages = [{"family": f"f{i}", "slug": f"s{i}", "pr_packet_exists": True} for i in range(16)]
        readiness = {"pclc_total": 16, "packages": packages, "pr_packets_total": 16, "pr_packets_wave16_count": 0}
        result = pclv_03_pr_packet_count_matches_ready_count(readiness)
        assert result.passed

    def test_pass_wave16_addition_explained(self):
        packages = [{"family": f"f{i}", "slug": f"s{i}", "pr_packet_exists": True} for i in range(14)]
        packages += [{"family": "html", "slug": "xps", "pr_packet_exists": True},
                     {"family": "psd", "slug": "png", "pr_packet_exists": True}]
        readiness = {"pclc_total": 16, "packages": packages, "pr_packets_total": 16, "pr_packets_wave16_count": 2}
        result = pclv_03_pr_packet_count_matches_ready_count(readiness)
        assert result.passed


# ============================================================
# run_all_pclv
# ============================================================

class TestRunAllPCLV:
    def test_wave16_correct_state_passes(self):
        packages = [{"family": f"f{i}", "slug": f"s{i}", "pr_packet_exists": True} for i in range(16)]
        readiness = {"pclc_total": 16, "packages": packages, "pr_packets_total": 16, "pr_packets_wave16_count": 0}
        state = {"pclc_count": 16}
        results = run_all_pclv(state, readiness)
        assert all(r.passed for r in results), [r for r in results if not r.passed]

    def test_wave15_14_vs_16_fails(self):
        """Regression: 16 in state, 14 in readiness."""
        readiness = make_readiness(14)
        state = {"pclc_count": 16}
        results = run_all_pclv(state, readiness)
        assert any(not r.passed for r in results)
        assert any(r.rule_id == "PCLV-01" and not r.passed for r in results)


# ============================================================
# SHV-01
# ============================================================

class TestSHV01:
    def test_pass_no_pfx(self):
        git_status = "M  src/example.py\nA  tests/test_foo.py\n"
        result = shv_01_no_pfx_untracked_or_staged(git_status)
        assert result.passed

    def test_fail_wave15_pattern_untracked_pfx(self):
        """Regression: Wave 15 had test-cert.pfx as untracked."""
        git_status = "?? test-cert.pfx\nM  src/example.py\n"
        result = shv_01_no_pfx_untracked_or_staged(git_status)
        assert not result.passed
        assert "test-cert.pfx" in str(result.detail)

    def test_fail_staged_pfx(self):
        git_status = "A  credentials.pfx\n"
        result = shv_01_no_pfx_untracked_or_staged(git_status)
        assert not result.passed

    def test_pass_gitignored_pfx_not_in_status(self):
        """If .pfx is gitignored, it won't appear in git status --short output at all."""
        git_status = "M  src/example.py\n"  # No pfx in output
        result = shv_01_no_pfx_untracked_or_staged(git_status)
        assert result.passed


# ============================================================
# SHV-02
# ============================================================

class TestSHV02:
    def test_pass_no_secret_files(self):
        result = shv_02_no_pem_key_p12_untracked_or_staged("M  src/foo.py\n")
        assert result.passed

    def test_fail_untracked_pem(self):
        result = shv_02_no_pem_key_p12_untracked_or_staged("?? server.pem\n")
        assert not result.passed

    def test_fail_staged_key(self):
        result = shv_02_no_pem_key_p12_untracked_or_staged("A  private.key\n")
        assert not result.passed

    def test_fail_p12(self):
        result = shv_02_no_pem_key_p12_untracked_or_staged("?? identity.p12\n")
        assert not result.passed


# ============================================================
# SHV-03
# ============================================================

class TestSHV03:
    def test_pass_no_credential_filenames(self):
        result = shv_03_no_credential_filenames_staged("M  src/validators.py\n")
        assert result.passed

    def test_fail_staged_token_file(self):
        result = shv_03_no_credential_filenames_staged("A  api-token.json\n")
        assert not result.passed

    def test_fail_staged_secret_file(self):
        result = shv_03_no_credential_filenames_staged("A  secrets.json\n")
        assert not result.passed

    def test_pass_untracked_credential_file_not_staged(self):
        # SHV-03 only fires on staged files (code 'A' or 'M' in index position)
        result = shv_03_no_credential_filenames_staged("?? secret.json\n")
        assert result.passed  # untracked doesn't trigger SHV-03


# ============================================================
# run_all_shv integration
# ============================================================

class TestRunAllSHV:
    def test_clean_git_status_all_pass(self):
        git_status = "M  src/validators.py\nA  tests/test_validators.py\n"
        results = run_all_shv(git_status)
        assert all(r.passed for r in results)
        assert len(results) == 3

    def test_wave15_git_status_pfx_fails(self):
        """Exact Wave 15 git status pattern: test-cert.pfx untracked."""
        git_status = "?? test-cert.pfx\nM  src/example.py\n?? input1.pdf\n"
        results = run_all_shv(git_status)
        failed = [r for r in results if not r.passed]
        assert any(r.rule_id == "SHV-01" for r in failed), "SHV-01 must fail for Wave 15 pattern"

    def test_post_wave16_gitignore_fix_passes(self):
        """After adding *.pfx to .gitignore, test-cert.pfx no longer appears in git status."""
        git_status = "M  .gitignore\nM  src/example.py\n"  # pfx gone from untracked
        results = run_all_shv(git_status)
        assert all(r.passed for r in results)
