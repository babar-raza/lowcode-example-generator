# Package Authority Depth Summary — Sprint 60 Phase 6

**Sprint:** sprint60-sprint59-closure-repair-destination-readme-gate-20260521
**Date:** 2026-05-21

---

## Format Authority (inherited from Sprint 59 — no change)

| Metric | Value |
|--------|-------|
| Total types | 42 |
| Unknown input formats | 0 |
| Authority source | `format_contract` (100%) |
| Confidence | `high` |
| Sprint 59 proof | Valid — no format contract changes since Sprint 59 |

All 42 scenarios have `selected_input_format` resolved from `format_contract` via
`workspace/verification/latest/families/{family}/scenario-input-format-map.json`.

**Verdict:** `IO_AUTHORITY_COMPLETE_42_42_ZERO_UNKNOWN`

---

## Destination ID Authority (Sprint 60 new — closes 4 Sprint 59 gaps)

Sprint 59 had 3 `PRESENT_NO_AUTHORITY` destination audit entries. The root cause was a
scenario_id construction defect in the Sprint 59 audit script. Sprint 60 resolves this
with the `DestinationIdMapper` module.

### Source Module

`src/plugin_examples/publisher/destination_id_mapper.py`

### 4 Gaps Closed

#### Gap 1: `diagram-diagram-converter` (double-prefix bug)

- Sprint 59 constructed: `diagram-diagram-diagram-converter` (triple "diagram")
- Canonical: `diagram-diagram-converter`
- Root cause: Sprint 59 prepended `diagram-` to the repo dir name `diagram-diagram-converter`,
  which already encoded the family prefix. Result: triple prefix.
- Fix: `FAMILIES_WITH_PREFIXED_DIRS = frozenset({"diagram"})` — diagram dir names ARE the
  full scenario_id.
- Note: `diagram-diagram-converter` is NOT a double-prefix bug — DiagramConverter class
  is intentionally in the `diagram` family, making `diagram-diagram-converter` the canonical ID.

#### Gap 2: `diagram-pdf-converter` (double-prefix bug)

- Sprint 59 constructed: `diagram-diagram-pdf-converter`
- Canonical: `diagram-pdf-converter`
- Same fix as Gap 1.

#### Gap 3: `pdf-pdf-aconverter` (naming convention mismatch)

- Repo dir: `pdfa-converter`
- Sprint 59 constructed: `pdf-pdfa-converter`
- Canonical: `pdf-pdf-aconverter` (class name: `PdfAConverter`)
- Fix: `REPO_DIR_ALIAS_MAP = {"pdf/pdfa-converter": "pdf-pdf-aconverter"}`

#### Gap 4: `pdf-image-extractor` (validator too literal)

- Sprint 59 audit verdict: `output_format_in_programcs: false`
- Root cause: ImageExtractor writes PNG images to `ResultCollection` (in-memory),
  not to a named file path. Sprint 59 audit checked for a literal `.png` extension in
  `Program.cs`.
- Fix: `RESULT_COLLECTION_OUTPUT_APIS = frozenset({"pdf-image-extractor", "pdf-text-extractor"})`
  — these APIs prove output format via API contract, not file extension.
- Sprint 60 audit verdict: `MATCH_WITH_POLICY`

### Tests

`tests/unit/test_destination_id_mapper.py` — 23 tests, all passing.

Key tests:
- `test_diagram_no_double_prefix_for_diagram_converter` — verifies canonical ID is preserved
- `test_pdfa_converter_alias` — verifies pdfa-converter → pdf-pdf-aconverter
- `test_image_extractor_result_collection_policy` — verifies RESULT_COLLECTION_OUTPUT_APIS
- `test_is_double_family_prefix_not_triggered_for_canonical_diagram_converter` — verifies
  `diagram-diagram-converter` is NOT flagged as a bug (only triple prefix is)

---

## Per-Family Summary

| Family | Version | Scenarios | Format Authority | Destination ID Policy | Gaps S59 | Gaps Closed S60 |
|--------|---------|-----------|-----------------|----------------------|----------|----------------|
| Cells | 26.5.1 | 9 | 9/9 high | standard | 0 | 0 |
| Words | 26.5.0 | 8 | 8/8 high | standard | 0 | 0 |
| PDF | 26.5.0 | 19 | 19/19 high | standard+alias+policy | 2 | 2 |
| Diagram | 26.5.0 | 2 | 2/2 high | prefixed_dirs | 2 | 2 |
| Email | 26.4.0 | 1 | 1/1 high | standard | 0 | 0 |
| Slides | 26.5.0 | 3 | 3/3 high | standard | 0 | 0 |
| **Total** | | **42** | **42/42** | | **4** | **4** |

---

## Verdict

`IO_AND_DESTINATION_AUTHORITY_COMPLETE`

- Format authority: 42/42 from `format_contract` (inherited, unchanged)
- Destination ID authority: 42/42 (4 gaps closed by `DestinationIdMapper`)
- Content audit: `CONTENT_AUDITED_42_42_AUTHORITY_MAPPED`
