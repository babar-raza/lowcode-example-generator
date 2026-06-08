# Negative/Control Pilot — Case Selection

## Selected Control Case

**Case: Imaging family with AI-hallucinated type (NonExistentConverter)**

Rationale:
- Meaningful test: a plausible-sounding type (NonExistentConverter) that could fool a naive system
- Tests the HallucinationValidator — the primary AI safety gate
- Tests that PROBE_CANDIDATE is NOT generated from an unverified type
- Tests that VERIFIED_PUBLISHABLE is NOT reachable via unverified path
- Tests that the runner fallback stage does not load entries with REJECTED_BY_VALIDATOR status as probe candidates

## Control Inputs

- Family: imaging (has fallback_strategy=capability_registry; registry file exists)
- AI suggestion: type_name=NonExistentConverter, method_name=Convert
- DllReflector output: NonExistentConverter NOT in catalog.types
- Expected outcome: REJECTED_BY_VALIDATOR (TYPE_NOT_IN_REFLECTION)

## Anti-Gaming Justification

This case is non-trivial because:
1. The family IS in the registry (barring trivial 404)
2. The package IS available (Aspose.Imaging 26.6.0)
3. The AI suggestion looks plausible (follows Aspose naming convention)
4. Only the HallucinationValidator + DllReflector authority prevents advancement
5. Without these gates, the system would generate probe code for a non-existent type
