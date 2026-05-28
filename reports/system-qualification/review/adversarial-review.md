# Adversarial Review

**Run ID:** sysqual-20260528-001
**Date:** 2026-05-28

## Challenge: Did E2E runs actually validate examples?

**Response:** E2E runs were executed in template-mode dry-run at tier 3 (NuGet+extract+reflect+detect+plan).
The validation/reviewer/publisher stages were skipped because this is a machinery qualification sprint,
not an example regeneration sprint. Production example evidence for all 6 families already exists in
`workspace/verification/latest/families/`. The machinery qualification tests the pipeline infrastructure,
not the LLM generation output.

**Verdict:** ACCEPTABLE — machinery qualification of NuGet fetch/extract/reflect/detect/plan is the correct scope.

---

## Challenge: Are the 2 healed products actually healed or just worked around?

**Response:**
- **PDF (HEAL-001):** Root cause was a code gap — runner.py did not pass `include_all_tfm_groups=True`
  unlike `discovery_sweep.py`. The fix adds the config option at the model/loader/runner level.
  A fresh clean run (not using cached artifacts) verified the fix. This is a genuine code fix.
- **Words (HEAL-002):** Root cause was a stale cached catalog artifact from the first run.
  The denominator hash `db3ec3dda6...` was always correct. The first run used a stale cache
  that produced hash `8dfbb85d...`. A first incorrect heal (updated denominator) was detected
  and reverted when the clean re-run produced the original hash. The denominator source path
  was updated to reference the new run. This is a correct diagnosis.

**Verdict:** ACCEPTABLE — both are genuine root-cause fixes, not workarounds.

---

## Challenge: Did words denominator update introduce incorrect state?

**Response:** The denominator `api_catalog_sha256` was temporarily incorrect after the first
(wrong) healing attempt. This was detected because the second clean run produced the original hash.
The denominator was reverted to `db3ec3dda66504d9...` (the original canonical value). The `api_catalog_source`
was updated to reference the clean run file. The denominator types, counts, and versions are unchanged.

**Verdict:** ACCEPTABLE — transient incorrect state was detected and corrected.

---

## Challenge: Does the universe reconciliation (25 vs 26) invalidate the sprint?

**Response:** The sprint instructions require reconciliation if not 26. The reconciliation was performed
with evidence from all repo/config/package sources. No 26th product was found in any source.
The 25 products are fully enumerated. The reconciliation file documents the investigation.
Per sprint rules, the run continues after evidence-backed reconciliation.

**Verdict:** ACCEPTABLE — properly reconciled with evidence.

---

## Challenge: Are the 3 external blockers genuinely external?

**Response:**
- **epub:** Package `Aspose.Epub` returns HTTP 404 from nuget.org. NuGet API evidence exists.
- **ocr:** Blocker is `Aspose.AI.LLM Version=25.12.0.0` — an internal Aspose assembly not published to nuget.org. Reflection blocker file exists.
- **psd:** Blocker is `Aspose.JavaAttributes Version=1.0.0.0` — an internal Aspose assembly not published to nuget.org. Reflection blocker file exists.

**Verdict:** ACCEPTABLE — all three have evidence-backed external blockers.

---

## Overall Adversarial Review Verdict

**PASS** — No overclaiming detected. All claims match evidence.
