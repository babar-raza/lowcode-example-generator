# PDF Role Classification + Options-Aware Review Sprint — Gate 0 Preflight Review

**Date:** 2026-05-04
**Sprint:** PDF Role Classification + Options-Aware Review Sprint
**Gate:** Gate 0 — Mandatory Referenced-File Inspection
**Verdict:** `PDF_ROLE_OPTIONS_SPRINT_GATE_0_PASS`

---

## Purpose

Before executing the PDF Role Classification + Options-Aware Review Sprint, every referenced artifact from prior sprints must be inspected and classified as VERIFIED / STALE / CONTRADICTORY / MISSING / NEEDS_FIX. Any items requiring correction must be resolved before the sprint begins.

---

## Summary

| Classification | Count |
|---|---|
| VERIFIED | 20 |
| VERIFIED_MINOR_STALE (expected drift) | 1 |
| STALE_EXPECTED (historical artifacts) | 5 |
| CONTRADICTORY | 0 |
| MISSING | 0 |
| NEEDS_FIX | 0 |
| Already fixed (prior session) | 1 |

**Gate 0 Result: PASS** — No blocking issues found.

---

## File Inspection Results

### 1. `workspace/verification/latest/family-generation-readiness-rank.json` — VERIFIED

- 3 families: cells=ready, words=false, pdf=false
- PDF `generation_blocked_by`: `[family_status_is_discovery_only, needs_type_role_rules]`
- PDF `workflow_root_candidate_count=0` (auto-classifier uses static-method heuristic; PDF uses instance methods)
- PDF `options_type_count=41`, `eligibility_status=eligible`

### 2. `workspace/verification/latest/pdf-source-of-truth-proof.json` — VERIFIED

- Aspose.PDF 26.4.0, netstandard2.0, 101 types, 71 methods, eligibility=eligible
- api_catalog_path: `discovery-pdf-20260504-142323`
- Reflection succeeded after assembly deduplication (excluded_count=2)

### 3. `workspace/verification/latest/unified-state-reconciliation-review.json` — VERIFIED_MINOR_STALE

- Finding RECONCILE-06 mentions "41 total, 31 closed" — stale (matrix updated to 42/32/10 after prior session fix)
- Not a blocker — snapshot was accurate at write time

### 4. `src/plugin_examples/dependencies/assembly_identity.py` — VERIFIED

- Full PE/ECMA-335 Assembly table parser with `deduplicate_assemblies()` function
- `AssemblyIdentity` and `DeduplicationResult` dataclasses
- Falls back to filename stem on non-PE files

### 5. `src/plugin_examples/discovery_sweep.py` — VERIFIED

- Dedup wired before `build_catalog()` (lines 197-226)
- `compute_generation_readiness()` emits `generation_ready`, `generation_blocked_by`, `discovery_status`, `reflection_status`, `evidence_source`
- GAP-NEW-01 fix: single-family runs merge into existing `family-generation-readiness-rank.json`

### 6. `tools/DllReflector/Program.cs` — VERIFIED

- Lines 70-76: `HashSet<string>` dedup by `GetFileNameWithoutExtension` before `PathAssemblyResolver`
- NuGet deps take precedence over `TRUSTED_PLATFORM_ASSEMBLIES`
- Prevents `FileLoadException: System.Text.Json Version=8.0.0.0` for PDF

### 7. `tests/unit/test_pdf_assembly_dedup.py` — VERIFIED

- 11 tests across 4 test classes; all pass in 759-test suite

### 8. `workspace/verification/latest/pdf-dependency-dedup-report.json` — VERIFIED

- `excluded_count=2` (System.Memory, System.Buffers — same_file=true)
- `kept_count=19`, `dedup_by=assembly_simple_name`

### 9. `workspace/verification/latest/open-taskcard-closure-matrix.json` — VERIFIED

- 42 total / 32 closed / 10 open
- `followup-aspose-net-link-standardization` present as `CLOSED_VERIFIED` (added in prior referenced-file gate)
- 4 PDF taskcards OPEN: role-classification, options-aware, fixture-strategy, repo-target-mapping
- **Prior session fix applied**: was missing `followup-aspose-net-link-standardization` entry

### 10. `workspace/verification/latest/all-family-lowcode-discovery.json` — VERIFIED

- Contains cells+words from last discover-lowcode run (by design)
- PDF absent — `pdf-source-of-truth-proof.json` is the canonical PDF artifact
- Cells: 22 types, 33 methods; Words: 25 types, 230 methods

### 11. `src/plugin_examples/publisher/repo_access_resolver.py` — VERIFIED

- Bearer auth confirmed at line 42: `{"Authorization": f"Bearer {token}"}`
- A2 Sprint fix verified

### 12. `src/plugin_examples/publisher/release_status.py` — VERIFIED

- `errors='replace'` at line 39 in `matrix_path.read_text(encoding='utf-8', errors='replace')`
- A2 Sprint fix verified

### 13. `pipeline/configs/families/pdf.yml` — VERIFIED

