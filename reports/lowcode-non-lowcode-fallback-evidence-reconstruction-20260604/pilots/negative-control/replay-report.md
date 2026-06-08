# Negative/Control Pilot Replay Report

Sprint: non-lowcode-fallback-evidence-reconstruction-20260604
Replay type: MODULE_EXECUTION

## Control Case

- Input type: NonExistentConverter (plausible-sounding hallucinated type)
- Input method: Convert
- DllReflector catalog: does NOT contain NonExistentConverter

## Module Executed

plugin_examples.ai_acceleration.HallucinationValidator.validate()

## Result

- Input status: AI_DRAFT
- Output status: REJECTED_BY_VALIDATOR
- Rejection reason: TYPE_NOT_IN_REFLECTION
- Probe generated: False
- Registry entry created: False
- VERIFIED_PUBLISHABLE reached: False
- format-authority mutated: False

## Verdict

CONTROL_PASS_SAFE_BLOCK
