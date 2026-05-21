# Destination Program.cs I/O Audit Policy — Sprint 61 Phase 6

## Defect Closed

**SD60-05:** `content-audit-repaired.json` recorded `input_format_in_programcs=null`
for all 42 examples. Sprint 60 never parsed Program.cs — the I/O classification
existed structurally but was never populated with real data.

---

## Policy: Program.cs I/O Classification

Each example's Program.cs **MUST** be parsed to extract:

1. **Input format**: File extension from `"input.EXT"` string literal
2. **Output format**: File extension from `"output.EXT"` string literal,
   or `stdout` (StringResult), or `directory` (Directory.Create)

Classification is stored as `input_format_in_programcs` and
`output_format_in_programcs` in the destination audit record.

### Classification Statuses

| Status | Meaning |
|--------|---------|
| `BOTH_KNOWN` | Both input and output formats extracted from Program.cs |
| `INPUT_KNOWN_OUTPUT_SPECIAL` | Input known; output is stdout or directory |
| `OUTPUT_ONLY_KNOWN` | Input uses data source or runtime input; output format known |
| `NEITHER_KNOWN` | No local package or completely unresolved |

---

## Before State (Sprint 61 Audit — SD60-05)

All 42 records: `input_format_in_programcs=null`, `io_classification=NULL_NOT_PARSED`

**Root cause:** Program.cs parsing was never implemented. The content-audit-repaired.json
field existed as a placeholder but was never populated.

---

## After State (Post Repair)

| Classification | Count |
|---------------|-------|
| BOTH_KNOWN | 37 |
| INPUT_KNOWN_OUTPUT_SPECIAL | 1 (email-converter: output is directory) |
| OUTPUT_ONLY_KNOWN | 3 (words-mail-merger, words-report-builder, pdf-text-extractor) |
| NEITHER_KNOWN | 1 (pdf-pdf-aconverter: no local package) |

**37/42 have both formats known from Program.cs.**

The 3 OUTPUT_ONLY_KNOWN cases use data sources or runtime-generated inputs
and have no `"input.EXT"` literal in Program.cs.

---

## Extraction Patterns

```python
# Input format
re.search(r'[""]input(\\.\\w+)[""]', content, re.IGNORECASE)

# Output format
re.search(r'[""]output(\\.\\w+)[""]', content, re.IGNORECASE)

# Special cases
if "StringResult" in content or "GetString" in content:
    output_ext = "stdout"
if re.search(r'Directory\\.Create|CreateDirectory', content):
    output_ext = "directory"
```

---

## Audit Evidence Files

| File | Description |
|------|-------------|
| `programcs-io-audit-before.json` | Before: 42/42 NULL_NOT_PARSED (SD60-05) |
| `programcs-io-audit-after.json` | After: 37/42 BOTH_KNOWN, 5 special cases |
| `build_phase6_artifacts.py` | Build script |
