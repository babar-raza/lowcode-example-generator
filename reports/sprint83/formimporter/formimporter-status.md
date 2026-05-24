# FormImporter Status — Sprint 83

## Current Status: BLOCKED_EXTERNAL

FormImporter (PDF Wave H) remains blocked by an upstream Aspose.PDF library bug.

## Bug Details

- **Package**: Aspose.PDF for .NET
- **Affected version**: 26.5.0 and later
- **Bug type**: NullReferenceException in FormImporter API during field extraction
- **Pipeline response**: Pin NuGet to ≤26.5.0 via TRG-01 guard in evidence validator
- **Repro preserved**: `workspace/defect-repros/pdf-formimporter-nullref/`

## Sprint-by-Sprint Carry-Forward

| Sprint | Status | Action |
|--------|--------|--------|
| Sprint 75 | BLOCKED_EXTERNAL | Bug discovered, repro preserved |
| Sprint 76-82 | BLOCKED_EXTERNAL | No upstream fix available |
| Sprint 83 | BLOCKED_EXTERNAL | No upstream fix available — carry forward |

## TRG-01 Guard

EV TRG-01 fires when NuGet > 26.5.0 is detected in any PDF example's `Directory.Packages.props`. This prevents regression if the pin is accidentally removed.

## Resolution Path

Monitor Aspose.PDF release notes. When the NullReferenceException is fixed in a new version:
1. Update repro to verify fix
2. Remove NuGet pin (or update to fixed version)
3. Generate FormImporter example (PDF Wave H = 1 example)
4. Add to handoff
5. Schedule for next publication sprint

---
*Lane D — Sprint 83 — 2026-05-24*
