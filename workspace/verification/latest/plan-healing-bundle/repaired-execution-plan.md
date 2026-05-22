# Sprint 34 README Production Gap Healing — REPAIRED EXECUTION PLAN

## Plan-Healing Sprint Metadata
- **Plan version**: 2.0 (repaired)
- **Base commit**: `1c337ad` (2026-05-18 15:03, "fix(readme-portfolio): generalize source-truth facts extraction and portfolio-wide README healing")
- **Branch**: `main` (14 commits ahead of origin/main)
- **Working tree**: CLEAN at plan-repair time
- **Test count at baseline**: 1789 passing
- **Evidence contract version**: V6 (67 categories)

---

## 1. Context

README.md files in target example repositories do not reflect all examples present in the repo after multiple PRs merge. The publication pipeline renders README per-PR-package, listing only that package's examples. Successive PR merges overwrite the README, dropping entries from earlier PRs.

**Hypothesis (to be verified by execution agent)**: README rendering at `__main__.py:837-839` discovers examples only from `package_path/examples/{family}/lowcode/`, and `build_readme_context()` in `readme_renderer.py:173` receives only that list. No cumulative aggregation logic exists. The execution agent MUST verify this hypothesis against the actual code paths before implementing fixes.

**Scope**: 6 active families — Cells, Words, PDF, Diagram, Email, Slides. PDF is worst case (8 PR-dry-run packages). No local clones of target repos exist; all remote interaction is via GitHub API.

---

## 2. Verified Inventory (from plan-healing exploration)

### PR Dry-Run Packages (actual disk state)

| Package | Examples | Names |
|---------|----------|-------|
| `cells-controlled-pilot` | 9 | html-converter, image-converter, json-converter, pdf-converter, spreadsheet-converter, spreadsheet-locker, spreadsheet-merger, spreadsheet-splitter, text-converter |
| `words-controlled-pilot` | 8 | comparer, converter, mail-merger, merger, replacer, report-builder, splitter, watermarker |
| `words-report-builder` | 1 | report-builder (subset/duplicate of words-controlled-pilot) |
| `pdf-controlled-pilot` | 3 | doc-converter, html, xls-converter |
| `pdf-controlled-pilot-wave1` | 2 | merger, splitter |
| `pdf-controlled-pilot-wave2` | 1 | optimizer |
| `pdf-controlled-pilot-pr5` | 3 | jpeg, png, tiff |
| `pdf-controlled-pilot-pr6` | 3 | image-extractor, table-generator, toc-generator |
| `pdf-controlled-pilot-pr7` | 2 | form-flattener, security |
| `pdf-controlled-pilot-pr8` | 2 | form-editor, form-exporter |
| `pdf-controlled-pilot-pr9` | 1 | signature |
| `diagram-controlled-pilot` | 2 | diagram-diagram-converter, diagram-pdf-converter |
| `email-controlled-pilot` | 1 | converter |
| `slides-controlled-pilot` | 3 | compress, convert, merger |

### Published Examples (from memory/evidence — execution agent must re-verify)

| Family | Published to remote main | Source |
|--------|--------------------------|--------|
| Cells | 9 (all) | PR#1 merged |
| Words | 4 (converter, watermarker, splitter, replacer) + 4 more (merger, comparer, mail-merger, report-builder) via subsequent PRs | PR#1 + later PRs |
| PDF | 5 (merger, text-extractor, pdfa-converter, splitter, optimizer) | PR#1 + PR#4 merged |
| Diagram | 2 (all) | PR#1 merged |
| Email | 1 (converter) | PR#1 merged |
| Slides | 3 (compress, convert, merger) | PR#1 merged |

**CRITICAL**: These published counts are hypotheses from memory. The execution agent MUST verify by:
1. Reading post-merge validation JSONs in `workspace/verification/latest/`
2. Querying GitHub API via `gh` if authenticated
3. Cross-checking against publication ledgers and evidence bundles

### PDF Unique Example Universe

17 unique examples in PR packages + 2 published-only (text-extractor, pdfa-converter not in any package) = 19 total. Execution agent must verify text-extractor and pdfa-converter are truly absent from all packages.

