# Example Publication Contract v1
**Sprint**: wave21-20260608
**Status**: ADOPTED

## Principle
After candidate discovery, both LowCode-namespace and non-LowCode-plugin pipelines must use
identical downstream processing. The only allowed difference is how the initial candidate record is
created.

## Pipeline Stages (shared for all families post-discovery)

| # | Stage | Owner |
|---|-------|-------|
| 1 | Candidate discovery | LowCode: namespace scan; Non-LowCode: plugin page/probe |
| 2 | Canonical identity verification | Shared: products.aspose.net URL confirmed |
| 3 | Fixture/source acquisition | Shared: from GitHub examples repo, probe output, or hand-crafted |
| 4 | Example generation | Shared: canonical_packager.py |
| 5 | Manifest generation | Shared: manifest_generator |
| 6 | Expected-output generation | Shared: expected_output_generator |
| 7 | Restore / build / run validation | Shared: dotnet restore+build+run |
| 8 | Output validation | Shared: output_validator |
| 9 | PR packet generation | Shared: publication/pr_packet_builder.py |
| 10 | Target repo publication | Shared: GitHub API push to repo branch |
| 11 | State / registry update | Shared: registry YAML update |
| 12 | Evidence authority | Shared: evidence bundle + sidecar + attestation |
| 13 | Independent verification | Shared: IV checklist |

## Folder Convention

### Plugin-only repos (single product type)
```
examples/<family>/<slug>/
```
Rationale: Repo name already signals plugin context (e.g. Aspose.BarCode.Plugins-for-.NET-Examples).
No disambiguation needed within the repo.

### Multi-type repos (if future combined repos)
```
examples/<family>/lowcode/<slug>/     # LowCode namespace examples
examples/<family>/plugins/<slug>/     # Non-LowCode plugin examples
```

## Required Public Files Per Example

| File | LowCode | Non-LowCode Plugin | Notes |
|------|---------|-------------------|-------|
| Program.cs | ✓ | ✓ | |
| <family>-<slug>.csproj | ✓ | ✓ | No Version attribute (central mgmt) |
| example.manifest.json | ✓ | ✓ | REQUIRED — public contract |
| expected-output.json | ✓ | ✓ | REQUIRED — public contract |
| README.md | ✓ | ✓ | Per-example |
| input.<ext> | if needed | if needed | Input fixtures |

## Required Repo-Level Files

| File | Purpose |
|------|---------|
| README.md | Examples index table |
| Directory.Packages.props | Central package version management |
| Directory.Build.props | Shared build properties |
| global.json | .NET SDK version pinning |
| .gitignore | Ignore build artifacts |
| .github/workflows/build.yml | CI validation |

## Internal Evidence Files (NOT public)

| File | Status |
|------|--------|
| output-validation.json | Sprint evidence only — not public contract |
| restore.log / build.log / run.log | Sprint evidence only |
| source-provenance.json | Sprint evidence only |

## Status Taxonomy

| Status | Meaning |
|--------|---------|
| CANONICAL_PACKAGE_PROVEN | Example built and run locally, output validated |
| PR_PACKET_READY | All public files generated, PR packet complete |
| PR_CREATED | Live PR exists with verified URL |
| EXTERNAL_REVIEW_PENDING | Awaiting human review/merge |
| MERGED | PR merged to main |
| PUBLISHED | Package live on products.aspose.net |

## Schema Fields Added to Candidate Record

```json
{
  "namespace_source": "LOWCODE | NON_LOWCODE_PLUGIN",
  "public_repo_kind": "LOWCODE_EXAMPLES | PLUGIN_EXAMPLES",
  "folder_namespace_segment": "lowcode | '' (empty for plugin-only repos)",
  "discovery_method": "LOWCODE_NAMESPACE_SCAN | PLUGIN_PAGE_PROBE | MANUAL"
}
```
