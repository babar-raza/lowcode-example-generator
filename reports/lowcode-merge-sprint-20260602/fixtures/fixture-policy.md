# Persistent Fixture Policy

## Rules
1. Examples generate input files programmatically at runtime — no external fixture files required
2. All 44 publishable examples are self-contained: they create their own input data
3. PFX certificates: RUNTIME_ONLY — generated in memory, never committed to git
4. PDF input files: bundled in workspace for E2E testing; examples generate their own at runtime
5. Network-dependent features (TSA timestamps): classified ENVIRONMENT_DEPENDENT_PASS
6. No example requires external fixture files that cannot be regenerated

## Fixture Categories
- PROGRAMMATIC_INPUT: Example creates its own input (42 examples)
- RUNTIME_CRYPTO: PFX/certificate generated at runtime (words/signer)
- ENVIRONMENT_DEPENDENT: Requires network/TSA server (pdf/timestamp)
