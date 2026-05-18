# All-Family LowCode Launch Scoreboard — Sprint 32

**Date:** 2026-05-18
**Verdict:** LAUNCH_READY_PENDING_OPERATOR_APPROVAL

## Portfolio Status

| Family | Status | Published | PR-Ready | Version | Runtime Verified |
|--------|--------|-----------|----------|---------|-----------------|
| **Cells** | FAMILY_COMPLETE | 9/9 | 0 | 26.4.0 | Yes |
| **Words** | PILOT_COMPLETE | 8/8 pilot | 0 | 26.5.0 | Yes |
| **PDF** | PARTIAL_CANARY | 5/19 pilot | 14 | 26.4/26.5 | Yes |
| **Diagram** | PILOT_COMPLETE | 2/2 | 0 | 26.4.0 | Yes |
| **Email** | PILOT_COMPLETE | 1/1 | 0 | 26.4.0 | Sprint32 ✓ |
| **Slides** | PILOT_COMPLETE | 3/3 | 0 | 26.5.0 | Sprint32 ✓ |

## Totals

- **Total published:** 28 examples
- **Total with PRs ready:** 42 examples (after PDF publication)
- **PDF PR packages:** 6 packages, 14 examples, all 0 bin/obj
- **Gate:** PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL not set

## Sprint 32 Runtime Verifications

- **Email Converter** (lane-e1): BUILD PASS, RUN PASS — output HTML 2002 bytes
- **Slides Compress/Convert/Merger** (lane-e2): ALL BUILD+RUN PASS

## To Publish PDF (all 14 pending examples)

```powershell
$env:GITHUB_TOKEN = [Environment]::GetEnvironmentVariable('GH_TOKEN', 'User')
$env:PLUGIN_EXAMPLES_LIVE_PUBLISH_APPROVAL = 'APPROVE_LIVE_PR'
# Then run publish-pr commands from pdf-release-candidate-publication-packet.json
```
