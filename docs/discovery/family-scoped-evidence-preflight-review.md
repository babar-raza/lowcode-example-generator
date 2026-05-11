# Family-Scoped Evidence Preflight Review

**Date:** 2026-05-05
**Sprint:** Family-Scoped Evidence Promotion and Latest-State Isolation
**Gate verdict:** `PASS_PROCEED_TO_IMPLEMENTATION`

---

## Referenced Artifact Review (14 artifacts)

| Artifact | Classification | Note |
|---|---|---|
| cells-tier5-monthly-rerun-proof.json | VERIFIED | run_id=pilot-cells-20260430-175422 |
| cells-tier5-e2e-evidence-review.json | VERIFIED | overall_verdict=E2E_VERIFIED_WITH_KNOWN_LIMITATION |
| docs/discovery/cells-tier5-monthly-rerun-proof.md | VERIFIED | Created last sprint |
| docs/discovery/cells-tier5-e2e-evidence-review.md | VERIFIED | Created last sprint |
| open-taskcard-closure-matrix.json | VERIFIED | 45/35/10 |
| docs/discovery/open-taskcard-closure-matrix.md | MISSING | JSON is authoritative; MD will be created in Phase 6 |
| family-generation-readiness-rank.json | VERIFIED | 3 families confirmed |
| all-family-lowcode-discovery.json | VERIFIED | Global file, multi-family |
| Cells run evidence/latest/ | VERIFIED | 22 files, canonical Cells evidence |
| Words run evidence/latest/ | VERIFIED | 20 files, confirmed 19 files overlap with Cells |
| runner.py promote_latest (lines 1229-1250) | NEEDS_FIX | Root cause — no family scoping |
| publisher.py _verify_evidence | NEEDS_FIX | Reads validation-results.json without family-scoped fallback |
| release_status.py | VERIFIED | Already reads only family-prefixed and global files |
| linked-nibbling-hamster.md | VERIFIED | Exists; will be amended in Phase 6 |

Gate 0: No missing blockers. All referenced artifacts found. 2 NEEDS_FIX confirmed. Proceed.

---

## Q1: Which Files Were Overwritten?

The previous review identified **4** files with visible discrepancy. The actual overwrite count was **19**:

```
aggregate-gate-results.json     api-consumer-relationships.json
api-delta-report.json           blocked-scenarios.json
example-gate-results.json       example-impact-report.json
example-reviewer-results.json   fixture-strategy-plan.json
gate-results.json               llm-fewshot-patterns.json
llm-preflight.json              plugin-type-role-classification.json
pr-candidate-manifest.json      reviewer-preflight.json
runnable-entrypoint-scores.json scenario-feedback-updates.json
scenario-input-format-map.json  stale-existing-examples.json
validation-results.json
```

The 4 that showed visible discrepancy were the ones where Cells had 9 entries and Words only had 4.

---

## Q3: Root Cause Code

**File:** [src/plugin_examples/runner.py:1229-1238](src/plugin_examples/runner.py#L1229)

```python
if promote_latest:
    import shutil
    src_latest = evidence_dir / "latest"
    dst_latest = verification_dir / "latest"          # ← flat, no family!
    dst_latest.mkdir(parents=True, exist_ok=True)
    if src_latest.exists():
        for f in src_latest.iterdir():
            if f.is_file() and f.name != ".gitkeep":
                shutil.copy2(f, dst_latest / f.name)  # ← overwrites any family
```

No family tag, no subdirectory — any run's files overwrite any other run's files.

---

## Q4-Q7: Evidence File Taxonomy

| Scope | Examples |
|---|---|
| **Global** | all-family-lowcode-discovery.json, family-generation-readiness-rank.json, open-taskcard-closure-matrix.json, release-status.json |
| **Family-scoped** (all 22 run evidence files) | validation-results.json, pr-candidate-manifest.json, gate-results.json, llm-preflight.json, ... |
| **Already family-prefixed (safe at top level)** | {family}-source-of-truth-proof.json, {family}-live-pr-result.json, etc. |
| **Run-scoped only** | pilot-report.json (stays in runs/{run_id}/), evidence_dir/latest/ |

---

## Q8: What Tests Missed This

No tests check cross-family evidence isolation. Tests verified stage behavior and publisher logic but not that two sequential family promotions preserve each family's evidence in separate directories.

---

## Q9: Required Behavior Change

| | Current | Required |
|---|---|---|
| Primary write | `verification/latest/{file}` | `verification/latest/families/{family}/{file}` |
| Backward-compat | (none) | `verification/latest/{file}` with `_last_promoted_by.json` notice |
| Metadata | (none) | `_evidence_metadata.json` in `families/{family}/` |
| Reader preference | Flat top-level only | `families/{family}/` first, fallback to top-level |
| Cross-family isolation | None | Cells files never overwrite Words and vice versa |
