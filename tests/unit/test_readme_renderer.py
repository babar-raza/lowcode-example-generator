"""Tests for the root README template, renderer, auditor, and CLI command."""

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TEMPLATE_PATH = _REPO_ROOT / "templates" / "root-readme" / "lowcode-family-readme.md.j2"


def _make_family_config(
    family: str = "cells",
    display_name: str = "Aspose.Cells for .NET",
    nuget_package_id: str = "Aspose.Cells",
    owner: str = "aspose-cells-net",
    repo: str = "Aspose.Cells.LowCode-for-.NET-Examples",
    allowed_types: list[str] | None = None,
) -> MagicMock:
    """Build a minimal FamilyConfig-shaped mock."""
    cfg = MagicMock()
    cfg.family = family
    cfg.display_name = display_name

    cfg.nuget.package_id = nuget_package_id
    cfg.nuget.target_framework_preference = ["net8.0"]

    cfg.github.published_plugin_examples_repo.owner = owner
    cfg.github.published_plugin_examples_repo.repo = repo
    cfg.github.published_plugin_examples_repo.branch = "main"

    cfg.generation.allowed_types = allowed_types or []

    cfg.template_hints.default_input_extension = ".xlsx"
    return cfg


def _make_examples(names: list[str], output_formats: dict[str, str] | None = None) -> list[dict]:
    """Build minimal example metadata list."""
    fmts = output_formats or {}
    return [{"name": n, "output_format": fmts.get(n, "")} for n in names]


# ---------------------------------------------------------------------------
# TestRootReadmeTemplate
# ---------------------------------------------------------------------------


class TestRootReadmeTemplate:
    """Template file structural requirements."""

    def test_root_readme_template_requires_family_metadata(self):
        """Template must use {{ display_name }}, {{ family }}, and {{ nuget_package_id }}."""
        assert _TEMPLATE_PATH.exists(), "Template file missing"
        content = _TEMPLATE_PATH.read_text(encoding="utf-8")
        assert "{{ display_name }}" in content, "Template must use {{ display_name }}"
        assert "{{ family }}" in content, "Template must use {{ family }}"
        assert "{{ nuget_package_id }}" in content, "Template must use {{ nuget_package_id }}"

    def test_root_readme_template_has_required_section_headings(self):
        """Template must contain all required section headings."""
        content = _TEMPLATE_PATH.read_text(encoding="utf-8")
        required = [
            "## Overview",
            "## Included Examples",
            "## Requirements",
            "## How to Run",
            "## Package Installation",
            "## Validation Status",
            "## Useful Links",
        ]
        for section in required:
            assert section in content, f"Template missing section: {section}"

    def test_root_readme_template_has_examples_loop(self):
        """Template must iterate over examples with a Jinja2 for-loop."""
        content = _TEMPLATE_PATH.read_text(encoding="utf-8")
        # Allow for whitespace-control variants: {% for ... %} or {%- for ... -%}
        assert "for ex in examples" in content, "Template must have examples for-loop"
        assert "{{ ex.name }}" in content, "Template must use ex.name"
        assert "{{ ex.api_class }}" in content, "Template must use ex.api_class"


# ---------------------------------------------------------------------------
# TestRootReadmeRenderer
# ---------------------------------------------------------------------------


class TestRootReadmeRenderer:
    """Tests for build_readme_context() and render_readme()."""

    def test_root_readme_renderer_uses_family_config(self):
        """build_readme_context must populate all required fields from family config."""
        from plugin_examples.publisher.readme_renderer import build_readme_context, ReadmeContext

        cfg = _make_family_config(
            family="cells",
            display_name="Aspose.Cells for .NET",
            nuget_package_id="Aspose.Cells",
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
        )
        examples = _make_examples(["html-converter", "pdf-converter"])

        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=examples,
            package_version="26.4.0",
        )

        assert isinstance(ctx, ReadmeContext)
        assert ctx.family == "cells"
        assert ctx.display_name == "Aspose.Cells for .NET"
        assert ctx.nuget_package_id == "Aspose.Cells"
        assert ctx.target_repo_owner == "aspose-cells-net"
        assert ctx.target_repo_name == "Aspose.Cells.LowCode-for-.NET-Examples"
        assert ctx.package_version == "26.4.0"
        assert ctx.target_framework == "net8.0"
        assert "Aspose.Cells" in ctx.nuget_url
        assert "aspose-cells-net" in ctx.target_repo_url

    def test_root_readme_renderer_lists_only_validated_examples(self, tmp_path):
        """render_readme must include exactly the examples provided — no extras."""
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_family_config()
        examples = _make_examples(
            ["html-converter", "pdf-converter"],
            output_formats={"html-converter": "html", "pdf-converter": "pdf"},
        )
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=examples,
            package_version="26.4.0",
        )
        rendered = render_readme(ctx)

        assert "html-converter" in rendered
        assert "pdf-converter" in rendered
        # No third example should appear
        assert "image-converter" not in rendered
        assert "spreadsheet-merger" not in rendered

    def test_root_readme_renderer_excludes_blocked_scenarios(self, tmp_path):
        """Blocked examples must not appear in the rendered README."""
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_family_config()
        # Only 2 examples provided — blocked ones are not in the list
        examples = _make_examples(["html-converter", "pdf-converter"])
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=examples,
            package_version="26.4.0",
        )
        rendered = render_readme(ctx)

        # These blocked scenarios from the plan must not appear
        assert "json-converter" not in rendered
        assert "spreadsheet-locker" not in rendered

    def test_root_readme_renderer_uses_family_specific_repo_links(self):
        """Rendered README must contain target-repo-specific links, not generic ones."""
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_family_config(
            family="words",
            display_name="Aspose.Words for .NET",
            nuget_package_id="Aspose.Words",
            owner="aspose-words-net",
            repo="Aspose.Words.LowCode-for-.NET-Examples",
            allowed_types=["Converter", "Watermarker", "Splitter", "Replacer"],
        )
        cfg.template_hints.default_input_extension = ".docx"

        examples = _make_examples(["converter", "watermarker"])
        ctx = build_readme_context(
            family="words",
            family_config=cfg,
            examples=examples,
            package_version="26.4.0",
        )
        rendered = render_readme(ctx)

        assert "aspose-words-net" in rendered
        assert "Aspose.Words.LowCode-for-.NET-Examples" in rendered
        assert "Aspose.Words" in rendered
        # No Cells content
        assert "aspose-cells-net" not in rendered
        assert "Aspose.Cells" not in rendered

    def test_root_readme_renderer_does_not_reference_central_repo(self):
        """Rendered README must not reference the central combined examples repo."""
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_family_config()
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=_make_examples(["html-converter"]),
            package_version="26.4.0",
        )
        rendered = render_readme(ctx)

        assert "aspose-plugins-examples-dotnet" not in rendered
        assert "central repo" not in rendered.lower()

    def test_root_readme_renderer_words_notes_controlled_pilot(self):
        """Words README must mention allowed types from the controlled pilot."""
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_family_config(
            family="words",
            display_name="Aspose.Words for .NET",
            nuget_package_id="Aspose.Words",
            owner="aspose-words-net",
            repo="Aspose.Words.LowCode-for-.NET-Examples",
            allowed_types=["Converter", "Watermarker", "Splitter", "Replacer"],
        )
        cfg.template_hints.default_input_extension = ".docx"
        examples = _make_examples(["converter", "watermarker", "splitter", "replacer"])
        ctx = build_readme_context(
            family="words",
            family_config=cfg,
            examples=examples,
            package_version="26.4.0",
        )
        rendered = render_readme(ctx)

        # The controlled pilot note must appear
        assert any(
            t in rendered for t in ["Converter", "Watermarker", "Splitter", "Replacer"]
        ), "Words README must mention at least one allowed type"
        assert "controlled pilot" in rendered.lower() or "Controlled pilot" in rendered


