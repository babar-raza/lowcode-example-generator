Sprint 84 — Overlap and Ownership Check
========================================
Date: 2026-05-24

## Lane Ownership Matrix

| Lane | Owner Topic           | Files Owned (prefix)               | Forbidden Paths |
|------|-----------------------|------------------------------------|-----------------|
| A    | Publication gate      | publication/live-*                 | none (skip)     |
| B    | PR batching strategy  | publication/pr-batching-*          | merge-readiness/ |
| C    | Root README conflict  | conflicts/                         | publication/pr-creation-* |
| D    | Handoff/remote truth  | handoff/, remote/                  | conflicts/      |
| E    | Merge/post-merge      | merge-readiness/, publication/merge-* | conflicts/   |
| F    | Product/system        | product/, version-drift/, formimporter/, post-merge-runtime/, readiness/ | evidence/ |
| G    | Validator hardening   | evidence/validator-*               | sprint-state.json |
| H    | Evidence consistency  | evidence-consistency/, git/, logs/ | publication/    |
| I    | Taskcard sync         | tracking/                          | evidence/       |
| J    | IV                    | iv/, review/iv-findings.md         | everything else |

## Overlap Risks

### B vs C
- B owns pr-batching-strategy.md; C owns root-readme-pr-conflict-strategy.md
- B says: "1 PR per family unless conflict requires split"
- C says: what the splits are (if any)
- Resolution: C informs B. C runs first logically. No file conflict.

### C vs E
- C owns conflicts/ directory
- E owns merge-readiness/ (includes whether open PRs block merge)
- No file overlap. E may reference C's output.

### D vs H
- D owns remote/ directory (remote-repo-state-*.json)
- H owns evidence-consistency/ and git/ (dirty classification)
- No file overlap.

### G vs H
- G owns validator test results (evidence/validator-test-results.txt)
- H owns test-run.log in logs/
- Coordination: G writes validator-test-results.txt; H writes logs/test-run.log (full pytest output)
- No conflict — different files, different directories.

## Conclusion
No lane conflicts detected. All lanes may execute in parallel.