---

## 3. Inventory Mode Definitions (HARD RULES)

The execution agent MUST use these inventory modes:

### Mode A: `repo_actual_inventory`
Examples physically present in the target repo's main/default branch. Determined by:
1. GitHub API contents listing (`gh api repos/{owner}/{repo}/contents/examples/{family}/lowcode`)
2. Post-merge validation JSONs
3. If no API access: infer from publication ledgers + merged PR evidence

### Mode B: `current_package_overlay_inventory`
For a single-package PR: `repo_actual_inventory` UNION `current_package_examples`. This is what the PR branch will contain after merge.

### Mode C: `batch_overlay_inventory`
For a multi-package batch PR: `repo_actual_inventory` UNION ALL `batch_package_examples`. Only used when the execution plan intentionally applies multiple packages to the same branch.

### Mode D: `pending_evidence_only_inventory`
Examples that are PR-ready or package-ready but NOT present in the target branch. These MUST NOT be listed in the README "Included Examples" section. They MAY appear in a clearly marked "Pending / Not Yet Merged" section only if the repo convention supports it.

### HARD RULE
**README "Included Examples" or equivalent present-tense example sections MUST list ONLY examples that will exist in the target repo branch after the PR merges.** No pending/future examples in the present-tense inventory table.

### Source Priority (when sources disagree)
1. Target repo actual checkout state (GitHub API or local clone) — highest authority
2. Post-merge validation JSON — second authority (verified after merge)
3. PR dry-run package contents on disk — third (verified locally)
4. Publication ledgers / evidence bundles — fourth (claims, not direct observation)
5. Memory / config files — lowest (hypotheses only)

When lower-priority sources contradict higher-priority sources, the execution agent MUST document the conflict and use the higher-priority source.

---

## 4. Taskcards (Execution Sprint)

### Taskcard State Machine

All taskcards follow this lifecycle:
```
proposed → in_progress → implemented → verified → closed_verified
                    ↘ blocked → closed_blocked_with_evidence
```

No taskcard may close from summary text alone. Closeout requires:
- Output artifact(s) exist at specified path(s)
- Verification command passes
- Evidence file written

### Taskcard Table

| ID | Title | Owner Lane | Input Artifacts | Output Artifacts | Gate Dep | Verify Command | Closeout | Blocked If |
|----|-------|-----------|-----------------|------------------|----------|----------------|----------|------------|
| TC-README-001 | Affected repo + PR inventory | Lane B | Family YAMLs, post-merge JSONs, PR dry-run dirs | `workspace/verification/latest/readme-affected-repo-inventory.json` | Gate 0 | JSON exists + schema valid | Inventory JSON has all 6 families with repo URLs + example counts | GitHub API unavailable (degrade to local-only) |
| TC-README-002 | README manual-edit forensic review | Lane C | Repo inventory from TC-001, `gh` access | `workspace/verification/latest/readme-manual-edit-forensic.json` | TC-001 | JSON exists + lists commit history per repo | Per-repo README git log present + manual edit classification | No `gh` auth (degrade to local evidence only) |
| TC-README-003 | README-vs-example coverage audit | Lane B | Repo inventory, PR dry-run READMEs | `workspace/verification/latest/readme-coverage-audit-before.json` | TC-001 | JSON lists per-family: readme_count, inventory_count, missing, extra | All 6 families audited | None (local-only operation) |
| TC-README-004 | Root-cause code-path verification | Lane D | `__main__.py`, `readme_renderer.py`, `readme_auditor.py` | `workspace/verification/latest/readme-root-cause-verification.json` | None | JSON documents exact code paths + line numbers + hypothesis result | Hypothesis confirmed or corrected with evidence | None |
| TC-README-005 | README source-of-truth design | Lane E | Root-cause from TC-004, inventory modes | Design section in evidence JSON | TC-004 | Design covers all inventory modes + conflict resolution | Inventory mode definitions documented | None |
| TC-README-006 | Pipeline healing implementation | Lane F | Design from TC-005 | `readme_inventory.py`, modified `__main__.py`, `readme_renderer.py` | TC-005 | Targeted tests pass | All modified files pass linting + targeted tests | None |
| TC-README-007 | README validator/gate (staleness) | Lane G | TC-006 implementation | Modified `readme_auditor.py`, staleness gate in `__main__.py` | TC-006 | Staleness tests pass | publish-pr fails closed on stale README for PR branch content | None |
| TC-README-008 | README backfill all repos | Lane H | TC-006 + TC-007 implementation | Per-family README before/after snapshots, updated `workspace/pr-dry-run/*/README.md` | TC-007 | Idempotency rerun produces no diff | All local READMEs updated + remote classified as updated/blocked | Token/approval gates for remote |
| TC-README-009 | Tests + evidence bundle | Lane I | All prior TCs | Test logs, evidence bundle ZIP | TC-008 | Full test suite passes + bundle validates | 1789+ tests pass, bundle contract validates | Test failures |
| TC-README-010 | Final closure decision | Lane A | All TCs | Final verdict in evidence bundle | TC-009 | All TCs closed_verified OR closed_blocked_with_evidence | Verdict rendered | Any TC still in_progress |

