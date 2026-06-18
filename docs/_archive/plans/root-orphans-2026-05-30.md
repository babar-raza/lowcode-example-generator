# Root Orphans Audit

Audit date: 2026-05-30

Root-orphan contract: the `docs/` root is reserved for `docs/README.md` only, plus folders such as `docs/_audit/` and `docs/_archive/`. Any other file directly under `docs/` is a root orphan and must be triaged.

## Sweep Method

Command used:

```powershell
Get-ChildItem docs -File | Select-Object -ExpandProperty FullName
```

Result:

```text
C:\Users\prora\OneDrive\Documents\GitHub\lowcode-example-generator-gitlab\docs\README.md
```

## Root Orphans

No root orphan files were found.

| orphan_path | brief content summary | likely target area (overview/guides/reference/ops/dev/arch) | action (move/merge/archive/delete) | canonical merge target (if merge) | risks/notes |
|---|---|---|---|---|---|
| None | No files directly under `docs/` other than `docs/README.md`. | N/A | keep | N/A | Root currently satisfies the root-orphan contract. |

## Standing Recommendation

Add a lightweight docs hygiene check that fails when `docs/` maxdepth 1 contains any file other than `README.md`. This recommendation is not a current code claim; it is a proposed action because no enforcement code was found during the audit.