# ---------------------------------------------------------------------------
# TestWriteReadme
# ---------------------------------------------------------------------------


class TestWriteReadme:
    def test_write_readme_creates_file(self, tmp_path):
        """write_readme must create a file at the specified path."""
        from plugin_examples.publisher.readme_renderer import write_readme

        out_path = tmp_path / "README.md"
        content = "# Test README\n\nHello world.\n"
        result = write_readme(content, out_path)

        assert result == out_path
        assert out_path.exists()
        assert out_path.read_text(encoding="utf-8") == content


# ---------------------------------------------------------------------------
# TestRootReadmeAuditor
# ---------------------------------------------------------------------------


class TestRootReadmeAuditor:
    def _make_valid_readme(self, package_version: str = "26.4.0", example_names: list[str] | None = None) -> str:
        """Build a minimal valid README string that should pass audit."""
        names = example_names or ["html-converter", "pdf-converter"]
        rows = "\n".join(
            f"| `{n}` | `{n.replace('-', '').capitalize()}` | xlsx | html | "
            f"`dotnet run --project examples/cells/lowcode/{n}` |"
            for n in names
        )
        return f"""# Aspose.Cells for .NET LowCode Examples

## Overview

Aspose.Cells LowCode provides high-level APIs.

## Included Examples

| Example | Demonstrated API | Input | Output | Run |
|---------|-----------------|-------|--------|-----|
{rows}

## Requirements

- .NET 8.0+
- NuGet: Aspose.Cells v{package_version}

## How to Run

```bash
dotnet restore
dotnet run --project examples/cells/lowcode/html-converter
```

## Package Installation

```bash
dotnet add package Aspose.Cells
```

## Validation Status

Gate verdict: `PR_DRY_RUN_READY`

## Useful Links

- NuGet: https://www.nuget.org/packages/Aspose.Cells
- KB: https://kb.aspose.net/cells
"""

    def test_root_readme_auditor_passes_for_valid_readme(self):
        """audit_readme must return passed=True for a well-formed README."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        content = self._make_valid_readme()
        ctx = {
            "package_version": "26.4.0",
            "examples": [{"name": "html-converter"}, {"name": "pdf-converter"}],
            "family": "cells",
        }
        result = audit_readme(content, ctx)
        assert result.passed is True, f"Expected PASS but warnings: {result.warnings}"

    def test_root_readme_auditor_detects_missing_example(self):
        """audit_readme must fail when an expected example is absent from the table."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        content = self._make_valid_readme(example_names=["html-converter"])
        # Context expects 2 examples but README only has 1
        ctx = {
            "package_version": "26.4.0",
            "examples": [{"name": "html-converter"}, {"name": "pdf-converter"}],
            "family": "cells",
        }
        result = audit_readme(content, ctx)
        assert result.passed is False
        assert "pdf-converter" in result.missing_examples

    def test_root_readme_auditor_detects_stale_package_version(self):
        """audit_readme must fail when the package version in README doesn't match context."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        content = self._make_valid_readme(package_version="25.0.0")
        ctx = {
            "package_version": "26.4.0",  # newer version
            "examples": [{"name": "html-converter"}, {"name": "pdf-converter"}],
            "family": "cells",
        }
        result = audit_readme(content, ctx)
        assert result.passed is False
        assert result.stale_version is True

    def test_root_readme_auditor_detects_catalog_symbol_noise(self):
        """audit_readme must fail when raw catalog symbol noise is present."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        # Inject DocFX/catalog noise pattern
        content = self._make_valid_readme() + "\nM:Aspose.Cells.LowCode.HtmlConverter.Process("
        ctx = {
            "package_version": "26.4.0",
            "examples": [{"name": "html-converter"}, {"name": "pdf-converter"}],
            "family": "cells",
        }
        result = audit_readme(content, ctx)
        assert result.passed is False
        assert result.catalog_symbol_noise_found is True

    def test_root_readme_auditor_detects_missing_section(self):
        """audit_readme must fail when a required section is missing."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        # Build README without ## Package Installation
        content = self._make_valid_readme()
        content = content.replace("## Package Installation", "## Install")

        ctx = {
            "package_version": "26.4.0",
            "examples": [{"name": "html-converter"}, {"name": "pdf-converter"}],
            "family": "cells",
        }
        result = audit_readme(content, ctx)
        assert result.passed is False
        assert "## Package Installation" in result.missing_sections


# ---------------------------------------------------------------------------
# TestPackageWorkflowRendersReadme
# ---------------------------------------------------------------------------


class TestPackageWorkflowRendersReadme:
    def test_package_workflow_renders_root_readme(self, tmp_path):
        """build_readme_context + render_readme + write_readme pipeline writes file."""
        from plugin_examples.publisher.readme_renderer import (
            build_readme_context,
            render_readme,
            write_readme,
        )

        cfg = _make_family_config()
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=_make_examples(["html-converter", "pdf-converter"]),
            package_version="26.4.0",
        )
        content = render_readme(ctx)
        out = write_readme(content, tmp_path / "README.md")

        assert out.exists()
        assert "Aspose.Cells for .NET" in out.read_text(encoding="utf-8")
        assert "html-converter" in out.read_text(encoding="utf-8")
        assert "26.4.0" in out.read_text(encoding="utf-8")

    def test_monthly_update_regenerates_root_readme_when_examples_change(self, tmp_path):
        """Re-rendering with an updated example list overwrites the previous README."""
        from plugin_examples.publisher.readme_renderer import (
            build_readme_context,
            render_readme,
            write_readme,
        )

        cfg = _make_family_config()

        # First render: 2 examples
        ctx1 = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=_make_examples(["html-converter", "pdf-converter"]),
            package_version="26.4.0",
        )
        write_readme(render_readme(ctx1), tmp_path / "README.md")

        # Second render: 3 examples (new version)
        ctx2 = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=_make_examples(["html-converter", "pdf-converter", "image-converter"]),
            package_version="26.5.0",
        )
        write_readme(render_readme(ctx2), tmp_path / "README.md")

        content = (tmp_path / "README.md").read_text(encoding="utf-8")
        assert "26.5.0" in content
        assert "image-converter" in content
        # Old version not present
        assert "26.4.0" not in content


# ---------------------------------------------------------------------------
# TestCLIRenderRootReadme
# ---------------------------------------------------------------------------


class TestCLIRenderRootReadme:
    def _run_cli(self, args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-m", "plugin_examples"] + args,
            capture_output=True,
            text=True,
            timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(cwd or _REPO_ROOT),
        )

    def test_cli_render_root_readme_exits_zero_for_cells(self):
        """CLI render-root-readme for cells must exit 0 and write README + audit files."""
        result = self._run_cli(
            [
                "render-root-readme",
                "--family",
                "cells",
                "--package-path",
                "workspace/pr-dry-run/cells-controlled-pilot",
                "--promote-latest",
            ]
        )
        assert result.returncode == 0, f"Exit {result.returncode}\n{result.stderr}"
        assert "Audit: PASS" in result.stdout or "PASS" in result.stdout

        # Check outputs
        readme = _REPO_ROOT / "workspace" / "pr-dry-run" / "cells-controlled-pilot" / "README.md"
        audit = _REPO_ROOT / "workspace" / "verification" / "latest" / "cells-root-readme-audit.json"
        render = _REPO_ROOT / "workspace" / "verification" / "latest" / "cells-root-readme-render-result.json"
        assert readme.exists(), "README.md not written"
        assert audit.exists(), "Audit JSON not written"
        assert render.exists(), "Render result JSON not written"

        audit_data = json.loads(audit.read_text(encoding="utf-8"))
        assert audit_data["passed"] is True

    def test_cli_render_root_readme_exits_zero_for_words(self):
        """CLI render-root-readme for words must exit 0 and produce 4 examples."""
        result = self._run_cli(
            [
                "render-root-readme",
                "--family",
                "words",
                "--package-path",
                "workspace/pr-dry-run/words-controlled-pilot",
                "--promote-latest",
            ]
        )
        assert result.returncode == 0, f"Exit {result.returncode}\n{result.stderr}"

        render = _REPO_ROOT / "workspace" / "verification" / "latest" / "words-root-readme-render-result.json"
        assert render.exists()
        data = json.loads(render.read_text(encoding="utf-8"))
        assert data["examples_count"] == 9  # 8 main-class + 1 companion (signer); signer dir exists in package
        assert data["no_remote_write_performed"] is True


# ---------------------------------------------------------------------------
# TestPublishPrLiveBlocksOnAuditFailure
# ---------------------------------------------------------------------------


class TestPublishPrLiveBlocksOnAuditFailure:
    """Verify that publish-pr live mode blocks when README audit fails."""

    def test_publish_pr_source_blocks_live_on_audit_failure(self):
        """__main__.py publish-pr handler must return 1 for live mode when README audit fails.

        This test reads the source code to confirm the blocking conditional is structurally
        correct. It guards against future refactors that silently remove the live-publish block.
        """
        import re

        cmd_path = _REPO_ROOT / "src" / "plugin_examples" / "commands" / "publish_pr.py"
        source = cmd_path.read_text(encoding="utf-8")
        # Must have: if not _readme_audit.passed: if live_mode: return 1
        # Check the pattern exists as a block in the publish-pr README integration section
        assert "_readme_audit.passed" in source, "publish-pr must check _readme_audit.passed"
        assert re.search(
            r"not _readme_audit\.passed.*\n\s+if live_mode",
            source,
        ), "publish-pr must have 'if live_mode' guard inside the audit failure branch"
        # Also assert the live-mode branch returns 1
        assert re.search(
            r"if live_mode:\s*\n\s+print.*README audit FAILED.*\n\s+return 1",
            source,
        ), "publish-pr live mode must return 1 on README audit failure"

    def test_readme_audit_failure_is_detectable(self):
        """Verify audit_readme correctly classifies a stale-version README as failed.

        This ensures the audit used by publish-pr can surface failures that the
        live-mode guard will act on.
        """
        from plugin_examples.publisher.readme_auditor import audit_readme

        bad_readme = "\n".join(
            [
                "## Overview",
                "Content.",
                "## Included Examples",
                "| Example | Demonstrated API | Input | Output | Run |",
                "|---------|-----------------|-------|--------|-----|",
                "| `html-converter` | `HtmlConverter` | `xlsx` | `html` | `dotnet run` |",
                "## Requirements",
                "v25.0.0",  # stale version
                "## How to Run",
                "run it",
                "## Package Installation",
                "install",
                "## Validation Status",
                "gate",
                "## Useful Links",
                "links",
            ]
        )
        ctx = {
            "package_version": "26.4.0",  # newer version — should flag stale
            "examples": [{"name": "html-converter"}],
            "family": "cells",
        }
        result = audit_readme(bad_readme, ctx)
        assert result.passed is False, "Stale version must cause audit failure"
        assert result.stale_version is True


class TestPublishReadmeCommand:
    """Tests for the publish-readme CLI command."""

    def test_publish_readme_subparser_exists(self):
        """publish-readme must be a registered subcommand."""
        cmd_path = _REPO_ROOT / "src" / "plugin_examples" / "commands" / "publish_readme.py"
        source = cmd_path.read_text(encoding="utf-8")
        assert (
            '"publish-readme"' in source or "'publish-readme'" in source
        ), "publish-readme subparser must be registered"

    def test_publish_readme_requires_approval_for_live(self):
        """publish-readme must check approval_token before any live remote write."""
        cmd_path = _REPO_ROOT / "src" / "plugin_examples" / "commands" / "publish_readme.py"
        source = cmd_path.read_text(encoding="utf-8")
        # The publish-readme handler must call check_approval
        assert "check_approval" in source, "publish-readme must call check_approval()"
        # Must have live mode guard: if not approved: return 1
        import re

        assert re.search(
            r"if not approved:\s*\n\s+print.*blocked", source
        ), "publish-readme must return 1 when not approved"

    def test_publish_readme_uses_tempdir_for_readme_only(self):
        """publish-readme must create a temp dir with only README.md (not full package)."""
        cmd_path = _REPO_ROOT / "src" / "plugin_examples" / "commands" / "publish_readme.py"
        source = cmd_path.read_text(encoding="utf-8")
        assert (
            "TemporaryDirectory" in source
        ), "publish-readme must use tempfile.TemporaryDirectory for README-only commit"

    def test_publish_readme_no_change_detection_present(self):
        """publish-readme must detect when remote README already matches pipeline output."""
        cmd_path = _REPO_ROOT / "src" / "plugin_examples" / "commands" / "publish_readme.py"
        source = cmd_path.read_text(encoding="utf-8")
        assert "NO_CHANGE" in source, "publish-readme must have NO_CHANGE detection"
        assert (
            "remote_readme_content.strip() == readme_content.strip()" in source or "no_change" in source
        ), "publish-readme must compare remote vs rendered content"

    def test_publish_readme_dry_run_writes_simulation_evidence(self):
        """publish-readme dry-run must write {family}-readme-backfill-simulation.json."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "plugin_examples",
                "publish-readme",
                "--family",
                "cells",
                "--approval-token",
                "APPROVE_LIVE_PR",
                "--promote-latest",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            env={**__import__("os").environ, "PYTHONPATH": str(_REPO_ROOT / "src")},
            timeout=60,
        )
        assert result.returncode == 0, f"publish-readme dry-run must exit 0; got:\n{result.stdout}\n{result.stderr}"
        ev_path = _REPO_ROOT / "workspace" / "verification" / "latest" / "cells-readme-backfill-simulation.json"
        assert ev_path.exists(), f"Evidence file not created: {ev_path}"

    def test_publish_readme_dry_run_words_writes_simulation_evidence(self):
        """publish-readme dry-run for words must write words-readme-backfill-simulation.json."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "plugin_examples",
                "publish-readme",
                "--family",
                "words",
                "--approval-token",
                "APPROVE_LIVE_PR",
                "--promote-latest",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            env={**__import__("os").environ, "PYTHONPATH": str(_REPO_ROOT / "src")},
            timeout=60,
        )
        assert result.returncode == 0, f"publish-readme dry-run must exit 0; got:\n{result.stdout}\n{result.stderr}"
        ev_path = _REPO_ROOT / "workspace" / "verification" / "latest" / "words-readme-backfill-simulation.json"
        assert ev_path.exists(), f"Evidence file not created: {ev_path}"

    def test_publish_readme_dry_run_no_remote_write(self):
        """publish-readme dry-run simulation evidence must have no_remote_write_performed=true."""
        import json

        ev_path = _REPO_ROOT / "workspace" / "verification" / "latest" / "cells-readme-backfill-simulation.json"
        if not ev_path.exists():
            import pytest

            pytest.skip("Run test_publish_readme_dry_run_writes_simulation_evidence first")
        data = json.loads(ev_path.read_text(encoding="utf-8"))
        assert (
            data.get("no_remote_write_performed") is True
        ), "Dry-run evidence must confirm no remote write was performed"
        assert data.get("dry_run") is True, "Evidence must mark dry_run=true"

    def test_publish_readme_live_blocks_without_token(self):
        """publish-readme live mode must exit non-zero when GITHUB_TOKEN is absent."""
        import subprocess

        env_no_token = {k: v for k, v in __import__("os").environ.items() if k != "GITHUB_TOKEN"}
        env_no_token["PYTHONPATH"] = str(_REPO_ROOT / "src")
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "plugin_examples",
                "publish-readme",
                "--family",
                "cells",
                "--publish",
                "--approval-token",
                "APPROVE_LIVE_PR",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            env=env_no_token,
            timeout=30,
        )
        assert result.returncode != 0, "publish-readme live must fail when GITHUB_TOKEN is absent"
        assert (
            "GITHUB_TOKEN" in result.stdout or "GITHUB_TOKEN" in result.stderr
        ), "Error message must mention GITHUB_TOKEN"

    def test_publish_readme_live_blocks_without_approval(self):
        """publish-readme live mode must exit non-zero when approval token is wrong."""
        import subprocess

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "plugin_examples",
                "publish-readme",
                "--family",
                "cells",
                "--publish",
                "--approval-token",
                "WRONG_TOKEN",
            ],
            capture_output=True,
            text=True,
            cwd=str(_REPO_ROOT),
            env={**__import__("os").environ, "PYTHONPATH": str(_REPO_ROOT / "src"), "GITHUB_TOKEN": "dummy"},
            timeout=30,
        )
        assert result.returncode != 0, "publish-readme live must fail when approval token is wrong"
        assert (
            "blocked" in result.stdout.lower() or "blocked" in result.stderr.lower()
        ), "Error message must mention 'blocked'"


# ---------------------------------------------------------------------------
# TestManifestApiSymbolExtraction
# ---------------------------------------------------------------------------


class TestManifestApiSymbolExtraction:
    """Tests for read_manifest_api_symbol() and the package_path integration."""

    def _write_manifest(self, tmp_path: Path, claimed_symbols: list) -> Path:
        import json

        manifest = tmp_path / "example.manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "scenario_id": "test-scenario",
                    "package_id": "Aspose.Test",
                    "package_version": "26.4.0",
                    "target_framework": "net8.0",
                    "claimed_symbols": claimed_symbols,
                    "status": "generated",
                }
            ),
            encoding="utf-8",
        )
        return manifest

    def test_read_manifest_api_symbol_extracts_cells_process_method(self, tmp_path):
        from plugin_examples.publisher.readme_renderer import read_manifest_api_symbol

        manifest = self._write_manifest(
            tmp_path,
            [
                "Aspose.Cells.LowCode.HtmlConverter",
                "Aspose.Cells.LowCode.HtmlConverter.Process",
                "Aspose.Cells.LowCode.HtmlConverter.Process",
            ],
        )
        result = read_manifest_api_symbol(manifest)
        assert result == "HtmlConverter.Process"

    def test_read_manifest_api_symbol_extracts_words_specific_method(self, tmp_path):
        from plugin_examples.publisher.readme_renderer import read_manifest_api_symbol

        manifest = self._write_manifest(
            tmp_path,
            [
                "Aspose.Words.LowCode.Watermarker",
                "Aspose.Words.LowCode.Watermarker.SetText",
            ],
        )
        result = read_manifest_api_symbol(manifest)
        assert result == "Watermarker.SetText"

    def test_read_manifest_api_symbol_returns_none_for_missing_file(self, tmp_path):
        from plugin_examples.publisher.readme_renderer import read_manifest_api_symbol

        missing = tmp_path / "nonexistent" / "example.manifest.json"
        result = read_manifest_api_symbol(missing)
        assert result is None

    def test_read_manifest_api_symbol_returns_none_for_class_only_symbols(self, tmp_path):
        """When all symbols have ≤4 parts (class-only), return None."""
        from plugin_examples.publisher.readme_renderer import read_manifest_api_symbol

        manifest = self._write_manifest(
            tmp_path,
            [
                "Aspose.Cells.LowCode.HtmlConverter",
            ],
        )
        result = read_manifest_api_symbol(manifest)
        assert result is None

    def test_read_manifest_api_symbol_returns_none_for_empty_symbols(self, tmp_path):
        from plugin_examples.publisher.readme_renderer import read_manifest_api_symbol

        manifest = self._write_manifest(tmp_path, [])
        result = read_manifest_api_symbol(manifest)
        assert result is None

    def test_build_readme_context_reads_manifest_when_package_path_given(self, tmp_path):
        """When package_path is set, build_readme_context reads manifest for api_class."""
        from plugin_examples.publisher.readme_renderer import build_readme_context
        import json

        # Create manifest + Program.cs at expected path
        example_dir = tmp_path / "examples" / "cells" / "lowcode" / "html-converter"
        example_dir.mkdir(parents=True)
        (example_dir / "example.manifest.json").write_text(
            json.dumps(
                {
                    "claimed_symbols": [
                        "Aspose.Cells.LowCode.HtmlConverter",
                        "Aspose.Cells.LowCode.HtmlConverter.Process",
                    ]
                }
            ),
            encoding="utf-8",
        )
        (example_dir / "Program.cs").write_text(
            'class P { static void Main() { var i = "input.xlsx"; var o = "output.html"; } }',
            encoding="utf-8",
        )

        cfg = _make_family_config(
            family="cells",
            display_name="Aspose.Cells for .NET",
            nuget_package_id="Aspose.Cells",
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
        )
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=[{"name": "html-converter", "output_format": "html"}],
            package_version="26.4.0",
            package_path=tmp_path,
        )
        assert ctx.examples[0].api_class == "HtmlConverter.Process"

    def test_build_readme_context_falls_back_when_no_manifest(self, tmp_path):
        """When package_path set but manifest absent, fall back to _infer_api_class."""
        from plugin_examples.publisher.readme_renderer import build_readme_context

        # Create Program.cs but no manifest
        example_dir = tmp_path / "examples" / "cells" / "lowcode" / "html-converter"
        example_dir.mkdir(parents=True)
        (example_dir / "Program.cs").write_text(
            'class P { static void Main() { var i = "input.xlsx"; var o = "output.html"; } }',
            encoding="utf-8",
        )
        cfg = _make_family_config(
            family="cells",
            display_name="Aspose.Cells for .NET",
            nuget_package_id="Aspose.Cells",
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
        )
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=[{"name": "html-converter", "output_format": "html"}],
            package_version="26.4.0",
            package_path=tmp_path,  # no manifest file under tmp_path
        )
        assert ctx.examples[0].api_class == "HtmlConverter"

    def test_build_readme_context_skips_manifest_when_package_path_is_none(self):
        """When package_path=None (default), manifest is not read — inferred class name used."""
        from plugin_examples.publisher.readme_renderer import build_readme_context

        cfg = _make_family_config(
            family="cells",
            display_name="Aspose.Cells for .NET",
            nuget_package_id="Aspose.Cells",
            owner="aspose-cells-net",
            repo="Aspose.Cells.LowCode-for-.NET-Examples",
        )
        ctx = build_readme_context(
            family="cells",
            family_config=cfg,
            examples=[{"name": "html-converter", "output_format": "html"}],
            package_version="26.4.0",
            # package_path omitted — defaults to None
        )
        assert ctx.examples[0].api_class == "HtmlConverter"

    def test_auditor_warns_for_unqualified_api_class(self):
        """audit_readme warns when api_class column has no dot (class-only, no method)."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        readme = (
            "## Overview\n\n"
            "## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Description |\n"
            "|---------|-----------------|-------|--------|-------------|\n"
            "| `html-converter` | `HtmlConverter` | xlsx | html | Convert |\n\n"
            "## Requirements\n\n## How to Run\n\n## Package Installation\n\n"
            "## Validation Status\n\n## Useful Links\n\n"
        )
        context = {
            "package_version": "26.4.0",
            "examples": [{"name": "html-converter"}],
            "family": "cells",
        }
        result = audit_readme(readme, context)
        assert (
            "html-converter" in result.unqualified_api_classes
        ), "html-converter must be flagged as having unqualified api_class"
        assert any("HtmlConverter" in w for w in result.warnings), "Warning must mention the api_class value"

    def test_auditor_does_not_fail_for_unqualified_api_class(self):
        """Unqualified api_class is advisory only — must NOT set passed=False alone."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        # Complete README that satisfies all non-advisory checks, including kb link
        readme = (
            "## Overview\n\n"
            "## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Description |\n"
            "|---------|-----------------|-------|--------|-------------|\n"
            "| `html-converter` | `HtmlConverter` | xlsx | html | Convert |\n\n"
            "## Requirements\n\n## How to Run\n\n## Package Installation\n\n"
            "## Validation Status\n\n"
            "## Useful Links\n\nhttps://kb.aspose.net/cells/\n\n"
        )
        context = {
            "package_version": "",
            "examples": [{"name": "html-converter"}],
            "family": "cells",
        }
        result = audit_readme(readme, context)
        # Advisory: unqualified_api_classes is populated
        assert "html-converter" in result.unqualified_api_classes, "html-converter should be flagged as advisory"
        # But passed must be True — the qualifier warning is advisory only
        assert (
            result.passed is True
        ), "Unqualified api_class is advisory only — audit must still pass when no other issues"

    def test_auditor_accepts_method_qualified_api_class_without_unqualified_warning(self):
        """When api_class contains a dot (e.g. HtmlConverter.Process), no advisory warning."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        readme = (
            "## Overview\n\n"
            "## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Description |\n"
            "|---------|-----------------|-------|--------|-------------|\n"
            "| `html-converter` | `HtmlConverter.Process` | xlsx | html | Convert |\n\n"
            "## Requirements\n\n## How to Run\n\n## Package Installation\n\n"
            "## Validation Status\n\n## Useful Links\n\n"
        )
        context = {
            "package_version": "26.4.0",
            "examples": [{"name": "html-converter"}],
            "family": "cells",
        }
        result = audit_readme(readme, context)
        assert result.unqualified_api_classes == [], "No unqualified api_classes expected when method qualifier present"
        assert not any(
            "lacks method qualifier" in w for w in result.warnings
        ), "No advisory warning expected for method-qualified api_class"