---

## 5. Lane Ownership and File Rules

| Lane | Role | Owned Files | Shared Files (coordinator approval) |
|------|------|-------------|--------------------------------------|
| A — Coordinator | Taskcards, gates, integration, final bundle | Evidence bundle ZIP, final verdict | All taskcard JSONs, plan file |
| B — Repo Inventory | Affected repo discovery, coverage audit | `readme-affected-repo-inventory.json`, `readme-coverage-audit-*.json` | None |
| C — Forensic Review | Manual edit detection, preservation rules | `readme-manual-edit-forensic.json` | None |
| D — Root Cause | Code-path tracing, hypothesis verification | `readme-root-cause-verification.json` | None |
| E — Design | Inventory model, source-of-truth design | Design docs in evidence | None |
| F — Implementation | `readme_inventory.py`, renderer/facts extensions, CLI changes | `src/plugin_examples/publisher/readme_inventory.py`, modifications to `readme_renderer.py`, `readme_facts.py`, `__main__.py` | None |
| G — Gating | Staleness detection, fail-closed gates | Modifications to `readme_auditor.py`, staleness gate additions in `__main__.py` | `__main__.py` shared with Lane F — coordinate |
| H — Backfill | README regeneration, before/after snapshots | `workspace/pr-dry-run/*/README.md`, snapshot evidence | None |
| I — Tests | Test creation, full suite validation, CI checks | `tests/unit/test_readme_inventory.py`, `tests/unit/test_readme_auditor.py` additions, test logs | None |

### Overlap Rules
- `__main__.py` is shared between Lane F (CLI cumulative discovery) and Lane G (staleness gate). Lane F modifies first, Lane G modifies second. Coordinator verifies no conflicts.
- No lane may edit another lane's owned files without coordinator approval.
- All evidence JSONs in `workspace/verification/latest/` follow naming convention `readme-{topic}.json`.

---

## 6. Implementation Steps (Execution Sprint)

### Gate 0 — Preflight
1. Record: repo root, branch, HEAD SHA, origin URL, dirty state, Python venv path, env flags (`APPROVE_LIVE_PR`, `GITHUB_TOKEN`, `GH_TOKEN`)
2. Run `.venv/Scripts/python.exe -c "import plugin_examples; print('import OK')"` to verify environment
3. Run `git status` — if dirty outside workspace/verification/latest/, STOP and document
4. Record baseline test count: `.venv/Scripts/python.exe -m pytest tests/ --co -q | tail -1`
5. Check `gh auth status` — record authenticated or not (non-blocking)
6. Output: `workspace/verification/latest/readme-preflight.json`

