"""README renderer for LowCode family example repositories.

Renders a family-specific README.md from a Jinja2 template using data derived
from the family config and current run evidence. No hardcoded Cells/Words content.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from plugin_examples.publisher.aspose_links import build_aspose_net_links

logger = logging.getLogger(__name__)

_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[3]
    / "templates"
    / "root-readme"
    / "lowcode-family-readme.md.j2"
)

# Nuget base URL for badge + package page construction
_NUGET_BASE = "https://www.nuget.org/packages"

# Map from family name to URL fragment used in Aspose product URLs (e.g. "cells" -> "cells")
# All lowercase; matches what Aspose uses in product/docs URLs.
_FAMILY_URL_SLUG: dict[str, str] = {
    "cells": "cells",
    "words": "words",
    "pdf": "pdf",
    "slides": "slides",
    "email": "email",
    "imaging": "imaging",
    "drawing": "drawing",
    "tasks": "tasks",
    "note": "note",
    "cad": "cad",
    "barcode": "barcode",
    "html": "html",
    "3d": "3d",
    "ocr": "ocr",
    "zip": "zip",
    "finance": "finance",
    "pub": "pub",
    "page": "page",
    "tex": "tex",
    "font": "font",
    "svg": "svg",
    "gis": "gis",
    "diagram": "diagram",
}


@dataclass
class ExampleEntry:
    """Metadata for a single validated example in the README."""
    name: str                   # directory name, e.g. "html-converter"
    api_class: str              # LowCode API class name, e.g. "HtmlConverter"
    input_format: str           # e.g. "xlsx"
    output_format: str          # e.g. "html"
    description: str = ""       # optional human-readable description


@dataclass
class ReadmeContext:
    """All variables available in the Jinja2 README template."""
    family: str
    display_name: str
    product_name: str               # short product name, e.g. "Cells" (used in URLs)
    nuget_package_id: str
    package_version: str
    target_repo_owner: str
    target_repo_name: str
    target_repo_url: str
    nuget_url: str
    nuget_version_badge_url: str
    nuget_downloads_badge_url: str
    github_license_badge_url: str
    product_page_url: str
    docs_url: str
    kb_url: str
    api_reference_url: str
    blog_url: str
    support_url: str
    temporary_license_url: str
    contact_url: str
    examples: list[ExampleEntry]
    target_framework: str = "net8.0"
    allowed_types: list[str] | None = None
    gate_verdict: str = "PR_DRY_RUN_READY"
    generation_date: str = ""
    validation_summary: dict = field(default_factory=dict)


def _infer_api_class(example_name: str) -> str:
    """Infer the LowCode API class name from the example directory name.

    Converts kebab-case directory name to PascalCase class name.
    e.g. "html-converter" -> "HtmlConverter"
         "spreadsheet-locker" -> "SpreadsheetLocker"
    """
    return "".join(part.capitalize() for part in example_name.split("-"))


def _infer_input_format(example_name: str, family: str, default_extension: str = "xlsx") -> str:
    """Infer the primary input format for an example from its name and family."""
    name_lower = example_name.lower()
    # Operations that take multiple inputs
    if "merger" in name_lower or "comparer" in name_lower:
        return f"2x {default_extension}"
    # Splitter takes single file and splits it
    if "splitter" in name_lower:
        return default_extension
    return default_extension


def _pick_target_framework(preference: list[str]) -> str:
    """Pick the preferred target framework, favouring net8.0 if present."""
    if not preference:
        return "net8.0"
    for fw in preference:
        if fw == "net8.0":
            return "net8.0"
    for fw in preference:
        if fw.startswith("net") and not fw.startswith("netstandard"):
            return fw
    return preference[0]


def build_readme_context(
    family: str,
    family_config,
    examples: list[dict],
    package_version: str,
    gate_verdict: str = "PR_DRY_RUN_READY",
    generation_date: str = "",
) -> ReadmeContext:
    """Build a ReadmeContext from family config and runtime evidence.

    Args:
        family: Family name (e.g. "cells").
        family_config: FamilyConfig dataclass loaded from pipeline/configs/families/*.yml.
        examples: List of example metadata dicts with at least ``name`` and optionally
            ``output_format``. Each dict corresponds to one validated example directory.
        package_version: NuGet package version string (e.g. "26.4.0").
        gate_verdict: Gate verdict string written into the Validation Status table.
        generation_date: ISO timestamp string; defaults to utcnow if empty.

    Returns:
        Populated ReadmeContext ready to pass to render_readme().

    Raises:
        ValueError: If required fields are missing from family_config.
    """
    if not generation_date:
        generation_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # --- Pull fields from family config ---
    display_name: str = getattr(family_config, "display_name", None)
    if not display_name:
        raise ValueError(f"family_config.display_name is required for family '{family}'")

    nuget_cfg = getattr(family_config, "nuget", None)
    if nuget_cfg is None:
        raise ValueError(f"family_config.nuget is required for family '{family}'")
    nuget_package_id: str = getattr(nuget_cfg, "package_id", None)
    if not nuget_package_id:
        raise ValueError(f"family_config.nuget.package_id is required for family '{family}'")

    tf_preference = getattr(nuget_cfg, "target_framework_preference", [])
    target_framework = _pick_target_framework(tf_preference)

    github_cfg = getattr(family_config, "github", None)
    if github_cfg is None:
        raise ValueError(f"family_config.github is required for family '{family}'")
    pub_repo = getattr(github_cfg, "published_plugin_examples_repo", None)
    if pub_repo is None:
        raise ValueError(
            f"family_config.github.published_plugin_examples_repo is required for family '{family}'"
        )
    target_repo_owner: str = pub_repo.owner
    target_repo_name: str = pub_repo.repo

    generation_cfg = getattr(family_config, "generation", None)
    allowed_types: list[str] | None = None
    if generation_cfg is not None:
        raw = getattr(generation_cfg, "allowed_types", [])
        if raw:
            allowed_types = list(raw)

    template_hints = getattr(family_config, "template_hints", None)
    default_ext = "xlsx"
    if template_hints is not None:
        raw_ext = getattr(template_hints, "default_input_extension", ".xlsx")
        default_ext = raw_ext.lstrip(".")

    # --- Derive product name (PascalCase family name used in Aspose URLs) ---
    product_name = family.capitalize()  # "cells" -> "Cells"

    # --- Derive URLs ---
    slug = _FAMILY_URL_SLUG.get(family, family)
    nuget_url = f"{_NUGET_BASE}/{nuget_package_id}"
    target_repo_url = f"https://github.com/{target_repo_owner}/{target_repo_name}"
    nuget_version_badge_url = (
        f"https://img.shields.io/nuget/v/{nuget_package_id}.svg?style=flat"
        f"&label=NuGet%3A%20{nuget_package_id}"
    )
    nuget_downloads_badge_url = (
        f"https://img.shields.io/nuget/dt/{nuget_package_id}.svg?style=flat"
    )
    github_license_badge_url = (
        f"https://img.shields.io/github/license/{target_repo_owner}/{target_repo_name}"
    )
    # All Aspose .NET product links come from the canonical builder — no aspose.com constants.
    _aspose_links = build_aspose_net_links(slug)
    product_page_url = _aspose_links.product_page_url
    docs_url = _aspose_links.docs_url
    kb_url = _aspose_links.kb_url
    api_reference_url = _aspose_links.api_reference_url
    blog_url = _aspose_links.blog_url
    support_url = _aspose_links.free_support_url
    temporary_license_url = _aspose_links.temporary_license_url
    contact_url = _aspose_links.contact_url

    # --- Build example entries ---
    example_entries: list[ExampleEntry] = []
    for ex in examples:
        name: str = ex.get("name", "") or ex.get("scenario_id", "")
        if not name:
            continue
        output_format: str = ex.get("output_format", "") or ex.get("run_output_format", "")
        if not output_format:
            # Infer from name
            n = name.lower()
            if "html" in n:
                output_format = "html"
            elif "image" in n or "img" in n:
                output_format = "png"
            elif "json" in n:
                output_format = "json"
            elif "pdf" in n:
                output_format = "pdf"
            elif "text" in n or "txt" in n:
                output_format = "txt"
            elif "lock" in n:
                output_format = default_ext
            else:
                output_format = default_ext

        input_fmt = _infer_input_format(name, family, default_ext)
        api_class = _infer_api_class(name)

        example_entries.append(ExampleEntry(
            name=name,
            api_class=api_class,
            input_format=input_fmt,
            output_format=output_format,
        ))

    if not example_entries:
        raise ValueError(
            f"No examples provided for family '{family}'. "
            "At least one example is required to render a README."
        )

    return ReadmeContext(
        family=family,
        display_name=display_name,
        product_name=product_name,
        nuget_package_id=nuget_package_id,
        package_version=package_version,
        target_repo_owner=target_repo_owner,
        target_repo_name=target_repo_name,
        target_repo_url=target_repo_url,
        nuget_url=nuget_url,
        nuget_version_badge_url=nuget_version_badge_url,
        nuget_downloads_badge_url=nuget_downloads_badge_url,
        github_license_badge_url=github_license_badge_url,
        product_page_url=product_page_url,
        docs_url=docs_url,
        kb_url=kb_url,
        api_reference_url=api_reference_url,
        blog_url=blog_url,
        support_url=support_url,
        temporary_license_url=temporary_license_url,
        contact_url=contact_url,
        examples=example_entries,
        target_framework=target_framework,
        allowed_types=allowed_types,
        gate_verdict=gate_verdict,
        generation_date=generation_date,
    )


def render_readme(
    context: ReadmeContext,
    template_path: Path | None = None,
) -> str:
    """Render the README.md content from the Jinja2 template.

    Args:
        context: Populated ReadmeContext.
        template_path: Override the default template path (for testing).

    Returns:
        Rendered Markdown string.

    Raises:
        FileNotFoundError: If the template file does not exist.
        jinja2.TemplateError: If the template has syntax errors.
    """
    from jinja2 import Environment, FileSystemLoader, StrictUndefined

    tpath = template_path or _TEMPLATE_PATH
    tpath = Path(tpath)
    if not tpath.exists():
        raise FileNotFoundError(f"README template not found: {tpath}")

    env = Environment(
        loader=FileSystemLoader(str(tpath.parent)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        autoescape=False,
    )
    template = env.get_template(tpath.name)

    # Convert dataclass fields to dict for template; examples as list of dicts
    ctx_dict = {
        "family": context.family,
        "display_name": context.display_name,
        "product_name": context.product_name,
        "nuget_package_id": context.nuget_package_id,
        "package_version": context.package_version,
        "target_repo_owner": context.target_repo_owner,
        "target_repo_name": context.target_repo_name,
        "target_repo_url": context.target_repo_url,
        "nuget_url": context.nuget_url,
        "nuget_version_badge_url": context.nuget_version_badge_url,
        "nuget_downloads_badge_url": context.nuget_downloads_badge_url,
        "github_license_badge_url": context.github_license_badge_url,
        "product_page_url": context.product_page_url,
        "docs_url": context.docs_url,
        "kb_url": context.kb_url,
        "api_reference_url": context.api_reference_url,
        "blog_url": context.blog_url,
        "support_url": context.support_url,
        "temporary_license_url": context.temporary_license_url,
        "contact_url": context.contact_url,
        "examples": [
            {
                "name": ex.name,
                "api_class": ex.api_class,
                "input_format": ex.input_format,
                "output_format": ex.output_format,
                "description": ex.description,
            }
            for ex in context.examples
        ],
        "target_framework": context.target_framework,
        "allowed_types": context.allowed_types,
        "gate_verdict": context.gate_verdict,
        "generation_date": context.generation_date,
    }

    rendered = template.render(**ctx_dict)
    logger.info(
        "README rendered for %s: %d examples, %d chars",
        context.family,
        len(context.examples),
        len(rendered),
    )
    return rendered


def write_readme(content: str, output_path: Path) -> Path:
    """Write rendered README content to a file.

    Args:
        content: Rendered Markdown string.
        output_path: Destination path (README.md in package root).

    Returns:
        The path the file was written to.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    logger.info("README.md written: %s (%d bytes)", output_path, len(content))
    return output_path
