<!-- GENERATED — do not edit manually. -->
# PDF Fixture Generator Change Plan

**Date:** 2026-05-05
**Sprint:** PDF Fixture Strategy Review
**Phase:** Phase 5 — Generator Change Plan
**Status:** PLANNED — not implemented in this sprint

---

## Prerequisites Before Any Change

| Prerequisite | Status |
|---|---|
| `followup-pdf-fixture-strategy-review` | CLOSED this sprint |
| `followup-pdf-family-repo-target-mapping` | OPEN — must close first |
| `followup-pdf-controlled-pilot-enablement` | OPEN — requires human approval |

**Do not implement CHG-1 until all prerequisites are closed and human approval is given.**

---

## Changes Required

### CHG-1: Activate `pdf.yml` (CRITICAL — gated)

**File:** `pipeline/configs/families/pdf.yml`

```yaml
# BEFORE
status: discovery_only

# AFTER (only after human approval)
status: active
generation:
  allowed_types: [Merger, Splitter, Optimizer, TextExtractor]
  preferred_methods_per_type:
    Merger: Process
    Splitter: Process
    Optimizer: Process
    TextExtractor: Process
```

**Gate:** `followup-pdf-controlled-pilot-enablement` must be closed with explicit human approval.

---

### CHG-2: Update `pdf.yml` `template_hints`

**File:** `pipeline/configs/families/pdf.yml`

Add corrected API patterns to `template_hints`:

```yaml
template_hints:
  # ... existing lines ...
  output_creation_pattern: 'options.AddOutput(new FileDataSource("output.pdf"))'
  result_check_pattern: 'result.ResultCollection.Count > 0'
  text_extractor_result_pattern: '((StringResult)result.ResultCollection[0]).Text'
  splitter_output_note: 'Do not use format strings like {0} — use plain output.pdf'
```

---

### CHG-3: Planner Output Format Map

**File:** `src/plugin_examples/scenario_planner/planner.py`
**Function:** `_infer_output_format()`

Add PDF types:
```python
"Merger": ".pdf",
"Splitter": ".pdf",
"Optimizer": ".pdf",
"TextExtractor": None,  # No file output
```

Set `family_default=".pdf"` when PDF family is detected.

---

### CHG-4: Packet Builder — PDF Constraints

**File:** `src/plugin_examples/generator/packet_builder.py`

Add PDF-specific forbidden/required constraints:

**FORBIDDEN:**
- `new FileSaveTarget(...)` — use `new FileDataSource(...)` for output
- `result.IsSuccess` — use `result.ResultCollection.Count > 0`
- `result.OperationResult` — use `result.ResultCollection`
- Format strings in Splitter output (`output_{0}.pdf`) — use `output.pdf`

**REQUIRED:**
- `using Aspose.Pdf;` and `using Aspose.Pdf.LowCode;`
- For TextExtractor: `using Aspose.Pdf.Text;`
- Create input PDF programmatically before LowCode API call
- For TextExtractor: no `AddOutput()`, read from `ResultCollection[0] as StringResult`

---

### CHG-5: Code Validator — PDF Rules

**File:** `src/plugin_examples/generator/code_generator.py`
**Function:** `_validate_code()`

Add PDF-specific rules when `self.ctx.family == "pdf"`:
- Reject `new FileSaveTarget(` → `pdf_wrong_output_type`
- Reject `.IsSuccess` → `pdf_result_is_success_missing`
- Reject `.OperationResult` → `pdf_result_operation_result_missing`
- Reject static call pattern for plugin types → `pdf_static_pattern_forbidden`
- For TextExtractor: reject `AddOutput(` → `pdf_text_extractor_no_output`

---

### CHG-6: Runtime Feedback — PDF Patterns

**File:** `src/plugin_examples/scenario_planner/runtime_feedback.py`

Add actionable repair patterns:
- `cannot convert.*FileSaveTarget.*IDataSource` → `pdf_wrong_output_type` (actionable, repair: use FileDataSource)
- `does not contain.*IsSuccess` → `pdf_result_is_success_missing` (actionable)
- `does not contain.*OperationResult` → `pdf_result_operation_result_missing` (actionable)

---

### CHG-7: Output Validator — PDF Validation

**File:** `src/plugin_examples/verifier_bridge/output_validator.py`

Add `expected-output.json` schemas for PDF pilot types:

| Type | Validation |
|---|---|
| Merger | `file_exists: true`, `pdf_header: true`, `min_bytes: 1000` |
| Splitter | `file_exists: true`, `pdf_header: true`, `min_bytes: 1000` |
| Optimizer | `file_exists: true`, `pdf_header: true`, `min_bytes: 1000` |
| TextExtractor | `console_contains: "Extracted:"`, `no_file_output: true` |

---

## Implementation Order

1. CHG-3 — planner output format
2. CHG-4 — packet builder constraints
3. CHG-5 — code validator rules
4. CHG-6 — runtime feedback patterns
5. CHG-7 — output validator rules
6. CHG-2 — `pdf.yml` template hints
7. *(await `followup-pdf-family-repo-target-mapping` closure)*
8. CHG-1 — activate `pdf.yml` with human approval
