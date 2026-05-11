# LowCode Example Generator: Risk and Contradiction Register

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** REGISTER_COMPLETE

---

## Contradiction Register

| ID | Severity | Claim A | Claim B | Verdict | Action | Sprint | Blocking |
|----|----------|---------|---------|---------|--------|--------|---------|
| C1 | ~~HIGH~~ RESOLVED | Cells PR#1 merge SHA is f6e5515c (memory) | No local cells-pr1-merge-result.json | RESOLVED: `cells-post-merge-clean-checkout-validation.json` confirms SHA `f6e5515c070184e4b08a2cff647220bea1113b08` | No action needed | R0 | NO |
| C2 | ~~HIGH~~ RESOLVED | Words PR#1 merge SHA is b66fb43 (memory) | No local words-pr1-merge-result.json | RESOLVED: `words-post-merge-clean-checkout-validation.json` confirms SHA `b66fb43023d4d1af7162270ac9d3ef3ef881451f` | No action needed | R0 | NO |
| C3 | HIGH | release-status.json covers all active families | release-status.json families_checked=["cells","words"] only | B is true; PDF excluded by CLI defaults | Fix `__main__.py` line 269-270; taskcard NEW-05 | R7 | YES for PDF release tracking |
| C4 | MEDIUM | email.yml enabled=true | email.yml is in disabled/ directory, not scanned | Both true but contradictory intent; config is inert | Decide: move to active dir or fix enabled flag | R2 | NO (currently inert) |
| C5 | MEDIUM | slides.yml enabled=true | slides.yml is in disabled/ directory, not scanned | Both true but contradictory intent; config is inert | Same resolution path as C4 | R2 | NO (currently inert) |
| C6 | MEDIUM | monthly-package-refresh.yml covers all families | Workflow defaults to cells only | B is true; words and PDF not refreshed monthly | Extend workflow to cover all active families | R14 | NO (monthly only) |
| C7 | MEDIUM | Words has 9 workflow_root candidates (readiness rank) | Words denominator shows workflow_root_types: null | Both can be true: rank uses heuristic; denominator requires formal classification | Run FULL_SOT classification for Words | R7/R9 | YES for FULL_SOT |
| C8 | LOW | 76 taskcards, 15 open (memory) | 77 taskcards, 16 open (source file) | B is authoritative; memory was stale | Updated | R0 | NO |
| C9 | LOW | "No examples generated outside Cells" | 12 Words + 2 Email examples in workspace/runs/ | B is true; audit itself marked claim as MISLEADING | Document as historical; not production artifacts | R0 | NO |

---

## Risk Register

| Risk ID | Category | Description | Likelihood | Impact | Mitigation | Owner Sprint |
|---------|----------|-------------|------------|--------|------------|-------------|
| RK-001 | CREDENTIAL | GITHUB_TOKEN may lack Contents:Write for aspose-pdf-net | MEDIUM | HIGH | Probe permissions before PR creation; stop on 403 | R8 |
| RK-002 | LLM | PDF Optimizer 2nd consecutive PASS may not be achieved non-deterministically | MEDIUM | MEDIUM | R2 constraint injection reduces risk; max 3 attempts | R8 |
| RK-003 | DISCOVERY | Group C families may have no LowCode namespaces at all | HIGH | MEDIUM | Each discovery run classifies as CONFIRMED_NO_LOWCODE if namespace absent | R3 |
| RK-004 | FIXTURE | Words Comparer/Merger blocked by missing pair-fixture strategy | HIGH | MEDIUM | R9 prerequisite: implement pair-fixture before relaunch | R9 |
| RK-005 | FIXTURE | PDF FormEditor/FormFlattener/FormImporter blocked by missing form-fields PDF fixture | HIGH | MEDIUM | R10 prerequisite: implement form-fields fixture | R10 |
| RK-006 | CLASSIFICATION | 16 Words types labeled NON_RUNNABLE but not formally classified via DllReflector | MEDIUM | MEDIUM | NEW-07: run FULL_SOT classification | R7 |
| RK-007 | COMPLETION_QUEUE | 21 PDF deferred WORKFLOW_ROOT types and 16 Words deferred types not in completion queue | HIGH | HIGH | R6.5: add all missing entries with PLANNED_NOT_ATTEMPTED state | R6.5 |
| RK-008 | DENOMINATOR | Words workflow_root_types=NULL; FULL_SOT equation cannot be evaluated | HIGH | MEDIUM | NEW-07: classify all 25 Words types | R7 |
| RK-009 | NETWORK | NuGet download failures for Group C families (network, unlisted, or .NET-only) | MEDIUM | MEDIUM | Document failures per family; continue with other families | R3 |
| RK-010 | SCOPE | Some Aspose products may be Java-only with no .NET release | MEDIUM | LOW | Verify NuGet availability before YAML creation; document as OUT_OF_SCOPE | R1 |
| RK-011 | REVIEWER | EXAMPLE_REVIEWER_PATH not set; new family examples will skip reviewer gate | HIGH | MEDIUM | Set EXAMPLE_REVIEWER_PATH before R11 generation waves | R11 |
| RK-012 | STALE_RECORD | PDF Splitter runtime failure "input.docx" is stale; RC-005 not formally superseded | LOW | LOW | R6.5: document superseded status in root-cause register | R6.5 |

