# Overlap Control

## File Overlap Matrix

| File/Path | Lane B | Lane C | Lane D | Lane E | Lane F |
|-----------|--------|--------|--------|--------|--------|
| pipeline/configs/denominators/*.json | WRITE | READ | READ | VALIDATE | TEST |
| src/plugin_examples/publisher/release_status.py | WRITE | READ | READ | READ | TEST |
| src/plugin_examples/evidence_contract.py | READ | READ | READ | READ | WRITE |
| src/plugin_examples/publisher/readme_*.py | READ | READ | WRITE | READ | TEST |
| workspace/pr-dry-run/* | READ | WRITE | READ | - | VALIDATE |
| workspace/verification/latest/* | READ | WRITE | WRITE | WRITE | VALIDATE |

## Serialization Protocol

1. Lane A completes evidence intake first (read-only)
2. Lane B performs denominator reconciliation (serialized: no other lane writes denominators during B)
3. Lane E runs health/drift checks after B stabilizes denominators
4. Lane D performs README audits after B/E complete
5. Lane C performs PDF publication readiness after B/D complete
6. Lane F runs tests at every checkpoint
7. Lane G only starts after Lanes A-F are green

## Active Conflicts

- workspace/pr-dry-run/pdf-controlled-pilot-pr5/README.md: unstaged modification (3 files)
  - Resolution: These are expected README modifications from cumulative rendering. Not blocking.
- leg.zip: untracked file at repo root
  - Resolution: Not project-related. Ignore.