# ---------------------------------------------------------------------------
# TestReadmeRendererAsposeNetUrls
# ---------------------------------------------------------------------------


class TestReadmeRendererAsposeNetUrls:
    """Verify that build_readme_context() produces canonical aspose.net links."""

    def _build_ctx(self, family: str = "cells") -> object:
        from plugin_examples.publisher.readme_renderer import build_readme_context

        cfg = _make_family_config(
            family=family,
            display_name=f"Aspose.{family.capitalize()} for .NET",
            nuget_package_id=f"Aspose.{family.capitalize()}",
            owner=f"aspose-{family}-net",
            repo=f"Aspose.{family.capitalize()}.LowCode-for-.NET-Examples",
        )
        return build_readme_context(
            family=family,
            family_config=cfg,
            examples=[{"name": "html-converter", "output_format": "html"}],
            package_version="26.4.0",
        )

    def test_readme_context_cells_product_url_is_aspose_net(self):
        ctx = self._build_ctx("cells")
        assert "aspose.net" in ctx.product_page_url
        assert "aspose.com" not in ctx.product_page_url
        assert ctx.product_page_url == "https://products.aspose.net/cells"

    def test_readme_context_cells_docs_url_is_aspose_net(self):
        ctx = self._build_ctx("cells")
        assert ctx.docs_url == "https://docs.aspose.net/cells"

    def test_readme_context_has_kb_url(self):
        ctx = self._build_ctx("cells")
        assert hasattr(ctx, "kb_url"), "ReadmeContext must have kb_url field"
        assert "kb.aspose.net" in ctx.kb_url

    def test_readme_context_has_contact_url(self):
        ctx = self._build_ctx("cells")
        assert hasattr(ctx, "contact_url"), "ReadmeContext must have contact_url field"
        assert ctx.contact_url == "https://about.aspose.net/contact/"

    def test_readme_context_no_net_suffix_on_product_url(self):
        for family in ("cells", "words", "pdf"):
            ctx = self._build_ctx(family)
            assert not ctx.product_page_url.endswith(
                "/net"
            ), f"product_page_url must not end with /net: {ctx.product_page_url}"

    def test_readme_context_blog_url_uses_categories_pattern(self):
        ctx = self._build_ctx("cells")
        assert "/categories/" in ctx.blog_url
        assert "aspose.cells-plugin-family" in ctx.blog_url

    def test_rendered_cells_readme_has_no_aspose_com(self):
        """Full render of Cells README must contain no forbidden aspose.com links."""
        from plugin_examples.publisher.readme_renderer import render_readme
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links

        ctx = self._build_ctx("cells")
        rendered = render_readme(ctx)
        forbidden = find_forbidden_aspose_com_links(rendered)
        assert forbidden == [], f"Rendered Cells README has forbidden links: {forbidden}"

    def test_rendered_words_readme_has_no_aspose_com(self):
        """Full render of Words README must contain no forbidden aspose.com links."""
        from plugin_examples.publisher.readme_renderer import render_readme
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links

        cfg = _make_family_config(
            family="words",
            display_name="Aspose.Words for .NET",
            nuget_package_id="Aspose.Words",
            owner="aspose-words-net",
            repo="Aspose.Words.LowCode-for-.NET-Examples",
        )
        from plugin_examples.publisher.readme_renderer import build_readme_context

        ctx = build_readme_context(
            family="words",
            family_config=cfg,
            examples=[{"name": "converter", "output_format": "docx"}],
            package_version="26.4.0",
        )
        rendered = render_readme(ctx)
        forbidden = find_forbidden_aspose_com_links(rendered)
        assert forbidden == [], f"Rendered Words README has forbidden links: {forbidden}"


