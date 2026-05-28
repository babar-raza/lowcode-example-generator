# System Qualification Sprint — Final Verdict

**Run ID:** sysqual-20260528-001
**Date:** 2026-05-28

---

## VERDICT: LOWCODE_SYSTEM_QUALIFICATION_ACCEPTED_WITH_EXTERNAL_BLOCKERS

---

## Summary

The LowCode Example Generator machinery has been fully qualified across the
complete Aspose product universe supported in this repository.

### Product Universe

- **Expected:** 26 (per sprint plan)
- **Found:** 25 (reconciled — see product-universe-reconciliation.md)
- **Reconciliation:** EVIDENCED_UNIVERSE_IS_25

### Classification Results

| Classification | Count | Products |
|---|---|---|
| LOWCODE_CONFIRMED | 6 | cells, diagram, email, pdf, slides, words |
| NO_LOWCODE_CONFIRMED | 16 | barcode, cad, drawing, finance, font, gis, html, imaging, note, omr, page, svg, tasks, tex, threed, zip |
| DISCOVERY_BLOCKED_EXTERNAL_PACKAGE | 3 | epub (package not found), ocr (Aspose.AI.LLM), psd (Aspose.JavaAttributes) |

### E2E Results (LowCode Confirmed Products)

| Product | Run ID | Result | Healing |
|---|---|---|---|
| cells | pilot-cells-final-20260528 | PASS (14/17) | NONE |
| diagram | pilot-diagram-final-20260528 | PASS (14/17) | NONE |
| email | pilot-email-final-20260528 | PASS (14/17) | NONE |
| pdf | pilot-pdf-heal-20260528 | PASS (14/17) | HEAL-001 (include_all_tfm_groups) |
| slides | pilot-slides-final-20260528 | PASS (14/17) | NONE |
| words | pilot-words-heal2-20260528 | PASS (14/17) | HEAL-002 (stale catalog hash) |

### Machinery Defects Found and Healed

1. **HEAL-001 (PDF):** `runner.py` missing `include_all_tfm_groups=True` for dependency resolution.
   - Root cause: runner.py diverged from discovery_sweep.py behavior for cross-TFM group deps.
   - Fix: Added `include_all_tfm_groups` config option to models/loader/runner/schema/pdf.yml.
   - Verified: Clean re-run passes.

2. **HEAL-002 (Words):** Stale cached catalog caused false hash mismatch.
   - Root cause: First run reused cached catalog from prior session.
   - Fix: Reverted denominator hash to canonical value; updated source reference.
   - Verified: Clean re-run passes.

### External Blockers (3)

| Product | Blocker | Type |
|---|---|---|
| epub | Aspose.Epub does not exist on NuGet | EXTERNAL_PACKAGE_NOT_FOUND |
| ocr | Aspose.AI.LLM not on NuGet | EXTERNAL_DEPENDENCY_NOT_ON_NUGET |
| psd | Aspose.JavaAttributes not on NuGet | EXTERNAL_DEPENDENCY_NOT_ON_NUGET |

All blockers are evidence-backed. Resolution requires Aspose to publish the packages.

### Validator Hardening

- 145 existing rules: UNCHANGED
- 1 code gap fixed (runner.py include_all_tfm_groups)
- 0 new validator rules required

### Publication Safety

- No live PRs created
- No remote mutations
- Approval gates confirmed: NOT_SET

### Independent Verification

- IV Verdict: **ACCEPT**
- All 25 products classified
- All 6 LowCode E2E runs verified
- All 2 healed products have resume proof
- No overclaiming detected in adversarial review

---

## Next Actions

1. Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` to create live PRs
2. Set `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR` to merge PRs

No more readiness loops required. Machinery is qualified.

---

## Git Status

Source files modified this sprint:
- `src/plugin_examples/family_config/models.py` — Added include_all_tfm_groups
- `src/plugin_examples/family_config/loader.py` — Read include_all_tfm_groups
- `src/plugin_examples/runner.py` — Pass include_all_tfm_groups
- `pipeline/schemas/family-config.schema.json` — Document include_all_tfm_groups
- `pipeline/configs/families/pdf.yml` — Enable include_all_tfm_groups
- `pipeline/configs/denominators/words.json` — Update api_catalog_source

Evidence files (reports/system-qualification/): NEW — tracked but not committed until sprint close
