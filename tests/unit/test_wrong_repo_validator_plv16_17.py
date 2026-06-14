"""Tests for PLV-16 (fixture source never a publication target) and
PLV-17 (PR URL allowlist) — Wave 25 Lane A.
"""

from __future__ import annotations

import pytest

from plugin_examples.fixture_factory.publication_lifecycle_validators import (
    _APPROVED_PUBLICATION_REPOS,
    _FIXTURE_SOURCE_REPO_OWNERS,
    PlvResult,
    check_plv_16_fixture_source_not_publication_target,
    check_plv_17_pr_url_allowlist,
)

# ── PLV-16 ─────────────────────────────────────────────────────────────────────


def test_plv16_pass_when_no_fixture_repos_referenced():
    result = PlvResult()
    check_plv_16_fixture_source_not_publication_target(
        ["aspose-barcode-net/Aspose.BarCode.Plugins-for-.NET-Examples"], result
    )
    assert result.failed == 0
    assert result.passed == 1


def test_plv16_fail_when_fixture_source_repo_referenced():
    result = PlvResult()
    check_plv_16_fixture_source_not_publication_target(["aspose-barcode/Aspose.BarCode-for-.NET"], result)
    assert result.failed == 1
    check = result.checks[0]
    assert check["status"] == "FAIL"
    assert check["code"] == "PLV-16"
    assert "aspose-barcode/Aspose.BarCode-for-.NET" in check["detail"]


def test_plv16_fail_detects_multiple_violations():
    result = PlvResult()
    check_plv_16_fixture_source_not_publication_target(
        [
            "aspose-svg/Aspose.SVG-for-.NET",
            "aspose-cad-net/Aspose.CAD.Plugins-for-.NET-Examples",
            "aspose-cells/Aspose.Cells-for-.NET",
        ],
        result,
    )
    assert result.failed == 1  # one FAIL call but lists multiple violations
    assert "aspose-svg/Aspose.SVG-for-.NET" in result.checks[0]["detail"]
    assert "aspose-cells/Aspose.Cells-for-.NET" in result.checks[0]["detail"]
    # publication target repo should NOT appear in violations
    assert "aspose-cad-net" not in result.checks[0]["detail"]


def test_plv16_pass_when_empty_list():
    result = PlvResult()
    check_plv_16_fixture_source_not_publication_target([], result)
    assert result.failed == 0
    assert result.passed == 1


# ── PLV-17 ─────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("repo", list(_APPROVED_PUBLICATION_REPOS))
def test_plv17_pass_for_all_approved_publication_repos(repo):
    result = PlvResult()
    url = f"https://github.com/{repo}/pull/1"
    check_plv_17_pr_url_allowlist(url, result)
    assert result.failed == 0
    assert result.passed == 1


def test_plv17_fail_for_fixture_source_repo_url():
    result = PlvResult()
    check_plv_17_pr_url_allowlist("https://github.com/aspose-barcode/Aspose.BarCode-for-.NET/pull/42", result)
    assert result.failed == 1
    assert result.checks[0]["code"] == "PLV-17"


def test_plv17_fail_for_unknown_repo_url():
    result = PlvResult()
    check_plv_17_pr_url_allowlist("https://github.com/some-org/some-repo/pull/99", result)
    assert result.failed == 1


def test_plv17_pass_for_barcode_publication_repo():
    result = PlvResult()
    check_plv_17_pr_url_allowlist(
        "https://github.com/aspose-barcode-net/Aspose.BarCode.Plugins-for-.NET-Examples/pull/1",
        result,
    )
    assert result.passed == 1
    assert result.failed == 0


# ── Separation invariant ───────────────────────────────────────────────────────


def test_fixture_source_owners_and_publication_repos_never_overlap():
    """Publication repos must use different org owners than fixture source repos."""
    for pub_repo in _APPROVED_PUBLICATION_REPOS:
        pub_owner = pub_repo.split("/")[0]
        assert pub_owner not in _FIXTURE_SOURCE_REPO_OWNERS, (
            f"Publication repo owner {pub_owner!r} conflicts with fixture source owners — "
            "repo separation policy violated"
        )
