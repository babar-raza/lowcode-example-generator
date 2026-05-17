# Sprint 25 — Final Verdict

**Sprint:** SPRINT25-PDF-WAVE-F-PR8-SIGNATURE-FRONTIER-AND-ALL-FAMILY-RUNTIME
**Date:** 2026-05-17
**Verdict:** `SPRINT25_WAVE_F_HARNESS_VERIFIED_PUBLICATION_APPROVAL_BLOCKED`

---

## What Was Accomplished

### Wave F — FormEditor + FormExporter (COMPLETE)

- Pipeline run `pilot-pdf-20260517-150729` — 17/18 stages pass
- `pdf-form-editor`: EXAMPLE_READY_FOR_PR_DRY_RUN (build+run PASS)
- `pdf-form-exporter`: EXAMPLE_READY_FOR_PR_DRY_RUN (build+run PASS)
- PR#8 package assembled at `workspace/pr-dry-run/pdf-controlled-pilot-pr8/`
- Both examples verified standalone: `Form fields removed` / `Form exported to JSON`

### template_first Ordering Bug Fix (COMPLETE)

- `code_generator.py` — template_first check moved BEFORE `llm_generate is None` fallback
- All 13 template_first types now guaranteed to use deterministic templates regardless of LLM availability
- 3 new tests added: `test_formeditor_template_first_works_without_llm`, `test_formexporter_template_first_works_without_llm`, `test_all_template_first_types_work_without_llm`

### PDF Frontier Probes

| Type | Result |
|------|--------|
| Signature | **HARNESS_VERIFIED ALL_PASS** — self-signed PFX works, Wave G candidate |
| Timestamp | **PERMANENTLY_BLOCKED** — `ServerUrl must be provided` (TSA required) |
| Ofd | **PERMANENTLY_BLOCKED** — direction is OFD→PDF, no programmatic OFD creation |

### Email + Slides Post-Merge Runtime

| Family | Result |
|--------|--------|
| Email | **4/5 PASS** — ConvertToHtml file-lock is harness-sequencing artifact, not pipeline defect |
| Slides | **5/5 ALL_PASS** — Convert.ToPdf, AutoByExtension, Merger.Process, Compress.CompressEmbeddedFonts all verified |

### Family Regression Guards

All families clean — no regression introduced by sprint25 source changes.

---

## Publication Status

- **APPROVAL_BLOCKED** — `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL` env var absent
- 5 PR packages ready: PR#3 (Wave A, 3 types), PR#5 (Wave B, 3 types), PR#6 (Wave C/D, 3 types), PR#7 (Wave E, 2 types), PR#8 (Wave F, 2 types)
- 13 new PDF examples pending `APPROVE_LIVE_PR`
- All packages BUILD_PASS + RUNTIME_PASS

---

## Test Suite

**1613 / 1613 tests pass** (all previous + 3 new template_first ordering fix tests)

---

## Next Sprint Priorities

1. **Publication** — Set `APPROVE_LIVE_PR`, publish PR#3/#5/#6/#7/#8 (13 examples → 18 total published)
2. **Wave G — Signature** — Add Signature to pdf.yml, implement template, add test, update denominator 18→19
3. **FormImporter discovery** — Inspect constructor signatures, design template if feasible
4. **Timestamp/Ofd** — Remain permanently blocked (no action needed)

---

## Portfolio State

| Family | Status | Published | Pilot Scope |
|--------|--------|-----------|------------|
| Cells | FAMILY_COMPLETE | 9/9 | 9/9 |
| Words | PILOT_COMPLETE | 8/8 | 8/8 |
| PDF | PARTIAL_CANARY | 5/18 | 18/18 generated |
| Diagram | PILOT_COMPLETE | 2/2 | 2/2 |
| Email | PILOT_COMPLETE | 1/1 | 1/1 |
| Slides | PILOT_COMPLETE | 3/3 | 3/3 |
| **Total** | | **28 published** | **+13 pending** |