### Gate 1 — Inventory (Lane B: TC-001, TC-003)
1. For each of 6 active families, read `pipeline/configs/families/{family}.yml` → extract `github.published_plugin_examples_repo.{owner, repo, branch}`
2. Scan `workspace/pr-dry-run/{family}-*` → list example directories per package
3. Read `workspace/verification/latest/{family}-post-merge-clean-checkout-validation.json` → extract published examples
4. If `gh` authenticated: `gh api repos/{owner}/{repo}/contents/examples/{family}/lowcode` → get `repo_actual_inventory`
5. If not authenticated: use post-merge JSON as best available `repo_actual_inventory`
6. Cross-reference all sources. Document conflicts.
7. For each PR dry-run package README.md, parse example table → count listed examples
8. Compare README example count vs package example count → produce coverage audit
9. Output: `readme-affected-repo-inventory.json`, `readme-coverage-audit-before.json`

### Gate 2 — Forensic Review (Lane C: TC-002; Lane D: TC-004)
1. For each affected repo, if `gh` authenticated: `gh api repos/{owner}/{repo}/commits?path=README.md` → list README commits
2. Classify each commit as: automated (pipeline-generated), manual (human edit), or unknown
3. If any manual commits found: extract the diff, document what was changed, record preservation requirements
4. **Finding from plan-healing exploration**: No manual README edits detected in any target repo — all automated via template. Execution agent MUST re-verify this.
5. Trace code paths in `__main__.py` (publish-pr: lines 837-839, 853-909) and `readme_renderer.py` (build_readme_context: line 173). Verify single-package discovery hypothesis.
6. Output: `readme-manual-edit-forensic.json`, `readme-root-cause-verification.json`

