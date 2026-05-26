# Root Orphans

Audit mode: docs root hygiene.

Last refreshed: 2026-05-26.

Contract: `docs/` root is reserved for `docs/README.md` only, plus folders such as `docs/_audit/` and `docs/_archive/`. Any other direct file under `docs/` is a ROOT ORPHAN and must be triaged.

Root sweep command used:

```powershell
Get-ChildItem docs -File | Select-Object -ExpandProperty Name
```

Result:

```text
README.md
```

No root orphans were found.

| orphan_path | brief content summary | likely target area | action | canonical merge target | risks/notes |
|---|---|---|---|---|---|
| None | No direct files under `docs/` besides `docs/README.md` | N/A | N/A | N/A | Root hygiene currently passes. |