---

## Root-Cause Register (Current Known Cases)

| Case ID | Family | Example ID | Root Cause | Description | Resolved | Resolution Evidence |
|---------|--------|-----------|-----------|-------------|----------|-------------------|
| RC-001 | pdf | pdf-optimizer | WRONG_OPTIONS_CLASS | LLM used abstract PluginOptions instead of concrete OptimizeOptions | YES | backlog/pdf/examples-backlog.json, R2 fix |
| RC-002 | pdf | pdf-optimizer | FORBIDDEN_CORE_API_USAGE | LLM hallucinated Aspose.Pdf.LowCode.DataSources sub-namespace | YES | repair-attempts.json, code_generator.py FORBIDDEN constraints |
| RC-003 | pdf | pdf-optimizer | LLM_REPAIR_PROMPT_GAP | Repair prompt lacked FORBIDDEN constraint list | YES | docs/plans/r2-final-verification.md |
| RC-004 | pdf | pdf-splitter | WRONG_DATASOURCE_USAGE | SplitOptions used FileSaveTarget instead of FileDataSource for AddOutput | YES | backlog/pdf/examples-backlog.json |
| RC-005 | pdf | pdf-splitter | STALE_RECORD | Runtime failure "input.docx" is stale record from earlier wrong-fixture run | PARTIAL | runtime-failure-classifications.json (needs superseded marker) |
| RC-006 | pdf | pdf-text-extractor | LLM_REPAIR_PROMPT_GAP | Repair prompt lacked full C# reference block | YES | backlog/pdf/examples-backlog.json |
| RC-007 | words | words-comparer, words-merger | MISSING_PAIR_FIXTURE | Comparer and Merger require 2 input docs; no paired fixture strategy | NO | backlog/words/excluded-scenarios.json |
| RC-008 | words | words-mailmerger | MISSING_TEMPLATE_FIXTURE | MailMerger requires template DOCX with merge field names | NO | backlog/words/excluded-scenarios.json |
| RC-009 | words | words-splitter-split | MISSING_ENUM_STRATEGY | SplitCriteria enum values not discoverable from DllReflector catalog | NO | backlog/words/excluded-scenarios.json |
| RC-010 | words | Context classes (8) | LOWCODE_API_REQUIRES_STATEFUL_CONTEXT | Context classes assumed non-runnable but not formally proven | NO | backlog/words/excluded-scenarios.json |
| RC-011 | pdf | 21 deferred WORKFLOW_ROOT types | COMPLETION_QUEUE_GAP | Types classified and deferred but no completion queue entry | NO | pdf-type-role-classification.json |
| RC-012 | words | 25 types | DENOMINATOR_GAP | workflow_root_types=NULL in words denominator | NO | pipeline/configs/denominators/words.json |
| RC-013 | all | n/a | BACKLOG_SYNC_GAP | Backlog-to-taskcard bridge not implemented | NO | followup-backlog-to-taskcard-bridge (OPEN) |
| RC-014 | all | n/a | TASKCARD_SYNC_GAP | Completion queue has only 17 entries; 37 deferred types not in queue | NO | workspace/queues/example-completion-queue.json |
| RC-015 | all | n/a | POST_MERGE_VERIFICATION_GAP | Release-status defaults exclude PDF | NO | __main__.py lines 269-270 |
