"""Tests for aspose_links.py — canonical Aspose .NET URL builder and validators.

All generated LowCode example README.md files must use aspose.net URLs.
These tests verify the URL builder produces correct aspose.net links and that
the validators detect all forbidden aspose.com URLs and policy violations.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# TestAsposeNetLinksBuilder
# ---------------------------------------------------------------------------

class TestAsposeNetLinksBuilder:
    """Tests for build_aspose_net_links()."""

    def test_cells_links_use_aspose_net_not_aspose_com(self):
        """All cells URLs must use aspose.net domain."""
        from plugin_examples.publisher.aspose_links import build_aspose_net_links

        links = build_aspose_net_links("cells")
        for field_name, url in vars(links).items():
            assert "aspose.com" not in url, (
                f"{field_name} uses aspose.com — must use aspose.net: {url}"
            )
            assert "aspose.net" in url, (
                f"{field_name} missing aspose.net domain: {url}"
            )

    def test_words_links_use_aspose_net_not_aspose_com(self):
        """All words URLs must use aspose.net domain."""
        from plugin_examples.publisher.aspose_links import build_aspose_net_links

        links = build_aspose_net_links("words")
        for field_name, url in vars(links).items():
            assert "aspose.com" not in url, (
                f"{field_name} uses aspose.com — must use aspose.net: {url}"
            )
            assert "aspose.net" in url, (
                f"{field_name} missing aspose.net domain: {url}"
            )

    def test_pdf_links_use_aspose_net_not_aspose_com(self):
        """All pdf URLs must use aspose.net domain."""
        from plugin_examples.publisher.aspose_links import build_aspose_net_links

        links = build_aspose_net_links("pdf")
        for field_name, url in vars(links).items():
            assert "aspose.com" not in url, (
                f"{field_name} uses aspose.com — must use aspose.net: {url}"
            )

    def test_product_docs_reference_kb_have_no_net_platform_suffix(self):
        """product, docs, reference, and KB URLs must NOT end with /net."""
        from plugin_examples.publisher.aspose_links import build_aspose_net_links

        for slug in ("cells", "words", "pdf"):
            links = build_aspose_net_links(slug)
            for url in (links.product_page_url, links.docs_url, links.api_reference_url, links.kb_url):
                assert not url.endswith("/net"), (
                    f"URL must not end with /net platform suffix: {url}"
                )
                assert f"/{slug}/net" not in url, (
                    f"URL must not contain /{slug}/net platform suffix: {url}"
                )

    def test_cells_product_url_is_correct(self):
        from plugin_examples.publisher.aspose_links import build_aspose_net_links
        links = build_aspose_net_links("cells")
        assert links.product_page_url == "https://products.aspose.net/cells"

    def test_cells_docs_url_is_correct(self):
        from plugin_examples.publisher.aspose_links import build_aspose_net_links
        links = build_aspose_net_links("cells")
        assert links.docs_url == "https://docs.aspose.net/cells"

    def test_cells_kb_url_is_correct(self):
        from plugin_examples.publisher.aspose_links import build_aspose_net_links
        links = build_aspose_net_links("cells")
        assert links.kb_url == "https://kb.aspose.net/cells"

    def test_cells_api_reference_url_is_correct(self):
        from plugin_examples.publisher.aspose_links import build_aspose_net_links
        links = build_aspose_net_links("cells")
        assert links.api_reference_url == "https://reference.aspose.net/cells"

    def test_blog_url_uses_categories_and_plugin_family_pattern(self):
        """Blog URL must use /categories/aspose.{slug}-plugin-family/ pattern."""
        from plugin_examples.publisher.aspose_links import build_aspose_net_links

        for slug in ("cells", "words", "pdf"):
            links = build_aspose_net_links(slug)
            expected_fragment = f"aspose.{slug}-plugin-family/"
            assert expected_fragment in links.blog_url, (
                f"Blog URL for {slug} must contain {expected_fragment!r}: {links.blog_url}"
            )
            assert "/categories/" in links.blog_url, (
                f"Blog URL must use /categories/ (plural): {links.blog_url}"
            )
            assert "/category/" not in links.blog_url, (
                f"Blog URL must NOT use /category/ (singular): {links.blog_url}"
            )

    def test_contact_url_is_about_aspose_net_contact(self):
        """Contact URL must be about.aspose.net/contact/."""
        from plugin_examples.publisher.aspose_links import build_aspose_net_links

        for slug in ("cells", "words", "pdf"):
            links = build_aspose_net_links(slug)
            assert links.contact_url == "https://about.aspose.net/contact/", (
                f"Wrong contact URL for {slug}: {links.contact_url}"
            )

    def test_temporary_license_url_is_purchase_aspose_net(self):
        from plugin_examples.publisher.aspose_links import build_aspose_net_links
        links = build_aspose_net_links("cells")
        assert links.temporary_license_url == "https://purchase.aspose.net/temporary-license"

    def test_support_url_uses_forum_aspose_net_with_trailing_slash(self):
        from plugin_examples.publisher.aspose_links import build_aspose_net_links
        links = build_aspose_net_links("cells")
        assert links.free_support_url == "https://forum.aspose.net/c/cells/"
        assert links.free_support_url.endswith("/")


# ---------------------------------------------------------------------------
# TestFindForbiddenAsposeComLinks
# ---------------------------------------------------------------------------

class TestFindForbiddenAsposeComLinks:
    """Tests for find_forbidden_aspose_com_links()."""

    def test_detects_products_aspose_com(self):
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = "See [product](https://products.aspose.com/cells/net) for info."
        result = find_forbidden_aspose_com_links(md)
        assert any("products.aspose.com" in r for r in result)

    def test_detects_docs_aspose_com(self):
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = "See [docs](https://docs.aspose.com/cells/net)."
        result = find_forbidden_aspose_com_links(md)
        assert any("docs.aspose.com" in r for r in result)

    def test_detects_reference_aspose_com(self):
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = "[API ref](https://reference.aspose.com/cells/net)"
        result = find_forbidden_aspose_com_links(md)
        assert any("reference.aspose.com" in r for r in result)

    def test_detects_blog_aspose_com(self):
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = "[Blog](https://blog.aspose.com/category/cells)"
        result = find_forbidden_aspose_com_links(md)
        assert any("blog.aspose.com" in r for r in result)

    def test_detects_purchase_aspose_com(self):
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = "[license](https://purchase.aspose.com/temporary-license)"
        result = find_forbidden_aspose_com_links(md)
        assert any("purchase.aspose.com" in r for r in result)

    def test_detects_forum_aspose_com(self):
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = "[forum](https://forum.aspose.com/c/cells)"
        result = find_forbidden_aspose_com_links(md)
        assert any("forum.aspose.com" in r for r in result)

    def test_detects_about_aspose_com(self):
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = "[contact](https://about.aspose.com/contact-us/)"
        result = find_forbidden_aspose_com_links(md)
        assert any("about.aspose.com" in r for r in result)

    def test_clean_readme_returns_empty(self):
        """A README with only aspose.net links must return no forbidden links."""
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = (
            "[product](https://products.aspose.net/cells)\n"
            "[docs](https://docs.aspose.net/cells)\n"
            "[kb](https://kb.aspose.net/cells)\n"
            "[forum](https://forum.aspose.net/c/cells/)\n"
            "[nuget](https://www.nuget.org/packages/Aspose.Cells)\n"
        )
        result = find_forbidden_aspose_com_links(md)
        assert result == [], f"Expected no forbidden links, got: {result}"

    def test_allows_github_and_nuget_and_shields(self):
        """github.com, nuget.org, shields.io must not be flagged."""
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        md = (
            "[![badge](https://img.shields.io/nuget/v/Aspose.Cells.svg)](https://www.nuget.org/packages/Aspose.Cells)\n"
            "[repo](https://github.com/aspose-cells-net/Aspose.Cells.LowCode-for-.NET-Examples)\n"
        )
        result = find_forbidden_aspose_com_links(md)
        assert result == [], f"Non-Aspose links must not be flagged: {result}"


# ---------------------------------------------------------------------------
# TestFindPlatformPathErrors
# ---------------------------------------------------------------------------

class TestFindPlatformPathErrors:
    """Tests for find_platform_path_errors()."""

    def test_detects_products_aspose_net_cells_net(self):
        from plugin_examples.publisher.aspose_links import find_platform_path_errors
        md = "[product](https://products.aspose.net/cells/net)"
        result = find_platform_path_errors(md, "cells")
        assert len(result) > 0

    def test_detects_docs_aspose_net_words_net(self):
        from plugin_examples.publisher.aspose_links import find_platform_path_errors
        md = "[docs](https://docs.aspose.net/words/net)"
        result = find_platform_path_errors(md, "words")
        assert len(result) > 0

    def test_clean_aspose_net_returns_empty(self):
        from plugin_examples.publisher.aspose_links import find_platform_path_errors
        md = "[product](https://products.aspose.net/cells)"
        result = find_platform_path_errors(md, "cells")
        assert result == []


# ---------------------------------------------------------------------------
# TestFindWrongBlogLinks
# ---------------------------------------------------------------------------

class TestFindWrongBlogLinks:
    """Tests for find_wrong_blog_links()."""

    def test_detects_blog_aspose_com_category(self):
        from plugin_examples.publisher.aspose_links import find_wrong_blog_links
        md = "[blog](https://blog.aspose.com/category/cells)"
        result = find_wrong_blog_links(md)
        assert len(result) > 0

    def test_correct_blog_aspose_net_returns_empty(self):
        from plugin_examples.publisher.aspose_links import find_wrong_blog_links
        md = "[blog](https://blog.aspose.net/categories/aspose.cells-plugin-family/)"
        result = find_wrong_blog_links(md)
        assert result == []


# ---------------------------------------------------------------------------
# TestFindWrongContactLinks
# ---------------------------------------------------------------------------

class TestFindWrongContactLinks:
    """Tests for find_wrong_contact_links()."""

    def test_detects_about_aspose_com_contact_us(self):
        from plugin_examples.publisher.aspose_links import find_wrong_contact_links
        md = "[contact](https://about.aspose.com/contact-us/)"
        result = find_wrong_contact_links(md)
        assert len(result) > 0

    def test_correct_about_aspose_net_returns_empty(self):
        from plugin_examples.publisher.aspose_links import find_wrong_contact_links
        md = "[contact](https://about.aspose.net/contact/)"
        result = find_wrong_contact_links(md)
        assert result == []


# ---------------------------------------------------------------------------
# TestFindMissingRequiredLinks
# ---------------------------------------------------------------------------

class TestFindMissingRequiredLinks:
    """Tests for find_missing_required_links()."""

    def test_detects_missing_kb_link(self):
        from plugin_examples.publisher.aspose_links import find_missing_required_links
        md = "[product](https://products.aspose.net/cells)\n[docs](https://docs.aspose.net/cells)"
        result = find_missing_required_links(md, "cells")
        assert any("kb.aspose.net" in r for r in result)

    def test_no_missing_when_kb_present(self):
        from plugin_examples.publisher.aspose_links import find_missing_required_links
        md = "[kb](https://kb.aspose.net/cells)"
        result = find_missing_required_links(md, "cells")
        assert result == []


# ---------------------------------------------------------------------------
# TestRendererUsesAsposeNetLinks
# ---------------------------------------------------------------------------

def _make_family_config(
    family: str = "cells",
    display_name: str = "Aspose.Cells for .NET",
    nuget_package_id: str = "Aspose.Cells",
    owner: str = "aspose-cells-net",
    repo: str = "Aspose.Cells.LowCode-for-.NET-Examples",
    allowed_types: list[str] | None = None,
) -> MagicMock:
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


class TestRendererUsesAsposeNetLinks:
    """Integration tests: renderer must produce aspose.net links."""

    def _build_rendered(self, family: str, display_name: str, nuget_id: str,
                        owner: str, repo: str, ext: str = ".xlsx") -> str:
        from plugin_examples.publisher.readme_renderer import build_readme_context, render_readme
        cfg = _make_family_config(family=family, display_name=display_name,
                                   nuget_package_id=nuget_id, owner=owner, repo=repo)
        cfg.template_hints.default_input_extension = ext
        ctx = build_readme_context(
            family=family, family_config=cfg,
            examples=[{"name": "test-example", "output_format": "pdf"}],
            package_version="26.4.0",
        )
        return render_readme(ctx)

    def test_cells_rendered_readme_uses_aspose_net_links(self):
        rendered = self._build_rendered(
            "cells", "Aspose.Cells for .NET", "Aspose.Cells",
            "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples",
        )
        assert "products.aspose.net/cells" in rendered
        assert "docs.aspose.net/cells" in rendered
        assert "reference.aspose.net/cells" in rendered
        assert "kb.aspose.net/cells" in rendered
        assert "aspose.cells-plugin-family" in rendered
        assert "forum.aspose.net/c/cells/" in rendered
        assert "purchase.aspose.net/temporary-license" in rendered
        assert "about.aspose.net/contact/" in rendered

    def test_words_rendered_readme_uses_aspose_net_links(self):
        rendered = self._build_rendered(
            "words", "Aspose.Words for .NET", "Aspose.Words",
            "aspose-words-net", "Aspose.Words.LowCode-for-.NET-Examples", ".docx",
        )
        assert "products.aspose.net/words" in rendered
        assert "docs.aspose.net/words" in rendered
        assert "reference.aspose.net/words" in rendered
        assert "kb.aspose.net/words" in rendered
        assert "aspose.words-plugin-family" in rendered
        assert "purchase.aspose.net/temporary-license" in rendered

    def test_pdf_rendered_readme_uses_aspose_net_links(self):
        rendered = self._build_rendered(
            "pdf", "Aspose.PDF for .NET", "Aspose.PDF",
            "aspose-pdf-net", "Aspose.PDF.LowCode-for-.NET-Examples",
        )
        assert "products.aspose.net/pdf" in rendered
        assert "docs.aspose.net/pdf" in rendered
        assert "kb.aspose.net/pdf" in rendered

    def test_rendered_readme_includes_kb_link(self):
        rendered = self._build_rendered(
            "cells", "Aspose.Cells for .NET", "Aspose.Cells",
            "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples",
        )
        assert "kb.aspose.net" in rendered, "Rendered README must include KB link"

    def test_rendered_readme_includes_contact_link(self):
        rendered = self._build_rendered(
            "cells", "Aspose.Cells for .NET", "Aspose.Cells",
            "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples",
        )
        assert "about.aspose.net/contact/" in rendered

    def test_rendered_readme_does_not_include_wrong_contact(self):
        rendered = self._build_rendered(
            "cells", "Aspose.Cells for .NET", "Aspose.Cells",
            "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples",
        )
        assert "about.aspose.com/contact-us/" not in rendered

    def test_rendered_readme_has_no_forbidden_aspose_com_links(self):
        """Rendered README must contain zero forbidden aspose.com product/doc/ref links."""
        from plugin_examples.publisher.aspose_links import find_forbidden_aspose_com_links
        for family, display, nuget, owner, repo in [
            ("cells", "Aspose.Cells for .NET", "Aspose.Cells",
             "aspose-cells-net", "Aspose.Cells.LowCode-for-.NET-Examples"),
            ("words", "Aspose.Words for .NET", "Aspose.Words",
             "aspose-words-net", "Aspose.Words.LowCode-for-.NET-Examples"),
        ]:
            rendered = self._build_rendered(family, display, nuget, owner, repo)
            forbidden = find_forbidden_aspose_com_links(rendered)
            assert forbidden == [], (
                f"{family} README contains forbidden aspose.com links: {forbidden}"
            )

    def test_rendered_readme_has_no_platform_path_errors(self):
        """Rendered README must not contain aspose.net/{slug}/net."""
        from plugin_examples.publisher.aspose_links import find_platform_path_errors
        for family in ("cells", "words"):
            rendered = self._build_rendered(
                family, f"Aspose.{family.capitalize()} for .NET",
                f"Aspose.{family.capitalize()}",
                f"aspose-{family}-net", f"Aspose.{family.capitalize()}.LowCode-for-.NET-Examples",
            )
            errors = find_platform_path_errors(rendered, family)
            assert errors == [], (
                f"{family} README has platform path errors: {errors}"
            )


# ---------------------------------------------------------------------------
# TestAuditorRejectsAsposeComLinks
# ---------------------------------------------------------------------------

class TestAuditorRejectsAsposeComLinks:
    """Tests that readme_auditor.py rejects forbidden aspose.com links."""

    def _make_valid_readme(self, extra_links: str = "") -> str:
        return f"""# Aspose.Cells for .NET LowCode Examples

