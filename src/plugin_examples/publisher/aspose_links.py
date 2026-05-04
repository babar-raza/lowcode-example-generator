"""Canonical Aspose .NET link builder for LowCode example README files.

All generated README.md files for .NET LowCode example repositories must use
aspose.net URLs (the .NET-specific domain). aspose.com is a multi-platform
site where the platform appears as a path segment (e.g. /cells/net). On
aspose.net the domain is already .NET-specific, so no platform suffix is used.

This module is the single source of truth for all Aspose link construction.
The renderer, auditor, and tests all import from here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class AsposeNetLinks:
    """Canonical .NET README links for one Aspose family."""

    product_page_url: str
    docs_url: str
    kb_url: str
    api_reference_url: str
    blog_url: str
    temporary_license_url: str
    free_support_url: str
    contact_url: str


def build_aspose_net_links(family_slug: str) -> AsposeNetLinks:
    """Build canonical aspose.net links for the given family slug.

    Args:
        family_slug: Lowercase family name, e.g. "cells", "words", "pdf".

    Returns:
        AsposeNetLinks with all eight canonical URLs.
    """
    return AsposeNetLinks(
        product_page_url=f"https://products.aspose.net/{family_slug}",
        docs_url=f"https://docs.aspose.net/{family_slug}",
        kb_url=f"https://kb.aspose.net/{family_slug}",
        api_reference_url=f"https://reference.aspose.net/{family_slug}",
        blog_url=f"https://blog.aspose.net/categories/aspose.{family_slug}-plugin-family/",
        temporary_license_url="https://purchase.aspose.net/temporary-license",
        free_support_url=f"https://forum.aspose.net/c/{family_slug}/",
        contact_url="https://about.aspose.net/contact/",
    )


# ---------------------------------------------------------------------------
# Forbidden domain patterns
# ---------------------------------------------------------------------------

_FORBIDDEN_ASPOSE_COM_DOMAINS: list[str] = [
    "products.aspose.com",
    "docs.aspose.com",
    "kb.aspose.com",
    "reference.aspose.com",
    "blog.aspose.com",
    "purchase.aspose.com",
    "forum.aspose.com",
    "about.aspose.com",
]

# Compiled pattern: any https?://forbidden-domain... URL
_FORBIDDEN_COM_PATTERN = re.compile(
    r"https?://(?:" + "|".join(re.escape(d) for d in _FORBIDDEN_ASPOSE_COM_DOMAINS) + r")[^\s)\]]*"
)

# Wrong blog pattern: blog.aspose.com/category/ (singular)
_WRONG_BLOG_PATTERN = re.compile(r"https?://blog\.aspose\.com/category/[^\s)\]]*")

# Wrong contact pattern: about.aspose.com/contact-us/
_WRONG_CONTACT_PATTERN = re.compile(r"https?://about\.aspose\.com/contact-us/?[^\s)\]]*")


def find_forbidden_aspose_com_links(markdown: str) -> list[str]:
    """Return all forbidden aspose.com product/doc/ref/forum/... links in markdown.

    These are links that belong on aspose.net instead.

    Args:
        markdown: Full README.md content as a string.

    Returns:
        List of matching URL strings, empty if none found.
    """
    return _FORBIDDEN_COM_PATTERN.findall(markdown)


def find_platform_path_errors(markdown: str, family_slug: str) -> list[str]:
    """Return aspose.net URLs that incorrectly include the /net platform suffix.

    On aspose.net the domain is already .NET-specific, so
    products.aspose.net/cells/net is wrong — it should be
    products.aspose.net/cells.

    Args:
        markdown: Full README.md content as a string.
        family_slug: Lowercase family name, e.g. "cells".

    Returns:
        List of offending URL strings, empty if none found.
    """
    slug = re.escape(family_slug)
    pattern = re.compile(
        rf"https?://(?:products|docs|reference|kb)\.aspose\.net/{slug}/net[^\s)\]]*"
    )
    return pattern.findall(markdown)


def find_wrong_blog_links(markdown: str) -> list[str]:
    """Return blog.aspose.com/category/... links (wrong domain + wrong path).

    The correct pattern is blog.aspose.net/categories/aspose.{slug}-plugin-family/.

    Args:
        markdown: Full README.md content as a string.

    Returns:
        List of matching URL strings, empty if none found.
    """
    return _WRONG_BLOG_PATTERN.findall(markdown)


def find_wrong_contact_links(markdown: str) -> list[str]:
    """Return about.aspose.com/contact-us/ links (wrong domain + wrong path).

    The correct URL is https://about.aspose.net/contact/.

    Args:
        markdown: Full README.md content as a string.

    Returns:
        List of matching URL strings, empty if none found.
    """
    return _WRONG_CONTACT_PATTERN.findall(markdown)


def find_missing_required_links(markdown: str, family_slug: str | None = None) -> list[str]:
    """Return identifiers for required links that are absent from the markdown.

    Currently checks for:
    - KB link (kb.aspose.net)

    Args:
        markdown: Full README.md content as a string.
        family_slug: Optional family slug for family-specific checks.

    Returns:
        List of missing link identifiers, empty if all required links present.
    """
    missing: list[str] = []
    if "kb.aspose.net" not in markdown:
        identifier = f"kb.aspose.net/{family_slug}" if family_slug else "kb.aspose.net"
        missing.append(identifier)
    return missing
