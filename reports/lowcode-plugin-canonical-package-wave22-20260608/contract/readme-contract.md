# README Contract

Date: 2026-06-08

## Per-Example README.md Requirements
Every public example must have a `README.md` that includes:
1. **Title**: `# <family>/<slug>`
2. **Purpose**: 1-2 sentences describing what the example demonstrates
3. **NuGet Package**: the package name and version policy
4. **Canonical URL**: link to products.aspose.net
5. **Prerequisites**: .NET SDK version requirement
6. **Build & Run**: exact commands
7. **Expected Output**: description of produced artifacts/stdout
8. **Input Fixture** (if applicable): description of input file used

## Root README.md Requirements
Every repo must have a root `README.md` that includes:
1. Repo description
2. Example index table (slug, operation, package, canonical URL)
3. Build instructions
4. Contract section (files per example)
5. Validation note (CI)

## Validation
PPV-04 (manifest exists), PPV-09 (root README), and new RDV-01..05 validators enforce this contract.
