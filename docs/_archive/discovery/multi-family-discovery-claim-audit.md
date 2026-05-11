# Multi-Family API Catalog Expansion Sprint — Claim Audit

**Audited:** 2026-04-30
**Auditor:** Independent verification pass
**Branch:** main (HEAD: b501f67)
**Commands run:** `git status`, `find workspace`, `PYTHONPATH=src pytest tests/unit`, `discover-lowcode --families cells words pdf --promote-latest`

---

## Claim Verdicts

| # | Claim | Verdict | Evidence | Risk |
|---|-------|---------|----------|------|
| 1 | Discovery expanded to Cells + Words + PDF | VERIFIED | `all-family-lowcode-discovery.json`: total_families=3 | low |
| 2 | No examples generated outside Cells | MISLEADING | `workspace/runs/multi-family-words/` contains 12 generated Words examples (dated 2026-04-29); `workspace/runs/multi-family-email/` contains 2 generated Email examples. These predate the discover-lowcode sprint run; the discover-lowcode command itself cannot generate examples. The final report omitted disclosure of these pre-existing generated artifacts. | HIGH |
| 3 | No LLM calls occurred | PARTIALLY TRUE | discover-lowcode command has no LLM import path. multi-family-words pilot run showed `llm_available: false`. However workspace/verification/latest/llm-preflight.json from prior Cells run shows `gpt_oss` was live. No LLM was called during the April 30 discovery commands. | medium |
| 4 | No live publishing occurred | VERIFIED | No GITHUB_TOKEN used. publisher.py not called from discovery_sweep.py. All run reports show `dry_run: true`. | low |
| 5 | Cells eligible: Aspose.Cells.LowCode | VERIFIED | cells-source-of-truth-proof.json: eligibility_status=eligible, 22 types, 33 methods | low |
| 6 | Words eligible: Aspose.Words.LowCode | VERIFIED | words-source-of-truth-proof.json: eligibility_status=eligible, 25 types, 230 methods, 9 workflow_root candidates confirmed by type_classifier | low |
| 7 | PDF blocked: MetadataLoadContext duplicate System.Text.Json | VERIFIED | all-family-lowcode-discovery.json error field contains full FileLoadException stack trace. Reproduced in three separate runs (2026-04-30 15:25, 15:57, current). Root cause confirmed: System.Text.Json.dll extracted twice (via System.Net.Http.Json + direct dep) into resolved-libs/, second load fails with FileLoadException. | low |
| 8 | all-family-lowcode-discovery.json written | VERIFIED | Present in workspace/verification/latest/; stable across 3 runs | low |
| 9 | family-generation-readiness-rank.json written | VERIFIED | Present in workspace/verification/latest/ | low |
| 10 | cells-source-of-truth-proof.json written | VERIFIED | Present in workspace/verification/latest/ | low |
| 11 | words-source-of-truth-proof.json written | VERIFIED | Present in workspace/verification/latest/ | low |
| 12 | PDF proof not written because reflection failed before catalog stage | VERIFIED | all-family-lowcode-discovery.json: catalog_path=null, eligibility_status=blocked. By design, write_source_of_truth_proof is only called after catalog is built. | low |
| 13 | All 457 unit tests pass | VERIFIED | `pytest tests/unit -q --timeout=60`: 457 passed in 12.85s | low |
| 14 | Outstanding taskcards: followup-pdf-reflection-dedup + followup-words-generation-enable | FALSE — INCOMPLETE | At least 4 additional taskcards must be opened. See Taskcards section. | HIGH |

---

## Bugs Found During Audit

### BUG-1: __main__.py logger NameError (FIXED in this audit)

**File:** `src/plugin_examples/__main__.py:179`
**Symptom:** `discover-lowcode` command exits with `NameError: name 'logger' is not defined` after writing ranking file. Exit code 1 despite files being written correctly.
**Root cause:** `logger.info(...)` called in `main()` but no `logger = logging.getLogger(__name__)` in scope.
**Fix applied:** Replaced with `logging.getLogger(__name__).info(...)`.
**Status:** FIXED.

### BUG-2: discovery_only families are NOT blocked by runner.py

**File:** `src/plugin_examples/runner.py:279`
**Symptom:** `_stage_load_config` only checks `config.status == "experimental"`. A `python -m plugin_examples run --family words` proceeds without any guard.
**Root cause:** The `discovery_only` status was added to schema and enforced in discovery_sweep.py but NOT in runner.py.
**Fix required:** Add `if ctx.config.status == "discovery_only": raise RuntimeError(...)` guard before generation pipeline starts.
**Taskcard:** `followup-discovery-only-safety` (OPENED).

### BUG-3: disabled/ folder still contains experimental words.yml and pdf.yml

