# Approval-Gated Publication Plan — Wave 10

Sprint: lowcode-plugin-canonical-package-wave10-20260605
Date: 2026-06-05
Version: v3

---

## Summary

| Category | Count |
|---|---|
| Total registry entries | 70 |
| PUBLICATION_READY (Wave 8 + Wave 9, proven) | 16 |
| PUBLICATION_CANDIDATE_LOCAL_CLEAN (Wave 10, new) | 17 |
| **Total packages with full proof** | **33** |
| NEEDS_PACKAGE_PROOF (CANONICAL_IDENTITY_VERIFIED, no package) | 10 |
| MISSING_CANONICAL_URL | 22 |
| SLUG_ALIAS_PENDING_MIGRATION | 5 |

---

## Tier 1: PUBLICATION_READY (16 packages — Wave 8 + Wave 9)

These 16 packages were proven in prior sprints and are approved for publication. No further approval required.

**Wave 8 (4):**
- html/html-to-pdf-converter
- imaging/image-converter
- imaging/image-resizer
- note/convert-onenote-to-pdf

**Wave 9 (12):**
- html/html-to-docx-converter
- html/html-to-image-converter
- imaging/image-compressor
- imaging/image-cropper
- imaging/image-filters
- imaging/image-merger
- imaging/add-watermark
- imaging/image-rotator
- note/convert-onenote-to-word
- note/convert-onenote-to-image
- tasks/project-to-pdf-converter
- tasks/mpp-to-excel

**Gate:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` — PREVIOUSLY USED

---

## Tier 2: PUBLICATION_CANDIDATE_LOCAL_CLEAN (17 packages — Wave 10)

These 17 packages were built in this sprint with full package proof (Program.cs, .csproj, output-validation.json PASS, source-provenance.json, package-manifest.json). They require approval before publication.

**Packages:**
- barcode/1d-barcode-writer
- barcode/1d-barcode-reader
- barcode/2d-barcode-writer
- barcode/2d-barcode-reader
- drawing/convert-drawing
- drawing/create-drawing
- finance/convert-xbrl
- ocr/scan-document
- ocr/image-text-finder
- ocr/invoice-to-text
- ocr/photo-to-text
- ocr/table-to-text
- psd/animation-maker
- psd/photo-processor
- svg/svg-to-image-converter
- tex/latex-figure-renderer
- zip/compress-files

**Required action to advance to PUBLICATION_READY:**
1. Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVED` for Wave 10
2. Run publication pipeline for each family
3. Verify PR creation and merge

**Gate:** `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` — NOT_SET (Wave 10)

---

## Tier 3: NEEDS_PACKAGE_PROOF (10 packages — Wave 11 queue)

CANONICAL_IDENTITY_VERIFIED but no package built yet. These are the 10 entries migrated from SLUG_ALIAS_REQUIRED in this sprint. They are in the Wave 11 queue.

- ocr/scanned-image-to-text
- ocr/scanned-pdf-to-text
- page/xps-converter
- page/eps-to-pdf
- page/ps-converter
- psd/psd-to-pdf
- tasks/mpp-to-html
- tasks/mpp-to-png
- zip/universal-extractor
- zip/universal-compressor

---

## Tier 4: Blocked (27 entries)

- MISSING_CANONICAL_URL (22): Require canonical URL discovery before any package work
- SLUG_ALIAS_PENDING_MIGRATION (5): Require canonical_plugin_slug confirmation before migration

---

## Approval Checklist (for Wave 10 Tier 2)

- [ ] Independent Verification (Lane H) completed: IV_ACCEPT or IV_ACCEPT_WITH_CAVEATS
- [ ] All 17 Wave 10 packages pass FPP validator
- [ ] CCV validator passes with 0 errors
- [ ] Full pytest suite passes (0 failures)
- [ ] Protected files unchanged (hashes verified)
- [ ] Exact-path git commit created
- [ ] Evidence ZIP + SHA-256 written
- [ ] `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` set to APPROVED for Wave 10