# ---------------------------------------------------------------------------
# Diagram README healing regression tests
# ---------------------------------------------------------------------------

_DIAGRAM_CONVERTER_PROGRAM_CS = """\
using System;
using System.IO;
using Aspose.Diagram;
using Aspose.Diagram.LowCode;

class Program
{
    static void Main()
    {
        string workDir = Path.Combine(Path.GetTempPath(), "Demo");
        Directory.CreateDirectory(workDir);

        string inputPath = Path.Combine(workDir, "input.vsdx");
        string outputPath = Path.Combine(workDir, "output.vdx");

        var diagram = new Diagram();
        diagram.Save(inputPath, SaveFileFormat.Vsdx);

        DiagramConverter.Process(inputPath, outputPath);

        Console.WriteLine("Done");
    }
}
"""

_PDF_CONVERTER_PROGRAM_CS = """\
using System;
using System.IO;
using Aspose.Diagram;
using Aspose.Diagram.LowCode;

class Program
{
    static void Main()
    {
        string workDir = Path.Combine(Path.GetTempPath(), "Demo");
        Directory.CreateDirectory(workDir);

        string inputPath = Path.Combine(workDir, "input.vsdx");
        string outputPath = Path.Combine(workDir, "output.pdf");

        var diagram = new Diagram();
        diagram.Save(inputPath, SaveFileFormat.Vsdx);

        PdfConverter.Process(inputPath, outputPath);

        Console.WriteLine("Done");
    }
}
"""