**Files:** `pipeline/configs/families/disabled/words.yml`, `pipeline/configs/families/disabled/pdf.yml`
**Symptom:** The sprint created NEW active configs at `pipeline/configs/families/words.yml` and `pdf.yml` (status: discovery_only) but did NOT remove the old disabled/ versions (status: experimental). Both coexist.
**Risk:** The disabled/ versions with `experimental` status could be used accidentally by `run` command if the active configs are removed. Also misleads operators reading the filesystem.
**Fix required:** Delete `pipeline/configs/families/disabled/words.yml` and `pipeline/configs/families/disabled/pdf.yml` once active configs are confirmed correct.
**Taskcard:** `followup-disabled-configs-cleanup` (OPENED).

---

## Words Eligibility — Independent Verification

Ran `classify_catalog` on `workspace/runs/discovery-words-*/catalog/words/api-catalog.json`:

| Role | Types |
|------|-------|
| `workflow_root` | Comparer, Converter, MailMergeDataSource, MailMerger, Merger, Replacer, ReportBuilder, Splitter, Watermarker (9 total) |
| `options` | MailMergeOptions, ReportBuilderOptions, SplitOptions (3 total) |
| `settings_model` | ComparerContext, MergerContext, ReportBuilderContext, SignerContext, SplitterContext, WatermarkerContext (6 total) |
| `abstract_base` | ProcessorContext (1) |
| `operation_facade` | Processor (1) |
| `utility` | MailMergerContext, ReplacerContext (2) |
| `unknown` | ConverterContext (1) |
| `enum` | MergeFormatMode, SplitCriteria (2) |

- workflow_root count: **9** (matches ranking JSON)
- provider_callback count: **0** (matches ranking JSON)
- options count: **3** (matches ranking JSON)
- `MailMergeDataSource` classified as workflow_root (confidence 0.70) — this type is a data source interface, not a standalone workflow root. It has 4 methods with static access. This is a potential misclassification that warrants review before generation.
- Fixture sources ARE configured in words.yml — matches `fixture_access_status: configured`.

**Conclusion:** Words generation readiness data is evidence-backed. The "low risk" classification is correct given the scoring rules (wrc >= 3 + fixture sources). However, `MailMergeDataSource` classification and options-aware rules review are required before generation.

---

## PDF Blocker — Independent Verification

Error reproduced three times identically:
```
System.IO.FileLoadException: The assembly 'System.Text.Json, Version=8.0.0.0' has already been loaded into this MetadataLoadContext.
```

**Root cause:** `resolve_dependencies()` fetches two packages both containing `System.Text.Json.dll`:
1. `System.Text.Json` (direct dep, older version)
2. `System.Net.Http.Json` (which also bundles/depends on System.Text.Json)

Both extract to `resolved-libs/System.Text.Json.dll`. Second load of same filename into MetadataLoadContext's PathAssemblyResolver throws.

**Fix path:** Deduplicate dependency DLLs by assembly identity (assembly name + public key token) before passing to DllReflector. Last-write-wins or highest-version-wins strategy.

---

## Family Config Safety Gap

`runner.py` `_stage_load_config` only blocks `experimental` families:

```python
if ctx.config.status == "experimental" and not getattr(ctx, "_allow_experimental", False):
    raise RuntimeError(...)
```

**No equivalent guard for `discovery_only`.** A user can run:
```
python -m plugin_examples run --family words
```
and the full pipeline (generation, validation, publish) will proceed. This violates the sprint invariant "Words generation is NOT allowed."

---

## Pre-existing Generated Words Examples

`workspace/runs/multi-family-words/generated/words/` contains 12 generated template-mode Words examples:
- words-comparer, words-converter, words-mail-merge-data-source, words-mail-merger, words-mail-merger-context, words-merger, words-processor, words-replacer, words-replacer-context, words-report-builder, words-splitter, words-watermarker

**When generated:** 2026-04-29 via `scripts/pilot_run.py --family words --template-mode --run-id multi-family-words --no-skip-run`

**Verdict:** COMPLETE, DATA-FLOW PROOF ONLY (template_mode, llm_available=false)

**Build result:** 10/12 runtime passed. 2 failures (unknown pattern).

These were NOT generated by the Multi-Family API Catalog Expansion Sprint. The `discover-lowcode` command has no generation pathway. The final report's claim "No examples generated outside Cells" is technically scoped to the sprint's discover-lowcode command, but the workspace contains Words generation artifacts that were never disclosed.

**Email examples also exist:** `workspace/runs/multi-family-email/generated/email/` — 2 examples, both built and passed, dated 2026-04-29.

---

## Opened/Reopened Taskcards

