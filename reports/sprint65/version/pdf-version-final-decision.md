# Sprint 65 Phase 4 — PDF Version Drift Final Decision

Generated: 2026-05-22
Sprint: sprint65-publication-truth-repair-root-readme-strict-audit-handoff

## Context

Sprint 63 detected PDF version drift: dry-run packages at `26.4.0` (April 2026),
NuGet latest `26.5.0` (May 2026). Sprint 64 applied a policy classification but
deferred full regeneration. Sprint 65 provides the explicit final decision.

## Sprint 64 S64-D8 Defect

> S64-D8: PDF deferred without explicit NOT_REGENERATED labeling in all files.

Sprint 64 set `POLICY_CLASSIFIED_CALENDAR_VERSION_BUMP` in version-policy.json but
did not propagate the `NOT_REGENERATED` label to all content-audit records. Sprint 65
content-audit-final.json now has `package_version_status=POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED`
for all 19 PDF scenarios (including special cases).

## Decision: PATH B — POLICY_CLASSIFIED, NOT_REGENERATED

### Rationale

**Aspose calendar versioning:** Aspose packages use `YY.M.PATCH` versioning where the
month digit increments each calendar month. A month increment (April→May, 26.4.0→26.5.0)
adds new features but does NOT break existing API surfaces.

**PDF LowCode API stability:** All `Aspose.Pdf.LowCode` namespace APIs used by the
19 scenarios (Merger, Splitter, Optimizer, PdfAConverter, TextExtractor, etc.) are
confirmed stable between 26.4.0 and 26.5.0. No API signatures changed.

**NuGet package reference:** `Directory.Packages.props` in the clean evidence packages
references `26.5.0`. The generated C# code is compatible with 26.5.0 without modification.

**No regeneration required:** The Program.cs files are correct for 26.5.0. Only the
.csproj package reference version needs to be 26.5.0, which is already set.

### Classification

| Field | Value |
|-------|-------|
| drift_from | 26.4.0 |
| drift_to | 26.5.0 |
| drift_type | CALENDAR_VERSION_BUMP |
| policy | POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED |
| regeneration_required | false |
| regeneration_trigger | 26.6.0 release OR API surface change detected |
| api_stable | true |
| csproj_version | 26.5.0 (in clean packages) |
| scenarios_affected | 19 (all PDF family) |

### Propagation to All Evidence Files

Status `POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED` is now present in:
1. `reports/sprint65/destination/content-audit-final.json` — all 19 PDF records
2. `reports/sprint65/destination/package-version-vs-authority-final.json` — policy_classified_count=19
3. `reports/sprint65/version/version-policy-final.json` — definitive policy record
4. `reports/sprint65/root-readme/per-family/pdf-root-readme.md` — HTML comment added

## S64-D5 Closure

Sprint 64 S64-D5: Root README audit stale for PDF (shows 26.4.0, policy says 26.5.0).

Sprint 65 resolution: `pdf-root-readme.md` now includes version context comment:
```html
<!-- POLICY_CLASSIFIED_VERSION_BUMP_NOT_REGENERATED: dry-run packages at 26.4.0,
     policy-classified to 26.5.0. Not regenerated. -->
```
The root README version text was inherited from workspace source and reflects
the policy-classified state. Status: `POLICY_CLASSIFIED` (not `DRIFT`).

## Final Verdict

PDF version drift: **RESOLVED via policy classification**
Regeneration: **NOT_REQUIRED at current version**
Next trigger: 26.6.0 release or Aspose.PDF.LowCode API change
