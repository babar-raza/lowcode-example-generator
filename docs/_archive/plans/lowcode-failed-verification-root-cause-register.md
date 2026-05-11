# LowCode Example Generator: Failed Verification Root-Cause Register

**Generated:** 2026-05-09
**Sprint:** R0 (Planning and Evidence Normalization)
**Status:** REGISTER_ACTIVE

---

## Root-Cause Taxonomy (31 categories)

### Generation Failures
- `WRONG_OPTIONS_CLASS` - LLM used abstract base class instead of concrete options class
- `FORBIDDEN_CORE_API_USAGE` - LLM used non-LowCode core API (e.g., TextAbsorber, File.Copy)
- `LLM_REPAIR_PROMPT_GAP` - Repair prompt lacked required constraints or reference code
- `HALLUCINATED_NAMESPACE` - LLM invented sub-namespace that does not exist
- `WRONG_METHOD_SIGNATURE` - LLM used incorrect method overload
- `WRONG_RESULT_ACCESS` - LLM used incorrect result property (e.g., .Value on StringResult)

### Build Failures
- `MISSING_USING_DIRECTIVE` - Required using statement missing
- `WRONG_TYPE_ARGUMENT` - Wrong type parameter for generic method
- `MISSING_NUGET_REFERENCE` - Required NuGet package not in project file
- `NAMESPACE_NOT_FOUND` - LLM referenced namespace that does not exist in package

### Runtime Failures
- `WRONG_INPUT_FORMAT` - Input file has wrong extension/format for the operation
- `MISSING_FIXTURE_FILE` - Required input fixture file does not exist
- `API_EXCEPTION` - Aspose API threw exception at runtime
- `OUTPUT_MISSING` - Expected output file not created
- `WRONG_OUTPUT_CONTENT` - Output created but content validation failed
- `UNKNOWN_RUNTIME_FAILURE` - Classification placeholder; requires investigation

### Fixture Gaps
- `MISSING_FIXTURE` - No fixture strategy exists for required input type
- `MISSING_PAIR_FIXTURE` - Operation requires 2 input files; pair fixture strategy not implemented
- `MISSING_TEMPLATE_FIXTURE` - Operation requires template document with field names
- `MISSING_ENUM_STRATEGY` - Enum values not discoverable from DllReflector catalog
- `WRONG_FIXTURE_SHAPE` - Fixture provides wrong structure for operation

### Classification Gaps
- `CLASSIFICATION_GAP` - Type not classified as WORKFLOW_ROOT, OPTIONS, RESULT, etc.
- `LOWCODE_API_REQUIRES_STATEFUL_CONTEXT` - Type requires stateful setup; cannot be standalone
- `LOWCODE_API_NOT_STANDALONE` - Abstract base class; cannot instantiate directly

### Governance Gaps
- `COMPLETION_QUEUE_GAP` - Planned example not tracked in completion queue
- `DENOMINATOR_GAP` - Denominator equation cannot be evaluated (missing field)
- `BACKLOG_SYNC_GAP` - Backlog entry not linked to taskcard
- `TASKCARD_SYNC_GAP` - Example not tracked by any open taskcard
- `POST_MERGE_VERIFICATION_GAP` - Published example not tracked in release-status
- `STALE_RECORD` - Historical failure entry superseded by later fix; not yet marked

### System Gaps
- `VALIDATOR_FALSE_POSITIVE` - Validator incorrectly classified a passing example as failure
- `PRODUCT_API_LIMITATION` - Operation requires capabilities not available in LowCode API

---

## Known Cases

### RESOLVED Cases

| Case ID | Family | Example | Category | Fix Applied | Evidence |
|---------|--------|---------|---------|------------|---------|
| RC-001 | pdf | pdf-optimizer | WRONG_OPTIONS_CLASS | R2: FORBIDDEN constraint injection in code_generator.py | repair-attempts.json |
| RC-002 | pdf | pdf-optimizer | FORBIDDEN_CORE_API_USAGE | R2: FORBIDDEN(DataSources sub-namespace) added | repair-attempts.json |
| RC-003 | pdf | pdf-optimizer | LLM_REPAIR_PROMPT_GAP | R2: Full REQUIRED+FORBIDDEN block added to repair prompt | docs/plans/r2-final-verification.md |
| RC-004 | pdf | pdf-splitter | WRONG_DATASOURCE_USAGE | Fixed: SplitOptions AddOutput uses FileDataSource not FileSaveTarget | backlog/pdf/examples-backlog.json |
| RC-006 | pdf | pdf-text-extractor | LLM_REPAIR_PROMPT_GAP | Fixed: Full C# reference block added to repair prompt | backlog/pdf/examples-backlog.json |

