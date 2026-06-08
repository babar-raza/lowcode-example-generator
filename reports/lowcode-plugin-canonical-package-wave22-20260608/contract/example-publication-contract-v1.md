# Example Publication Contract v1

Date: 2026-06-08
Sprint: Wave 22

## Scope
Applies to all Aspose .NET plugin and LowCode example repos.

## Required Public Files (per example)
| File | Description |
|------|-------------|
| `Program.cs` | Runnable C# example |
| `<slug>.csproj` | Project file (no explicit PackageReference Version) |
| `README.md` | Per-example documentation with purpose, prerequisites, build, run, expected output |
| `example.manifest.json` | Public contract: inputs, outputs, namespace_source, canonical_url |
| `expected-output.json` | Public contract: expected stdout markers, output file contract |

## Internal Evidence Files (must NOT replace public contract)
| File | Description |
|------|-------------|
| `output-validation.json` | Sprint evidence; must coexist with expected-output.json, not replace it |
| `fixture.*` / `*.dwg` / etc. | Input fixtures; provenance documented in example.manifest.json |

## Required Root Files
| File | Description |
|------|-------------|
| `README.md` | Root repo index with example table |
| `Directory.Packages.props` | Central package management |
| `Directory.Build.props` | Shared build props |
| `.gitignore` | Ignores bin/obj/artifacts |
| `.github/workflows/build.yml` | CI workflow |

## Folder Convention
### LowCode Repos
`examples/<family>/lowcode/<slug>/`

### Plugin/Non-LowCode Repos
`examples/<family>/<slug>/`
(Repo name provides context: `*.Plugins-for-.NET-Examples`)

## PR Contract
### Plugin Repos (NON_LOWCODE_PLUGIN)
- Title: `feat(plugins): add Aspose.<Family> plugin examples (<N> packages)`
- Body: uses "plugin API examples" — not "low-code"
- Branch: `plugins/wave<N>/<family>-plugin-examples` (Wave 22+ new branches)
- Legacy: `lowcode/wave19/` branches on existing open PRs are grandfathered

### LowCode Repos
- Title: `feat(lowcode): add <family> examples (<N> packages)`
- Body: uses "LowCode" / "low-code" terminology
- Branch: `lowcode-examples-<family>-<descriptor>`

## PR Lifecycle
1. PR created → EXTERNAL_REVIEW_PENDING
2. CI passes → CHECKS_PASSED
3. Maintainer approves → MERGE_READY_APPROVAL_BLOCKED (external gate)
4. Maintainer merges → MERGED
5. Source branch deleted → BRANCH_CLEANED
6. State matrix updated → PUBLISHED (after release pipeline)

## README Content Requirements
### Per-example README.md
- Title (# <family>/<slug>)
- Purpose: what this example demonstrates
- Prerequisites: .NET SDK version, NuGet package
- Build & Run commands
- Expected Output: description of what the example produces
- Input Fixture notes (if applicable)

### Root README.md
- Repo description
- Example index table: slug, operation, package, canonical URL
- Build/run instructions
- Contract description (files included per example)
