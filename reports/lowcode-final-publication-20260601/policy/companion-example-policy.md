# Companion Example Policy

## Definition
A companion example demonstrates functionality closely related to a LowCode family but whose primary type is NOT a LowCode main class (e.g., DigitalSignatureUtil.Sign for words/signer).

## Criteria for PUBLISH_COMPANION_EXAMPLE
1. The example compiles and runs successfully (E2E PASS).
2. It provides clear user value as supplementary reference code.
3. It is clearly labeled as a companion (not counted in the main-class denominator).
4. It does not duplicate an existing main-class example.

## Denominator Contribution
Companion examples do NOT count toward the canonical 42-example denominator.
They are published as bonus content in the family package.

## Labeling
Package README must indicate companion status: "This example demonstrates [type] which is not a LowCode main class but provides related functionality."

## Current Companions
| Example | Family | Reason |
|---------|--------|--------|
| words/signer | words | DigitalSignatureUtil.Sign uses SignerContext (CONTEXT_MODEL), not a LowCode main class |

## Decision Authority
Agent-delegated per sprint `lowcode-final-publication-20260601`.
