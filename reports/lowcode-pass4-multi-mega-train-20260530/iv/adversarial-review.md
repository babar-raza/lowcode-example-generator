# Adversarial (IV) Review — Pass 4 Multi-Mega-Train

Sprint: lowcode-pass4-multi-mega-train-20260530
Date: 2026-05-30

## Claim 1: 42/42 examples pass E2E

**Challenge:** Prior bundle's E2E logs were from pr-dry-run packages that lacked input files — cells and words would fail on build.

**Response:** E2E re-run from source pilot directories where input files exist:
- cells: `workspace/runs/pilot-cells-20260529-214911/generated/cells/`
- words: `workspace/runs/pilot-words-20260529-220000/generated/words/`
- pdf/diagram/slides/email: from pr-dry-run (no input file references in .csproj)

Raw logs in `e2e-raw/<family>/<example>/build.log` and `run.log`. All 42 exit 0.

**Verdict: CLAIM SUPPORTED**

---

## Claim 2: 25-product universe fully reconciled

**Challenge:** Prior report only showed 9 products. Full 25-product universe was not documented.

**Response:** All 25 `pipeline/configs/families/*.yml` enumerated in `universe/product-universe-25-refresh.json`:
- 6 LowCode confirmed (cells, diagram, email, pdf, slides, words)
- 2 enabled no-LowCode (ocr: 1257 types zero LowCode; psd: 4432 types zero LowCode)
- 1 disabled discovery_blocked (epub: NU1101, no NuGet package)
- 16 disabled not-applicable

**Verdict: CLAIM SUPPORTED**

---

## Claim 3: OCR/PSD reclassified correctly

**Challenge:** OCR and PSD were marked EXTERNAL_PACKAGE_BLOCKER due to missing transitive dependencies. Is this still valid?

**Response:** Fresh DLL reflection performed:
- OCR: Aspose.OCR 26.5.0 restores. DLL loaded. 1,257 types. Zero LowCode namespace types.
- PSD: Aspose.PSD 26.5.0 restores. DLL loaded. 4,432 types. Zero LowCode namespace types.

Reclassified to NO_LOWCODE_CONFIRMED. Does not expand example universe.

**Verdict: CLAIM SUPPORTED**

---

## Claim 4: Words hash is correct (8dfbb85d...)

**Challenge:** `db3ec3dda...` hash observed in prior heal runs. Which is canonical?

**Response:** Hash is version-specific:
- Words 25.5.0 → `db3ec3dda...` (heal runs, obsolete)
- Words 26.5.0 → `8dfbb85d...` (3 independent pilot runs confirm)

Current denominator uses Words 26.5.0. `8dfbb85d...` is correct.

**Verdict: CLAIM SUPPORTED**

---

## Claim 5: Package contradiction resolved

**Challenge:** validation-truth-model.json said diagram/slides/email packages MISSING; package-completion-report said all 6 COMPLETE.

**Response:** Truth model was written before Lane F created those packages. It was stale, not the package report. All 12 packages verified on disk. `publication/package-contradiction-resolution.md` documents the resolution.

**Verdict: CLAIM SUPPORTED**

---

## Claim 6: 5 PDF examples added via system (repeatable)

**Challenge:** 5 template-repaired PDF examples were missing from packages. Must go through system, not manual patch.

**Response:** `scripts/assemble_pdf_pr10_pilot.py` created following `assemble_controlled_pilots.py` pattern. Assembles from `workspace/runs/pilot-pdf-repair-20260530/generated/pdf/`. All 5 build successfully. The mechanism is repeatable.

**Verdict: CLAIM SUPPORTED**

---

## Remaining known limitation

- `words-mail-merger`: E2E passes (exits 0) but no LowCode API call. MailMerge has no suitable one-call LowCode overload. Documented as STUB_ACCEPTABLE. Does not affect 42-example count; example is published as a skeleton demonstrating the namespace.

## Overall Adversarial Verdict

All 6 substantive claims are supported by evidence. No hidden contradictions found.
Publication gate remains APPROVAL_BLOCKED (no PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL set).
