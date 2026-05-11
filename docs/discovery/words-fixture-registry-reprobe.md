# Words Fixture Registry Reprobe — Sprint A1 HEAL-007

**Date:** 2026-05-04 07:25 UTC
**Sprint:** Sprint A1 — README PR Merge, Post-Merge Verify, Fixture Registry Probe
**Verdict:** `FIXTURE_REGISTRY_STILL_403_GAP_002_OPEN_WORKAROUND_STABLE`

---

## Finding

The Words fixture source repo (`aspose-words/Aspose.Words-for-.NET:master:Examples/Data`) returned `github_api_403_forbidden` again with the refreshed `GITHUB_TOKEN`. This is the same result as prior probes.

## Root Cause

The current `GITHUB_TOKEN` has write access to `aspose-words-net` org repos (evidenced by successful PR creation and merge for Words PR #1 and PR #2). However, the fixture source (`aspose-words/Aspose.Words-for-.NET`) is in a different GitHub org (`aspose-words`) and requires a separate, explicit read-access grant.

## Impact

- **Workaround:** `programmatic_input` — all 4 controlled pilot scenarios create input DOCX via `Document + DocumentBuilder`. This is stable and covers Converter, Watermarker, Splitter, Replacer.
- **GAP-002 status:** OPEN — will require operator action to grant read access to `aspose-words/Aspose.Words-for-.NET`

## Discovery Sweep Result

The `discover-lowcode --families words` run succeeded for reflection and catalog generation:
- 25 plugin types, 230 plugin methods found
- LowCode namespace: `Aspose.Words.LowCode`
- 9 workflow root candidates

## Recommendation

Do not retry fixture probe with current token. Document the fixture access as a separate org-level access grant needed. The programmatic_input workaround is sufficient for the controlled pilot scope.
