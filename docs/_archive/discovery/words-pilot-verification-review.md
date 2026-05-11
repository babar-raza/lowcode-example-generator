# Words Pilot Verification and Promotion Review

**Date:** 2026-05-01
**Family:** Aspose.Words LowCode
**Run:** `workspace/runs/pilot-words-20260501-144945`
**Overall Verdict:** `PR_DRY_RUN_READY`

---

## Executive Summary

All 4 approved Words controlled pilot scenarios passed build, runtime, and semantic output validation. PR dry-run packaging is approved. Live publishing remains blocked. Broader Words generation (beyond the 4 approved types) remains blocked.

Two additional fixes were required during this verification sprint:
- `preferred_methods_per_type` config added to ensure each type demonstrates the correct primary method
- Factory method ordering fix in planner ensures operation methods appear before `Create` in `target_methods`

---

## Scenario Results

| ID | Type | Method | Build | Runtime | Semantic | Verdict |
|----|------|--------|-------|---------|----------|---------|
| WORDS-001 | Converter | Convert | PASS | PASS | PASS (PDF: %PDF, 58073 bytes) | READY |
| WORDS-002 | Watermarker | SetText | PASS | PASS | PASS (DOCX: CONFIDENTIAL confirmed) | READY |
| WORDS-003 | Splitter | ExtractPages | PASS | PASS | PASS (page 1 extracted, page 2 absent) | READY |
| WORDS-004 | Replacer | Replace | PASS | PASS | PASS (World present, {{name}} absent) | READY |

---

## Evidence Files Verified

| File | Status |
|------|--------|
| words-source-of-truth-proof.json | EXISTS CURRENT |
| words-catalog-review.json | EXISTS CURRENT |
| words-type-role-classification.json | EXISTS CURRENT |
| words-options-usage-review.json | EXISTS CURRENT |
| words-generation-candidate-rank.json | EXISTS CURRENT |
| words-controlled-pilot-allowlist.json | CREATED THIS SPRINT |
| words-fixture-strategy.json | CREATED THIS SPRINT |
| generated-words-fixtures.json | CREATED THIS SPRINT |
| words-semantic-validation-results.json | CREATED THIS SPRINT |
| words-example-completeness-audit.json | CREATED THIS SPRINT |
| example-gate-results.json | CURRENT |
| aggregate-gate-results.json | CURRENT |
| pr-candidate-manifest.json | CURRENT (4 candidates) |
| gate-results.json | CURRENT (PR_DRY_RUN_READY) |

---

## Example Completeness Audit

All 4 examples contain: `Program.cs`, `.csproj`, `README.md`, `example.manifest.json`, `expected-output.json`.

No forbidden patterns found in any example:
- No `Console.ReadKey` / `Console.ReadLine`
- No `TODO` / `NotImplementedException`
- No absolute local paths
- No `MailMerger`, `ReportBuilder`, `Comparer`, `Merger`
- No `Splitter.Split` or `SplitOptions`
- No `MailMergeDataSource` standalone usage

All 4 use `programmatic_input` strategy — no pre-existing fixture files required.

---

## Semantic Output Validation

### WORDS-001 Converter
- Output: `output.pdf`, 58073 bytes
- PDF header: `%PDF` ✓

### WORDS-002 Watermarker
- Output: `output.docx`, 22032 bytes
- Valid DOCX ZIP ✓
- Watermark confirmed in `word/header1.xml`: `v:textpath string="CONFIDENTIAL"` ✓

### WORDS-003 Splitter.ExtractPages
- Output: `output.docx`, 18062 bytes
- Valid DOCX ZIP ✓
- Page 1 content present ✓
- Page 2 content absent (correctly excluded) ✓

### WORDS-004 Replacer.Replace
- Output: `output.docx`, 18064 bytes
- Valid DOCX ZIP ✓
- `World` replacement text present in `word/document.xml` ✓
- `{{name}}` placeholder absent ✓
- `replaceCount > 0` validated in code ✓

---

## Allowlist Enforcement

- 4 scenarios planned
- **21 scenarios blocked** as `blocked_pilot_not_in_scope`
- Blocked types include: Comparer, Merger, MailMerger, ReportBuilder, Processor, Signer, and all non-operation types
- Enforcement: `planner.py` allowlist check, `words.yml` `allowed_types` config

---

## Fixes Applied This Sprint

### Fix 1: `preferred_methods_per_type` config
Root cause: `Create` (factory method) appeared first in `target_methods`, causing LLM to demonstrate the factory instead of the intended operation.

Changes:
- `models.py`: Added `preferred_methods_per_type: dict[str, str]`
- `loader.py`: Parses `preferred_methods_per_type` from YAML
- `schema.json`: Added `preferred_methods_per_type` property
- `words.yml`: `Watermarker: SetText`, `Splitter: ExtractPages`, `Replacer: Replace`, `Converter: Convert`
- `planner.py`: `preferred_method` param moves specified method to position 0 in `target_methods`
- `runner.py`: Passes `preferred_methods_per_type` to `plan_scenarios()`

### Fix 2: Factory method ordering
Operation methods now precede `Create`/`CreateXxx` methods in `target_methods`, ensuring the LLM always sees the primary operation first even without an explicit `preferred_method` override.

---

## Gate Summary

| Gate | Result |
|------|--------|
| Scenario Planning | PASSED (4 ready, 21 blocked) |
| Example Generation | PASSED (4/4) |
| Build Validation | PASSED (4/4) |
| Runtime Validation | PASSED (4/4) |
| Example Reviewer | PASSED |

---

## Taskcard State

### Closed This Sprint
- `followup-words-converter-fix` — CLOSED
- `followup-words-splitter-fix` — CLOSED
- `followup-words-output-extension-prompt-guard` — CLOSED

### Still Open
- `followup-words-split-criteria-enumeration` — unblocks WORDS-005
- `followup-words-pair-fixture-strategy` — unblocks WORDS-006, WORDS-007
- `followup-words-mail-merger-fixture-documentation` — unblocks WORDS-008
- `followup-pdf-reflection-dedup` — unblocks PDF family
- `followup-family-readiness-ranker-trust` — observability
- `followup-fixture-token-ci` — CI integration

### New Taskcard
- `followup-words-docx-semantic-validation` (NEW) — Automate DOCX text extraction for pipeline validation

---

## Publishing Policy

| Action | Status |
|--------|--------|
| Live publish | BLOCKED (dry-run only) |
| PR dry-run packaging | ALLOWED |
| Words broader generation | BLOCKED (allowlist in words.yml restricts to 4 types) |
| Words controlled pilot (4 types) | ALLOWED |
| Cells generation | ALLOWED |
| PDF generation | BLOCKED (reflection fails) |

---

## Test Suite

528 tests passing, 0 failing.

---

## Recommended Next Sprint

**Words PR Packaging Sprint** — Package the 4 approved examples (`words-converter`, `words-watermarker`, `words-splitter`, `words-replacer`) into a PR candidate against `aspose-plugins-examples-dotnet`. Scope: dry-run PR creation, no merge, validate PR diff structure.

After PR packaging: evaluate expanding pilot to WORDS-005 (pending `followup-words-split-criteria-enumeration`).
