# Security Count Decision — Sprint 31

**Date:** 2026-05-17
**Decision:** SECURITY_IS_COUNTED_AND_PRESENT_IN_PR7

## Finding

Security is present in `workspace/pr-dry-run/pdf-controlled-pilot-pr7/examples/pdf/lowcode/security/` and has been since Sprint 23.

- Sprint 23 commit `8dce137`: "Wave E (Security + FormFlattener): both ALL_PASS via template_first generation."
- PR#7 package contains: `security/` + `form-flattener/` = **2 examples**
- Aspose.PDF version: 26.5.0
- bin/obj count: 0
- Blocking flags: none

## Sprint 30 Error

Sprint 30 `pdf-pr7-final-package-audit.json` incorrectly recorded:
```json
"examples": ["form-flattener"]
```

Correct value should be:
```json
"examples": ["security", "form-flattener"]
```

This was a documentation error. The package itself was never wrong.

## Count Decision

| PR | Examples | Correct |
|----|----------|---------|
| PR#3 | doc-converter, html, xls-converter | 3 |
| PR#5 | jpeg, png, tiff | 3 |
| PR#6 | image-extractor, table-generator, toc-generator | 3 |
| PR#7 | **security, form-flattener** | **2** (not 1) |
| PR#8 | form-editor, form-exporter | 2 |
| PR#9 | signature | 1 |
| **Total** | | **14** |

**Security is COUNTED. Total PR-ready = 14. All 14 examples are in clean packages.**