### UNRESOLVED Cases

| Case ID | Family | Example | Category | Required Fix | Owner Sprint |
|---------|--------|---------|---------|------------|-------------|
| RC-005 | pdf | pdf-splitter | STALE_RECORD | Mark runtime-failure-classifications.json entry as superseded | R6.5 |
| RC-007 | words | words-comparer, words-merger | MISSING_PAIR_FIXTURE | Implement pair-input fixture strategy in fixture_registry.py | R9 |
| RC-008 | words | words-mailmerger | MISSING_TEMPLATE_FIXTURE | Create template DOCX fixture with merge field names | R9 |
| RC-009 | words | words-splitter-split | MISSING_ENUM_STRATEGY | Implement SplitCriteria enum value discovery in scenario_planner | R9 |
| RC-010 | words | 8 Context classes | LOWCODE_API_REQUIRES_STATEFUL_CONTEXT | Run DllReflector classification; confirm NON_RUNNABLE formally | R7 (NEW-07) |
| RC-011 | pdf | 21 deferred WORKFLOW_ROOT | COMPLETION_QUEUE_GAP | Add all 21 types to completion queue with PLANNED_NOT_ATTEMPTED state | R6.5 |
| RC-012 | words | all 25 types | DENOMINATOR_GAP | Run FULL_SOT classification; set workflow_root_types in words.json | R7 (NEW-07) |
| RC-013 | all | n/a | BACKLOG_SYNC_GAP | Implement backlog-to-taskcard bridge | R8 (taskcard followup-backlog-to-taskcard-bridge) |
| RC-014 | all | n/a | TASKCARD_SYNC_GAP | Add 37 deferred examples (21 PDF + 16 Words) to completion queue | R6.5 |
| RC-015 | all | n/a | POST_MERGE_VERIFICATION_GAP | Fix release-status CLI default to include PDF | R7 (NEW-05) |

---

## Investigation Notes

### RC-005: PDF Splitter Stale Runtime Failure
- `runtime-failure-classifications.json` records: `"unknown_runtime_failure"` with detail `"Input file not found: input.docx"`
- This is confusing because Splitter processes PDF, not DOCX
- Root cause: Earlier test run (pre-pilot) used wrong fixture type (DOCX instead of PDF programmatic fixture)
- Current backlog entry for pdf-splitter: `resolved: true` (latest run in pilot-pdf-20260508-155520 shows Splitter PASS)
- Required action: Add `superseded: true, superseded_by: "pilot-pdf-20260508-155520"` to the runtime failure record
- Classification: STALE_RECORD (not UNKNOWN_RUNTIME_FAILURE)

### RC-010: Words Context Classes
- 8 Context classes assumed NON_RUNNABLE_REQUIRES_STATEFUL_CONTEXT
- Classification is heuristic (from readiness rank), not formal DllReflector proof
- Until NEW-07 runs, these remain in `NON_RUNNABLE_PENDING_CLASSIFICATION` state
- If classification reveals any are actually WORKFLOW_ROOT: immediate relaunch candidate
- Risk: If any are misclassified as non-runnable, coverage percentage is understated

### RC-011: PDF Phantom Planned Scenarios
- `pdf-type-role-classification.json` shows 25 WORKFLOW_ROOT types with pilot_deferred_reason for 21
- `workspace/queues/example-completion-queue.json` has only 4 PDF entries (all pilot types)
- 21 phantom planned scenarios: classified, deferred, but not tracked
- Required action (R6.5): Add each with state `PLANNED_NOT_ATTEMPTED`, link to taskcard `followup-pdf-remaining-candidate-classification`
