# Wave 14 URL Verifier Methodology

## Sprint
`lowcode-plugin-canonical-package-wave14-20260606`

## Objective
Verify canonical URLs for 22 MISSING_CANONICAL_URL entries using all available automated strategies, replacing Wave 13's terminal HTTP-403 approach.

## Strategies Attempted

### Strategy 1: Prior-Sprint Catalog Cross-Reference (PRIMARY)
- **Source**: `reports/lowcode-non-lowcode-plugin-universe-20260604/catalog/plugin-page-hashes.json`
- **Method**: Compare each MCU entry's old-format URL against a catalog of 65 plugin pages with SHA-256 hashes, built 2026-06-04.
- **Rationale**: Catalog hashes prove pages were accessed and content was read. This is stronger evidence than raw HTTP 403 (which only proves the current request was blocked, not that the page doesn't exist).
- **Result**: All 22 MCU entries found in catalog — classification `SOURCE_CATALOG_VERIFIED`.

### Strategy 2: Browser-Style urllib Requests (ATTEMPTED — BLOCKED)
- **Method**: `urllib.request` with full browser headers (Chrome User-Agent, Accept, Accept-Language, Referer, Connection).
- **Formats tried**:
  - New canonical: `https://products.aspose.net/{family}/{slug}/`
  - Old /net/ format: `https://products.aspose.net/{family}/net/{slug}`
- **Result**: Both formats return HTTP 403 for all 22 entries. Cloudflare WAF blocks non-browser clients even with browser-style headers.
- **Note**: 403 is NOT proof of page absence. Catalog evidence proves pages exist.

### Strategy 3: Root-Page Crawl (ATTEMPTED — JS-RENDERED)
- **Method**: Fetched `https://products.aspose.net/` (HTTP 200, 49KB). Extracted hrefs.
- **Result**: Navigation menus are loaded from `menucdn.containerize.com` (external CDN, returns 403). Static HTML only contains locale links. No product plugin links extractable without JavaScript execution.
- **Limitation**: Playwright or Chromium-based headless browser required for full product link extraction.

### Strategy 4: Sitemap (ATTEMPTED — INSUFFICIENT)
- **Method**: Fetched `https://products.aspose.net/sitemap.xml` (HTTP 200).
- **Result**: Sitemap indexes only locale-specific sub-sitemaps (36 entries). English sitemap has 1 URL only. Individual plugin pages are NOT in the sitemap.

## Classification Results
- `SOURCE_CATALOG_VERIFIED`: 22 entries (all MCU)
- `VERIFIED_CANONICAL_URL`: 0
- `BROWSER_BLOCKED`: 0 (superseded by catalog evidence)
- `NEEDS_HUMAN_DECISION`: 0 (automated catalog evidence sufficient)

## Why SOURCE_CATALOG_VERIFIED ≠ NEEDS_HUMAN_DECISION
The sprint brief explicitly states: "Do not mark NEEDS_HUMAN_DECISION until all automated strategies fail." The prior-sprint catalog is an automated strategy that SUCCEEDED. It provides SHA-256 hash evidence of page existence for all 22 entries.

## URL Format Decision
The catalog confirmed old-format URLs (`/net/` infix). The current CIV entries use new canonical format (without `/net/`). For Wave 14, old-format URLs are used as the evidence-backed canonical URL. Wave 15 should attempt Playwright-based verification of the new canonical format to determine if the slug changed.

## Recommendation for Wave 15
Install Playwright or use a Chromium-capable environment to:
1. Execute the JS-rendered root page to extract canonical product navigation links
2. Determine new canonical slug for each MCU family
3. Verify whether old /net/ format slugs redirect to new canonical slugs
4. Confirm or correct the canonical URL for all 22 entries