def _make_diagram_config():
    """Build a minimal Diagram FamilyConfig mock."""
    return _make_family_config(
        family="diagram",
        display_name="Aspose.Diagram for .NET",
        nuget_package_id="Aspose.Diagram",
        owner="aspose-diagram-net",
        repo="Aspose.Diagram.LowCode-for-.NET-Examples",
        allowed_types=["DiagramConverter", "PdfConverter"],
    )


def _setup_diagram_package(tmp_path):
    """Create a mock package directory with Program.cs files for diagram examples."""
    for name, content in [
        ("diagram-diagram-converter", _DIAGRAM_CONVERTER_PROGRAM_CS),
        ("diagram-pdf-converter", _PDF_CONVERTER_PROGRAM_CS),
    ]:
        prog_dir = tmp_path / "examples" / "diagram" / "lowcode" / name
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(content, encoding="utf-8")
    return tmp_path


class TestDiagramReadmeFactsExtraction:
    """TC-README-CLAIMS-001 regression tests: facts extraction from Program.cs."""

    def test_diagram_facts_extraction_returns_vsdx_vdx_pdf(self, tmp_path):
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        pkg = _setup_diagram_package(tmp_path)
        examples = [{"name": "diagram-diagram-converter"}, {"name": "diagram-pdf-converter"}]
        facts = extract_example_readme_facts("diagram", pkg, examples)

        assert len(facts.facts) == 2
        dc = next(f for f in facts.facts if f.example_name == "diagram-diagram-converter")
        pc = next(f for f in facts.facts if f.example_name == "diagram-pdf-converter")

        assert dc.input_extension == "vsdx"
        assert dc.output_extension == "vdx"
        assert dc.validation_status == "verified"
        assert dc.proof_source == "program_cs"

        assert pc.input_extension == "vsdx"
        assert pc.output_extension == "pdf"
        assert pc.validation_status == "verified"

    def test_facts_include_sha256_and_snippet(self, tmp_path):
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        pkg = _setup_diagram_package(tmp_path)
        examples = [{"name": "diagram-diagram-converter"}]
        facts = extract_example_readme_facts("diagram", pkg, examples)

        fact = facts.facts[0]
        assert fact.source_file_sha256, "SHA256 must be non-empty"
        assert len(fact.source_file_sha256) == 64
        assert fact.snippet_content, "Snippet must be non-empty"
        assert "DiagramConverter.Process" in fact.snippet_content
        assert fact.snippet_mode == "full_file"


