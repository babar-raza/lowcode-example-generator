# E2E Run Summary: email

**Run ID:** sysqual-20260528-001
**Pilot Run ID:** pilot-email-final-20260528
**Pipeline Verdict:** DATA_FLOW_PROTOTYPE_ONLY
**Stages Passed:** 14/17
**Healing Required:** False
**Machinery Verdict:** PASS

## Stage Results

| Stage | Status |
|---|---|
| load_config | success |
| nuget_fetch | success |
| version_drift_preflight | success |
| dependency_resolution | success |
| extraction | success |
| reflection | success |
| plugin_detection | success |
| api_delta | success |
| impact_mapping | success |
| fixture_registry | success |
| example_mining | success |
| scenario_planning | success |
| llm_preflight | success |
| generation | success |
| validation | skipped (template mode) |
| reviewer | skipped (template mode) |
| publisher | skipped (dry-run) |

## Healing

NO

## Notes

All 14 machinery stages passed. Validation/reviewer/publisher are skipped in
template-mode dry-run qualification. Production evidence for all examples
exists in workspace/verification/latest/families/email/.
