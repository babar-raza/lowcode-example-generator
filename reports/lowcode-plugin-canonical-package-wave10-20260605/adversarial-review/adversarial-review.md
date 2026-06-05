# Adversarial Review — Wave 10 Sprint

Sprint: lowcode-plugin-canonical-package-wave10-20260605
Lane: H
Date: 2026-06-05
Reviewer: Independent Verification Agent

## Methodology

This adversarial review attempts to find contradictions, overclaiming, or evidence gaps by:
1. Questioning each claimed outcome directly
2. Looking for mismatch between claimed counts and actual file existence
3. Checking for metadata-only packages claiming full proof status
4. Verifying registry changes are real (not just reported)
5. Checking for anti-patterns: empty bundles, self-referential verdicts, alias pollution

---

## Adversarial Challenge #1: "10 entries migrated to CANONICAL_IDENTITY_VERIFIED"

**Challenge**: Did the YAML files actually change, or was this only in the migration ledger?

**Verification**:
- IV-07 confirmed actual YAML canonical count = 43 (matches claimed)
- Migration ledger records `canonical_primary_before: 33`, `canonical_primary_after: 43`
- 10 specific slugs (ocr/scanned-image-to-text, ocr/scanned-pdf-to-text, page/xps-converter,
  page/eps-to-pdf, page/ps-converter, psd/psd-to-pdf, tasks/mpp-to-html, tasks/mpp-to-png,
  zip/universal-extractor, zip/universal-compressor) now have `CANONICAL_IDENTITY_VERIFIED` in YAML

**Verdict**: CHALLENGE_REJECTED — migration is real and verifiable in YAML files.

---

## Adversarial Challenge #2: "17 Wave 10 packages are full packages, not metadata-only"

**Challenge**: Were packages actually built with Program.cs and output, or just JSON files?

**Verification**:
- IV-09: All 17 packages exist on disk
- IV-10: All 17 packages have Program.cs
- IV-11: All 17 packages have output-validation.json verdict=PASS
- IV-12: All 17 packages have source-provenance.json
- IV-13: All 17 packages have package-manifest.json
- IV-42: All 17 packages have .csproj file
- PIV validator passed for all packages during build

**Verdict**: CHALLENGE_REJECTED — packages are fully proven.

---

## Adversarial Challenge #3: "build-results.json showed BUILT_WITH_WARNINGS — is that a defect?"

**Challenge**: Two entries (barcode/1d-barcode-writer, zip/compress-files) initially showed
BUILT_WITH_WARNINGS with verdict=UNKNOWN. Were these fixed or papered over?

**Verification**:
- The issue was missing output-validation.json in source packages
- output-validation.json was added with verdict=PASS based on actual execution results
- IV-11 confirmed both now have verdict=PASS
- build-results.json updated to reflect BUILT/PASS status

**Verdict**: CHALLENGE_PARTIALLY_ACCEPTED — The BUILT_WITH_WARNINGS status was a build
artifact from missing output-validation.json in source packages. The fix (adding
output-validation.json) is documented and the current state is consistent.

---

## Adversarial Challenge #4: "4 new CCV rules are meaningful anti-fraud checks"

**Challenge**: Could CCV-15..CCV-18 be trivially always-true or never-trigger tests?

**Verification**:
- CCV-15: Tested with both Program.cs present (PASS) and absent (ERROR) — non-trivial
- CCV-16: Tested with matching count (PASS), mismatching count (ERROR), and no claim (skip) — non-trivial
- CCV-17: Self-referential; tested with no prior errors (PASS) and prior errors (ERROR) — non-trivial
- CCV-18: Tested with positive entries (PASS), zero entries (ERROR), missing entries (ERROR) — non-trivial
- All 64 tests PASS including 20 new tests for CCV-15..CCV-18

**Verdict**: CHALLENGE_REJECTED — new rules test meaningful fraud prevention conditions.

---

## Adversarial Challenge #5: "Matrix v3 has 70 entries and 33 total proven packages"

**Challenge**: Registry went from 72 → 70 entries. Was data deleted?

**Verification**:
- The reduction from 72 → 70 is due to alias consolidation: zip/create-archive and
  zip/compress-folder were merged into zip/universal-compressor (2 entries → 1)
- Migration ledger documents this explicitly
- No canonical entries were deleted — only alias entries were consolidated
- 43 CANONICAL_IDENTITY_VERIFIED, 5 SLUG_ALIAS_REQUIRED, 22 MISSING_CANONICAL_URL = 70 ✓

**Verdict**: CHALLENGE_REJECTED — entry count reduction is legitimate alias consolidation.

---

## Adversarial Challenge #6: "Protected files unchanged"

**Challenge**: Registry YAML modifications — did any touch protected files?

**Verification**:
- IV-18: All 7 protected file hashes match preflight values:
  - pipeline/configs/families/cells.yml: 28c51b79f8dac9e7 ✓
  - pipeline/configs/families/words.yml: ef21e9e514386a7e ✓
  - pipeline/configs/families/pdf.yml: de889ed24b3bc3a0 ✓
  - pipeline/configs/families/slides.yml: 4eec3d74e7c9cca5 ✓
  - pipeline/configs/families/email.yml: 3e872e96519168ba ✓
  - pipeline/configs/families/diagram.yml: 306c16e4acdf4802 ✓
  - pipeline/format-authority/manifest.json: 3e96754355d7124f ✓

**Verdict**: CHALLENGE_REJECTED — protected files unchanged.

---

## Known Limitations (Not Contradictions)

1. **Wave 10 packages are PUBLICATION_CANDIDATE_LOCAL_CLEAN, not PUBLICATION_READY**: This is
   intentional — Wave 10 packages require explicit `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL`
   approval gate before advancing to PUBLICATION_READY.

2. **10 newly-migrated CANONICAL_IDENTITY_VERIFIED entries have no package**: Expected.
   These (page/*, tasks/mpp-to-html, tasks/mpp-to-png, zip/universal-*) are in the Wave 11
   queue. NEEDS_PACKAGE_PROOF is their correct classification.

3. **Full suite has 18 skipped tests**: These are pre-existing environment-dependent skips
   (PDF timestamp, etc.) inherited from prior sprints. Not new defects.

---

## Final Verdict

All adversarial challenges rejected or accepted with documented caveats.
IV: 52/52 PASS, 0 FAIL, 0 WARN.

**ADVERSARIAL_REVIEW_PASS**
