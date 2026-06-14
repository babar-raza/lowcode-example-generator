"""Command: catalog-discover — discover plugin pages for non-LowCode Aspose families."""

from __future__ import annotations

import datetime
import json
import logging
import re
from dataclasses import asdict
from pathlib import Path

logger = logging.getLogger(__name__)

# Default family slug → products.aspose.net index URL
_FAMILY_INDEX_URLS: dict[str, str] = {
    "barcode": "https://products.aspose.net/barcode/net/",
    "imaging": "https://products.aspose.net/imaging/net/",
    "zip": "https://products.aspose.net/zip/net/",
    "html": "https://products.aspose.net/html/net/",
    "cad": "https://products.aspose.net/cad/net/",
    "ocr": "https://products.aspose.net/ocr/net/",
    "psd": "https://products.aspose.net/psd/net/",
    "svg": "https://products.aspose.net/svg/net/",
    "omr": "https://products.aspose.net/omr/net/",
    "gis": "https://products.aspose.net/gis/net/",
    "tasks": "https://products.aspose.net/tasks/net/",
    "note": "https://products.aspose.net/note/net/",
    "drawing": "https://products.aspose.net/drawing/net/",
    "font": "https://products.aspose.net/font/net/",
    "finance": "https://products.aspose.net/finance/net/",
    "page": "https://products.aspose.net/page/net/",
    "tex": "https://products.aspose.net/tex/net/",
}

_COMMON_VERBS = frozenset(
    [
        "generate",
        "convert",
        "read",
        "write",
        "create",
        "edit",
        "parse",
        "render",
        "export",
        "import",
        "compress",
        "decompress",
        "extract",
        "merge",
        "split",
        "rotate",
        "resize",
        "crop",
        "watermark",
        "sign",
        "recognize",
        "scan",
        "load",
        "save",
        "encode",
        "decode",
        "validate",
        "transform",
        "process",
    ]
)

# File format tokens to extract from page content
_FORMAT_RE = re.compile(
    r"\b(PDF|DOCX?|XLSX?|PPTX?|PNG|JPG|JPEG|GIF|BMP|TIFF?|SVG|HTML|ZIP|RAR"
    r"|CAD|DWG|DXF|PSD|AI|EMF|WMF|WEBP|ICO|JSON|XML|CSV|TXT|RTF|EPS|PS"
    r"|MPP|MHTML|EPUB|MOBI|DJVU|PCL|XPS)\b"
)

# NuGet package hints on page
_NUGET_RE = re.compile(r"Aspose\.[A-Za-z0-9]+")

# Plugin page link pattern: /net/<slug>  or /<family>/net/<slug>
_PLUGIN_LINK_RE = re.compile(
    r'href="([^"]*(?:/net/|/\w+/net/)[^"]*)"',
    re.IGNORECASE,
)

# Sitemap url extraction
_SITEMAP_URL_RE = re.compile(r"<loc>([^<]+)</loc>")


def add_parser(subparsers):
    """Register the catalog-discover subcommand."""
    parser = subparsers.add_parser(
        "catalog-discover",
        help="Discover non-LowCode plugin pages from products.aspose.net",
    )
    parser.add_argument(
        "--family",
        metavar="FAMILY",
        help="Single family slug to discover (e.g. barcode)",
    )
    parser.add_argument(
        "--families",
        nargs="+",
        metavar="FAMILY",
        help="Multiple family slugs to discover",
    )
    parser.add_argument(
        "--all-families",
        action="store_true",
        help="Discover all known non-LowCode families",
    )
    parser.add_argument(
        "--replay",
        action="store_true",
        help="Use cached pages only — no HTTP calls",
    )
    parser.add_argument(
        "--sitemap",
        action="store_true",
        help="Attempt sitemap discovery before family-page discovery",
    )
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Write catalog JSON to this path (default: pipeline/plugin-capability-registry/website-catalog.json)",
    )
    parser.add_argument(
        "--delay-ms",
        type=int,
        default=1000,
        help="Delay between HTTP requests in milliseconds (default: 1000)",
    )
    parser.add_argument(
        "--enrich-registry",
        action="store_true",
        help="Write plugin_page_hash back into registry YAMLs",
    )
    parser.set_defaults(func=handle)
    return parser


