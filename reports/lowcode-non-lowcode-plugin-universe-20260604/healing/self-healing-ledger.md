# Self-Healing Ledger — Plugin Universe Sprint 20260604

Generated: 2026-06-04T00:00:00Z

## Healing Policy

- Loop 1: mandatory for all system-owned defects found during pilot wave
- Loop 2: allowed if Loop 1 partially resolved the defect
- Stop after Loop 2: classify remaining blocker; do not continue
- External blockers (package unavailability, license restrictions): NOT system defects

## Defect Classification Codes

| code | trigger |
|------|---------|
| CATALOG_DEFECT | Crawler, normalizer, or cache failure |
| PACKAGE_ALIAS_DEFECT | Wrong package ID used; alias not found |
| REFLECTION_DEFECT | DllReflector invocation or parsing failure |
| HEURISTIC_MATCHER_DEFECT | Matcher returned wrong or empty results |
| AI_VALIDATION_DEFECT | HallucinationValidator advanced wrong status |
| REGISTRY_SCHEMA_DEFECT | Registry YAML failed schema validation unexpectedly |
| PROBE_GENERATOR_DEFECT | Template generation or PR-rule enforcement failure |
| FIXTURE_DEFECT | TIER-1 fixture not generated or wrong provenance |
| VALIDATOR_DEFECT | NL-V rule logic error or SKIP logic incorrect |
| RUNNER_INTEGRATION_DEFECT | fallback_registry_lookup stage incorrect behavior |
| EVIDENCE_DEFECT | Required artifact missing or malformed |

## Defects Found This Sprint

| # | defect_id | code | family | description | loop | resolution |
|---|-----------|------|--------|-------------|------|-----------|
| — | — | — | — | No system-owned defects found as of sprint open | — | — |

## Issues Investigated

### Issue 1: runner.py fallback stage returning 0 candidates for barcode/imaging

- **Reported**: TRAIN A of prior sprint
- **Root cause**: Filter used `status == "PROBE_CANDIDATE"` but both barcode and imaging had advanced to `PROBE_CONFIRMED`
- **Classification**: RUNNER_INTEGRATION_DEFECT (system-owned)
- **Resolution**: Loop 1 — added `_FALLBACK_USABLE_STATUSES = frozenset({"PROBE_CANDIDATE", "PROBE_CONFIRMED", "VERIFIED_PUBLISHABLE"})`
- **Post-heal result**: HEALED_AND_RERUN_PASS — runner now returns 2 candidates for barcode, 1 for imaging, 1 for zip

### Issue 2: Inline bash script quoting failure (catalog builder)

- **Reported**: TRAIN A shell execution
- **Root cause**: Nested quotes in `python -c "..."` with Python string literals
- **Classification**: EVIDENCE_DEFECT (script delivery method)
- **Resolution**: Loop 1 — moved script to `scripts/build_catalog.py` and executed as file
- **Post-heal result**: HEALED_AND_RERUN_PASS

## External Blockers (not system defects)

| blocker_id | family | code | description |
|-----------|--------|------|-------------|
| EXT-001 | threed | PROBE_BLOCKED_LICENSE | Aspose.3D trial may produce watermarked/empty 3D output |
| EXT-002 | gis | PROBE_BLOCKED_API | GIS rendering requires valid geospatial datasets |
| EXT-003 | omr | PROBE_BLOCKED_LICENSE | OMR requires valid template + scan image |

## Post-Healing States

| family | state |
|--------|-------|
| barcode | HEALED_WITH_CLASSIFIED_EXTERNAL_BLOCKER — system healed; remaining blockers are external license |
| imaging | HEALED_WITH_CLASSIFIED_EXTERNAL_BLOCKER — same |
| zip | HEALED_AND_RERUN_PASS — no blockers |

## Rules

- Do not treat external blockers as system defects
- Do not stop after first contradiction — exhaust 2 loops
- Do not close with pass verdict if system-owned pilot defect remains after Loop 2
- External package/license blockers acceptable only if logs prove the blocker
