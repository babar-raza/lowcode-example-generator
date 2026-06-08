# Sitemap Fetch Proof — products.aspose.net

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Sitemap Fetch Attempt

### Primary: https://products.aspose.net/en/sitemap.xml
- **Result**: FETCHED (HTTP 200)
- **Content**: 1 URL — only `https://products.aspose.net/` (root)
- **Plugin pages discovered via sitemap**: 0
- **Assessment**: Sitemap is minimal; does not enumerate individual plugin pages

### Sitemap Index: https://products.aspose.net/sitemap.xml
- **Result**: FETCHED (HTTP 200)
- **Content**: 36 locale sub-sitemap URLs (en, de, fr, es, zh, ja, ru, pt, it, ko, ar, pl, fa, id, cs, vi, tr, th, sv, el, ...)
- **Assessment**: Index references localized sitemaps; /en/ sitemap only has root URL

### Plugin Page Direct Fetch Attempts
- Target: https://products.aspose.net/barcode/net/generate-barcode
- Result: HTTP 403 Forbidden (all User-Agent variations tested)
- User-Agents tried: curl, Wget, LowcodeGenerator, Chrome/120

### Blocker Classification
- **Blocker**: CRAWL_BLOCKED — products.aspose.net returns 403 for plugin pages from this environment
- **Sitemap URLs found via sitemap.xml**: 1 (root only)
- **Plugin page content**: NOT FETCHABLE directly

---

## Alternative: GitHub Repository Crawl

Since products.aspose.net plugin pages are 403-blocked, we use the official GitHub repositories
as the source-code authority. These repositories are:
1. Maintained by Aspose engineering teams
2. Linked from official product documentation
3. Used in Aspose's own demo sites
4. Confirmed real via GitHub API (18/18 repos accessible)

### Repo Discovery
- All 18 family repos confirmed via GitHub API
- See `.local/code-cache/github-repo-index.json`

---

## Plugin Page Inventory Source

The 65 plugin URLs from the prior sprint catalog are used as the canonical URL inventory.
These URLs were fetched and hashed in the prior sprint (plugin-page-hashes.json).
This sprint cannot re-fetch page content (403 blocked) but treats these as the canonical URL list.

### Blocker Evidence
```
$ curl -I "https://products.aspose.net/barcode/net/generate-barcode"
HTTP/1.1 403 Forbidden
```

All direct page fetches return 403. This is a CRAWL_BLOCKED external blocker, not a system defect.

---

## What Was Successfully Fetched

1. Sitemap index (36 localized sub-sitemaps identified)
2. /en/ sub-sitemap (1 URL: root)
3. 18/18 GitHub repo existence confirmed
4. 18/18 GitHub repo file trees fetched (full recursive)
5. Total C# example files available across repos: 3,193
6. Plugin source map built: 55/65 plugins have matched GitHub example files
