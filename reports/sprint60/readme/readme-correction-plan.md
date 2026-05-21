# README Correction Plan — Sprint 60 Phase 3

**Date:** 2026-05-21

---

## Example README Corrections Required

### 42/42 Content Checks: PASS
All 42 example READMEs in the destination repos contain:
- Family name (Aspose.{Family} or family keyword)
- API class (workflow_type)
- Package ID

No example README corrections are required for Sprint 60.

---

## Root README Corrections

### Words Root README — Version Drift
- **Repo:** aspose-words-net/Aspose.Words.LowCode-for-.NET-Examples
- **Current:** No version reference in root README
- **Package version drift:** 26.4.0 → 26.5.0 (NuGet published, repo not updated)
- **Policy:** Version intentionally omitted from root README; version lives in `Directory.Packages.props`
- **Action:** Update `Directory.Packages.props` in the repo to reference 26.5.0 when Words is re-published. Root README update is OPTIONAL (not required by policy).
- **Gate:** Requires `APPROVE_README_PUSH` for any README push
- **Status:** CARRY_FORWARD to publication sprint

### Diagram Root README — Version Drift
- **Repo:** aspose-diagram-net/Aspose.Diagram.LowCode-for-.NET-Examples
- **Current:** No version reference in root README
- **Package version drift:** 26.4.0 → 26.5.0 (NuGet published, repo not updated)
- **Policy:** Same as Words — version intentionally omitted
- **Action:** Same as Words
- **Status:** CARRY_FORWARD to publication sprint

---

## Sprint 60 README Status Summary

| Scope | Count | Status |
|-------|-------|--------|
| Example READMEs (content audit) | 42/42 | PASS |
| Root READMEs (presence) | 6/6 | PASS |
| Root READMEs (version policy) | 6/6 | CLASSIFIED |
| Version drift corrections | 2 (Words, Diagram) | CARRY_FORWARD |
| README gate wired | 1 | Phase 4 |
