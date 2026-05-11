# LowCode Example Generator: All-Family Roadmap

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Supersedes:** docs/plans/full-completion-roadmap.md
**Status:** ROADMAP_ACTIVE

---

## Execution Phases

### R0: Plan Amendment and Evidence Normalization [COMPLETE]
- Mode: planning + artifact production
- Objective: Produce all R0 artifacts; resolve contradictions; publish execution handoff
- Families: All (analysis only)
- Gate: All artifacts written; contradiction register complete; taskcards proposed

### R1: Product Candidate Inventory and YAML Creation [PENDING - parallel with R2, R7, R8]
- Mode: research + YAML creation (safe write)
- Objective: Create discovery_only YAML configs for all Group C candidate families
- Families: 20 Group C candidates
- Pre-gate: R0 complete
- Actions: Verify NuGet package IDs; create pipeline/configs/families/{family}.yml
- Gate: Every Aspose .NET family has YAML or OUT_OF_SCOPE documentation
- Taskcard: NEW-01

### R2: Email and Slides Blocker Investigation [PENDING - parallel with R1, R8]
- Mode: investigation + config fixes
- Objective: Resolve Email and Slides discovery blockers
- Families: email, slides
- Pre-gate: R0 complete
- Actions: Move configs to active path; fix Slides DLL name; run discovery
- Gate: Each has definitive status: LOWCODE_CONFIRMED, NO_LOWCODE, or BLOCKED with root cause
- Taskcards: NEW-02, NEW-03

### R3: All-Family Discovery [PENDING - requires R1 + R2]
- Mode: read-only against NuGet + reflection
- Objective: Run discovery for all candidate families
- Families: All Group C + unblocked Email/Slides
- Command: `--all-families --promote-latest`
- Gate: Every family has exactly one discovery result
- Produces: all-family-lowcode-discovery.json (updated)

### R4: Source-of-Truth Proofs for Newly Confirmed Families [PENDING - requires R3]
- Mode: reflection, catalog building
- Objective: Create source-of-truth proof for each LowCode-confirmed family
- Gate: Each confirmed family has api_catalog_sha256, total_lowcode_types >= 1, namespace confirmed

### R5: Type-Role Classification for All LowCode-Confirmed Families [PENDING - requires R4]
- Mode: classification via tier-1 dry-run
- Objective: Classify every LowCode type as WORKFLOW_ROOT, OPTIONS, RESULT, etc.
- Gate: Every confirmed family has plugin-type-role-classification.json
- Includes: Words 25-type full classification (NEW-07), PDF 21 unclassified WORKFLOW_ROOT types

### R6: All-Family Denominator and No-Silent-Drop Governance [PENDING - requires R5]
- Mode: denominator files, schema validation
- Objective: Create denominator JSON for all LowCode-confirmed families
- Gate: Denominator equation holds for every family
- Produces: pipeline/configs/denominators/{family}.json per new family

### R6.5: Dropped Planned Example Verification Failure Audit [PENDING - requires R6]
- Mode: audit + evidence normalization
- Objective: Find every planned example that failed or was dropped; reconcile all tracking
- Families: All (Cells, Words, PDF, new)
- Actions:
  1. Add 21 PDF deferred WORKFLOW_ROOT types to completion queue
  2. Add Words deferred types with proper states
  3. Verify and supersede RC-005 stale record
  4. Verify denominator equation holds (9-term formula)
  5. Generate 3 healing artifacts
- Gate: Every planned runnable example has exactly one state; completion queue 100% coverage
- Taskcards: TASK-NEW-08 through TASK-NEW-18

### R7: Existing Family Reconciliation [PENDING - can run after R0, parallel with R1-R6]
- Mode: evidence normalization + CLI fixes
- Objective: Normalize Cells/Words/PDF against all-family model; fix CLI defaults
- Actions:
  1. Fix release-status CLI default to include PDF (NEW-05)
  2. Words workflow_root classification (NEW-07)
  3. Verify completion queue PDF entries
- Gate: release-status covers cells/words/pdf; Words denominator non-null

