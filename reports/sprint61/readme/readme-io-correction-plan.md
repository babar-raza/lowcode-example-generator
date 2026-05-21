# README I/O Correction Plan — Sprint 61

## Overview

41 of 42 examples have correction text ready to add. 1 example (`pdf-pdf-aconverter`)
has no local package and requires manual authoring.

## Counts

| Status | Count |
|--------|-------|
| Corrections with known I/O | 41 |
| No local package (manual) | 1 |
| Total | 42 |

## Machine-Readable Plan

Full per-example correction text is in `readme-io-correction-plan.json`.

Each entry contains:
- `scenario_id`
- `current_status` (before correction)
- `target_status` (after correction)
- `input_format`
- `output_format`
- `correction_text_to_add` (exact Markdown block to insert)

## Special Cases

| Scenario | Note |
|----------|------|
| `pdf-text-extractor` | Output is stdout (StringResult) |
| `email-converter` | Output is a directory of converted files |
| `words-mail-merger` | Input is data source — input format unknown |
| `words-report-builder` | Input is data source + template — input format unknown |
| `pdf-pdf-aconverter` | No local package — both formats unknown |

## Publication Gate

Pushing corrections requires `PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH`.
This is enforced by `check_readme_audit_gate` in `publish-pr` live mode (Phase 5).

**Status: AUDIT_COMPLETE — PUSH DEFERRED TO SPRINT 62**