class TestDiagramReadmeNoXlsx:
    """TC-README-XLSX-002 regression tests: no xlsx claims for diagram."""

    def test_diagram_readme_no_xlsx_in_table(self, tmp_path):
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_diagram_config()
        cfg.template_hints.default_input_extension = ".vsdx"
        cfg.template_hints.default_output_extension = ".vdx"
        pkg = _setup_diagram_package(tmp_path)
        examples = [{"name": "diagram-diagram-converter"}, {"name": "diagram-pdf-converter"}]

        ctx = build_readme_context(
            family="diagram",
            family_config=cfg,
            examples=examples,
            package_version="26.1.0",
            package_path=pkg,
        )
        rendered = render_readme(ctx)

        # Table must not contain xlsx
        import re

        table_match = re.search(r"## Included Examples\s*\n(.*?)(?=\n## |\Z)", rendered, re.DOTALL)
        assert table_match, "Examples table not found"
        table = table_match.group(1)
        assert "xlsx" not in table.lower(), f"xlsx found in Diagram examples table: {table}"

    def test_diagram_readme_correct_formats(self, tmp_path):
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_diagram_config()
        cfg.template_hints.default_input_extension = ".vsdx"
        cfg.template_hints.default_output_extension = ".vdx"
        pkg = _setup_diagram_package(tmp_path)
        examples = [{"name": "diagram-diagram-converter"}, {"name": "diagram-pdf-converter"}]

        ctx = build_readme_context(
            family="diagram",
            family_config=cfg,
            examples=examples,
            package_version="26.1.0",
            package_path=pkg,
        )
        rendered = render_readme(ctx)

        assert "| `vsdx` | `vdx` |" in rendered
        assert "| `vsdx` | `pdf` |" in rendered

    def test_diagram_generic_output_no_xlsx(self, tmp_path):
        """The generic output line should not mention xlsx for diagram."""
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_diagram_config()
        cfg.template_hints.default_input_extension = ".vsdx"
        cfg.template_hints.default_output_extension = ".vdx"
        pkg = _setup_diagram_package(tmp_path)
        examples = [{"name": "diagram-diagram-converter"}, {"name": "diagram-pdf-converter"}]

        ctx = build_readme_context(
            family="diagram",
            family_config=cfg,
            examples=examples,
            package_version="26.1.0",
            package_path=pkg,
        )
        rendered = render_readme(ctx)

        # Find the line with "output file in the project directory"
        for line in rendered.splitlines():
            if "output file in the project" in line:
                assert "xlsx" not in line.lower(), f"xlsx in generic output line: {line}"
                break


class TestSnippetPresent:
    """TC-README-SNIPPETS-003 regression tests."""

    def test_snippet_present_from_program_cs(self, tmp_path):
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme

        cfg = _make_diagram_config()
        cfg.template_hints.default_input_extension = ".vsdx"
        cfg.template_hints.default_output_extension = ".vdx"
        pkg = _setup_diagram_package(tmp_path)
        examples = [{"name": "diagram-diagram-converter"}]

        ctx = build_readme_context(
            family="diagram",
            family_config=cfg,
            examples=examples,
            package_version="26.1.0",
            package_path=pkg,
        )
        rendered = render_readme(ctx)

        assert "## Source Code" in rendered
        assert "DiagramConverter.Process" in rendered
        assert "<details>" in rendered