## Overview
Aspose.Cells LowCode provides high-level APIs.

## Included Examples

| Example | Demonstrated API | Input | Output | Run |
|---------|-----------------|-------|--------|-----|
| `html-converter` | `HtmlConverter` | `xlsx` | `html` | `dotnet run --project examples/cells/lowcode/html-converter` |

## Requirements
- .NET 8.0+
- NuGet: Aspose.Cells v26.4.0

## How to Run
```bash
dotnet restore
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
{extra_links}
"""

    def _ctx(self) -> dict:
        return {
            "package_version": "26.4.0",
            "examples": [{"name": "html-converter"}],
            "family": "cells",
        }

    def test_auditor_rejects_products_aspose_com(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [Product](https://products.aspose.com/cells/net)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False
        assert len(result.forbidden_aspose_com_links) > 0

    def test_auditor_rejects_docs_aspose_com(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [Docs](https://docs.aspose.com/cells/net)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False
        assert len(result.forbidden_aspose_com_links) > 0

    def test_auditor_rejects_reference_aspose_com(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [API](https://reference.aspose.com/cells/net)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False

    def test_auditor_rejects_blog_aspose_com_category(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [Blog](https://blog.aspose.com/category/cells)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False
        assert len(result.wrong_blog_links) > 0 or len(result.forbidden_aspose_com_links) > 0

    def test_auditor_rejects_purchase_aspose_com(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [License](https://purchase.aspose.com/temporary-license)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False

    def test_auditor_rejects_forum_aspose_com(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [Forum](https://forum.aspose.com/c/cells)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False

    def test_auditor_rejects_about_aspose_com_contact_us(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "Contact [Aspose Sales](https://about.aspose.com/contact-us/)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False
        assert len(result.wrong_contact_links) > 0 or len(result.forbidden_aspose_com_links) > 0

    def test_auditor_rejects_aspose_net_with_platform_suffix(self):
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [Product](https://products.aspose.net/cells/net)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is False
        assert len(result.platform_path_errors) > 0

    def test_auditor_rejects_missing_kb_link(self):
        """Audit must fail when KB link is absent."""
        from plugin_examples.publisher.readme_auditor import audit_readme
        # Build a README without any kb.aspose.net link
        content = """# Aspose.Cells for .NET LowCode Examples

## Overview
Content.

## Included Examples

| Example | Demonstrated API | Input | Output | Run |
|---------|-----------------|-------|--------|-----|
| `html-converter` | `HtmlConverter` | `xlsx` | `html` | `dotnet run` |

## Requirements
- NuGet: Aspose.Cells v26.4.0

## How to Run
run it

## Package Installation
install

## Validation Status
gate

## Useful Links
- [Product](https://products.aspose.net/cells)
"""
        result = audit_readme(content, self._ctx())
        assert result.passed is False
        assert len(result.missing_required_links) > 0

    def test_auditor_passes_clean_aspose_net_readme(self):
        """Audit must pass when all links are correct aspose.net."""
        from plugin_examples.publisher.readme_auditor import audit_readme
        content = self._make_valid_readme(
            "- [Product](https://products.aspose.net/cells)\n"
            "- [Docs](https://docs.aspose.net/cells)\n"
            "- [Ref](https://reference.aspose.net/cells)\n"
            "- [Blog](https://blog.aspose.net/categories/aspose.cells-plugin-family/)\n"
            "- [Forum](https://forum.aspose.net/c/cells/)\n"
            "- [License](https://purchase.aspose.net/temporary-license)\n"
            "Contact [Sales](https://about.aspose.net/contact/)"
        )
        result = audit_readme(content, self._ctx())
        assert result.passed is True, f"Clean README should pass but got: {result.warnings}"

    def test_publish_path_blocks_on_forbidden_links(self):
        """__main__.py publish-readme path must call audit_readme() before live PR creation.

        This structural test verifies the existing hard stop is in place and that
        after adding URL validation to audit_readme(), the publish path automatically
        blocks READMEs with forbidden aspose.com links.
        """
        main_path = _REPO_ROOT / "src" / "plugin_examples" / "__main__.py"
        source = main_path.read_text(encoding="utf-8")
        # The publish-readme handler must call audit_readme and block on failure
        assert "readme_audit = audit_readme(" in source or "audit_readme(" in source, \
            "publish-readme must call audit_readme()"
        assert "readme_audit.passed" in source or "_readme_audit.passed" in source, \
            "publish path must check audit.passed"
