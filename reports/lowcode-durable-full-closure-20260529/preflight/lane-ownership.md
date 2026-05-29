# Lane Ownership Map

| Lane | Name | Owner | Output Dir |
|------|------|-------|-----------|
| 0 | Coordinator Preflight | Agent | preflight/ |
| 1 | Prior Bundle Audit | Agent | audit/ |
| 2 | Durable Fix Promotion | Agent | healing/ + src/ + pipeline/configs/ |
| 3 | Clean Regeneration Proof | Agent | generation/ |
| 4 | Full E2E Validation | Agent | e2e/ |
| 5 | Gate Semantics Repair | Agent | gates/ + src/plugin_examples/gates/ |
| 6 | Local Publication Package | Agent | publication/ |
| 7 | Test Suite Hardening | Agent | tests/ + validators/ |
| 8 | Artifact Integrity | Agent | artifact/ |
| 9 | Product Universe Recheck | Agent | discovery/ + blockers/ |
| 10 | Work-Ahead | Agent | workahead/ |
| 11 | AI/LLM Accounting | Agent | ai/ |
| 12 | IV/Adversarial Review | Agent | iv/ |

## No Overlap Conflicts
- Lanes 2 and 3 overlap on source files (Lane 2 modifies source, Lane 3 reads result) — SEQUENTIAL dependency enforced
- Lanes 4 and 5 overlap on gate results — SEQUENTIAL dependency (Lane 4 output feeds Lane 5)
- All other lanes are independent and can proceed in parallel as agent capacity allows
