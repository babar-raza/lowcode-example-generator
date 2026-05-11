# LowCode Example Generator: Execution Handoff

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** HANDOFF_ACTIVE

---

## What Is Complete

| Deliverable | Status | Evidence |
|------------|--------|---------|
| Cells: 9 examples published | COMPLETE | cells-post-merge-clean-checkout-validation.json; PR#1 SHA f6e5515c |
| Words: 4 examples published (pilot) | COMPLETE | words-post-merge-clean-checkout-validation.json; PR#1 SHA b66fb43 |
| PDF PR#1: Merger + TextExtractor | COMPLETE | pdf-pr1-merge-result.json; SHA a9f9e254 |
| PDF PR#3 package: Merger + Splitter | PACKAGED | workspace/pr-dry-run/pdf-controlled-pilot-wave1/ |
| PDF Optimizer: 1st PASS | REVIEWED | pilot-pdf-20260508-155520; code_generator.py R2 fix active |
| R2 constraint injection fix | COMPLETE | code_generator.py FORBIDDEN constraints; 4 tests |
| Denominator model (3 families) | COMPLETE | pipeline/configs/denominators/{cells,words,pdf}.json |
| 77 taskcards tracked | COMPLETE | workspace/verification/latest/open-taskcard-closure-matrix.json |
| 1168 unit tests passing | PASSING | pytest tests/unit/ |

---

## What Is Blocked

| Item | Blocker | Required Action |
|------|---------|----------------|
| PDF PR#3 live creation | APPROVE_LIVE_PR env var not set | Set `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` |
| PDF PR#3 merge | APPROVE_MERGE_PR not set | Set `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR` |
| PDF Optimizer PR#4 | 2nd consecutive PASS needed + APPROVE_LIVE_PR | First: set token; Second: rerun with EXAMPLE_REVIEWER_PATH set |
| All-family reviewer gate | EXAMPLE_REVIEWER_PATH not set | Set `EXAMPLE_REVIEWER_PATH=/path/to/example-reviewer` |
| All-family discovery (Group C) | ~20 families have no YAML config | R1: Create discovery_only YAML configs |
| Email discovery | Config in disabled/; reflection unproven | R2: Move config to active path; test reflection |
| Slides discovery | DLL name mismatch | R2: Fix DLL name; move config to active path |
| Words FULL_SOT denominator | workflow_root_types=NULL | NEW-07: Run full type-role classification |

---

## What Must Execute Next (Priority Order)

### Immediate (can run in parallel)

**1. Phase D: Safe Existing-Family Repairs**
- Fix `release-status` CLI default to include PDF (`__main__.py` lines 269-270)
- Extend monthly workflow to cover cells/words/pdf
- Regenerate release-status.json including PDF

**2. Phase E: YAML Creation for Group C Families (R1)**
- Research and verify NuGet package IDs for 20 candidate families
- Create `pipeline/configs/families/{family}.yml` for each verified family
- Format: `status: discovery_only, enabled: true, package_id: {verified_id}, allowed_types: []`

**3. Phase F: Email/Slides Investigation (R2)**
- Slides: Add `dll_name_override` to slides.yml OR fix DllReflector naming
- Email: Move config to active path; run discovery with `--allow-experimental`
- Both: Create source-of-truth proof or document CONFIRMED_NO_LOWCODE

### After YAML Creation (R3)
- Run `--all-families --promote-latest` discovery
- Classify results per family: lowcode_confirmed, no_lowcode_found, discovery_blocked

### After Discovery (R4-R6)
- Source-of-truth proofs for newly confirmed families
- Type-role classification (including Words 25 types, PDF 21 unclassified types)
- Denominator files for new families

### Gated (requires approval tokens)
- Phase I: PDF PR#3 live creation: `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR` must be set first
- Phase I: PDF Optimizer 2nd PASS: `EXAMPLE_REVIEWER_PATH` must be set for reviewer gate

---

## Non-Negotiable Constraints

1. No live PR creation without `PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL=APPROVE_LIVE_PR`
2. No live merge without `PLUGIN_EXAMPLES_MERGE_PR_APPROVAL=APPROVE_MERGE_PR`
3. No source code changes without explicit sprint scope
4. No family generation without denominator + source-of-truth proof
5. No "published" claim without post-merge verification artifact
6. No silent drop of any planned runnable scenario
7. Stop if denominator equation fails to hold after corrective actions
8. Stop if tests fail after any config change
9. Stop and escalate if live PR returns HTTP 403

---

## Allowed Write Paths Per Sprint

| Sprint | Allowed Paths |
|--------|--------------|
| R0 (done) | docs/plans/lowcode-*.md, workspace/verification/latest/lowcode-*.json |
| R1 | pipeline/configs/families/{new_family}.yml (discovery_only only) |
| R2 | pipeline/configs/families/{email,slides}.yml (config fixes only) |
| R3-R6 | workspace/verification/latest/{family}-*.json, pipeline/configs/denominators/{new_family}.json |
| R7 | workspace/verification/latest/release-status.json, src/plugin_examples/__main__.py (default families only) |
| R8 | workspace/pr-dry-run/pdf-*, workspace/verification/latest/families/pdf/ |

### Forbidden Write Paths
- `pipeline/configs/families/cells.yml`, `words.yml`, `pdf.yml` (no changes without explicit scope)
- `src/plugin_examples/` (no source changes in R0; only R7/R8+ specific changes)
- `tests/unit/` (no test weakening ever; new tests only)
- `workspace/verification/latest/open-taskcard-closure-matrix.json` (only updated in Phase C)

---

## Environment Requirements Per Sprint

| Sprint | Required Variables |
|--------|------------------|
| R1 (YAML creation) | Python 3.13.2, .NET 9.0.200 |
| R2/R3 (discovery) | All above + GPT_OSS_ENDPOINT, GPT_OSS_API_KEY |
| R3+ (with reviewer) | All above + EXAMPLE_REVIEWER_PATH |
| R8 (PDF live PR) | All above + GITHUB_TOKEN (Contents:Write), APPROVE_LIVE_PR, APPROVE_MERGE_PR |

---

## Key File Paths Quick Reference

| Purpose | Path |
|---------|------|
| Active family configs | pipeline/configs/families/{cells,words,pdf}.yml |
| Disabled/experimental | pipeline/configs/families/disabled/{email,slides}.yml |
| Denominator files | pipeline/configs/denominators/{cells,words,pdf}.json |
| Completion queue | workspace/queues/example-completion-queue.json |
| Taskcard matrix | workspace/verification/latest/open-taskcard-closure-matrix.json |
| PDF PR#3 package | workspace/pr-dry-run/pdf-controlled-pilot-wave1/ |
| Backlog (pdf) | workspace/backlog/pdf/examples-backlog.json |
| Backlog (words) | workspace/backlog/words/excluded-scenarios.json |
| Type classification (pdf) | workspace/verification/latest/pdf-type-role-classification.json |
| Release status | workspace/verification/latest/release-status.json |
| Execution ledger | workspace/verification/latest/lowcode-single-go-autonomous-execution-ledger.json |
