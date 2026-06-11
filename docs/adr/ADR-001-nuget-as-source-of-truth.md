# ADR-001: NuGet Package as Primary API Source of Truth

**Status:** Accepted
**Date:** 2026-06-01
**Deciders:** Pipeline architecture team
**Supersedes:** N/A

---

## Context

The pipeline generates C# code examples from Aspose .NET plugin APIs. Before a code example can be generated, the pipeline must know which API types, methods, and namespaces are available in the target NuGet package.

Several source candidates were evaluated:

1. **NuGet package DLLs** — the actual published artifact, reflecting real available symbols.
2. **DocFX / XML doc comments** — documentation layer, sometimes out-of-date relative to the actual DLL.
3. **GitHub repository source** — unreleased code may be present; version drift is common.
4. **Third-party API catalogs** — external aggregation services; may lag or be incomplete.

The pipeline uses .NET DLL reflection (`tools/DllReflector`) against the downloaded NuGet `.nupkg` to discover the actual public API surface. This is then stored as a catalog (`*.reflection.json`) which drives all downstream code generation and validation.

---

## Decision

The **downloaded NuGet package** is the authoritative source for all API symbols used in example generation.

DocFX markdown and existing example repos are treated as **supporting inputs only** — they inform fixtures and patterns but do not override the DLL-reflected catalog.

---

## Consequences

**Positive:**
- Generated examples always compile against the actual published package version.
- Symbol catalog accurately reflects what users of the package will see.
- Catalog is deterministic and reproducible: same NuGet version → same symbols.
- Build/compile gates can be run locally without network access once the package is cached.

**Negative:**
- NuGet API rate limits can block the fetch stage during heavy use.
- Package delisting or yanking breaks the pipeline until config is updated.
- Requires `dotnet` SDK and `DllReflector` to be available in the execution environment.

**Mitigation:**
- `nuget-cache/` is maintained locally to reduce repeat fetches.
- `doctor` command checks NuGet connectivity as a prerequisite.
- Monthly refresh runs on a schedule to detect delisted or updated packages.

---

## Alternatives Considered

| Option | Rejected Reason |
|--------|----------------|
| DocFX as primary | Documentation lags behind releases; missing internal overloads |
| GitHub source as primary | May include unreleased code; version pinning is fragile |
| Manual symbol list | Does not scale to 38+ packages across 6+ families |
