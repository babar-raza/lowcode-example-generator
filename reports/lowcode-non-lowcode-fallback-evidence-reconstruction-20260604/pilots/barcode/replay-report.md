# BarCode Pilot Replay Report

Sprint: non-lowcode-fallback-evidence-reconstruction-20260604
Date: 2026-06-04
Replay type: MODULE_EXECUTION (actual Python modules, not hand-written JSON)

## Steps Executed from Real Modules

| Step | Module/File | Result |
|------|-------------|--------|
| 1 | pipeline/plugin-capability-registry/website-catalog.json | PASS — barcode entry found |
| 2 | pipeline/plugin-capability-registry/package-aliases.json | PASS — Aspose.BarCode |
| 3 | reflection/family-namespace-matrix.json | PASS — NO_LOWCODE_BUT_PLUGIN_SITE_PRESENT |
| 4 | plugin_examples.plugin_detector.heuristic_matcher.HeuristicMatcher | PASS — BarcodeGenerator.Save (confidence=0.75) |
| 5 | plugin_examples.ai_acceleration.HallucinationValidator | PASS — REFLECTION_CONFIRMED |
| 6 | plugin_examples.evidence_validator.rules.non_lowcode.NonLowCodeValidatorRules | PASS — 14/14 |
| 7 | plugin_examples.runner._stage_fallback_registry_lookup | PASS — OK, fallback_mode=True |

## Probe Evidence (from TC-IMPL-007)

- Probe project: reports/.../prototypes/barcode/probe/Program.cs (BarcodeGenerator.Save)
- Output: probe-output.png 17210 bytes
- Verdict: PROBE_CONFIRMED

## Raw Command Logs

See: pilots/barcode/raw-command-logs/step1-*.stdout through step7-*.stdout

## Final Verdict

PILOT_PASS_PROBE_CONFIRMED
All 7 module steps executed from actual source. No hand-written JSON used for replay.