def handle(args) -> int:
    """Handle the catalog-discover command."""
    import os

    repo_root = Path(__file__).resolve().parents[3]

    # Resolve families
    families: list[str] = []
    if getattr(args, "families", None):
        families = list(args.families)
    elif getattr(args, "family", None):
        families = [args.family]
    elif getattr(args, "all_families", False):
        families = list(_FAMILY_INDEX_URLS.keys())
    else:
        print("Error: specify --family, --families, or --all-families")
        return 1

    # Set delay env var for crawler
    if hasattr(args, "delay_ms"):
        os.environ["CATALOG_CRAWL_DELAY_MS"] = str(args.delay_ms)

    output_path = (
        Path(args.output)
        if getattr(args, "output", None)
        else (repo_root / "pipeline" / "plugin-capability-registry" / "website-catalog.json")
    )

    # Load existing catalog to merge/update
    existing_by_slug: dict[str, dict] = {}
    if output_path.exists():
        try:
            existing_data = json.loads(output_path.read_text(encoding="utf-8"))
            # Support both flat list and {"families": {...}} structure
            if isinstance(existing_data, list):
                for entry in existing_data:
                    if isinstance(entry, dict) and "slug" in entry:
                        existing_by_slug[entry["slug"]] = entry
            elif isinstance(existing_data, dict) and "families" in existing_data:
                for fam_slug, fam_entries in existing_data["families"].items():
                    if isinstance(fam_entries, list):
                        for entry in fam_entries:
                            if isinstance(entry, dict) and "slug" in entry:
                                existing_by_slug[entry["slug"]] = entry
        except (json.JSONDecodeError, KeyError, TypeError):
            pass

    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    all_entries: list[dict] = []
    total_errors: list[str] = []

    use_replay = getattr(args, "replay", False)
    use_sitemap = getattr(args, "sitemap", False)

    for family_slug in families:
        logger.info("Discovering family: %s", family_slug)
        entries, errors = _discover_family(
            family_slug=family_slug,
            repo_root=repo_root,
            replay=use_replay,
            use_sitemap=use_sitemap,
            timestamp=timestamp,
        )
        all_entries.extend(entries)
        total_errors.extend(errors)
        print(f"  {family_slug}: {len(entries)} entries, {len(errors)} errors")

    # Build output structure grouped by family
    families_map: dict[str, list[dict]] = {}
    for entry in all_entries:
        fam = entry.get("family_slug") or entry.get("family", "unknown")
        families_map.setdefault(fam, []).append(entry)

    # Merge with existing entries for families not in this run
    for slug, existing_entry in existing_by_slug.items():
        fam = existing_entry.get("family_slug") or existing_entry.get("family", "unknown")
        if fam not in families_map:
            families_map.setdefault(fam, []).append(existing_entry)

    catalog = {
        "generated_at": timestamp,
        "total_entries": sum(len(v) for v in families_map.values()),
        "families_discovered": list(families_map.keys()),
        "errors": total_errors,
        "families": families_map,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Catalog written: {output_path} ({catalog['total_entries']} entries)")

    if getattr(args, "enrich_registry", False):
        enriched = _enrich_registry_hashes(repo_root, families_map)
        print(f"Registry enrichment: {enriched} entries updated with plugin_page_hash")

    return 0


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------


def _discover_family(
    *,
    family_slug: str,
    repo_root: Path,
    replay: bool,
    use_sitemap: bool,
    timestamp: str,
) -> tuple[list[dict], list[str]]:
    """Discover all plugin pages for a family. Returns (entries, errors)."""
    from plugin_examples.website_catalog.crawler import (
        WebsiteCatalog,
        _fetch_url,  # noqa: WPS437 — internal helper, acceptable here
        normalize_url,
    )

    index_url = _FAMILY_INDEX_URLS.get(family_slug)
    if not index_url:
        return [], [f"No index URL configured for family: {family_slug}"]

    catalog = WebsiteCatalog(replay=replay)

    # Step 1: Gather candidate plugin page URLs
    plugin_urls: list[str] = []
    errors: list[str] = []

    if use_sitemap:
        sitemap_urls = _discover_via_sitemap(family_slug, index_url, replay)
        plugin_urls.extend(sitemap_urls)

    if not plugin_urls:
        # Fall back to crawling the family index page and extracting links
        index_result = catalog.crawl_family(family_slug, [index_url])
        errors.extend(index_result.errors)

        # Also try to extract plugin links from the index page HTML
        family_html = _get_page_html(index_url, replay)
        if family_html:
            extracted = _extract_plugin_links(family_html, index_url, family_slug)
            plugin_urls.extend(extracted)

        if not plugin_urls:
            # Use the index URL itself as the only page
            plugin_urls = [index_url]

    # Deduplicate, normalizing locales
    seen: set[str] = set()
    deduped: list[str] = []
    for u in plugin_urls:
        normalized = normalize_url(u)
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(normalized)

    # Step 2: Crawl each plugin page and build enriched entries
    result = catalog.crawl_family(family_slug, deduped)
    errors.extend(result.errors)

    enriched: list[dict] = []
    for base_entry in result.entries:
        html = _get_page_html(base_entry.url, replay) or ""
        entry_dict = _enrich_entry(base_entry, html, family_slug, timestamp)
        enriched.append(entry_dict)

    return enriched, errors


def _discover_via_sitemap(family_slug: str, base_url: str, replay: bool) -> list[str]:
    """Try to fetch /sitemap.xml and extract URLs for this family."""
    from urllib.parse import urlparse

    parsed = urlparse(base_url)
    sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

    content = _get_page_html(sitemap_url, replay)
    if not content:
        return []

    all_urls = _SITEMAP_URL_RE.findall(content)
    # Filter to URLs containing this family slug
    return [u for u in all_urls if f"/{family_slug}/" in u.lower()]


def _extract_plugin_links(html: str, base_url: str, family_slug: str) -> list[str]:
    """Extract plugin page links from family index HTML."""
    from urllib.parse import urljoin, urlparse

    base_parsed = urlparse(base_url)
    base_origin = f"{base_parsed.scheme}://{base_parsed.netloc}"

    links: list[str] = []
    for match in _PLUGIN_LINK_RE.finditer(html):
        href = match.group(1)
        if href.startswith("http"):
            full_url = href
        elif href.startswith("/"):
            full_url = base_origin + href
        else:
            full_url = urljoin(base_url, href)

        # Only include links plausibly for this family
        if family_slug in full_url.lower():
            links.append(full_url)

    return links


def _get_page_html(url: str, replay: bool) -> str | None:
    """Get page HTML from cache (replay) or live fetch."""
    import re as _re
    import time as _time

    from plugin_examples.website_catalog.crawler import (
        _cache_path,
        _fetch_url,
        _is_cache_fresh,
        _read_cache,
        normalize_url,
    )

    normalized = normalize_url(url)
    # Derive slug from URL for cache path
    slug = _re.sub(r"https?://[^/]+", "", normalized)
    slug = slug.strip("/").replace("/", "_").replace(".", "_") or "index"

    # We need family for cache path — extract from URL or use "general"
    parts = normalized.split("/")
    try:
        family_guess = parts[3] if len(parts) > 3 else "general"
    except IndexError:
        family_guess = "general"

    cache_file = _cache_path(family_guess, slug)

    if replay:
        if cache_file.exists():
            return _read_cache(cache_file)
        return None

    if _is_cache_fresh(cache_file):
        return _read_cache(cache_file)

    return _fetch_url(normalized)


def _enrich_entry(base_entry, html: str, family_slug: str, timestamp: str) -> dict:
    """Build an enriched entry dict from a PluginEntry and page HTML."""
    from plugin_examples.website_catalog.drift_detector import compute_page_hash

    # Extract title
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    marketing_title = re.sub(r"<[^>]+>", "", title_match.group(1)).strip() if title_match else base_entry.plugin_name

    # Extract description from meta or first <p>
    desc_match = re.search(
        r'<meta\s+name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    ) or re.search(r"<p[^>]*>(.*?)</p>", html, re.IGNORECASE | re.DOTALL)
    description = ""
    if desc_match:
        description = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()[:300]

    # Extract action verbs from page text
    page_text = re.sub(r"<[^>]+>", " ", html).lower()
    action_verbs = sorted(v for v in _COMMON_VERBS if re.search(rf"\b{v}\b", page_text))

    # Extract format tokens
    formats_found = list(dict.fromkeys(_FORMAT_RE.findall(html.upper())))

    # Split into input/output by context heuristic
    # Formats after "from" / "input" → input_formats; after "to" / "output" → output_formats
    input_formats: list[str] = []
    output_formats: list[str] = []
    for fmt in formats_found:
        fmt_lower = fmt.lower()
        # Check surrounding context for "to {fmt}" vs "from {fmt}"
        ctx_match = re.search(rf"\b(from|to|into|as|in)\s+{fmt_lower}\b", page_text)
        if ctx_match and ctx_match.group(1) in ("to", "into", "as"):
            output_formats.append(fmt)
        elif ctx_match and ctx_match.group(1) in ("from", "in"):
            input_formats.append(fmt)
        else:
            # No clear direction — add to both
            input_formats.append(fmt)
            output_formats.append(fmt)

    # Deduplicate
    input_formats = list(dict.fromkeys(input_formats))
    output_formats = list(dict.fromkeys(output_formats))

    # Extract NuGet hints
    nuget_hints = list(dict.fromkeys(_NUGET_RE.findall(html)))

    content_hash = compute_page_hash(html) if html else base_entry.page_hash

    return {
        "family": base_entry.family,
        "family_slug": family_slug,
        "plugin_name": base_entry.plugin_name,
        "plugin_slug": base_entry.slug,
        "url": base_entry.url,
        "canonical_url": base_entry.url,
        "slug": base_entry.slug,
        "marketing_title": marketing_title,
        "description": description,
        "action_verbs": action_verbs,
        "input_formats": input_formats,
        "output_formats": output_formats,
        "nuget_hints": nuget_hints,
        "page_hash": base_entry.page_hash,
        "content_hash": content_hash,
        "marketing_only": True,
        "extraction_timestamp": timestamp,
    }


def _enrich_registry_hashes(
    repo_root: Path, families_map: dict[str, list[dict]]
) -> int:
    """Write plugin_page_hash from catalog discovery back into registry YAMLs.

    For each family in families_map, look up the corresponding registry YAML
    and update the plugin_page_hash field on entries whose plugin_slug matches.
    """
    import yaml

    registry_dir = repo_root / "pipeline" / "plugin-capability-registry"
    updated_count = 0

    # Build slug → content_hash lookup from catalog discovery results
    hash_by_slug: dict[str, str] = {}
    for fam_entries in families_map.values():
        for entry in fam_entries:
            slug = entry.get("plugin_slug") or entry.get("slug", "")
            content_hash = entry.get("content_hash") or entry.get("page_hash")
            if slug and content_hash:
                hash_by_slug[slug] = content_hash

    # Also build family-level hash (hash of index page) for entries without
    # a direct slug match
    family_hash: dict[str, str] = {}
    for fam_slug, fam_entries in families_map.items():
        for entry in fam_entries:
            ch = entry.get("content_hash") or entry.get("page_hash")
            if ch:
                family_hash.setdefault(fam_slug, ch)

    for registry_file in sorted(registry_dir.glob("*.yaml")):
        if registry_file.name == "schema.yaml":
            continue
        family_slug = registry_file.stem

        with open(registry_file, encoding="utf-8") as fh:
            raw = fh.read()

        data = yaml.safe_load(raw) or {}
        entries = data.get("entries", []) or []
        modified = False

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            slug = entry.get("plugin_slug", "")
            # Try exact slug match first, then family-level fallback
            new_hash = hash_by_slug.get(slug) or family_hash.get(family_slug)
            if new_hash and entry.get("plugin_page_hash") != new_hash:
                entry["plugin_page_hash"] = new_hash
                modified = True
                updated_count += 1

        if modified:
            with open(registry_file, "w", encoding="utf-8") as fh:
                yaml.dump(data, fh, default_flow_style=False, allow_unicode=True, sort_keys=False)
            logger.info("Updated %s with plugin_page_hash", registry_file.name)

    return updated_count
