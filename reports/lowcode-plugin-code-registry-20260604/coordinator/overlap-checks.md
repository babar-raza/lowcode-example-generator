# Overlap Checks — Plugin-Code Registry Sprint

## Sprint: lowcode-plugin-code-registry-20260604

## Lane Boundary Checks

| Lane | Write Paths | Cross-Lane Risk | Status |
|------|-------------|-----------------|--------|
| LANE_0 | reports/.../coordinator/ | None | CLEAR |
| LANE_A | reports/.../qa/ | None | CLEAR |
| LANE_B | reports/.../crawl/, .local/catalog-cache/ | None | CLEAR |
| LANE_C | reports/.../code-harvest/, .local/code-cache/ | None | CLEAR |
| LANE_D | reports/.../manual-analysis/ | None | CLEAR |
| LANE_E | pipeline/plugin-code-registry/, reports/.../registry/ | Must not write to plugin-capability-registry | CLEAR |
| LANE_F | skills/ | None | CLEAR |
| LANE_G | reports/.../validation/ | None | CLEAR |
| LANE_H | reports/.../transformation/ | None | CLEAR |
| LANE_I | reports/.../validators/ | None | CLEAR |
| LANE_J | reports/.../qa/ | Shares qa/ with LANE_A; different files | CLEAR |
| LANE_K | .local/evidence-bundles/ | None | CLEAR |

## Protected File Checks

All six LowCode family YAMLs and format-authority must show empty diffs throughout sprint:
- pipeline/configs/families/cells.yml
- pipeline/configs/families/words.yml
- pipeline/configs/families/pdf.yml
- pipeline/configs/families/slides.yml
- pipeline/configs/families/email.yml
- pipeline/configs/families/diagram.yml
- pipeline/format-authority/manifest.json
- pipeline/format-authority/contracts/ (entire directory)

## New Registry vs Old Registry

- `pipeline/plugin-capability-registry/` = PRIOR SPRINT — READ ONLY reference
- `pipeline/plugin-code-registry/` = THIS SPRINT — new, separate registry

## Blocker Classification Codes

- CRAWL_BLOCKED
- SOURCE_FETCH_BLOCKED
- GIST_FETCH_BLOCKED
- MANUAL_ANALYSIS_INCOMPLETE
- REGISTRY_SCHEMA_DEFECT
- REGISTRY_POPULATION_DEFECT
- OFFICIAL_SNIPPET_VALIDATION_BLOCKED
- FIXTURE_BLOCKED
- PROTECTED_FILE_MUTATION
- EVIDENCE_BUNDLE_BLOCKED
