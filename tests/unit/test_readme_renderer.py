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

        cfg = _make_family_config(family="cells", display_name="Aspose.Cells for .NET",
                                   nuget_package_id="Aspose.Cells", owner="aspose-cells-net",
                                   repo="Aspose.Cells.LowCode-for-.NET-Examples")
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
            family="cells", family_config=cfg,
            examples=examples, package_version="26.4.0",
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
            family="cells", family_config=cfg,
            examples=examples, package_version="26.4.0",
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
            family="words", family_config=cfg,
            examples=examples, package_version="26.4.0",
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
            family="cells", family_config=cfg,
            examples=_make_examples(["html-converter"]), package_version="26.4.0",
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
            family="words", family_config=cfg,
            examples=examples, package_version="26.4.0",
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

    def _make_valid_readme(self, package_version: str = "26.4.0",
                            example_names: list[str] | None = None) -> str:
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
            build_readme_context, render_readme, write_readme,
        )

        cfg = _make_family_config()
        ctx = build_readme_context(
            family="cells", family_config=cfg,
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
            build_readme_context, render_readme, write_readme,
        )

        cfg = _make_family_config()

        # First render: 2 examples
        ctx1 = build_readme_context(
            family="cells", family_config=cfg,
            examples=_make_examples(["html-converter", "pdf-converter"]),
            package_version="26.4.0",
        )
        write_readme(render_readme(ctx1), tmp_path / "README.md")

        # Second render: 3 examples (new version)
        ctx2 = build_readme_context(
            family="cells", family_config=cfg,
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
            capture_output=True, text=True, timeout=30,
            env={**__import__("os").environ, "PYTHONPATH": "src"},
            cwd=str(cwd or _REPO_ROOT),
        )

    def test_cli_render_root_readme_exits_zero_for_cells(self):
        """CLI render-root-readme for cells must exit 0 and write README + audit files."""
        result = self._run_cli([
            "render-root-readme", "--family", "cells",
            "--package-path", "workspace/pr-dry-run/cells-controlled-pilot",
            "--promote-latest",
        ])
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
        result = self._run_cli([
            "render-root-readme", "--family", "words",
            "--package-path", "workspace/pr-dry-run/words-controlled-pilot",
            "--promote-latest",
        ])
        assert result.returncode == 0, f"Exit {result.returncode}\n{result.stderr}"

        render = _REPO_ROOT / "workspace" / "verification" / "latest" / "words-root-readme-render-result.json"
        assert render.exists()
        data = json.loads(render.read_text(encoding="utf-8"))
        assert data["examples_count"] == 4
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
        main_path = _REPO_ROOT / "src" / "plugin_examples" / "__main__.py"
        source = main_path.read_text(encoding="utf-8")
        # Must have: if not _readme_audit.passed: if live_mode: return 1
        # Check the pattern exists as a block in the publish-pr README integration section
        assert "_readme_audit.passed" in source, \
            "publish-pr must check _readme_audit.passed"
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

        bad_readme = "\n".join([
            "## Overview", "Content.",
            "## Included Examples",
            "| Example | Demonstrated API | Input | Output | Run |",
            "|---------|-----------------|-------|--------|-----|",
            "| `html-converter` | `HtmlConverter` | `xlsx` | `html` | `dotnet run` |",
            "## Requirements", "v25.0.0",  # stale version
            "## How to Run", "run it",
            "## Package Installation", "install",
            "## Validation Status", "gate",
            "## Useful Links", "links",
        ])
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
        """publish-readme must be a registered subcommand in __main__.py."""
        main_path = _REPO_ROOT / "src" / "plugin_examples" / "__main__.py"
        source = main_path.read_text(encoding="utf-8")
        assert '"publish-readme"' in source or "'publish-readme'" in source, \
            "publish-readme subparser must be registered"

    def test_publish_readme_requires_approval_for_live(self):
        """publish-readme must check approval_token before any live remote write."""
        main_path = _REPO_ROOT / "src" / "plugin_examples" / "__main__.py"
        source = main_path.read_text(encoding="utf-8")
        # The publish-readme handler must call check_approval
        assert "check_approval" in source, "publish-readme must call check_approval()"
        # Must have live mode guard: if not approved: return 1
        import re
        assert re.search(r"if not approved:\s*\n\s+print.*blocked", source), \
            "publish-readme must return 1 when not approved"

    def test_publish_readme_uses_tempdir_for_readme_only(self):
        """publish-readme must create a temp dir with only README.md (not full package)."""
        main_path = _REPO_ROOT / "src" / "plugin_examples" / "__main__.py"
        source = main_path.read_text(encoding="utf-8")
        assert "TemporaryDirectory" in source, \
            "publish-readme must use tempfile.TemporaryDirectory for README-only commit"

    def test_publish_readme_no_change_detection_present(self):
        """publish-readme must detect when remote README already matches pipeline output."""
        main_path = _REPO_ROOT / "src" / "plugin_examples" / "__main__.py"
        source = main_path.read_text(encoding="utf-8")
        assert "NO_CHANGE" in source, \
            "publish-readme must have NO_CHANGE detection"
        assert "remote_readme_content.strip() == readme_content.strip()" in source or \
               "no_change" in source, \
            "publish-readme must compare remote vs rendered content"

    def test_publish_readme_dry_run_writes_simulation_evidence(self):
        """publish-readme dry-run must write {family}-readme-backfill-simulation.json."""
        import subprocess
        result = subprocess.run(
            [
                str(_REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
                "-m", "plugin_examples",
                "publish-readme", "--family", "cells",
                "--approval-token", "APPROVE_LIVE_PR",
                "--promote-latest",
            ],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
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
                str(_REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
                "-m", "plugin_examples",
                "publish-readme", "--family", "words",
                "--approval-token", "APPROVE_LIVE_PR",
                "--promote-latest",
            ],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
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
        assert data.get("no_remote_write_performed") is True, \
            "Dry-run evidence must confirm no remote write was performed"
        assert data.get("dry_run") is True, "Evidence must mark dry_run=true"

    def test_publish_readme_live_blocks_without_token(self):
        """publish-readme live mode must exit non-zero when GITHUB_TOKEN is absent."""
        import subprocess
        env_no_token = {k: v for k, v in __import__("os").environ.items() if k != "GITHUB_TOKEN"}
        env_no_token["PYTHONPATH"] = str(_REPO_ROOT / "src")
        result = subprocess.run(
            [
                str(_REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
                "-m", "plugin_examples",
                "publish-readme", "--family", "cells",
                "--publish", "--approval-token", "APPROVE_LIVE_PR",
            ],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
            env=env_no_token,
            timeout=30,
        )
        assert result.returncode != 0, \
            "publish-readme live must fail when GITHUB_TOKEN is absent"
        assert "GITHUB_TOKEN" in result.stdout or "GITHUB_TOKEN" in result.stderr, \
            "Error message must mention GITHUB_TOKEN"

    def test_publish_readme_live_blocks_without_approval(self):
        """publish-readme live mode must exit non-zero when approval token is wrong."""
        import subprocess
        result = subprocess.run(
            [
                str(_REPO_ROOT / ".venv" / "Scripts" / "python.exe"),
                "-m", "plugin_examples",
                "publish-readme", "--family", "cells",
                "--publish", "--approval-token", "WRONG_TOKEN",
            ],
            capture_output=True, text=True, cwd=str(_REPO_ROOT),
            env={**__import__("os").environ, "PYTHONPATH": str(_REPO_ROOT / "src"),
                 "GITHUB_TOKEN": "dummy"},
            timeout=30,
        )
        assert result.returncode != 0, \
            "publish-readme live must fail when approval token is wrong"
        assert "blocked" in result.stdout.lower() or "blocked" in result.stderr.lower(), \
            "Error message must mention 'blocked'"


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
            family=family, family_config=cfg,
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
            assert not ctx.product_page_url.endswith("/net"), (
                f"product_page_url must not end with /net: {ctx.product_page_url}"
            )

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
            family="words", family_config=cfg,
            examples=[{"name": "converter", "output_format": "docx"}],
            package_version="26.4.0",
        )
        rendered = render_readme(ctx)
        forbidden = find_forbidden_aspose_com_links(rendered)
        assert forbidden == [], f"Rendered Words README has forbidden links: {forbidden}"
