# Crawl Gaps

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Gap 1: products.aspose.net Plugin Pages 403-Blocked

**Gap**: Direct crawl of products.aspose.net/barcode/net/generate-barcode and all 65 plugin pages
returns HTTP 403 from this environment.

**Blocker code**: CRAWL_BLOCKED

**Impact**: Cannot extract source-code links, gist links, inline snippets directly from plugin page HTML.

**Mitigation applied**:
- Page URLs confirmed from prior sprint hash ledger (65 entries, real hashes, prior crawl was live)
- GitHub official repos used as code authority (18/18 repos confirmed and tree-fetched)
- All 65 plugin pages have canonical URLs recorded

---

## Gap 2: Sitemap Does Not Enumerate Plugin Pages

**Gap**: The products.aspose.net/en/sitemap.xml only includes the root URL. Plugin pages are not
in the sitemap.

**Impact**: Cannot discover new plugin pages from sitemap alone.

**Mitigation applied**:
- Prior sprint catalog used as starting URL inventory (65 plugin pages across 18 families)
- GitHub repo structures confirm plugin feature coverage per family

---

## Gap 3: SVG Plugins Have Weak GitHub Matches

**Gap**: svg family has only 1/4 plugins matched from GitHub (only convert-svg-to-pdf matched).
Other SVG plugins (convert-svg-to-png, convert-svg-to-jpg, merge-svg) didn't match keyword patterns.

**Blocker code**: SOURCE_FETCH_BLOCKED (partial)

**Mitigation**: Manual analysis will determine SVG implementation model from SvgDocument API.

---

## Gap 4: OMR Plugins Have No GitHub Matches

**Gap**: omr family has 0/2 plugins matched from keyword search.

**Blocker code**: SOURCE_FETCH_BLOCKED

**Mitigation**: Manual analysis will use OMR documentation and prior reflection data.

---

## Gap 5: Finance parse-xbrl Has No Match

**Gap**: finance/parse-xbrl has no GitHub example match.

**Blocker code**: SOURCE_FETCH_BLOCKED (partial)

**Mitigation**: Manual analysis from finance family docs.

---

## Summary

| Gap | Code | Status |
|-----|------|--------|
| products.aspose.net 403 | CRAWL_BLOCKED | EXTERNAL — mitigated with GitHub repos |
| Sitemap minimal | CRAWL_BLOCKED | EXTERNAL — mitigated with prior catalog |
| SVG partial match | SOURCE_FETCH_BLOCKED | PARTIAL — manual analysis planned |
| OMR no match | SOURCE_FETCH_BLOCKED | EXTERNAL — manual analysis planned |
| Finance partial | SOURCE_FETCH_BLOCKED | PARTIAL — manual analysis planned |
