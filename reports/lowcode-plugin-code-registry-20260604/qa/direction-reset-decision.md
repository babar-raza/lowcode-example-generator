# Direction Reset Decision

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04
## Decision Status: CONFIRMED

---

## Decision

The sprint direction is corrected from reflection-first/KNOWN_PATTERN catalog to
**page-first/code-evidence registry**.

---

## New Authority Hierarchy

1. **PRIMARY**: products.aspose.net plugin pages — page prose, feature boundaries, official API descriptions
2. **PRIMARY**: Source-code links on plugin pages — inline snippets, gist links, GitHub links
3. **SECONDARY**: Official repository examples (aspose-*.github.io, aspose-*.net repos)
4. **VALIDATION ONLY**: DllReflector — confirms classes/methods exist, does NOT establish intent
5. **VALIDATION ONLY**: Probes — confirms runnable pattern, does NOT establish official workflow

---

## New Registry Invariants

1. Every registry entry must trace to a real `products.aspose.net` URL.
2. Every READY_FOR_TRANSFORMATION entry must have harvested code (inline/gist/github).
3. Entries without code evidence must be marked `NEEDS_MANUAL_MAPPING` or `BLOCKED_NO_CODE`.
4. Reflection/probe fields are `validation_*` fields — never discovery fields.
5. Family-level probe coverage must NOT be used as plugin-level coverage.
6. WEBSITE_PATTERN_UNVERIFIED entries may not advance to READY_FOR_TRANSFORMATION.

---

## Retained from Prior Work

- Package aliases (correct NuGet IDs)
- DllReflector (validation infrastructure)
- Probe generator (validation infrastructure)
- Runner fallback stage (execution infrastructure)
- 65 plugin page URLs (starting crawl list, content must be re-fetched)
- 6 probe-confirmed baselines (barcode, imaging, zip, tasks, cad, font)

---

## Rejected Approaches

- KNOWN_PATTERN-only URL catalog without page content
- Reflection-first class assignment without official code
- Family probe counted as plugin coverage
- REFLECTION_CANDIDATE → READY_FOR_TRANSFORMATION without code evidence

---

## This Sprint Deliverables

1. Real sitemap fetch from products.aspose.net/en/sitemap.xml
2. Plugin page content harvest: source links, gists, snippets per page
3. Manual family analysis: 20 families, per-family implementation model
4. Plugin-code registry: entries backed by page + code evidence
5. At least 3 official-code snippet validations
6. First 10 transformation candidates with page + code provenance
7. Repeatable skills for future agents
8. Validator design to prevent regression

---

## Acceptance Condition

This sprint is accepted when:
- products.aspose.net was actually crawled (not just pattern-generated)
- Official code was harvested or explicitly blocked with proof
- Manual family analysis exists for all 20 in-scope families
- Plugin-code registry exists with evidence-backed entries
- At least 3 official-code snippets validated or blocked
- Protected files unchanged
