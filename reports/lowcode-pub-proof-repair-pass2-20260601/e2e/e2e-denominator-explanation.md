# E2E Denominator Explanation

Sprint: lowcode-pub-proof-repair-pass2-20260601

## E2E Universe: 49 tested

### Publishable E2E: 44/44
- 42 main-class examples
- 1 companion (words/signer)
- 1 environment-dependent (pdf/timestamp)
- Total publishable: 44

### Diagnostic (non-publication) E2E: 5/5
- 4 duplicate examples (slides-compress, slides-convert, slides-merger, email-converter)
- 1 non-runnable helper (slides/for-each) — tested as diagnostic

### NOT in E2E (by design): 1
- pdf/form-importer — EXTERNAL_UPSTREAM_BUG, excluded because FormImporter.Process() throws NullReferenceException

### Explanation
49 = 44 publishable + 4 duplicates + 1 helper (slides/for-each).
FormImporter is NOT part of the 49. It is excluded from E2E.
