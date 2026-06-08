# LowCode Reference Contract

Extracted from merged LowCode repos on 2026-06-08.

## Source Repos (all merged)
- cells PR#7, diagram PR#3, email PR#2, pdf PR#22, slides PR#2, words PR#8
- All merged: 2026-06-02
- All source branches: DELETED

## Root Files Required
- `Directory.Build.props`
- `Directory.Packages.props`
- `README.md`

## Root Files Optional (but recommended)
- `.gitignore`
- `.github/workflows/*.yml`
- `global.json`

## Example Path Convention
`examples/<family>/lowcode/<slug>/`

## Example Required Files
- `Program.cs`
- `<slug>.csproj` (no explicit Version in PackageReference)
- `README.md`
- `example.manifest.json`
- `expected-output.json`

## Example Optional Files
- Input fixture (`input.*`)
- Output artifact (`output.*`)
- `output-validation.json` (internal evidence only; must not replace expected-output.json)

## PR Convention
- Title: `feat(lowcode): add <family> examples (<N> packages)`
- Body: documents packages, canonical URLs, status table
- Branch: `lowcode-examples-<family>-<descriptor>`

## Post-Merge Lifecycle
- PR merged by maintainer
- Source branch deleted after merge
- State matrix updated to MERGED
- Release pipeline triggered externally
