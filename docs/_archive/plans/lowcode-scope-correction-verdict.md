# LowCode Example Generator: Scope Correction Verdict

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** VERDICT_FINALIZED

---

## What Was Wrong in the Previous Roadmap

The previous roadmap treated Cells, Words, and PDF as the **full project scope**, deferring all-family discovery to a late phase ("Phase 6") after PDF publication work was complete. This is incorrect for the following reasons:

1. **The pipeline is config-driven.** `discovery_sweep.py` (lines 54-57) scans only `pipeline/configs/families/*.yml`. No YAML config = no discovery. The ~20 Aspose .NET families with no YAML config have never been attempted at all.

2. **The project goal is all Aspose .NET families with LowCode namespaces**, not just the three pilot families. Cells, Words, and PDF are pilot families only.

3. **Placing PDF PR work before establishing the full family universe** means the roadmap was planning inside an unknown denominator. The project cannot claim roadmap completeness without knowing which other families expose LowCode namespaces.

4. **"Others TBD" is not an acceptable final state.** Every candidate family must be named, classified, and either included in the generation pipeline or documented as OUT_OF_SCOPE with evidence.

---

## Which Assumptions Are Discarded

| Assumption | Why Discarded |
|-----------|---------------|
| "Cells, Words, PDF = the project" | They are the first three pilot families only |
| "Others TBD is acceptable as final state" | Every candidate family must be named and classified |
| "All-family discovery can wait" | Discovery is a hard gate before claiming roadmap completeness |
| "Existing pipeline/configs/families/ YAMLs define all families" | Only 5 families configured; ~20+ are not |
| "release-status covers all active families" | Defaults exclude PDF; covers only cells and words |
| "Monthly workflow covers all families" | Defaults to cells only |

---

## Which Parts Remain Useful

- All Cells/Words/PDF evidence, sprint execution records, and artifact paths remain valid.
- PDF PR#3/PR#4 sprint cards remain valid (moved to later phases in corrected order).
- No-silent-drop governance audit findings remain valid.
- Root-cause register findings remain valid.
- Contradiction register findings remain valid.

---

## How the Corrected Plan Changes Execution Order

**Previous (wrong) order:**
1. Complete PDF PR#3/PR#4
2. Expand Words
3. Discover other families (Phase 6)

**Corrected order:**
1. R0: Plan amendment and evidence normalization (this sprint)
2. R1: Product candidate inventory and YAML creation (in parallel with R7, R8)
3. R2: Email/Slides blocker investigation (in parallel with R1, R8)
4. R3: All-family discovery after YAML coverage
5. R4-R6: Source-of-truth, classification, denominators for new families
6. R6.5: Dropped planned example verification failure audit
7. R7: Existing family reconciliation (Cells, Words, PDF)
8. R8: PDF PR-ready publication unblocker (parallel with R1-R7)
9. R9+: Words/PDF/new family expansion waves

---

## Why All-Family Discovery Must Be an Early Gate

The pipeline cannot discover a family it has no YAML config for. Creating YAMLs for ~20 unknown families is a sprint action (R1), not a late-phase nicety. Without it:

- The project denominator is permanently incomplete.
- "100% coverage" claims are meaningless.
- Any roadmap completion claim is false because an unknown number of Aspose .NET families may expose LowCode namespaces.

---

## Verified Current State (from local files)

| Family | Status | Evidence |
|--------|--------|---------|
| Cells | 9/9 POST_MERGE_VERIFIED | completion-queue.json, denominators/cells.json, test_denominator_model.py |
| Words | 4/4 POST_MERGE_VERIFIED (pilot) | completion-queue.json, denominators/words.json |
| PDF | 2/4 pilot published; PR#3 ready; Optimizer needs 2nd PASS | pdf-pr1-merge-result.json, pdf-pr3-package-validation.json |
| Email | Config in disabled/, enabled=true, reflection unproven | disabled/email.yml |
| Slides | Config in disabled/, DLL name mismatch | disabled/slides.yml |
| ~20 others | No YAML config; discovery never attempted | pipeline/configs/families/ (only 3 active configs) |

---

## Verdict

**SCOPE_CORRECTION_REQUIRED_AND_APPLIED**

The roadmap has been amended. All-family discovery (R1-R3) is now an early gate. PDF PR work (R8) runs in parallel with R1/R2/R7 but is not the roadmap completion gate. The project is complete only when every Aspose .NET product family has been discovered, classified, denominated, generated, published, or explicitly governed with evidence.
