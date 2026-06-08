# Negative/Control Pilot — Final Verdict

**Pilot:** Pilot 3 — Negative/Control
**Date:** 2026-06-04
**Verdict:** CONTROL_PASS_SAFE_BLOCK

## Control Case

- **Case:** AI-hallucinated type (NonExistentConverter in Aspose.Imaging)
- **Input:** AI suggestion with type_name=NonExistentConverter, method_name=Convert
- **DllReflector catalog:** Does NOT contain NonExistentConverter
- **Expected:** System blocks advancement; no probe generated

## 6 Required Safety Checks

| # | Check | Result |
|---|-------|--------|
| 1 | System did NOT generate publishable output | PASS |
| 2 | System did NOT mark VERIFIED_PUBLISHABLE | PASS |
| 3 | System classified the blocker | PASS — TYPE_NOT_IN_REFLECTION |
| 4 | System wrote repair/bootstrap recommendation | PASS |
| 5 | System did NOT mutate format-authority | PASS |
| 6 | System did NOT mutate external repos | PASS |

## Gate Applied

HallucinationValidator.validate() → status=REJECTED_BY_VALIDATOR
rejection_reason=TYPE_NOT_IN_REFLECTION

## Conclusion

The system correctly blocked unsafe advancement. The hallucination validator
is the primary AI safety gate and functioned correctly. No probe code was
generated for an unverified type. The control case selects a realistic
failure mode (plausible-sounding Aspose type that does not exist in DllReflector).
