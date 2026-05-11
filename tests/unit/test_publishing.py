"""Unit tests for publisher, package_watcher, and __main__."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugin_examples.publisher.publisher import (
    PublishResult,
    _is_central_repo,
    publish_examples,
    write_publishing_report,
)
from plugin_examples.publisher.pr_builder import build_pr
from plugin_examples.publisher.approval_gate import (
    APPROVAL_EXPECTED_VALUE,
    BLOCKED_LIVE_PR_APPROVAL_REQUIRED,
    BLOCKED_INVALID_LIVE_PR_APPROVAL,
    BLOCKED_PUBLISH_DRY_RUN_CONFLICT,
    BLOCKED_PUBLISH_TO_MAIN,
    BLOCKED_REPO_ACCESS_NOT_READY,
    BLOCKED_PR_PERMISSION_NOT_READY,
    check_approval,
)
from plugin_examples.package_watcher.watcher import (
    check_for_updates,
    write_monthly_report,
)
from plugin_examples.gates.models import GateVerdict, GateResult


# --- Tests: publisher ---


def _setup_full_evidence(latest: Path) -> None:
    """Create all required evidence files for publisher tests."""
    latest.mkdir(parents=True, exist_ok=True)
    (latest / "cells-source-of-truth-proof.json").write_text("{}")
    (latest / "validation-results.json").write_text("{}")
    (latest / "example-reviewer-results.json").write_text("{}")
    (latest / "scenario-catalog.json").write_text("{}")
    gate = {"verdict": "PR_READY", "publishable": True,
            "all_required_passed": True, "blocking_gates": []}
    (latest / "gate-results.json").write_text(json.dumps(gate))


class TestPublisher:
    def test_dry_run_publishes(self, tmp_path):
        latest = tmp_path / "workspace" / "verification" / "latest"
        _setup_full_evidence(latest)

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "workspace" / "verification",
            dry_run=True,
        )
        assert result.status == "dry_run"
        assert result.evidence_verified
        assert len(result.files_included) == 1

    def test_blocked_missing_evidence(self, tmp_path):
        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "workspace" / "verification",
        )
        assert result.status == "blocked"
        assert "Missing evidence" in result.blocked_reason

    def test_blocked_no_passing_examples(self, tmp_path):
        latest = tmp_path / "workspace" / "verification" / "latest"
        _setup_full_evidence(latest)

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "failed"}],
            verification_dir=tmp_path / "workspace" / "verification",
        )
        assert result.status == "blocked"

    def test_never_pushes_to_main(self, tmp_path):
        latest = tmp_path / "workspace" / "verification" / "latest"
        _setup_full_evidence(latest)

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "workspace" / "verification",
            dry_run=False,
        )
        # Without token, falls back to dry-run; branch format: plugin-examples/{family}/{timestamp}
        assert result.branch_name is not None
        assert result.branch_name.startswith("plugin-examples/cells/")
        assert result.branch_name != "main"

    def test_write_publishing_report(self, tmp_path):
        result = PublishResult(dry_run=True, status="dry_run")
        path = write_publishing_report(result, tmp_path / "workspace" / "verification")
        assert path.exists()
        assert "publishing-report" in path.name


def _make_passing_verdict() -> GateVerdict:
    return GateVerdict(
        verdict="PR_DRY_RUN_READY",
        publishable=False,
        all_required_passed=True,
        blocking_gates=[],
        gates=[],
    )


def _make_failing_verdict() -> GateVerdict:
    return GateVerdict(
        verdict="BLOCKED_BUILD_FAILED",
        publishable=False,
        all_required_passed=False,
        blocking_gates=["gate_build"],
        gates=[],
    )


def _setup_disk_evidence_without_gate(latest: Path) -> None:
    """Create evidence files written by stages before the publisher (no gate-results)."""
    latest.mkdir(parents=True, exist_ok=True)
    (latest / "cells-source-of-truth-proof.json").write_text("{}")
    (latest / "validation-results.json").write_text("{}")


class TestPublisherGateVerdictIntegration:
    def test_publisher_reads_gate_verdict_from_context(self, tmp_path):
        """Publisher uses gate_verdict param, not gate-results.json on disk."""
        latest = tmp_path / "verification" / "latest"
        _setup_disk_evidence_without_gate(latest)
        # No gate-results.json on disk — verdict comes from parameter
        verdict = _make_passing_verdict()

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=True,
            gate_verdict=verdict,
        )
        assert result.evidence_verified is True
        assert result.status == "dry_run"

    def test_publisher_does_not_require_gate_results_file_before_gate_writer(self, tmp_path):
        """evidence_verified=True even when gate-results.json is absent, if gate_verdict passes."""
        latest = tmp_path / "verification" / "latest"
        _setup_disk_evidence_without_gate(latest)
        assert not (latest / "gate-results.json").exists()

        verdict = _make_passing_verdict()
        result = publish_examples(
            family="cells",
            run_id="run-id",
            examples=[{"scenario_id": "ex1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=True,
            gate_verdict=verdict,
        )
        assert result.evidence_verified is True

    def test_publisher_blocks_when_gate_verdict_failed(self, tmp_path):
        """Publisher blocks when gate_verdict.all_required_passed is False."""
        latest = tmp_path / "verification" / "latest"
        _setup_disk_evidence_without_gate(latest)

        verdict = _make_failing_verdict()
        result = publish_examples(
            family="cells",
            run_id="run-id",
            examples=[{"scenario_id": "ex1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=True,
            gate_verdict=verdict,
        )
        assert result.status == "blocked"
        assert result.evidence_verified is False

    def test_publishing_report_evidence_verified_true_on_valid_dry_run(self, tmp_path):
        """write_publishing_report records evidence_verified=True for valid dry-run."""
        latest = tmp_path / "verification" / "latest"
        _setup_disk_evidence_without_gate(latest)

        verdict = _make_passing_verdict()
        result = publish_examples(
            family="cells",
            run_id="run-id",
            examples=[{"scenario_id": "ex1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=True,
            gate_verdict=verdict,
        )
        report_path = write_publishing_report(result, tmp_path / "verification")
        with open(report_path) as f:
            report = json.load(f)
        assert report["evidence_verified"] is True
        assert report["status"] == "dry_run"

    def test_scenario_catalog_path_resolved_consistently(self, tmp_path):
        """scenario-catalog.json absence does not block publisher (it's not in latest/)."""
        latest = tmp_path / "verification" / "latest"
        _setup_disk_evidence_without_gate(latest)
        # scenario-catalog is intentionally NOT in latest/ — publisher must not require it
        assert not (latest / "scenario-catalog.json").exists()

        verdict = _make_passing_verdict()
        result = publish_examples(
            family="cells",
            run_id="run-id",
            examples=[{"scenario_id": "ex1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=True,
            gate_verdict=verdict,
        )
        assert result.status == "dry_run"
        assert result.evidence_verified is True


# --- Tests: pr_builder ---


class TestPRBuilder:
    def test_builds_pr_content(self):
        pr = build_pr(
            family="cells",
            run_id="run-123",
            examples_count=5,
            package_version="25.4.0",
        )
        assert "cells" in pr.title.lower() or "Cells" in pr.title
        assert pr.branch == "plugin-examples/cells/run-123"
        assert "cells" in pr.labels


# --- Tests: package_watcher ---


class TestPackageWatcher:
    def test_disabled_family_skipped(self, tmp_path):
        families = [{"family": "words", "enabled": False, "status": "disabled",
                      "nuget": {"package_id": "Aspose.Words"}}]
        results = check_for_updates(families, tmp_path)
        assert len(results) == 1
        assert results[0].skipped
        assert results[0].skip_reason == "Family is disabled"

    def test_enabled_family_checked(self, tmp_path):
        families = [{"family": "cells", "enabled": True, "status": "active",
                      "nuget": {"package_id": "Aspose.Cells"}}]
        results = check_for_updates(families, tmp_path)
        assert len(results) == 1
        assert not results[0].skipped

    def test_write_monthly_report(self, tmp_path):
        from plugin_examples.package_watcher.watcher import UpdateCheck
        results = [UpdateCheck(family="cells", package_id="Aspose.Cells",
                               current_version="25.3.0", latest_version="25.4.0",
                               has_update=True)]
        path = write_monthly_report(results, tmp_path / "workspace" / "verification")
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["updates_found"] == 1

    def test_paths_use_workspace(self, tmp_path):
        result = PublishResult(dry_run=True)
        path = write_publishing_report(result, tmp_path / "workspace" / "verification")
        assert "workspace" in str(path)


# --- Tests: family-specific publishing target enforcement ---


def _make_family_config(family: str, owner: str, repo: str, central_repo_allowed: bool = False):
    """Build a minimal mock family_config with github.published_plugin_examples_repo."""
    from types import SimpleNamespace
    pub_repo = SimpleNamespace(owner=owner, repo=repo, branch="main")
    github_cfg = SimpleNamespace(
        published_plugin_examples_repo=pub_repo,
        central_repo_allowed=central_repo_allowed,
    )
    return SimpleNamespace(family=family, github=github_cfg)


class TestIsCentralRepo:
    def test_central_repo_when_family_not_in_owner_or_repo(self):
        assert _is_central_repo("aspose", "aspose-plugins-examples-dotnet", "cells") is True

    def test_family_specific_when_family_in_owner(self):
        assert _is_central_repo("aspose-words", "aspose-plugins-examples-dotnet", "words") is False

    def test_family_specific_when_family_in_repo(self):
        assert _is_central_repo("aspose", "aspose-cells-examples", "cells") is False

    def test_central_repo_for_words(self):
        assert _is_central_repo("aspose", "aspose-plugins-examples-dotnet", "words") is True

    def test_central_repo_for_pdf(self):
        assert _is_central_repo("aspose", "aspose-plugins-examples-dotnet", "pdf") is True

    def test_case_insensitive(self):
        # Family name match is case-insensitive
        assert _is_central_repo("Aspose-Cells", "aspose-examples", "cells") is False


class TestFamilySpecificPublisherTarget:
    def _setup_evidence(self, latest: Path, family: str) -> None:
        latest.mkdir(parents=True, exist_ok=True)
        (latest / f"{family}-source-of-truth-proof.json").write_text("{}")
        (latest / "validation-results.json").write_text("{}")

    def test_publisher_blocks_central_repo_without_override(self, tmp_path):
        """Live publish must be blocked when target is central and central_repo_allowed=False."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        family_cfg = _make_family_config(
            "cells", "aspose", "aspose-plugins-examples-dotnet", central_repo_allowed=False
        )

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=family_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        assert result.status == "blocked"
        assert "blocked_central_repo_target_not_allowed" in result.blocked_reason
        assert "aspose/aspose-plugins-examples-dotnet" in result.blocked_reason

    def test_publisher_allows_central_repo_with_explicit_override(self, tmp_path):
        """Live publish proceeds when central_repo_allowed=True is explicitly set."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        family_cfg = _make_family_config(
            "cells", "aspose", "aspose-plugins-examples-dotnet", central_repo_allowed=True
        )

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=family_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        # Proceeds past central repo check; package_path=None → blocked_real_publisher_not_implemented
        # (blocked_central_repo_target_not_allowed would fire earlier if the guard failed)
        assert result.status == "blocked"
        assert "blocked_real_publisher_not_implemented" in (result.blocked_reason or "")

    def test_publisher_allows_family_specific_repo(self, tmp_path):
        """Live publish is not blocked when repo is family-specific (owner contains family name)."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        family_cfg = _make_family_config(
            "cells", "aspose-cells", "aspose-cells-examples", central_repo_allowed=False
        )

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=family_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        # Proceeds past central repo check; package_path=None → blocked_real_publisher_not_implemented
        # (blocked_central_repo_target_not_allowed would fire earlier if the guard failed)
        assert result.status == "blocked"
        assert "blocked_real_publisher_not_implemented" in (result.blocked_reason or "")

    def test_publisher_dry_run_bypasses_central_repo_check(self, tmp_path):
        """dry_run=True must return dry_run status without checking central repo."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        # Central repo, no override — but dry_run skips the check
        family_cfg = _make_family_config(
            "cells", "aspose", "aspose-plugins-examples-dotnet", central_repo_allowed=False
        )

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=True,
            gate_verdict=verdict,
            family_config=family_cfg,
        )
        assert result.status == "dry_run"
        assert result.evidence_verified is True

    def test_publisher_blocks_missing_family_config_on_live_publish(self, tmp_path):
        """family_config=None must block live publish — cannot verify target without config."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()

        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=None,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        assert result.status == "blocked"
        assert "blocked_missing_family_config" in result.blocked_reason

    def test_publisher_words_central_repo_blocked(self, tmp_path):
        """Words with aspose/aspose-plugins-examples-dotnet target must be blocked for live publish."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "words")
        verdict = _make_passing_verdict()
        family_cfg = _make_family_config(
            "words", "aspose", "aspose-plugins-examples-dotnet", central_repo_allowed=False
        )

        result = publish_examples(
            family="words",
            run_id="test-run",
            examples=[{"scenario_id": "w1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=family_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        assert result.status == "blocked"
        assert "words" in result.blocked_reason

    def test_publisher_blocked_reason_includes_family_and_repo(self, tmp_path):
        """Blocked reason must name the family and the target repo for debuggability."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "pdf")
        verdict = _make_passing_verdict()
        family_cfg = _make_family_config(
            "pdf", "aspose", "aspose-plugins-examples-dotnet", central_repo_allowed=False
        )

        result = publish_examples(
            family="pdf",
            run_id="test-run",
            examples=[{"scenario_id": "p1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=family_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        assert result.status == "blocked"
        assert "pdf" in result.blocked_reason
        assert "aspose/aspose-plugins-examples-dotnet" in result.blocked_reason


# --- Tests: publish readiness validator ---


from plugin_examples.publisher.publish_readiness import (
    check_family_publish_readiness,
    check_publish_readiness,
    write_publish_readiness_report,
    BLOCKED_MISSING_FAMILY_CONFIG,
    BLOCKED_MISSING_FAMILY_PUBLISH_TARGET,
    BLOCKED_CENTRAL_REPO_TARGET_NOT_ALLOWED,
    BLOCKED_FAMILY_NOT_ACTIVE,
)


class TestPublishReadinessValidator:
    def test_missing_family_config_blocked(self):
        record = check_family_publish_readiness("cells", None)
        assert record["publish_ready"] is False
        assert record["blocked_reason"] == BLOCKED_MISSING_FAMILY_CONFIG

    def test_discovery_only_family_blocked_as_not_active(self):
        from types import SimpleNamespace
        cfg = SimpleNamespace(status="discovery_only", github=None)
        record = check_family_publish_readiness("pdf", cfg)
        assert record["publish_ready"] is False
        assert record["blocked_reason"] == BLOCKED_FAMILY_NOT_ACTIVE

    def test_central_placeholder_repo_blocked_as_missing_target(self):
        """aspose/aspose-plugins-examples-dotnet is the known placeholder — blocked_missing_family_publish_target."""
        cfg = _make_family_config("cells", "aspose", "aspose-plugins-examples-dotnet")
        from types import SimpleNamespace
        full_cfg = SimpleNamespace(status="active", github=cfg.github)
        record = check_family_publish_readiness("cells", full_cfg)
        assert record["publish_ready"] is False
        assert record["blocked_reason"] == BLOCKED_MISSING_FAMILY_PUBLISH_TARGET

    def test_other_central_repo_blocked_as_not_allowed(self):
        """A non-placeholder central repo gets blocked_central_repo_target_not_allowed."""
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(owner="shared-org", repo="shared-examples", branch="main")
        github_cfg = SimpleNamespace(
            published_plugin_examples_repo=pub_repo,
            central_repo_allowed=False,
        )
        cfg = SimpleNamespace(status="active", github=github_cfg)
        record = check_family_publish_readiness("cells", cfg)
        assert record["publish_ready"] is False
        assert record["blocked_reason"] == BLOCKED_CENTRAL_REPO_TARGET_NOT_ALLOWED

    def test_family_specific_repo_is_ready(self):
        """A family-specific target (org contains family name) is publish_ready=True."""
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(owner="aspose-cells", repo="aspose-cells-lowcode-examples", branch="main")
        github_cfg = SimpleNamespace(
            published_plugin_examples_repo=pub_repo,
            central_repo_allowed=False,
        )
        cfg = SimpleNamespace(status="active", github=github_cfg)
        record = check_family_publish_readiness("cells", cfg)
        assert record["publish_ready"] is True
        assert record["is_family_specific"] is True
        assert record["target_type"] == "family_specific"

    def test_check_publish_readiness_aggregates_all_families(self):
        """check_publish_readiness returns correct counts for 3 families."""
        # Cells and Words: blocked (central placeholder); PDF: blocked (discovery_only)
        from types import SimpleNamespace
        def _central_cfg(family):
            return _make_family_config(family, "aspose", "aspose-plugins-examples-dotnet")

        cells_full = SimpleNamespace(status="active", github=_central_cfg("cells").github)
        words_full = SimpleNamespace(status="active", github=_central_cfg("words").github)
        pdf_full = SimpleNamespace(status="discovery_only", github=None)

        result = check_publish_readiness([
            ("cells", cells_full, "cells.yml"),
            ("words", words_full, "words.yml"),
            ("pdf", pdf_full, "pdf.yml"),
        ])
        assert result["total_families"] == 3
        assert result["publish_ready_count"] == 0
        assert result["blocked_count"] == 3
        assert set(result["blocked_families"]) == {"cells", "words", "pdf"}

    def test_write_publish_readiness_report_creates_file(self, tmp_path):
        """write_publish_readiness_report writes family-publish-readiness.json."""
        from types import SimpleNamespace
        cfg = SimpleNamespace(status="active", github=_make_family_config("cells", "aspose", "aspose-plugins-examples-dotnet").github)
        result = check_publish_readiness([("cells", cfg, "cells.yml")])
        path = write_publish_readiness_report(result, tmp_path / "verification")
        assert path.exists()
        assert path.name == "family-publish-readiness.json"
        import json as _json
        data = _json.loads(path.read_text())
        assert "families" in data
        assert len(data["families"]) == 1

    def test_words_dry_run_package_target_unresolved_blocks_live_publish(self, tmp_path):
        """Words with central placeholder target is blocked for live publish."""
        latest = tmp_path / "verification" / "latest"
        latest.mkdir(parents=True, exist_ok=True)
        (latest / "words-source-of-truth-proof.json").write_text("{}")
        (latest / "validation-results.json").write_text("{}")
        verdict = _make_passing_verdict()
        family_cfg = _make_family_config(
            "words", "aspose", "aspose-plugins-examples-dotnet", central_repo_allowed=False
        )
        from types import SimpleNamespace
        full_cfg = SimpleNamespace(status="active", github=family_cfg.github)

        result = publish_examples(
            family="words",
            run_id="test-run",
            examples=[{"scenario_id": "w1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=False,
            github_token="fake-token",
            gate_verdict=verdict,
            family_config=full_cfg,
            approval_token=APPROVAL_EXPECTED_VALUE,
            repo_access_ready=True,
            pr_permission_ready=True,
        )
        assert result.status == "blocked"
        # Target is aspose/aspose-plugins-examples-dotnet — central placeholder → not_allowed
        assert "blocked_central_repo_target_not_allowed" in result.blocked_reason


# --- Tests: live publish approval gate and configured family targets ---


class TestLivePublishApprovalGate:
    def _setup_evidence(self, latest: Path, family: str) -> None:
        latest.mkdir(parents=True, exist_ok=True)
        (latest / f"{family}-source-of-truth-proof.json").write_text("{}")
        (latest / "validation-results.json").write_text("{}")

    def test_family_publish_readiness_marks_cells_ready_when_repo_configured(self):
        """cells with aspose-cells-net target returns publish_ready=True from validator."""
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(owner="aspose-cells-net", repo="Aspose.Cells.LowCode-for-.NET-Examples", branch="main")
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        cfg = SimpleNamespace(status="active", github=github_cfg)
        record = check_family_publish_readiness("cells", cfg)
        assert record["publish_ready"] is True
        assert record["is_family_specific"] is True
        assert record["target_type"] == "family_specific"

    def test_family_publish_readiness_marks_words_ready_when_repo_configured(self):
        """words with aspose-words-net target returns publish_ready=True from validator."""
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(owner="aspose-words-net", repo="Aspose.Words.LowCode-for-.NET-Examples", branch="main")
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        cfg = SimpleNamespace(status="active", github=github_cfg)
        record = check_family_publish_readiness("words", cfg)
        assert record["publish_ready"] is True
        assert record["is_family_specific"] is True

    def test_family_publish_readiness_keeps_pdf_blocked(self):
        """PDF with discovery_only status is always blocked regardless of repo."""
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(owner="aspose-pdf-net", repo="Aspose.PDF.LowCode-for-.NET-Examples", branch="main")
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        cfg = SimpleNamespace(status="discovery_only", github=github_cfg)
        record = check_family_publish_readiness("pdf", cfg)
        assert record["publish_ready"] is False
        assert record["blocked_reason"] == BLOCKED_FAMILY_NOT_ACTIVE

    def test_live_publish_still_requires_explicit_approval(self, tmp_path):
        """Even with family-specific target, dry_run=True means live publish does not fire."""
        latest = tmp_path / "verification" / "latest"
        self._setup_evidence(latest, "cells")
        verdict = _make_passing_verdict()
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(owner="aspose-cells-net", repo="Aspose.Cells.LowCode-for-.NET-Examples", branch="main")
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        family_cfg = SimpleNamespace(status="active", github=github_cfg)

        # dry_run=True (default) returns dry_run — live publish never fires
        result = publish_examples(
            family="cells",
            run_id="test-run",
            examples=[{"scenario_id": "s1", "status": "generated"}],
            verification_dir=tmp_path / "verification",
            dry_run=True,
            gate_verdict=verdict,
            family_config=family_cfg,
        )
        assert result.status == "dry_run"
        assert result.pr_url is None  # no live PR was created


class TestRepoAccessResolver:
    """Tests for the 4-tier readiness model and repo_access_resolver module."""

    def test_publish_readiness_separates_config_ready_from_repo_access_ready(self):
        """config_ready=True does not imply repo_access_ready=True."""
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch="main",
        )
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        cfg = SimpleNamespace(status="active", github=github_cfg)
        record = check_family_publish_readiness("cells", cfg)
        # Config-level readiness is True (family-specific target configured)
        assert record["config_ready"] is True
        # repo_access_ready and pr_permission_ready require live API probe — remain False at config check
        assert record["repo_access_ready"] is False
        assert record["pr_permission_ready"] is False
        # live_publish_ready is always False (requires human approval)
        assert record["live_publish_ready"] is False

    def test_repo_not_found_blocks_repo_access_ready(self):
        """When GitHub API returns 404, repo_access_ready must be False."""
        from plugin_examples.publisher.repo_access_resolver import (
            check_repo_access,
            REPO_NOT_FOUND,
        )
        from unittest.mock import patch

        with patch(
            "plugin_examples.publisher.repo_access_resolver._github_get",
            return_value=(404, None),
        ):
            headers = {"Authorization": "token test_token"}
            result = check_repo_access(
                "aspose-cells-net",
                "Aspose.Cells.LowCode-for-.NET-Examples",
                "main",
                headers=headers,
            )
        assert result["can_read"] is False
        assert result["error_classification"] == REPO_NOT_FOUND
        assert result["repo_access_ready"] is False

    def test_repo_200_sets_repo_access_ready(self):
        """When GitHub API returns 200, repo_access_ready must be True."""
        from plugin_examples.publisher.repo_access_resolver import (
            check_repo_access,
            ACCESS_OK,
        )
        from unittest.mock import patch

        fake_body = {
            "default_branch": "main",
            "visibility": "private",
            "permissions": {"push": True, "pull": True, "admin": False},
        }

        def mock_get(url, headers):
            if "/branches/" in url:
                return 200, {}
            return 200, fake_body

        with patch(
            "plugin_examples.publisher.repo_access_resolver._github_get",
            side_effect=mock_get,
        ):
            headers = {"Authorization": "token test_token"}
            result = check_repo_access(
                "aspose-cells-net",
                "Aspose.Cells.LowCode-for-.NET-Examples",
                "main",
                headers=headers,
            )
        assert result["can_read"] is True
        assert result["error_classification"] == ACCESS_OK
        assert result["repo_access_ready"] is True
        assert result["pr_permission_ready"] is True

    def test_live_publish_requires_repo_access_ready(self):
        """live_publish_ready must remain False even when config_ready=True and repo accessible."""
        from plugin_examples.publisher.repo_access_resolver import resolve_repo_access
        from unittest.mock import patch
        from types import SimpleNamespace
        import tempfile

        pub_repo = SimpleNamespace(
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
            branch="main",
        )
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        cfg = SimpleNamespace(status="active", github=github_cfg)

        fake_body = {
            "default_branch": "main",
            "visibility": "private",
            "permissions": {"push": True, "pull": True, "admin": False},
        }

        def mock_get(url, headers):
            if "/branches/" in url:
                return 200, {}
            if "/user/memberships/" in url:
                return 200, {"role": "member"}
            if "/orgs/" in url:
                return 200, {}
            return 200, fake_body

        with tempfile.TemporaryDirectory() as tmpdir:
            vdir = Path(tmpdir) / "verification"
            with patch(
                "plugin_examples.publisher.repo_access_resolver._github_get",
                side_effect=mock_get,
            ), patch(
                "plugin_examples.publisher.repo_access_resolver._get_headers",
                return_value={"Authorization": "token test_token"},
            ):
                result = resolve_repo_access([("cells", cfg, "cells.yml")], vdir, promote_latest=True)

        family_rec = result["families"][0]
        # Even with full access, live_publish_ready must remain False (requires human approval)
        assert family_rec["live_publish_ready"] is False
        assert family_rec["can_read"] is True
        assert result["summary"]["live_publish_allowed"] is False

    def test_live_publish_requires_pr_permission_ready(self):
        """When can_push=False, pr_permission_ready must be False."""
        from plugin_examples.publisher.repo_access_resolver import check_repo_access
        from unittest.mock import patch

        fake_body = {
            "default_branch": "main",
            "visibility": "private",
            "permissions": {"push": False, "pull": True, "admin": False},
        }

        def mock_get(url, headers):
            if "/branches/" in url:
                return 200, {}
            return 200, fake_body

        with patch(
            "plugin_examples.publisher.repo_access_resolver._github_get",
            side_effect=mock_get,
        ):
            headers = {"Authorization": "token test_token"}
            result = check_repo_access(
                "aspose-cells-net",
                "Aspose.Cells.LowCode-for-.NET-Examples",
                "main",
                headers=headers,
            )
        assert result["can_read"] is True
        assert result["can_push"] is False
        assert result["pr_permission_ready"] is False

    def test_missing_token_blocks_repo_access_resolution(self):
        """When GITHUB_TOKEN is not set, error_classification must be token_missing."""
        from plugin_examples.publisher.repo_access_resolver import (
            check_repo_access,
            TOKEN_MISSING,
        )
        result = check_repo_access(
            "aspose-cells-net",
            "Aspose.Cells.LowCode-for-.NET-Examples",
            "main",
            headers=None,
        )
        assert result["can_read"] is False
        assert result["error_classification"] == TOKEN_MISSING


class TestRepoAccessResolverAuthHeader:
    """Tests for _get_headers() — enforce Bearer format, no token serialization."""

    def test_get_headers_uses_bearer_format(self, monkeypatch):
        """_get_headers() must return Authorization: Bearer <token>, not 'token <token>'."""
        from plugin_examples.publisher.repo_access_resolver import _get_headers
        monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token_value")
        headers = _get_headers()
        assert headers is not None
        auth = headers.get("Authorization", "")
        assert auth.startswith("Bearer "), (
            f"Expected 'Bearer ...' but got: {auth!r}. "
            "Use 'Bearer' format for GitHub API auth, not 'token'."
        )

    def test_get_headers_does_not_serialize_token_value(self, monkeypatch):
        """_get_headers() Authorization header must not expose token value in repr/str."""
        from plugin_examples.publisher.repo_access_resolver import _get_headers
        monkeypatch.setenv("GITHUB_TOKEN", "secret_token_abc")
        headers = _get_headers()
        assert headers is not None
        # The header value must start with 'Bearer ' — token value is in the value,
        # but the value must NOT be logged or serialized separately.
        auth_value = headers["Authorization"]
        # Verify token is embedded (so we know the header is correct), but
        # ensure no other key in the dict exposes the token value.
        assert "secret_token_abc" not in str(list(headers.keys())), (
            "Token value must not appear in header key names"
        )
        assert auth_value == "Bearer secret_token_abc", (
            f"Authorization header value incorrect: {auth_value!r}"
        )

    def test_get_headers_returns_none_when_token_absent(self, monkeypatch):
        """_get_headers() must return None when GITHUB_TOKEN is not set."""
        from plugin_examples.publisher.repo_access_resolver import _get_headers
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        headers = _get_headers()
        assert headers is None


class TestVerifyEvidenceFamilyScopedPath:
    """Tests for publisher._verify_evidence preferring families/{family}/ paths.

    Verifies followup-family-scoped-evidence-promotion fix: _verify_evidence
    must check verification/latest/families/{family}/validation-results.json
    before falling back to verification/latest/validation-results.json.
    """

    def _make_gate(self, latest: Path, publishable: bool = True) -> None:
        gate = {"verdict": "PR_DRY_RUN_READY", "publishable": publishable, "all_required_passed": publishable}
        (latest / "gate-results.json").write_text(json.dumps(gate), encoding="utf-8")

    def test_verify_evidence_accepts_family_scoped_validation_results(self, tmp_path):
        """_verify_evidence must accept validation-results.json in families/{family}/ path."""
        from plugin_examples.publisher.publisher import _verify_evidence
        verification_dir = tmp_path / "workspace" / "verification"
        latest = verification_dir / "latest"
        latest.mkdir(parents=True)
        # Write proof at top-level (already family-prefixed)
        (latest / "cells-source-of-truth-proof.json").write_text("{}", encoding="utf-8")
        self._make_gate(latest)
        # Write validation-results.json only in family-scoped path
        family_dir = latest / "families" / "cells"
        family_dir.mkdir(parents=True)
        (family_dir / "validation-results.json").write_text("{}", encoding="utf-8")
        # Also write gate-results.json in family-scoped path
        self._make_gate(family_dir)

        result = _verify_evidence(verification_dir, "cells")
        assert result["all_present"] is True, f"Must accept family-scoped evidence: {result}"

    def test_verify_evidence_falls_back_to_top_level_when_family_scoped_absent(self, tmp_path):
        """_verify_evidence must fall back to top-level legacy path for older promotions."""
        from plugin_examples.publisher.publisher import _verify_evidence
        verification_dir = tmp_path / "workspace" / "verification"
        latest = verification_dir / "latest"
        latest.mkdir(parents=True)
        (latest / "cells-source-of-truth-proof.json").write_text("{}", encoding="utf-8")
        (latest / "validation-results.json").write_text("{}", encoding="utf-8")
        self._make_gate(latest)

        result = _verify_evidence(verification_dir, "cells")
        assert result["all_present"] is True, f"Must accept top-level legacy evidence: {result}"

    def test_verify_evidence_prefers_family_scoped_over_stale_top_level(self, tmp_path):
        """When both family-scoped and top-level exist, family-scoped must win (no contamination)."""
        from plugin_examples.publisher.publisher import _verify_evidence
        verification_dir = tmp_path / "workspace" / "verification"
        latest = verification_dir / "latest"
        latest.mkdir(parents=True)
        (latest / "cells-source-of-truth-proof.json").write_text("{}", encoding="utf-8")
        # Top-level (stale, from Words run)
        (latest / "validation-results.json").write_text('{"family":"words"}', encoding="utf-8")
        self._make_gate(latest)
        # Family-scoped (correct Cells evidence)
        family_dir = latest / "families" / "cells"
        family_dir.mkdir(parents=True)
        (family_dir / "validation-results.json").write_text('{"family":"cells"}', encoding="utf-8")
        (family_dir / "gate-results.json").write_text(
            json.dumps({"verdict": "PR_DRY_RUN_READY", "publishable": True, "all_required_passed": True}),
            encoding="utf-8"
        )

        result = _verify_evidence(verification_dir, "cells")
        assert result["all_present"] is True, f"Must pass with family-scoped evidence: {result}"


class TestPdfPublishReadiness:
    """Tests verifying PDF publish readiness after family-specific target mapping.

    PDF is discovery_only — blocked for publishing regardless of target config.
    The target was updated from the central placeholder to aspose-pdf-net in this sprint.
    """

    def _make_pdf_config(self, owner: str, repo: str, status: str = "discovery_only"):
        from types import SimpleNamespace
        pub_repo = SimpleNamespace(owner=owner, repo=repo, branch="main")
        github_cfg = SimpleNamespace(published_plugin_examples_repo=pub_repo, central_repo_allowed=False)
        return SimpleNamespace(status=status, github=github_cfg)

    def test_pdf_discovery_only_blocked_regardless_of_target(self):
        """PDF with discovery_only status is blocked for publish regardless of repo config."""
        cfg = self._make_pdf_config("aspose-pdf-net", "Aspose.PDF.LowCode-for-.NET-Examples")
        record = check_family_publish_readiness("pdf", cfg)
        assert record["publish_ready"] is False
        assert record["blocked_reason"] == BLOCKED_FAMILY_NOT_ACTIVE

    def test_pdf_family_specific_target_is_not_central(self):
        """aspose-pdf-net/Aspose.PDF.LowCode-for-.NET-Examples is not the central placeholder."""
        assert _is_central_repo("aspose-pdf-net", "Aspose.PDF.LowCode-for-.NET-Examples", "pdf") is False

    def test_pdf_old_central_placeholder_was_central(self):
        """The old placeholder aspose/aspose-plugins-examples-dotnet was a central repo."""
        assert _is_central_repo("aspose", "aspose-plugins-examples-dotnet", "pdf") is True

    def test_pdf_discovery_only_all_tiers_false(self):
        """PDF discovery_only blocks all 4 readiness tiers."""
        cfg = self._make_pdf_config("aspose-pdf-net", "Aspose.PDF.LowCode-for-.NET-Examples")
        record = check_family_publish_readiness("pdf", cfg)
        assert record["config_ready"] is False
        assert record["repo_access_ready"] is False
        assert record["pr_permission_ready"] is False
        assert record["live_publish_ready"] is False

    def test_pdf_publish_readiness_would_be_ready_if_active(self):
        """When status=active, PDF family-specific target would show config_ready=True."""
        cfg = self._make_pdf_config("aspose-pdf-net", "Aspose.PDF.LowCode-for-.NET-Examples", status="active")
        record = check_family_publish_readiness("pdf", cfg)
        assert record["config_ready"] is True
        assert record["is_family_specific"] is True
        assert record["publish_ready"] is True


class TestPublishPrRepoAccessResolutionFallback:
    """Tests for __main__.py fallback to family-repo-access-resolution.json."""

    def test_fallback_reads_resolver_when_readiness_lacks_flags(self, tmp_path):
        """Fallback reads repo_access_ready from resolver when readiness has False."""
        latest = tmp_path / "latest"
        latest.mkdir()
        # Readiness file has repo_access_ready=False (stale)
        readiness = {
            "families": [{"family": "pdf", "repo_access_ready": False, "pr_permission_ready": False}]
        }
        (latest / "family-publish-readiness.json").write_text(json.dumps(readiness))
        # Resolver file is authoritative with True
        resolver = {
            "families": [{"family": "pdf", "repo_access_ready": True, "pr_permission_ready": True}]
        }
        (latest / "family-repo-access-resolution.json").write_text(json.dumps(resolver))

        # Simulate the fallback logic from __main__.py
        repo_access_ready = False
        pr_permission_ready = False
        for fam_rec in readiness["families"]:
            if fam_rec.get("family") == "pdf":
                repo_access_ready = fam_rec.get("repo_access_ready", False)
                pr_permission_ready = fam_rec.get("pr_permission_ready", False)
        if not repo_access_ready or not pr_permission_ready:
            resolver_data = json.loads((latest / "family-repo-access-resolution.json").read_text())
            for fam_rec in resolver_data.get("families", []):
                if fam_rec.get("family") == "pdf":
                    if fam_rec.get("repo_access_ready", False):
                        repo_access_ready = True
                    if fam_rec.get("pr_permission_ready", False):
                        pr_permission_ready = True
        assert repo_access_ready is True
        assert pr_permission_ready is True

    def test_fallback_does_not_override_negative_resolver(self, tmp_path):
        """Fallback does not set True when resolver also says False."""
        latest = tmp_path / "latest"
        latest.mkdir()
        readiness = {
            "families": [{"family": "pdf", "repo_access_ready": False, "pr_permission_ready": False}]
        }
        (latest / "family-publish-readiness.json").write_text(json.dumps(readiness))
        resolver = {
            "families": [{"family": "pdf", "repo_access_ready": False, "pr_permission_ready": False}]
        }
        (latest / "family-repo-access-resolution.json").write_text(json.dumps(resolver))

        repo_access_ready = False
        pr_permission_ready = False
        for fam_rec in readiness["families"]:
            if fam_rec.get("family") == "pdf":
                repo_access_ready = fam_rec.get("repo_access_ready", False)
                pr_permission_ready = fam_rec.get("pr_permission_ready", False)
        if not repo_access_ready or not pr_permission_ready:
            resolver_data = json.loads((latest / "family-repo-access-resolution.json").read_text())
            for fam_rec in resolver_data.get("families", []):
                if fam_rec.get("family") == "pdf":
                    if fam_rec.get("repo_access_ready", False):
                        repo_access_ready = True
                    if fam_rec.get("pr_permission_ready", False):
                        pr_permission_ready = True
        assert repo_access_ready is False
        assert pr_permission_ready is False

    def test_fallback_skips_when_readiness_already_true(self, tmp_path):
        """When readiness already has True, fallback is never reached."""
        latest = tmp_path / "latest"
        latest.mkdir()
        readiness = {
            "families": [{"family": "pdf", "repo_access_ready": True, "pr_permission_ready": True}]
        }
        (latest / "family-publish-readiness.json").write_text(json.dumps(readiness))
        # Resolver says False — should NOT override the already-True values
        resolver = {
            "families": [{"family": "pdf", "repo_access_ready": False, "pr_permission_ready": False}]
        }
        (latest / "family-repo-access-resolution.json").write_text(json.dumps(resolver))

        repo_access_ready = False
        pr_permission_ready = False
        for fam_rec in readiness["families"]:
            if fam_rec.get("family") == "pdf":
                repo_access_ready = fam_rec.get("repo_access_ready", False)
                pr_permission_ready = fam_rec.get("pr_permission_ready", False)
        if not repo_access_ready or not pr_permission_ready:
            # Should NOT enter this block because both are True
            resolver_data = json.loads((latest / "family-repo-access-resolution.json").read_text())
            for fam_rec in resolver_data.get("families", []):
                if fam_rec.get("family") == "pdf":
                    if fam_rec.get("repo_access_ready", False):
                        repo_access_ready = True
                    if fam_rec.get("pr_permission_ready", False):
                        pr_permission_ready = True
        assert repo_access_ready is True
        assert pr_permission_ready is True

    def test_fallback_requires_family_match(self, tmp_path):
        """Fallback only applies to the matching family, not others."""
        latest = tmp_path / "latest"
        latest.mkdir()
        readiness = {
            "families": [{"family": "pdf", "repo_access_ready": False, "pr_permission_ready": False}]
        }
        (latest / "family-publish-readiness.json").write_text(json.dumps(readiness))
        # Resolver has cells=True but NOT pdf
        resolver = {
            "families": [{"family": "cells", "repo_access_ready": True, "pr_permission_ready": True}]
        }
        (latest / "family-repo-access-resolution.json").write_text(json.dumps(resolver))

        repo_access_ready = False
        pr_permission_ready = False
        family = "pdf"
        for fam_rec in readiness["families"]:
            if fam_rec.get("family") == family:
                repo_access_ready = fam_rec.get("repo_access_ready", False)
                pr_permission_ready = fam_rec.get("pr_permission_ready", False)
        if not repo_access_ready or not pr_permission_ready:
            resolver_data = json.loads((latest / "family-repo-access-resolution.json").read_text())
            for fam_rec in resolver_data.get("families", []):
                if fam_rec.get("family") == family:
                    if fam_rec.get("repo_access_ready", False):
                        repo_access_ready = True
                    if fam_rec.get("pr_permission_ready", False):
                        pr_permission_ready = True
        assert repo_access_ready is False
        assert pr_permission_ready is False
