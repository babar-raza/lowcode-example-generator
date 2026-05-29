# Lane Ownership Map

**Sprint ID:** full-system-qualification-repair-20260529


| Lane | Owner | Paths |
|---|---|---|
| Lane 0 | Coordinator | preflight/, commands/ |
| Lane 1 | Audit | audit/ |
| Lane 2 | Discovery | discovery/ |
| Lane 3 | E2E | products/{family}/full-e2e/ |
| Lane 4 | Supervisor | supervisor/ |
| Lane 5 | Tests/Validators | tests/, validators/ |
| Lane 6 | Publication | publication/ |
| Lane 7 | Blockers | blockers/, workahead/ |
| Lane 8 | AI/LLM | ai/ |
| Lane 9 | State/Memory | state/ |
| Lane 10 | IV/Review | iv/ |
| Final | Evidence | evidence/, final-verdict.md, sprint-state.json |

No lane may modify another lane's path prefix without coordinator serialization.
