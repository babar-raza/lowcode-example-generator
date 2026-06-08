# Family Wave Roadmap — Non-LowCode Plugin Universe Bootstrap

Generated: 2026-06-04T00:00:00Z
Report Root: `reports/lowcode-non-lowcode-plugin-universe-20260604/`

---

## Wave Classification Criteria

| wave | criteria | action |
|------|----------|--------|
| WAVE-1 | Package available + reflection completed + PROBE_CONFIRMED | Ready for example generation |
| WAVE-2 | Package available + reflection completed + PROBE_FAILED or PROBE_CANDIDATE | Needs probe repair or AI mapping |
| WAVE-3 | Package available + reflection attempted + BLOCKED (license/API) | Needs external unblocking |
| WAVE-4 | Package available but reflection deferred or complex | Future sprint |

---

## Wave 1 — Probe-Confirmed Families (example generation ready)

These families have completed the full pipeline: reflection → heuristic → probe → PROBE_CONFIRMED.

| family | package_id | version | primary_type | primary_method | probe_verdict |
|--------|-----------|---------|-------------|---------------|--------------|
| barcode | Aspose.BarCode | 26.5.0 | BarcodeGenerator | Save | PROBE_CONFIRMED |
| imaging | Aspose.Imaging | 26.6.0 | Image | Save | PROBE_CONFIRMED |
| zip | Aspose.ZIP | 26.5.0 | Archive | Save | PROBE_CONFIRMED |

### Wave 1 Next Actions

- Generate multiple example packages per plugin operation (generate-barcode, save-image, create-zip)
- Write family README.md for products.aspose.net plugin pages
- Bootstrap `READY_FOR_EXAMPLE_GENERATION` entries in barcode.yaml, imaging.yaml, zip.yaml
- Add per-plugin entries to plugin-level registry (barcode: 5 ops, imaging: 8 ops, zip: 4 ops)

### Wave 1 Estimated Output

| family | plugins | examples | READMEs |
|--------|---------|---------|--------|
| barcode | 5 | 5–10 | 5 |
| imaging | 8 | 8–16 | 8 |
| zip | 4 | 4–8 | 4 |
| **total** | **17** | **17–34** | **17** |

---

## Wave 2 — Reflection-Complete / Probe-Needed Families

Reflection wave completed. API types confirmed. Probes needed.

| family | package_id | priority | primary_type_candidates | expected_probe_verdict |
|--------|-----------|----------|------------------------|----------------------|
| html | Aspose.HTML | HIGH | HtmlConverter, Document | PROBE_CANDIDATE → probe needed |
| tasks | Aspose.Tasks | HIGH | Project, TasksBaseObject | PROBE_CANDIDATE → probe needed |
| cad | Aspose.CAD | HIGH | Image (CAD.Image) | PROBE_CANDIDATE → probe needed |
| ocr | Aspose.OCR | HIGH | AsposeOcr | PROBE_CANDIDATE → probe needed |
| psd | Aspose.PSD | MEDIUM | Image (PSD.Image) | PROBE_CANDIDATE → probe needed |
| svg | Aspose.SVG | MEDIUM | SVGDocument | PROBE_CANDIDATE → probe needed |
| page | Aspose.Page | MEDIUM | PsDocument, XpsDocument | PROBE_CANDIDATE → probe needed |
| note | Aspose.Note | MEDIUM | Document (Note) | PROBE_CANDIDATE → probe needed |
| drawing | Aspose.Drawing | LOW | Bitmap, Graphics | PROBE_CANDIDATE → probe needed |
| font | Aspose.Font | LOW | Font (base class) | PROBE_CANDIDATE → probe needed |

### Wave 2 Next Sprint Execution Plan

For each Wave 2 family:
1. Run heuristic matcher → identify PROBE_CANDIDATE type + method
2. Generate probe (PR-01 through PR-10 enforced)
3. Run restore → build → run → validate
4. Record verdict (any of 12 authorized status values)
5. Populate plugin-level registry entry
6. If PROBE_CONFIRMED → promote to Wave 1 status

---

## Wave 3 — Blocked / Complex Families

| family | package_id | expected_blocker | action |
|--------|-----------|-----------------|--------|
| threed | Aspose.3D | PROBE_BLOCKED_LICENSE or complex rendering | Run probe; classify verdict |
| gis | Aspose.GIS | PROBE_BLOCKED_API (geospatial rendering) | Run probe; classify verdict |
| omr | Aspose.OMR | PROBE_BLOCKED_LICENSE | Run probe with known OMR template |
| finance | Aspose.Finance | PROBE_BLOCKED_LICENSE or schema-heavy | Run probe with XBRL sample |
| tex | Aspose.TeX | Rendering complexity | Run probe with minimal .tex input |

### Wave 3 Strategy

- License-blocked families: document taxonomy PROBE_FAILED_LICENSE; add to blocked registry entries
- API-complex families: attempt with minimal valid input first; document fallback approaches
- All failures must be classified (no PROBE_UNKNOWN)

---

## Wave 4 — Deferred Families

| family | reason | dependency |
|--------|--------|-----------|
| epub | Shares Aspose.HTML package; needs HTML Wave 2 results | After html PROBE_CONFIRMED |
| medical | New package (v26.3.0); API surface needs investigation | After Aspose.Medical DllReflector |

---

## Wave Execution Schedule

| wave | sprint | trigger |
|------|--------|--------|
| Wave 1 | Current (20260604) | Already PROBE_CONFIRMED |
| Wave 2 probes | Next sprint (20260605+) | After reflection wave inventory complete |
| Wave 2 examples | Next sprint (20260605+) | After PROBE_CONFIRMED verdicts |
| Wave 3 probes | Future sprint | After Wave 2 complete |
| Wave 4 | Future sprint | After Wave 3 + medical/epub package availability |

---

## Invariants (all waves)

- No publication PRs without merge approval
- No format-authority mutations (discovery-only status for all new families)
- No mutations to 6 LowCode family YAMLs
- All probes must capture restore + build + run logs
- All failures must be classified with failure_taxonomy
- VERIFIED_PUBLISHABLE requires probe_evidence field
- AI outputs enter as AI_DRAFT only; HallucinationValidator required
