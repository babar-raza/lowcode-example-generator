# Rejected or Misleading Claims from Prior Sprints

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Claim 1: KNOWN_PATTERN-Only Catalog Entries Are Registry-Ready

**Claim**: Plugin URLs constructed from `products.aspose.net/{family}/net/{operation}` patterns are
sufficient to populate a registry with reflection-derived class/method mappings.

**Rejection reason**: URL patterns without source-code evidence do not establish what API the official
product page actually recommends. Two different plugin pages may use completely different classes/methods
even within the same family.

**Correct approach**: Fetch the real page, extract official code examples, derive API mapping from code.

---

## Claim 2: Family-Level Probe = Plugin-Level Coverage

**Claim**: If `barcode: PROBE_CONFIRMED (generate-barcode)` then all 5 barcode plugins are validated.

**Rejection reason**: Each plugin page may have distinct API patterns. `generate-barcode` uses
`BarcodeGenerator` but `recognize-barcode` uses `BarCodeReader`. These are different classes.
One probe cannot cover all plugins in a family.

**Correct approach**: Each plugin requires its own code evidence before claiming coverage.

---

## Claim 3: Reflection-First Mapping

**Claim**: Scan DLL types, find classes matching plugin name patterns, assign as API mapping.

**Rejection reason**: Reflection finds what classes EXIST but not what classes the official page
RECOMMENDS for a specific use case. The official code example is authoritative; reflection is validation.

**Correct approach**: Get official code first, then use reflection to validate class existence.

---

## Claim 4: REFLECTION_CANDIDATE Implies Readiness

**Claim**: `REFLECTION_CANDIDATE` status with confidence 0.78 implies the plugin is near-ready for transformation.

**Rejection reason**: REFLECTION_CANDIDATE only means types were found in the DLL matching heuristic patterns.
It provides no evidence that the official page recommends those types, or that the usage pattern is correct.

**Correct approach**: READY_FOR_TRANSFORMATION requires real page URL + harvested code + symbol extraction.

---

## Claim 5: Wave Roadmap Implies Code Evidence

**Claim**: Wave 1 (PROBE_CONFIRMED families) are ready for example generation.

**Rejection reason**: Probe-confirmed means a probe ran and produced output. It does NOT mean the probe
matches what the official product page shows as the intended workflow for end users.

**Correct approach**: Generate examples from official page code patterns. Probes validate the generated examples.

---

## Claim 6: 65 Plugins Cataloged = 65 Plugins with Code Evidence

**Claim**: 65 plugin URLs in the page hash ledger means 65 plugins with evidence.

**Rejection reason**: The prior sprint only recorded page URLs and computed URL hashes. No page content
was parsed for source-code links, gist URLs, inline snippets, or official code examples.

**Correct approach**: This sprint must parse each of the 65 pages for code content.

---

## Summary

| Rejected Claim | Category | Impact |
|---------------|----------|--------|
| KNOWN_PATTERN catalog is sufficient | WRONG_AUTHORITY | Registry would be synthetic |
| Family-level probe = plugin coverage | WRONG_SCOPE | 59 of 65 plugins uncovered |
| Reflection-first mapping | WRONG_AUTHORITY | Classes guessed, not evidence-backed |
| REFLECTION_CANDIDATE = near-ready | WRONG_STATUS | Transformation would fail |
| Wave roadmap implies code evidence | WRONG_IMPLICATION | No official code harvested |
| 65 URLs = 65 plugins with evidence | WRONG_CLAIM | Only hashes, no content |