class TestAuditorFormatAndXlsxGuard:
    """TC-README-AUDITOR-004 regression tests."""

    def test_auditor_rejects_format_mismatch(self):
        from plugin_examples.publisher.readme_auditor import audit_readme

        readme = (
            "## Overview\n\n## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Run |\n"
            "|---------|-----------------|-------|--------|-----|\n"
            "| `ex1` | `Converter.Process` | `xlsx` | `pdf` | cmd |\n\n"
            "## Requirements\n## How to Run\n## Package Installation\n"
            "## Validation Status\n## Useful Links\n"
        )
        context = {
            "package_version": "",
            "examples": [{"name": "ex1", "input_format": "vsdx", "output_format": "pdf"}],
            "family": "diagram",
        }
        result = audit_readme(readme, context)
        assert not result.passed
        assert len(result.wrong_format_claims) > 0
        assert "vsdx" in result.wrong_format_claims[0]

    def test_auditor_rejects_xlsx_for_non_cells(self):
        from plugin_examples.publisher.readme_auditor import audit_readme

        readme = (
            "## Overview\n\n## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Run |\n"
            "|---------|-----------------|-------|--------|-----|\n"
            "| `ex1` | `DiagramConverter.Process` | `xlsx` | `xlsx` | cmd |\n\n"
            "## Requirements\n## How to Run\n## Package Installation\n"
            "## Validation Status\n## Useful Links\n"
        )
        context = {
            "package_version": "",
            "examples": [{"name": "ex1"}],
            "family": "diagram",
        }
        result = audit_readme(readme, context)
        assert not result.passed
        assert result.xlsx_cross_family_violation

    def test_auditor_accepts_xlsx_for_cells(self):
        from plugin_examples.publisher.readme_auditor import audit_readme

        readme = (
            "## Overview\n\n## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Run |\n"
            "|---------|-----------------|-------|--------|-----|\n"
            "| `ex1` | `HtmlConverter.Process` | `xlsx` | `html` | cmd |\n\n"
            "## Requirements\n## How to Run\n## Package Installation\n"
            "## Validation Status\n## Useful Links\n"
        )
        context = {
            "package_version": "",
            "examples": [{"name": "ex1"}],
            "family": "cells",
        }
        result = audit_readme(readme, context)
        assert not result.xlsx_cross_family_violation


class TestFailClosedBehavior:
    """Fail-closed regression tests."""

    def test_output_cannot_fallback_to_input_extension(self, tmp_path):
        """When facts are available, output comes from Program.cs, not config default."""
        from plugin_examples.publisher.readme_renderer import build_readme_context

        cfg = _make_diagram_config()
        cfg.template_hints.default_input_extension = ".vsdx"
        cfg.template_hints.default_output_extension = ".vdx"
        pkg = _setup_diagram_package(tmp_path)

        ctx = build_readme_context(
            family="diagram",
            family_config=cfg,
            examples=[{"name": "diagram-diagram-converter"}],
            package_version="26.1.0",
            package_path=pkg,
        )
        # Output must be vdx (from Program.cs), not vsdx (input extension)
        assert ctx.examples[0].output_format == "vdx"
        assert ctx.examples[0].input_format == "vsdx"

    def test_unknown_format_raises_valueerror(self, tmp_path):
        """If Program.cs lacks output pattern, build_readme_context raises ValueError with strict_facts."""
        from plugin_examples.publisher.readme_renderer import build_readme_context

        cfg = _make_diagram_config()
        cfg.template_hints.default_input_extension = ".vsdx"
        cfg.template_hints.default_output_extension = ".vdx"

        # Create a Program.cs without output pattern
        prog_dir = tmp_path / "examples" / "diagram" / "lowcode" / "broken-example"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(
            'class Program { static void Main() { var x = "input.vsdx"; } }',
            encoding="utf-8",
        )

        with pytest.raises(ValueError, match="unverified"):
            build_readme_context(
                family="diagram",
                family_config=cfg,
                examples=[{"name": "broken-example"}],
                package_version="26.1.0",
                package_path=tmp_path,
                strict_facts=True,
            )


# ---------------------------------------------------------------------------
# Extended facts extraction tests (portfolio generalization)
# ---------------------------------------------------------------------------