### R8: PDF PR-Ready Publication Unblocker [PENDING - can run after R0, parallel with R1-R7]
- Mode: publication (live, gated)
- Objective: Fix GitHub token; create PDF PR#3 live; merge; run Optimizer 2nd PASS
- Pre-gate: GITHUB_TOKEN Contents:Write + APPROVE_LIVE_PR set
- Status: BLOCKED_APPROVE_LIVE_PR_NOT_SET
- Actions: Probe permissions → PR#3 live → merge PR#3 → Optimizer 2nd PASS → PR#4
- Gate: PR#3 and PR#4 merged; PDF published_count=4
- Taskcard: followup-pdf-pr3-review-and-merge

### R9: Words Full Coverage Expansion [PENDING - requires R7]
- Mode: config + fixture + generation
- Objective: Expand Words beyond 4 pilot types
- Pre-gate: Words classification (NEW-07) complete; 5 expansion taskcards resolved
- Gate: All newly added Words types pass build+run+reviewer

### R10: PDF Full Workflow-Root Expansion [PENDING - requires R8 + R5]
- Mode: classification + config + generation
- Objective: Generate examples for 21 remaining PDF WORKFLOW_ROOT types
- Gate: All newly classified runnable PDF types have published examples or are backlogged

### R11: New LowCode Family Generation Waves [PENDING - requires R6 + R3]
- Mode: generation + validation + publication
- Objective: Generate, validate, publish for all newly discovered LowCode families
- Wave A: Families with LowCode + at least 1 runnable workflow root
- Wave B: Families with LowCode but 0 runnable roots → document
- Wave C: No LowCode found → document as CONFIRMED_NO_LOWCODE

### R12: Backlog Relaunch [PENDING - requires R11]
- Mode: system repair + relaunch
- Objective: Relaunch every backlogged example after root-cause fixes

### R12.5: Verification-Failure Healing and Relaunch [PENDING - requires R12]
- Mode: source repair + controlled relaunch
- Objective: Fix root causes; relaunch failed examples; close or escalate
- Gate: Every failed example has: RELAUNCH_PASSED, BLOCKED with evidence, or DROPPED_WITH_EVIDENCE

### R13: All-Family Post-Merge Verification and README Validation [PENDING - requires R12.5]
- Mode: verification
- Gate: All published examples pass post-merge checkout; all READMEs correct

### R14: Monthly Automation Extension [PENDING - requires R11]
- Mode: CI workflow extension
- Objective: Monthly workflow covers all active families
- Taskcard: NEW-04

### R15: Final All-Family Completion Audit [PENDING - requires all]
- Mode: verification
- Gate (ALL must hold):
  1. Denominator equation holds for every LowCode-confirmed family
  2. Zero families remain DISCOVERY_NOT_ATTEMPTED without OUT_OF_SCOPE documentation
  3. Zero planned runnable examples unaccounted for
  4. Zero published claims without post-merge verification
  5. All backlogged items have root cause, repair plan, owner sprint, or BLOCKED status
  6. release-status covers all active families
  7. Monthly CI covers all active families
- Evidence: lowcode-final-investigation-verdict.json with verdict ROADMAP_COMPLETE

---

## Parallelism Classification

| Sprint | Can Run In Parallel With | Must Wait For |
|--------|--------------------------|---------------|
| R0 | (first) | - |
| R1 | R2, R7, R8 | R0 |
| R2 | R1, R7, R8 | R0 |
| R3 | - | R1 + R2 |
| R4 | - | R3 |
| R5 | - | R4 |
| R6 | - | R5 |
| R6.5 | - | R6 |
| R7 | R1, R2, R3, R4, R5, R6, R8 | R0 |
| R8 | R1, R2, R3, R4, R5, R6, R7 | R0 + live credential gate |
| R9 | R10, R11 | R7 |
| R10 | R9, R11 | R8 + R5 |
| R11 | - | R6 + R3 |
| R12 | - | R11 |
| R12.5 | - | R12 + R6.5 |
| R13 | - | R12.5 |
| R14 | - | R11 |
| R15 | - | ALL |