### Gate 3 — Design (Lane E: TC-005)
1. Document inventory mode definitions (Section 3 above)
2. Design cumulative discovery algorithm
3. Define managed section markers: `<!-- GENERATED EXAMPLES INDEX START -->` / `<!-- GENERATED EXAMPLES INDEX END -->`
4. Define preservation rules:
   - Content outside managed markers preserved byte-for-byte
   - If no markers exist in a README, the entire README is replaced (it's pipeline-generated)
   - If manual content exists outside markers, it is preserved
   - Before/after snapshots taken for every README modification
5. Output: design section in `readme-root-cause-verification.json` or separate design doc

### Gate 4 — Implementation (Lane F: TC-006; Lane G: TC-007)

#### Lane F: Cumulative Discovery

**Create** `src/plugin_examples/publisher/readme_inventory.py`:

```python
@dataclass
class InventoryEntry:
    name: str                    # e.g. "doc-converter"
    source_package: str          # e.g. "pdf-controlled-pilot"
    source_type: str             # "pr_package" | "post_merge" | "repo_actual"
    output_format: str
    has_program_cs: bool
    package_path: Path | None    # path to package containing this example

@dataclass
class InventoryAuditTrail:
    family: str
    sources_scanned: list[dict]  # {source_type, path, entry_count}
    conflicts: list[dict]        # {example_name, sources, resolution}
    deduplication_log: list[str]

def discover_family_inventory(
    family: str,
    repo_root: Path,
    inventory_mode: str,           # "repo_actual" | "current_package_overlay" | "batch_overlay"
    current_package_path: Path | None = None,
    batch_package_paths: list[Path] | None = None,
    repo_actual_examples: list[str] | None = None,  # from GitHub API or post-merge JSON
) -> tuple[list[InventoryEntry], InventoryAuditTrail]:
    ...
```

**Modify** `readme_renderer.py:build_readme_context()`:
- Add optional `package_path_map: dict[str, Path] | None = None`
- When set, resolve each example's Program.cs from per-example path map
- Backward compatible: existing `package_path` continues to work

**Modify** `readme_facts.py:extract_example_readme_facts()`:
- Add optional `package_path_map: dict[str, Path] | None = None`
- When set, each example resolves its own Program.cs path
- Backward compatible

**Modify** `__main__.py` publish-pr (lines ~837-909):
- Before README rendering, call `discover_family_inventory()` with `inventory_mode="current_package_overlay"`
- Pass `repo_actual_examples` from post-merge JSON (or GitHub API if available)
- Pass `current_package_path` as the current package
- Build `package_path_map` from the inventory entries
- Pass cumulative examples + package_path_map to `build_readme_context()`
- PR file tree still contains only THIS package's files (existing behavior unchanged)

**Modify** `__main__.py` publish-readme (lines ~1617+):
- Use `discover_family_inventory()` with `inventory_mode="repo_actual"` for backfill
- Or `batch_overlay` if multiple packages specified

**Modify** `__main__.py` render-root-readme:
- Add `--cumulative` flag; when set, uses cumulative discovery

#### Lane G: Staleness Gate

**Modify** `readme_auditor.py`:
- Add `audit_readme_staleness(readme_content, expected_examples) -> ReadmeStalenessResult`
- Returns: `is_stale`, `missing_from_readme`, `extra_in_readme`, `inventory_count`, `readme_count`

**Integrate into publish-pr**:
- After README render, audit staleness against `current_package_overlay_inventory`
- **FAIL CLOSED** if README is stale against the intended PR branch content
- Other pending packages not in this PR branch MUST NOT cause failure
- Audit output classifies excluded examples as `pending_not_in_branch`

**Integrate into publish-readme**:
- **FAIL CLOSED** if README is stale against `repo_actual_inventory`

### Gate 5 — Backfill (Lane H: TC-008)

For each of 6 families:

1. Snapshot current README: `cp workspace/pr-dry-run/{family}-controlled-pilot/README.md workspace/verification/latest/readme-before-{family}.md`
2. Determine inventory mode:
   - Single-package families (Cells, Diagram, Email, Slides): `repo_actual` — all examples in one package
   - Multi-package families (Words, PDF): `batch_overlay` using all packages for that family
3. Render cumulative README
4. Snapshot after: save rendered README
5. Diff before/after: record in evidence
6. Write to `workspace/pr-dry-run/{family}-controlled-pilot/README.md`
7. For PR-specific packages (pdf-controlled-pilot-pr5 through pr9): render with `current_package_overlay` mode so each PR branch README is also correct
8. Run idempotency check: re-render → diff must be empty
9. Classify remote state:
   - If `APPROVE_LIVE_PR` + `GITHUB_TOKEN` set: can push via `publish-readme --publish`
   - If not set: classify as `blocked_with_evidence`, record exact env vars needed and command to run
10. Output: per-family before/after snapshots, diff, idempotency proof

### Gate 6 — Tests (Lane I: TC-009)

**New tests** (`tests/unit/test_readme_inventory.py`):
1. `test_discover_single_package` — single package → correct entries
2. `test_discover_multi_package_pdf` — PDF 8-package scenario → correct deduplication
3. `test_repo_actual_overlay` — repo_actual + current_package → union
4. `test_deduplication_repo_actual_wins` — priority ordering
5. `test_empty_family` — no sources → empty list
6. `test_audit_trail_records_sources` — all scanned sources in trail
7. `test_build_package_path_map` — maps example→package_path correctly
8. `test_inventory_mode_validation` — invalid mode raises

**New/extended tests** (`tests/unit/test_readme_auditor.py`):
9. `test_staleness_missing_examples` — README missing entries → stale=True
10. `test_staleness_all_present` — complete README → stale=False
11. `test_staleness_extra_examples` — README has extra entries → reports extra

**Extended** (`tests/unit/test_readme_renderer.py`):
12. `test_build_context_with_package_path_map` — multi-package fact extraction
13. `test_cumulative_readme_lists_all_examples` — rendered content has all entries

**Validation commands (in order)**:
```bash
# 1. Targeted tests (fail-fast during development)
.venv/Scripts/python.exe -m pytest tests/unit/test_readme_inventory.py -v
.venv/Scripts/python.exe -m pytest tests/unit/test_readme_renderer.py -v
.venv/Scripts/python.exe -m pytest tests/unit/test_readme_auditor.py -v

# 2. README-related tests
.venv/Scripts/python.exe -m pytest tests/ -k "readme" -v

# 3. Evidence contract tests
.venv/Scripts/python.exe -m pytest tests/ -k "evidence_contract" -v

# 4. Full suite (MUST run for final validation — NOT fail-fast)
.venv/Scripts/python.exe -m pytest tests/ -v --tb=short 2>&1 | tee workspace/verification/latest/readme-sprint-test-log.txt

# 5. Idempotency check per family
# (render README twice, diff must be empty)

# 6. git diff --check (no whitespace errors)
git diff --check

# 7. gh checks if authenticated
gh pr checks --repo {owner}/{repo} (if applicable)
```

### Gate 7 — Evidence Contract

**Update** `evidence_contract.py` — add V7 with new category:
```python
_REQUIRED_CATEGORIES_V7_NEW = {
    "readme_sync_audit": ["readme-sync-audit", "readme-cumulative-inventory"],
    "readme_coverage_audit": ["readme-coverage-audit"],
}
```

The `readme-sync-audit.json` records:
```json
{
  "audit_type": "readme_sync",
  "family_audits": [
    {
      "family": "pdf",
      "inventory_mode": "batch_overlay",
      "inventory_count": 19,
      "readme_count": 19,
      "is_stale": false,
      "missing_from_readme": [],
      "extra_in_readme": [],
      "pending_not_in_branch": []
    }
  ],
  "all_families_in_sync": true
}
```

### Gate 8 — Git and Evidence Closeout (Lane A: TC-010)

1. `git status` — verify clean or only expected changes
2. `git diff --stat` — record changed files
3. Stage exact paths only (NO `git add .`)
4. Commit message: `feat(sprint34-readme-healing): implement cumulative README sync with per-branch inventory modes and staleness gates`
5. `git log --oneline -3` — record commit SHA
6. Build evidence bundle ZIP (see Section 9)
7. Final `git status` — must be clean

---

## 7. Rollback and Recovery Model

### Pre-change Safeguards
- Snapshot all README.md files before modification (saved as `readme-before-{family}.md`)
- Record `git status` and HEAD SHA before any changes
- No changes to files outside the owned-files list per lane

### Abort Conditions
- Full test suite drops below 1789 passing → ABORT, revert all changes
- README render produces empty or <100 byte output → ABORT that family, continue others
- `readme_facts.py` import fails → ABORT (critical dependency broken)
- Working tree has unexpected dirty files → STOP, investigate

### Partial Failure Handling
- If one family's backfill fails, other families continue independently
- Failed family classified as `blocked_with_evidence` with exact error
- Evidence bundle still produced with partial results

### Revert Procedure
If a README render is wrong:
1. `git checkout -- workspace/pr-dry-run/{family}-controlled-pilot/README.md` (restores from last commit)
2. Or: copy from `workspace/verification/latest/readme-before-{family}.md` snapshot
3. Do NOT use `git reset --hard` or `git stash`

### Remote Update Recovery
- If `publish-readme --publish` fails mid-flight: the GitHub API creates PRs atomically. A failed API call leaves no partial PR.
- If a README-only PR is created but wrong: close via `gh pr close` and re-create
- All remote operations require explicit approval gates — no auto-push

---

## 8. Manual README Preservation Rules

### Detection
- For each affected repo: `gh api repos/{owner}/{repo}/commits?path=README.md&per_page=100` (if authenticated)
- Classify each commit author: `plugin-examples/*` branch = automated, other = manual
- **Plan-healing finding**: No manual README edits detected. Execution agent MUST re-verify.

### Preservation Protocol
1. If README has managed-section markers (`<!-- GENERATED EXAMPLES INDEX START/END -->`): only replace content between markers
2. If README has NO markers (current state — all pipeline-generated): full replacement is safe but markers SHOULD be introduced
3. If manual content is detected outside markers: preserve byte-for-byte, document in evidence
4. Before/after snapshots saved for every modification
5. Idempotency proof: re-running sync produces zero diff

### Managed Section Convention
```markdown
<!-- GENERATED EXAMPLES INDEX START -->
(pipeline-managed content here)
<!-- GENERATED EXAMPLES INDEX END -->
```

Introduce in the Jinja2 template. All content outside these markers in an existing README is preserved if present.

---

## 9. Evidence Bundle Contract

### Plan-Healing Sprint Bundle (THIS sprint)

File: `workspace/verification/sprint34-plan-healing-readme-production-gap-{timestamp}.zip`

Contents:
- `plan-healing-metadata.json` — sprint metadata, base commit, branch
- `repaired-execution-plan.md` — this plan file
- `taskcard-state-table.json` — TC-README-PLAN-001 through 010 with statuses
- `affected-repo-inventory-requirements.json` — what the execution agent must discover
- `inventory-mode-design.json` — 4 mode definitions + priority rules
- `manual-readme-preservation-design.json` — detection + preservation protocol
- `lane-ownership-table.json` — lane→file ownership + overlap rules
- `rollback-recovery-plan.json` — abort conditions, revert procedures
- `verification-command-matrix.json` — all test commands + expected outcomes
- `evidence-contract-requirements.json` — what V7 must check
- `git-status-final.txt`
- `git-log-final.txt`
- `changed-files-list.txt`
- `diff-summary.txt`
- `secret-redaction-proof.json` — grep for tokens/keys in bundle

### Execution Sprint Bundle (FUTURE sprint must produce)

File: `workspace/verification/sprint34-readme-healing-execution-{timestamp}.zip`

Required contents:
- `preflight-state.json` — repo root, branch, HEAD, env flags, venv, test count
- `readme-affected-repo-inventory.json` — all 6 families with URLs, counts, states
- `readme-pr-branch-inventory.json` — open PR branches per repo
- `readme-manual-edit-forensic.json` — per-repo README git log + classification
- `readme-before-{family}.md` — before snapshot per family (6 files)
- `readme-after-{family}.md` — after snapshot per family (6 files)
- `readme-coverage-audit-before.json` — stale/missing/extra before fixes
- `readme-coverage-audit-after.json` — must show all in-sync
- `readme-sync-audit.json` — per-family inventory audit
- `readme-root-cause-verification.json` — code path + hypothesis result
- `readme-idempotency-proof.json` — re-render diff = empty
- `test-log.txt` — full test suite output
- `git-status-final.txt`
- `git-log-final.txt` — commit SHA proof
- `changed-files-manifest.txt`
- `per-repo-blocked-state.json` — any repos that couldn't be updated remotely
- `secret-redaction-proof.json`

Bundle built AFTER final commit. If no commit made, bundle states why.

---

## 10. `readme_facts.py` Handling

**Status**: Already committed in `1c337ad` (2026-05-18 15:03). The user has also modified it with extended patterns (input1, template, source, result, report, output_signed). The file is a live dependency of `readme_renderer.py` line 16.

**Execution agent requirements**:
1. Read current `readme_facts.py` — verify it matches expected state (extended patterns present)
2. Run `python -c "from plugin_examples.publisher.readme_facts import extract_example_readme_facts; print('OK')"` to verify import
3. Run `pytest tests/ -k "readme_facts or readme_renderer" -v` to verify existing tests pass with it
4. If any test fails: diagnose and fix before proceeding (do NOT exclude the file)
5. If file has been further modified by user/linter since plan-healing: accept the modification as intentional

---

## 11. `publish-pr` Gating Rules (HARD)

The current plan's "WARNING for stale README in publish-pr" is UNSAFE. Corrected rules:

1. `publish-pr` MUST fail closed if README is stale against `current_package_overlay_inventory`
2. `current_package_overlay_inventory` = `repo_actual_inventory` UNION `current_package_examples`
3. Other pending packages NOT in this PR branch MUST NOT cause failure
4. Other pending packages NOT in this PR branch MUST NOT appear in the README "Included Examples" table
5. The audit output MUST classify excluded pending examples as `pending_not_in_branch`
6. For batch PRs: use `batch_overlay_inventory` instead

---

## 12. Final Execution Handoff Prompt

The following prompt is the complete, self-contained instruction for the execution agent. It is ready to send ONLY if this plan-healing sprint produces verdict `READY_FOR_SINGLE_GO_EXECUTION`.

---

BEGIN EXECUTION PROMPT (for next sprint):

```
You are working on the LowCode Example Generator / Aspose .NET Plugin Examples publication system.

MISSION: Sprint 34 README Production Gap Healing — Single-Go Execution

Implement the repaired execution plan from the plan-healing sprint to heal the README production gap.
The plan file is at: C:\Users\prora\.claude\plans\tingly-launching-pond.md

HARD RULES:
- Use .venv/Scripts/python.exe for all Python operations
- Do not stash, reset, restore, clean, or broad-stage files
- Do not use broad `git add .` — stage exact paths only
- Do not delete or overwrite manual README edits without preservation + evidence
- Do not treat the human as a blocker unless an external credential/token is truly unavailable
- Do not assume example counts — verify from disk and evidence
- README "Included Examples" MUST list ONLY examples present in the target branch
- publish-pr MUST fail closed if README is stale against PR branch content
- Full test suite must be run for final validation (not just fail-fast)
- Evidence bundle must be built AFTER final commit

TASKCARDS: TC-README-001 through TC-README-010 (see plan Section 4)
LANES: A through I (see plan Section 5)
GATES: 0 through 8 (see plan Section 6)
INVENTORY MODES: 4 modes defined (see plan Section 3)
ROLLBACK: See plan Section 7
EVIDENCE BUNDLE: See plan Section 9

IMPLEMENTATION ORDER:
1. Gate 0: Preflight — record state, verify environment
2. Gate 1: Inventory — discover all affected repos and examples (TC-001, TC-003)
3. Gate 2: Forensic — verify root cause, check for manual edits (TC-002, TC-004)
4. Gate 3: Design — document inventory modes and preservation rules (TC-005)
5. Gate 4: Implementation — create readme_inventory.py, modify renderer/auditor/CLI (TC-006, TC-007)
6. Gate 5: Backfill — update all README.md files with cumulative content (TC-008)
7. Gate 6: Tests — run targeted + full suite (TC-009)
8. Gate 7: Evidence contract — add V7 README category
9. Gate 8: Closeout — commit, bundle, verdict (TC-010)

KEY FILES TO CREATE:
- src/plugin_examples/publisher/readme_inventory.py (cumulative discovery engine)
- tests/unit/test_readme_inventory.py (inventory tests)

KEY FILES TO MODIFY:
- src/plugin_examples/publisher/readme_renderer.py (add package_path_map)
- src/plugin_examples/publisher/readme_facts.py (add package_path_map)
- src/plugin_examples/publisher/readme_auditor.py (add staleness detection)
- src/plugin_examples/__main__.py (fix publish-pr, publish-readme, render-root-readme)
- src/plugin_examples/evidence_contract.py (V7 with README category)
- tests/unit/test_readme_renderer.py (extend)
- workspace/pr-dry-run/*/README.md (backfill)

VALIDATION:
1. Targeted README tests pass
2. Evidence contract tests pass
3. Full test suite: .venv/Scripts/python.exe -m pytest tests/ -v --tb=short
4. Idempotency: re-render produces zero diff
5. git diff --check passes
6. Evidence bundle validates

FINAL RESPONSE FORMAT:
1. Verdict: SPRINT34_README_HEALING_COMPLETE or SPRINT34_README_HEALING_BLOCKED_WITH_EVIDENCE
2. Root cause confirmed/corrected
3. What was changed (file list)
4. Repos updated (local/remote/blocked)
5. Tests: count passing, any failures
6. Commit SHA
7. Evidence bundle absolute path
8. Unresolved blockers (if any)
```

END EXECUTION PROMPT

---

## 13. Plan-Healing Verdict Criteria

**READY_FOR_SINGLE_GO_EXECUTION** if:
- All 12 repair areas addressed in this plan
- Taskcard state machine defined with evidence-based closeout
- Inventory modes defined with hard rules
- Lane ownership non-overlapping (except documented shared files)
- Rollback model complete
- Evidence bundle contracts for both sprints defined
- `readme_facts.py` handling corrected (no longer "stage untracked")
- publish-pr gating corrected (fail-closed, not warning)
- Execution prompt is complete and self-contained
- No unresolved ambiguities that would block the execution agent

**PLAN_NEEDS_REPAIR** if any of the above is missing.
