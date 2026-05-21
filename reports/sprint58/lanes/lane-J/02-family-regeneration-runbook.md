# Process: Family Regeneration Runbook

**Process ID:** LANE-J-02
**Version:** Sprint 58
**Date:** 2026-05-21

---

## Overview

This runbook describes how to regenerate all 42 examples across 6 families and capture per-example evidence.

---

## Prerequisites

1. `PYTHONPATH=src` environment set
2. `.venv/Scripts/python.exe` available
3. `GPT_OSS_ENDPOINT`, `GPT_OSS_API_KEY`, `GPT_OSS_MODEL` set
4. `GH_TOKEN` set (classic PAT, repo scope)
5. Per-family configs validated (no instruction-style per_type_constraints)

---

## Per-Family Generation Commands

```bash
# Cells (9 examples)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family cells --require-validation --promote-latest

# Words (8 examples)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family words --require-validation --promote-latest

# PDF (19 examples — includes PdfAConverter)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family pdf --require-validation --promote-latest

# Diagram (2 examples)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family diagram --require-validation --promote-latest

# Email (1 example)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family email --require-validation --promote-latest

# Slides (3 examples)
PYTHONPATH=src .venv/Scripts/python.exe -m plugin_examples run \
  --family slides --require-validation --promote-latest
```

---

## Per-Example Evidence Capture

After generation, build the per-example directory from lifecycle records:

```
workspace/verification/latest/families/{family}/example-lifecycle-records.json
```

For each example, record 15 fields:
- `scenario_id`, `family`, `type_name`
- `generation_status`, `build_status`, `run_status` (values: `"passed"` | `"failed"` | `"skipped"`)
- `gate_results`, `failure_reasons`, `repair_attempts`
- `run_id`, `generated_at`, `gate_verdict`, `notes`

Write to: `reports/sprint58/regeneration/per-example/{family}-{type_name}.json`

---

## Acceptance Criteria

- All 42 examples: `generation_status=passed`, `build_status=passed`, `run_status=passed`
- `gate_verdict=EXAMPLE_READY_FOR_PR_DRY_RUN` for all 42
- `full-regeneration-ledger.json` shows `SPRINT58_REGENERATION_42_OF_42_PASS`
- Per-example directory: exactly 42 files

---

## Known Type Constraints

- **PdfAConverter**: REQUIRED `using Aspose.Pdf.Text;` — added to pdf.yml in Sprint 58
- **SpreadsheetConverter**: canonical_output_format = ".csv" (cross-format)
- **PDF plugins**: instance-method `new {Type}().Process(options)` — NOT static
- **TextExtractor**: no AddOutput(), read from ResultCollection[0]