- `status: discovery_only` — correct
- `published_plugin_examples_repo`: `aspose/aspose-plugins-examples-dotnet` (placeholder, correct for discovery_only)
- `template_hints` present with single-input and merger-input creation lines
- LLM `provider_order: [llm_professionalize, ollama]` — no gpt_oss, no openai (correct)

### 14. `docs/ci/environment-variables.md` — VERIFIED

- Documents all required environment variables
- States approval tokens must NOT be stored as CI secrets
- A2 Sprint creation confirmed

### 15. `workspace/verification/latest/stream-a-closure-verification.json` — STALE_EXPECTED

- Historical snapshot (38/30/8 taskcards at write time vs 42/32/10 now)
- `gate_0_result=PASS`, `verdict=STREAM_A_CLOSURE_VERIFIED_GATE_0_PASS` — still valid as history
- PR merge SHAs still correct

### 16. `c:/Users/prora/.claude/plans/linked-nibbling-hamster.md` — STALE_EXPECTED

- References matrix 42/31/11 (written before A2 closed fixture-token-ci) and test count 675 (pre-dedup sprint)
- Expected drift — plan file accumulates history; new section to be appended in Phase 5

### 17. `src/plugin_examples/publisher/aspose_links.py` — VERIFIED

- `build_aspose_net_links(family_slug)` returns 8 canonical aspose.net URLs
- Pattern: `https://{subdomain}.aspose.net/{family_slug}` (no /net suffix)
- 4 audit functions for finding forbidden/wrong links

### 18. `workspace/verification/latest/cells-merge-result.json` — STALE_EXPECTED

- Records README PR #2 merge (not examples PR #1) — expected; file is overwritten per merge
- Examples PR #1 SHA preserved in `stream-a-closure-verification.json`

### 19. `workspace/verification/latest/cells-source-of-truth-proof.json` — VERIFIED

- Aspose.Cells 26.4.0, 22 types, 33 methods, eligibility=eligible
- Fresh from Phase 1 discovery run

### 20. `workspace/verification/latest/words-source-of-truth-proof.json` — VERIFIED

- Aspose.Words 26.4.0, 25 types, 230 methods, eligibility=eligible
- Fresh from Phase 1 discovery run

### 21. `src/plugin_examples/__main__.py` — VERIFIED

- All required CLI commands present including `discover-lowcode`, `sync-taskcard-docs`, `release-status`, `render-root-readme`, `publish-pr`, `merge-pr`
- Audit JSON serialization fixed (A2 hardening)

### 22. `workspace/verification/latest/unified-verification-result.json` — VERIFIED

- 8 steps all PASS, 759 tests confirmed
- `step_4_sync_taskcard_docs` shows 41 total (stale, written before matrix fix) — harmless

### 23. `workspace/verification/latest/pdf-lowcode-catalog-inventory.json` — VERIFIED

- 101 types from Aspose.PDF 26.4.0 fully inventoried
- 25 WORKFLOW_ROOT candidates (instance-method IPlugin pattern)
- 51 OPTIONS types, 4 ENUMs, 5 interfaces, 6 RESULT, 3 DATA_SOURCE, 2 SAVE_TARGET, 4 BUILDER

### 24. `workspace/verification/latest/pdf-role-classification-plan.json` — VERIFIED

- 8-role taxonomy defined with criteria for each role
- Classification rules for pipeline: WRC identification, paired options, data sources, enums
- Acceptance criteria documented; does NOT enable generation

### 25. `workspace/verification/latest/pdf-controlled-pilot-plan.json` — VERIFIED

- 4 pilot types: Merger, Splitter, Optimizer, TextExtractor
- All use `programmatic_input` fixture strategy
- template_hints already in pdf.yml
- 4 prerequisite taskcards must all close before any generation

### 26. `workspace/verification/latest/pdf-family-repo-target-mapping-plan.json` — VERIFIED

- Proposed: `aspose-pdf-net / Aspose.PDF.LowCode-for-.NET-Examples`
- Current placeholder correct for discovery_only
- Repo provisioning steps documented

### 27. `workspace/verification/latest/unified-next-sprint-roadmap.json` — VERIFIED

- 7-sprint roadmap with correct priorities
- Priority 1 is current sprint (PDF Role Classification + Options-Aware Review)
- Immutable constraints preserved

---

## Pre-Sprint State

| Item | Value |
|---|---|
| Unit tests | 759 passing |
| Taskcard matrix | 42 total / 32 closed / 10 open |
| PDF status | discovery_only |
| PDF types | 101 |
| PDF methods | 71 |
| PDF generation_ready | false |
| PDF workflow_root_candidate_count | 0 |
| Cells | generation_ready=true, 9 examples merged |
| Words | generation_ready=false (pilot), 4 examples merged |

---

## Generation Policy (Unchanged)

| Family | Generation | Status |
|---|---|---|
| Cells | ALLOWED | Do not run unless new monthly batch |
| Words | PILOT_ONLY (4 types) | NOT ALLOWED to expand |
| PDF | BLOCKED | discovery_only; 4 taskcards must close + human approval |
| Live publish | BLOCKED | No new examples authorized |

---

## Gate 0 Result: PASS

No blocking issues found. Sprint execution is safe to begin.