class TestExtendedFactsExtraction:
    """Lane D: Generalized facts extraction for non-Diagram families."""

    def test_words_template_input_pattern(self, tmp_path):
        """Words mail-merger uses template.docx, result.docx — extended patterns."""
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        prog_dir = tmp_path / "examples" / "words" / "lowcode" / "mail-merger"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(
            'class P { static void Main() { string t = "template.docx"; string r = "result.docx"; } }',
            encoding="utf-8",
        )

        facts = extract_example_readme_facts("words", tmp_path, [{"name": "mail-merger"}])
        fact = facts.facts[0]
        assert fact.input_extension == "docx", f"Expected docx, got {fact.input_extension}"
        assert fact.output_extension == "docx", f"Expected docx, got {fact.output_extension}"
        assert fact.validation_status == "verified"

    def test_words_comparer_input1_pattern(self, tmp_path):
        """Words comparer uses input1.docx, output.docx — extended input pattern."""
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        prog_dir = tmp_path / "examples" / "words" / "lowcode" / "comparer"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(
            'class P { static void Main() { string i = "input1.docx"; string o = "output.docx"; } }',
            encoding="utf-8",
        )

        facts = extract_example_readme_facts("words", tmp_path, [{"name": "comparer"}])
        fact = facts.facts[0]
        assert fact.input_extension == "docx"
        assert fact.output_extension == "docx"
        assert fact.validation_status == "verified"

    def test_words_report_builder_report_output(self, tmp_path):
        """Words report-builder uses template.docx, report.docx — extended patterns."""
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        prog_dir = tmp_path / "examples" / "words" / "lowcode" / "report-builder"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(
            'class P { static void Main() { string t = "template.docx"; string r = "report.docx"; } }',
            encoding="utf-8",
        )

        facts = extract_example_readme_facts("words", tmp_path, [{"name": "report-builder"}])
        fact = facts.facts[0]
        assert fact.input_extension == "docx"
        assert fact.output_extension == "docx"
        assert fact.validation_status == "verified"

    def test_pdf_json_output(self, tmp_path):
        """PDF form-exporter uses input.pdf, output.json."""
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        prog_dir = tmp_path / "examples" / "pdf" / "lowcode" / "form-exporter"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(
            'class P { static void Main() { string i = "input.pdf"; string o = "output.json"; } }',
            encoding="utf-8",
        )

        facts = extract_example_readme_facts("pdf", tmp_path, [{"name": "form-exporter"}])
        fact = facts.facts[0]
        assert fact.input_extension == "pdf"
        assert fact.output_extension == "json"
        assert fact.validation_status == "verified"

    def test_cells_standard_patterns(self, tmp_path):
        """Cells uses input.xlsx, output.html — standard patterns."""
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        prog_dir = tmp_path / "examples" / "cells" / "lowcode" / "html-converter"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(
            'class P { static void Main() { string i = "input.xlsx"; string o = "output.html"; } }',
            encoding="utf-8",
        )

        facts = extract_example_readme_facts("cells", tmp_path, [{"name": "html-converter"}])
        fact = facts.facts[0]
        assert fact.input_extension == "xlsx"
        assert fact.output_extension == "html"
        assert fact.validation_status == "verified"

    def test_no_output_pattern_is_blocked(self, tmp_path):
        """Examples with no recognizable output pattern are blocked_unverified."""
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        prog_dir = tmp_path / "examples" / "pdf" / "lowcode" / "image-extractor"
        prog_dir.mkdir(parents=True, exist_ok=True)
        (prog_dir / "Program.cs").write_text(
            'class P { static void Main() { string i = "input.pdf"; var r = new ImageExtractor(); } }',
            encoding="utf-8",
        )

        facts = extract_example_readme_facts("pdf", tmp_path, [{"name": "image-extractor"}])
        fact = facts.facts[0]
        assert fact.input_extension == "pdf"
        assert fact.output_extension == ""
        assert fact.validation_status == "blocked_unverified"

    def test_portfolio_audit_cells_no_false_xlsx(self, tmp_path):
        """Cells xlsx claims are legitimate — auditor must NOT flag them."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        readme = (
            "## Overview\n\n## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Run |\n"
            "|---------|-----------------|-------|--------|-----|\n"
            "| `html-converter` | `HtmlConverter.Process` | `xlsx` | `html` | cmd |\n\n"
            "## Requirements\n## How to Run\n## Package Installation\n"
            "## Validation Status\n## Useful Links\n"
        )
        context = {"package_version": "", "examples": [{"name": "html-converter"}], "family": "cells"}
        result = audit_readme(readme, context)
        assert not result.xlsx_cross_family_violation

    def test_portfolio_audit_words_xlsx_is_violation(self):
        """Words xlsx claims are false — auditor must flag them."""
        from plugin_examples.publisher.readme_auditor import audit_readme

        readme = (
            "## Overview\n\n## Included Examples\n\n"
            "| Example | Demonstrated API | Input | Output | Run |\n"
            "|---------|-----------------|-------|--------|-----|\n"
            "| `converter` | `Converter.Convert` | `xlsx` | `pdf` | cmd |\n\n"
            "## Requirements\n## How to Run\n## Package Installation\n"
            "## Validation Status\n## Useful Links\n"
        )
        context = {"package_version": "", "examples": [{"name": "converter"}], "family": "words"}
        result = audit_readme(readme, context)
        assert result.xlsx_cross_family_violation


class TestApiMethodExtraction:
    """Tests for API method extraction from Program.cs source code."""

    def test_static_call_cells(self):
        """Static Cells API call is extracted correctly."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = "HtmlConverter.Process(inputPath, outputPath);"
        api, src = _extract_api_method(source)
        assert api == "HtmlConverter.Process"

    def test_instance_call_pdf(self):
        """Instance PDF API call (new Class().Process) is extracted."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = "var result = new Jpeg().Process(options);"
        api, src = _extract_api_method(source)
        assert api == "Jpeg.Process"

    def test_variable_call_pdf(self):
        """Variable-based PDF API call (var x = new C(); x.Process()) is extracted."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = (
            "var converter = new DocConverter();\n"
            "var options = new PdfToDocOptions();\n"
            "options.AddInput(new FileDataSource(inputPath));\n"
            "var result = converter.Process(options);"
        )
        api, src = _extract_api_method(source)
        assert api == "DocConverter.Process"

    def test_async_call_email(self):
        """Async Email API call is extracted."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = "await Converter.ConvertToHtml(stream, fileName, outputHandler);"
        api, src = _extract_api_method(source)
        assert api == "Converter.ConvertToHtml"

    def test_dispose_not_selected(self):
        """Dispose is ignored — Process is preferred."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = "var plugin = new Html();\n" "var result = plugin.Process(options);\n" "plugin.Dispose();"
        api, src = _extract_api_method(source)
        assert api == "Html.Process"
        assert "Dispose" not in api

    def test_pdf_pr3_apis_resolve_to_process(self):
        """PDF PR#3 html/doc-converter/xls-converter all resolve to .Process, not .Dispose."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        # html example
        html_src = (
            "var plugin = new Html();\n"
            "var options = new HtmlToPdfOptions();\n"
            "options.AddInput(new FileDataSource(inputPath));\n"
            "options.AddOutput(new FileDataSource(outputPath));\n"
            "var result = plugin.Process(options);\n"
            "plugin.Dispose();"
        )
        api, _ = _extract_api_method(html_src)
        assert api == "Html.Process", f"Expected Html.Process, got {api}"

        # doc-converter example
        doc_src = (
            "var converter = new DocConverter();\n"
            "var options = new PdfToDocOptions();\n"
            "options.AddInput(new FileDataSource(inputPath));\n"
            "options.AddOutput(new FileDataSource(outputPath));\n"
            "var result = converter.Process(options);"
        )
        api, _ = _extract_api_method(doc_src)
        assert api == "DocConverter.Process", f"Expected DocConverter.Process, got {api}"

    def test_slides_convert_resolves_to_topdf(self):
        """Slides convert resolves to Convert.ToPdf, not AutoByExtension."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = "Aspose.Slides.LowCode.Convert.ToPdf(inputPath, outputPath);"
        api, _ = _extract_api_method(source)
        assert api == "Convert.ToPdf"

    def test_words_merger_resolves_to_merge(self):
        """Words merger resolves to Merger.Merge, not Merger.Create."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = "Merger.Merge(outputPath, new[] { inputPath1, inputPath2 });"
        api, _ = _extract_api_method(source)
        assert api == "Merger.Merge"

    def test_words_mailmerger_resolves_to_execute(self):
        """Words mail-merger resolves to MailMerger.Execute."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = "MailMerger.Execute(templatePath, resultPath, fieldNames, fieldValues);"
        api, _ = _extract_api_method(source)
        assert api == "MailMerger.Execute"

    def test_unknown_method_returns_empty(self):
        """Source with no recognizable LowCode call returns empty."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = 'Console.WriteLine("hello");\n' 'File.WriteAllText("output.txt", "data");'
        api, _ = _extract_api_method(source)
        assert api == ""

    def test_options_class_not_selected(self):
        """Options classes (HtmlToPdfOptions, JpegOptions) are not selected as API."""
        from plugin_examples.publisher.readme_facts import _extract_api_method

        source = (
            "var options = new JpegOptions();\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.jpg"));\n'
            "var result = new Jpeg().Process(options);"
        )
        api, _ = _extract_api_method(source)
        assert api == "Jpeg.Process"
        assert "Options" not in api

    def test_full_facts_include_api_method(self, tmp_path):
        """extract_example_readme_facts populates api_method_extracted."""
        from plugin_examples.publisher.readme_facts import extract_example_readme_facts

        ex_dir = tmp_path / "examples" / "pdf" / "lowcode" / "merger"
        ex_dir.mkdir(parents=True)
        (ex_dir / "Program.cs").write_text(
            "using Aspose.Pdf.LowCode;\n"
            "var options = new MergeOptions();\n"
            'options.AddInput(new FileDataSource("input.pdf"));\n'
            'options.AddOutput(new FileDataSource("output.pdf"));\n'
            "var result = new Merger().Process(options);\n",
            encoding="utf-8",
        )

        facts = extract_example_readme_facts("pdf", tmp_path, [{"name": "merger"}])
        fact = facts.facts[0]
        assert fact.api_method_extracted == "Merger.Process"
        assert fact.api_method_validation == "verified"
        assert fact.api_symbol == "Merger.Process"
