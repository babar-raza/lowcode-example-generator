# Skills Adoption Ledger

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Usage Log

| Skill | Lane | When | Outcome |
|-------|------|------|---------|
| products-plugin-page-harvest | LANE_B | 2026-06-04 | CRAWL_BLOCKED — products.aspose.net returns 403; sitemap fetched but only root URL in /en/ sitemap |
| plugin-source-code-harvest | LANE_C | 2026-06-04 | SUCCESS — 18/18 GitHub repos accessible; 53/65 plugins have code fetched; 12 NO_MATCH |
| non-lowcode-family-manual-analysis | LANE_D | 2026-06-04 | SUCCESS — all 18 families analyzed; implementation models assigned for all |
| plugin-code-registry-authoring | LANE_E | 2026-06-04 | SUCCESS — 65 registry entries created; schema validated; 0 errors |
| plugin-code-to-example-transformation | LANE_G | 2026-06-04 | PARTIAL — 3 snippet validations run against fetched code; build/run attempted |

---

## Skill Effectiveness

### products-plugin-page-harvest
- **Blocker encountered**: CRAWL_BLOCKED (403)
- **Adaptation**: Used GitHub repos as source authority instead
- **Skill improvement needed**: Add fallback to GitHub repo tree when page is 403-blocked

### plugin-source-code-harvest
- **Success rate**: 53/65 (81%)
- **Gap**: 12 plugins with no exact match; some fetched wrong files (App.xaml.cs, SceneHierarchyTree.cs)
- **Skill improvement needed**: Better keyword matching; check file content rather than just path

### non-lowcode-family-manual-analysis
- **Coverage**: 18/18 families fully analyzed
- **Implementation models found**: 6 distinct models (LOAD_SAVE_OPTIONS most common)
- **Skill improvement needed**: None for this sprint

### plugin-code-registry-authoring
- **Coverage**: 65/65 entries
- **Invariant pass rate**: 100% (0 errors)
- **Skill improvement needed**: Add DllReflector validation step to advance CODE_HARVESTED → REFLECTION_CONFIRMED

### plugin-code-to-example-transformation
- **Coverage**: Used for 3 snippet validations in Lane G
- **Outcomes**: See validation/official-snippet-validation-summary.json

---

## Sprint: lowcode-plugin-canonical-identity-wave7-20260605
## Date: 2026-06-05

## Usage Log

| Skill | Lane | When | Outcome |
|-------|------|------|---------|
| canonical-plugin-identity-and-aliasing | LANE_A,B,C,E | 2026-06-05 | NEW SKILL — authored this sprint; governs PIV rules, canonical slug enforcement, and alias documentation |
| plugin-example-factory-dry-run | LANE_C,G | 2026-06-05 | SUCCESS — 4 canonical BarCode packages (C) + 4 Wave 7 packages (G) built; all 8 PASS |
| plugin-code-registry-authoring | LANE_B | 2026-06-05 | SUCCESS — 14 YAML files updated with canonical_plugin_slug + identity_status; 61 entries enriched |

---

## Skill Effectiveness (Wave 7 Sprint)

### canonical-plugin-identity-and-aliasing (NEW)
- **Created**: This sprint to codify canonical slug enforcement
- **Applied to**: 72 registry entries, 48 dry-run packages, 14 PIV rules
- **Key insight**: products.aspose.net URL last segment is the canonical slug authority
- **BarCode correction**: 4 internal slugs replaced by canonical: generate-barcode→1d-barcode-writer etc.

### plugin-example-factory-dry-run
- **Success rate**: 8/8 PASS this sprint (4 BarCode + 4 Wave 7)
- **PSD fix**: Aspose.PSD requires explicit `Aspose.Drawing` PackageReference even though it's a transitive dep
- **OCR pattern**: OcrInput.Add(filePath) + DetectAreasMode.TABLE for table-to-text
