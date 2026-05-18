"""README renderer for LowCode family example repositories.

Renders a family-specific README.md from a Jinja2 template using data derived
from the family config and current run evidence. No hardcoded Cells/Words content.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from plugin_examples.publisher.aspose_links import build_aspose_net_links
from plugin_examples.publisher.readme_facts import extract_example_readme_facts

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


def read_manifest_api_symbol(manifest_path: Path) -> str | None:
    """Read the primary demonstrated API symbol from example.manifest.json.

    Extracts ``ClassName.MethodName`` from the ``claimed_symbols`` list.
    The first symbol with 5+ dot-separated parts is treated as a method
    reference (e.g. ``Aspose.Cells.LowCode.HtmlConverter.Process``); the
    last two parts are returned as ``HtmlConverter.Process``.

    Args:
        manifest_path: Path to example.manifest.json.

    Returns:
        ``ClassName.MethodName`` string, or None if the manifest is missing,
        unreadable, or contains no method-level symbol.
    """
    try:
        data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    claimed = data.get("claimed_symbols", [])
    seen: set[str] = set()
    for sym in claimed:
        parts = sym.split(".")
        # Method symbols: Aspose.Family.LowCode.ClassName.MethodName = 5 parts
        if len(parts) >= 5:
            api_sym = f"{parts[-2]}.{parts[-1]}"
            if api_sym not in seen:
                seen.add(api_sym)
                return api_sym
    return None


@dataclass
class ExampleEntry:
    """Metadata for a single validated example in the README."""
    name: str                   # directory name, e.g. "html-converter"
    api_class: str              # LowCode API class name, e.g. "HtmlConverter"
    input_format: str           # e.g. "xlsx"
    output_format: str          # e.g. "html"
    description: str = ""       # optional human-readable description
    source_snippet: str = ""    # Program.cs content (full or excerpt)
    source_file_path: str = ""  # relative path to Program.cs
    snippet_sha256: str = ""    # SHA256 of the snippet content


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
    typical_outputs: str = ""   # family-aware output examples for prose


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
    package_path: Path | None = None,
    strict_facts: bool = False,
    package_path_map: dict[str, Path] | None = None,
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
        package_path: Path to the PR dry-run package directory containing
            ``examples/{family}/lowcode/{name}/example.manifest.json`` files.
            When set, the renderer reads each manifest to populate ``api_class``
            with a method-qualified symbol (e.g. ``HtmlConverter.Process``).
            Falls back to the directory-name inference if the manifest is absent.

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

    # --- Derive default output extension ---
    default_output_ext = "out"
    if template_hints is not None:
        raw_out = getattr(template_hints, "default_output_extension", ".out")
        default_output_ext = raw_out.lstrip(".")

    # Warn if non-cells family will inherit xlsx default
    if family != "cells" and default_ext == "xlsx":
        logger.warning(
            "Family '%s' inherits xlsx as default_input_extension — this is likely wrong. "
            "Set template_hints.default_input_extension in %s.yml.",
            family, family,
        )

    # --- Build example entries ---
    # When package_path or package_path_map is available, extract source-truth
    # facts from Program.cs.  package_path_map allows multi-package fact
    # extraction where each example may live in a different PR package.
    facts = None
    if package_path_map:
        # Multi-package mode: extract facts per-example from their own packages
        from plugin_examples.publisher.readme_facts import ExampleReadmeFacts
        combined_facts = ExampleReadmeFacts(family=family, generated_at="", source_artifact="multi-package")
        for ex in examples:
            ex_name = ex.get("name", "") or ex.get("scenario_id", "")
            if not ex_name or ex_name not in package_path_map:
                continue
            per_pkg = extract_example_readme_facts(
                family=family,
                package_path=package_path_map[ex_name],
                examples=[ex],
                manifest_reader=read_manifest_api_symbol,
            )
            combined_facts.facts.extend(per_pkg.facts)
        facts = combined_facts
    elif package_path is not None:
        facts = extract_example_readme_facts(
            family=family,
            package_path=Path(package_path),
            examples=examples,
            manifest_reader=read_manifest_api_symbol,
        )

    if facts is not None:
        # Fail-closed: when strict_facts is True, all facts must be verified
        for fact in facts.facts:
            if fact.validation_status != "verified":
                if strict_facts:
                    raise ValueError(
                        f"Example '{fact.example_name}': format claims unverified "
                        f"(input='{fact.input_extension}', output='{fact.output_extension}'). "
                        f"Cannot publish README with unverified format claims. "
                        f"Ensure Program.cs contains 'input.EXT' and 'output.EXT' patterns."
                    )
                logger.warning(
                    "Example '%s': format claims unverified — falling back to heuristic",
                    fact.example_name,
                )

    # Build a lookup from facts if available
    facts_by_name: dict[str, object] = {}
    if facts is not None:
        for fact in facts.facts:
            facts_by_name[fact.example_name] = fact

    example_entries: list[ExampleEntry] = []
    for ex in examples:
        name: str = ex.get("name", "") or ex.get("scenario_id", "")
        if not name:
            continue

        fact = facts_by_name.get(name)
        if fact is not None:
            # Source-truth-driven: use facts from Program.cs
            input_fmt = fact.input_extension
            output_format = fact.output_extension
            api_class = fact.api_symbol or _infer_api_class(name)
            source_snippet = fact.snippet_content
            source_file_path = fact.source_file_path
            snippet_sha256 = fact.snippet_content_sha256
        else:
            # Legacy heuristic fallback (no package_path provided)
            output_format = ex.get("output_format", "") or ex.get("run_output_format", "")
            if not output_format:
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
                    output_format = default_output_ext
                else:
                    output_format = default_output_ext

            input_fmt = _infer_input_format(name, family, default_ext)
            api_class = _infer_api_class(name)
            if package_path is not None:
                manifest_path = (
                    Path(package_path) / "examples" / family / "lowcode" / name / "example.manifest.json"
                )
                sym = read_manifest_api_symbol(manifest_path)
                if sym:
                    api_class = sym
            source_snippet = ""
            source_file_path = ""
            snippet_sha256 = ""

        example_entries.append(ExampleEntry(
            name=name,
            api_class=api_class,
            input_format=input_fmt,
            output_format=output_format,
            source_snippet=source_snippet,
            source_file_path=source_file_path,
            snippet_sha256=snippet_sha256,
        ))

    if not example_entries:
        raise ValueError(
            f"No examples provided for family '{family}'. "
            "At least one example is required to render a README."
        )

    # Build typical_outputs from actual example output formats
    output_exts = sorted({ex.output_format for ex in example_entries if ex.output_format})
    if output_exts:
        typical_outputs = ", ".join(f"`output.{ext}`" for ext in output_exts)
    else:
        typical_outputs = f"`output.{default_output_ext}`"

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
        typical_outputs=typical_outputs,
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
                "source_snippet": ex.source_snippet,
                "source_file_path": ex.source_file_path,
                "snippet_sha256": ex.snippet_sha256,
            }
            for ex in context.examples
        ],
        "target_framework": context.target_framework,
        "allowed_types": context.allowed_types,
        "gate_verdict": context.gate_verdict,
        "generation_date": context.generation_date,
        "typical_outputs": context.typical_outputs,
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