### TC-1: followup-pdf-reflection-dedup (REOPENED)
**Title:** Deduplicate dependency assemblies before DllReflector
**Reason:** PDF blocked by duplicate System.Text.Json in MetadataLoadContext.
**Acceptance:**
- Dependency DLLs deduplicated by assembly identity (name + public key token) before passing to DllReflector.
- PDF discovery runs without FileLoadException.
- pdf-source-of-truth-proof.json written when reflection succeeds.
- Unit test covers duplicate dependency identity deduplication.

### TC-2: followup-words-generation-enable (KEEP CLOSED — premature)
**Title:** Enable Words in generation pipeline
**Status:** Blocked on TC-3, TC-4, TC-5 first.

### TC-3: followup-discovery-only-safety (NEW)
**Title:** Block discovery_only families from generation pipeline
**Reason:** runner.py only guards `experimental` status. `discovery_only` families can be run through full generation pipeline.
**Acceptance:**
- runner.py `_stage_load_config` raises RuntimeError for `discovery_only` status.
- Test proves `run --family words` raises discovery_only guard error.
- Test proves `discover-lowcode --families words` still succeeds.

### TC-4: followup-words-options-aware-review (NEW)
**Title:** Verify Aspose.Words.LowCode options-aware rules before generation
**Reason:** Words has MailMergeOptions, ReportBuilderOptions, SplitOptions — each needs validation that options objects are properly constructed before use, mirroring the Cells NullRef fix.
**Acceptance:**
- Each options type's required fields identified from catalog.
- Packet builder constraints updated for Words (InputFile, OutputFile, options must not be null).
- Code validator rules extended to Words options.
- Runtime classifier covers Words-specific null options patterns.

### TC-5: followup-words-role-classification-review (NEW)
**Title:** Review MailMergeDataSource workflow_root classification
**Reason:** `MailMergeDataSource` is classified `workflow_root` at confidence 0.70 but it is a data provider interface (4 methods), not a primary workflow entry point. May generate invalid standalone examples.
**Acceptance:**
- Type role rules reviewed for data source/provider types.
- MailMergeDataSource either reclassified or generation guarded against standalone scenario planning.
- Test covers data source type classification.

### TC-6: followup-disabled-configs-cleanup (NEW)
**Title:** Remove stale disabled/ config files for words and pdf
**Reason:** `pipeline/configs/families/disabled/words.yml` and `disabled/pdf.yml` with `status: experimental` still exist alongside new active configs with `status: discovery_only`. Dual presence is misleading and unsafe.
**Acceptance:**
- disabled/words.yml deleted.
- disabled/pdf.yml deleted.
- email.yml and slides.yml remain in disabled/.

### TC-7: followup-family-readiness-ranker-trust (NEW)
**Title:** Add confidence and evidence_source fields to generation readiness ranking
**Reason:** family-generation-readiness-rank.json does not show confidence scores, evidence source paths, or catalog_path. "Low risk" cannot be fully traced from the ranking JSON alone.
**Acceptance:**
- Each ranking entry includes: `catalog_path`, `role_classification_source`, `confidence_notes`.
- Words entry documents MailMergeDataSource confidence concern.
- PDF entry includes blocked reason verbatim.

### TC-8: followup-fixture-token-ci (CARRY FORWARD from previous sprint)
**Title:** Document and enforce GitHub token handling for fixture discovery in CI
**Reason:** GitHub API 403 handling improved but CI readiness not proven.
**Acceptance (unchanged from previous sprint):**
- README and CI docs describe GITHUB_TOKEN.
- Without token, warning is explicit.
- With token, Authorization header is used.
- Fixture unavailable reasons are preserved.

---

## Closed Taskcards (Verified)

| ID | Title | Reason for Closure |
|----|-------|--------------------|
| followup-publisher-evidence-ordering | Publisher stage pre-evaluates gates | publishing-report.json shows evidence_verified: true |
| followup-discovery-sweep-deps | Discovery sweep resolves deps | Cells reflects with 8 deps, Words with 17 deps |
| followup-github-api-403 | Registry degrades gracefully with explicit reason | `github_api_403_rate_limited` reason code confirmed |

---

## Generation Policy

Based on this audit:

| Family | Generation Allowed | Reason |
|--------|-------------------|--------|
| **Cells** | YES (with review) | Active, eligible, options-aware rules in place, 9/9 PR_DRY_RUN_READY |
| **Words** | NO | Blocked by: TC-3 (safety guard), TC-4 (options-aware review), TC-5 (role review) |
| **PDF** | NO | Blocked by: TC-1 (reflection dedup), reflection still fails |
| **Email** | NO | Not in active config; disabled/ only |
| **Slides** | NO | Reflection blocked (DLL name mismatch) |
| **All-family** | NO | |
