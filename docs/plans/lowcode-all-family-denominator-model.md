# LowCode Example Generator: All-Family Denominator Model

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** PARTIAL - Cells/Words/PDF denominators exist; all others require R1-R6

---

## Extended Denominator Equation

The full 9-term equation handles all verification states:

```
planned_runnable_examples =
  published_post_merge_verified
  + pr_ready_examples
  + reviewed_awaiting_pr
  + blocked_examples
  + dropped_with_evidence_examples
  + backlogged_for_repair_examples
  + failed_verification_pending_triage
  + relaunch_ready_examples
  + non_runnable_with_source_of_truth
```

**Final Audit Conditions (all must be zero at R15):**
- `failed_verification_pending_triage = 0`
- `dropped_without_sufficient_evidence = 0`
- `backlog_without_taskcard = 0`
- `taskcard_without_backlog_link = 0`
- `denominator_entry_without_lifecycle = 0`
- `lifecycle_failure_without_completion_queue_state = 0`
- `completion_queue_missing_planned_runnable = 0`
- `release_status_contradicting_published_state = 0`

---

## Per-Family Denominator (Verified State)

### Cells (FULL_SOT - HOLDS)

| Term | Count |
|------|-------|
| published_post_merge_verified | 9 |
| pr_ready | 0 |
| reviewed_awaiting_pr | 0 |
| blocked | 0 |
| dropped_with_evidence | 0 |
| backlogged_for_repair | 0 |
| failed_verification_pending_triage | 0 |
| relaunch_ready | 0 |
| non_runnable_with_source_of_truth | 13 |
| **Total LowCode types** | **22** |
| **Equation holds** | **YES** |

Basis: FULL_SOT | Coverage: 9/9 = 100%

### Words (PILOT_ALLOWED - HOLDS for pilot; FULL_SOT NOT EVALUABLE)

| Term | Pilot Count | Full Count |
|------|-------------|------------|
| published_post_merge_verified | 4 | 4 |
| pr_ready | 0 | 0 |
| reviewed_awaiting_pr | 0 | 0 |
| blocked | 0 | 0 |
| dropped_with_evidence (fixture gap) | 0 | 5 (Comparer, Merger, MailMerger, SplitCriteria, Processor/ReportBuilder) |
| backlogged_for_repair | 0 | 0 |
| failed_verification_pending_triage | 0 | 0 |
| relaunch_ready | 0 | 0 |
| non_runnable_or_pending_classification | - | 16 (Context classes 8 + ENUM/OPTIONS 5 + others 3) |
| **Total LowCode types** | **25** | **25** |
| **Equation holds** | **YES (pilot)** | **NOT_EVALUABLE (workflow_root_types=NULL)** |

Basis: PILOT_ALLOWED | Pilot coverage: 4/4 = 100% | Full coverage: ~16% (4/25 estimated)

**Gap:** workflow_root_types=NULL in denominator JSON; FULL_SOT requires classification (NEW-07)

### PDF (PILOT_ALLOWED - HOLDS for pilot)

| Term | Pilot Count | Full Workflow Root Count |
|------|-------------|--------------------------|
| published_post_merge_verified | 2 | 2 |
| pr_ready | 1 | 1 |
| reviewed_awaiting_pr | 1 | 1 |
| blocked | 0 | 0 |
| dropped_with_evidence (pilot deferred) | 0 | 21 |
| backlogged_for_repair | 0 | 0 |
| failed_verification_pending_triage | 0 | 0 |
| relaunch_ready | 0 | 0 |
| non_runnable_with_source_of_truth | - | 76 |
| **Total LowCode types** | **4 (pilot)** | **101** |
| **Equation holds** | **YES (pilot)** | **YES (full: 2+1+1+0+21+76=101)** |

Basis: PILOT_ALLOWED | Pilot coverage: 2/4 published = 50% | Workflow root coverage: 2/25 = 8%

**Gap (RC-011):** 21 deferred WORKFLOW_ROOT types not in completion queue

### Email, Slides, All Group C Families

| Term | Value |
|------|-------|
| denominator_basis | NOT_ESTABLISHED |
| equation | NOT_EVALUABLE |
| required_action | Phase R1-R6 (YAML creation, discovery, classification, denominator) |

---

## Project-Wide Summary (Current State)

| Metric | Value |
|--------|-------|
| Total published (verified) | 15 (Cells=9, Words=4, PDF=2) |
| Total PR-ready | 1 (PDF Splitter) |
| Total reviewed-awaiting-PR | 1 (PDF Optimizer) |
| Families with confirmed LowCode | 3 (active) |
| Families potentially having LowCode | +2 (email, slides - unverified) |
| Families with no discovery evidence | ~20 (Group C) |
| Project denominator completeness | INCOMPLETE (family universe unknown) |

---

## Denominator Schema

All denominator files must validate against `pipeline/schemas/denominator.schema.json`.

Required fields:
- `family`, `source_package`, `source_version`, `api_catalog_sha256`
- `plugin_namespace`, `total_lowcode_types`, `workflow_root_types`
- `denominator_basis`, `runnable_scenarios`, `published_count`, `excluded_count`

Files:
- `pipeline/configs/denominators/cells.json` (exists, FULL_SOT)
- `pipeline/configs/denominators/words.json` (exists, PILOT_ALLOWED, workflow_root_types=NULL)
- `pipeline/configs/denominators/pdf.json` (exists, PILOT_ALLOWED)
- `pipeline/configs/denominators/{new_family}.json` (to be created in R6)
