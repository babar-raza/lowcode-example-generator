# Skill: Products Plugin Page Harvest

## Purpose
Crawl and extract content from products.aspose.net plugin pages for a given family/plugin.

## Inputs
- family_slug (e.g., "barcode")
- plugin_slug (e.g., "generate-barcode")
- Optional: sitemap URL override

## Outputs
- Page HTML (raw, cached in .local/catalog-cache/{family}/{plugin}.html)
- Page hash (SHA-256 of HTML content)
- Extracted: title, h1, h2, description
- Extracted: source_code_links, gist_links, github_links
- Extracted: inline_code_snippets
- Extracted: input_formats, output_formats from feature section
- Updated: crawl/plugin-page-inventory.json

## Prerequisites
- Network access to products.aspose.net
- .local/catalog-cache/ directory exists

## Step-by-Step Method

1. Construct canonical URL: `https://products.aspose.net/{family}/net/{plugin}`
2. Attempt HTTP GET with User-Agent browser string
3. If 403/blocked: record CRAWL_BLOCKED, use GitHub repo as fallback authority
4. If success: write HTML to `.local/catalog-cache/{family}/{plugin_slug}.html`
5. Compute SHA-256 of HTML content; store in page-hash-ledger.json
6. Extract from HTML:
   - `<h1>` for page title
   - Source code button/link with href matching github.com or gist.github.com
   - `<code>` / `<pre>` blocks for inline snippets
   - Format lists from "Supported Input Formats" / "Supported Output Formats" sections
7. Normalize locale: strip /en/, /de/, etc. prefix
8. Update crawl/plugin-page-inventory.json with new/updated entry
9. Update crawl/localized-duplicate-report.json

## Checks
- [ ] Page hash recorded
- [ ] Source-code links extracted (or CRAWL_BLOCKED recorded)
- [ ] Gist links extracted (or "none found" recorded)
- [ ] Inline snippets extracted (or "none found" recorded)
- [ ] Entry added to plugin-page-inventory.json

## Failure Modes
- HTTP 403: CRAWL_BLOCKED — use GitHub repo as authority; record in crawl-gaps.md
- HTTP 404: Plugin page does not exist — record as WEBSITE_PATTERN_UNVERIFIED
- Network timeout: Retry 3x; then record CRAWL_BLOCKED

## Evidence Requirements
- crawl/plugin-page-inventory.json entry
- crawl/plugin-page-hash-ledger.json updated
- If blocked: crawl/crawl-gaps.md entry with blocker code

## Example Entry
```json
{
  "url": "https://products.aspose.net/barcode/net/generate-barcode",
  "family_slug": "barcode",
  "plugin_slug": "generate-barcode",
  "page_hash": "1770337e14ce0847",
  "fetch_status": "HTTP_200",
  "source_code_links": ["https://github.com/aspose-barcode/..."],
  "gist_links": [],
  "inline_snippets": 2,
  "first_seen": "2026-06-04"
}
```

## Stop Rules
- Stop if page consistently returns 403 after 3 attempts with different User-Agents
- Do not guess page content from URL pattern alone

## Continue Rules
- Continue even if source-code links are empty (record as NO_SOURCE_LINK)
- Continue to next plugin if one fails
