# README Validator Policy — Sprint 60 Phase 3

**Date:** 2026-05-21

---

## Policy: Result-Collection Output APIs

**Applies to:** `pdf-image-extractor`, `pdf-text-extractor`

For LowCode APIs that return output via `ResultCollection` rather than writing to a named output file, the `output_format` claim is proved by API contract, not by a literal file extension in Program.cs or README.

- `ImageExtractor`: outputs PNG images to `ResultCollection` — `.png` will NOT appear as a file path in Program.cs
- `TextExtractor`: outputs extracted text to `StringResult` — no output file extension

**Validator rule:** For these scenario IDs, `output_format_in_programcs` must not be checked against a literal file extension. Instead, check that the API type is present and the correct ResultCollection pattern is used.

**Encoded in:** `DestinationIdMapper.RESULT_COLLECTION_OUTPUT_APIS`

---

## Policy: Root README Version References

**Applies to:** 6 destination repos

### Group A: Version Present (Consistent)
- Cells, PDF, Email, Slides: root README contains a version reference
- These READMEs were authored with an explicit version number
- Validator: `contains_version=true` expected; warn if false

### Group B: Version Intentionally Omitted
- **Words, Diagram:** root README does NOT contain a version pin
- These READMEs describe the package at the family level
- Version is managed in `Directory.Packages.props` — not duplicated in README
- Version drift (26.4.x → 26.5.x) is tracked in release-status; README update requires `APPROVE_README_PUSH`
- Validator: `contains_version=false` is EXPECTED for these families — do not raise a warning

**Validator rule:** `contains_version=false` for Words and Diagram is `POLICY_COMPLIANT`, not a warning. The validator must encode `VERSION_OPTIONAL_FAMILIES = {"words", "diagram"}` and skip the version check for them.

---

## Policy: Example README Minimum Content Checks

For each example-level README in a destination repo, the following checks apply:

| Check | Required | Notes |
|-------|----------|-------|
| Family name present | YES | "Aspose.{Family}" or "{family}" in README |
| Workflow type present | YES | API class name (e.g., "HtmlConverter") |
| Package ID present | YES | "Aspose.Cells", "Aspose.Pdf", etc. |
| Input format present | ADVISORY | May not be mentioned literally in minimal READMEs |
| Output format present | ADVISORY | May not be mentioned literally in minimal READMEs |
| "How to run" section | ADVISORY | "dotnet run" or similar |

**Minimum pass condition:** family_name + workflow_type + package_id all present → MATCH.
If any one is missing → PARTIAL (not FAIL — READMEs may be minimal by design).

---

## Policy: Content Audit vs Size Audit

**Sprint 59 violation:** README audit used `readme_present=true` and `readme_size=NNN` only — no content checks.

**Sprint 60 requirement:** README audit MUST check at minimum:
1. Family name in README
2. Workflow type/API class in README
3. Package ID in README

A README audit that only checks presence and size is classified as `AUDIT_SHALLOW` and is NOT acceptable as closure evidence.

**Encoded in:** `DestinationReadmeAuditPolicy.REQUIRED_CONTENT_FIELDS`
