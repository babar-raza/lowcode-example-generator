# Wave 3 Validator Rules — lowcode-plugin-example-factory-wave-20260605

## Status
Sprint: lowcode-plugin-example-factory-wave-20260605
Generated: 2026-06-05
Total new rules: 14 (W01–W14)

---

## W01 — REGISTRY_STATUS_TRANSITION_VALID
**Target**: PluginEntry.registry_status
**Rule**: Status must follow the defined FSM:
`PAGE_DISCOVERED → CODE_HARVESTED → READY_FOR_TRANSFORMATION → TRANSFORMED_TO_EXAMPLE_DRYRUN → PUBLICATION_CANDIDATE_LOCAL`
**Severity**: ERROR

## W02 — DRYRUN_PACKAGE_PATH_EXISTS
**Target**: PluginEntry.dryrun_package_path (when status=TRANSFORMED_TO_EXAMPLE_DRYRUN)
**Rule**: Field must be non-null and reference an existing directory
**Severity**: ERROR

## W03 — DRYRUN_VALIDATION_STATUS_SET
**Target**: PluginEntry.dryrun_validation_status (when status=TRANSFORMED_TO_EXAMPLE_DRYRUN)
**Rule**: Must be one of: DRYRUN_PASS, DRYRUN_FAIL, OUTPUT_MISSING, BUILD_FAILED
**Severity**: ERROR

## W04 — DRYRUN_PACKAGE_HAS_PROGRAM_CS
**Target**: dryrun_package_path/Program.cs
**Rule**: Package directory must contain Program.cs
**Severity**: ERROR

## W05 — DRYRUN_PACKAGE_HAS_CSPROJ
**Target**: dryrun_package_path/*.csproj
**Rule**: Package directory must contain exactly one .csproj file
**Severity**: ERROR

## W06 — DRYRUN_PACKAGE_HAS_README
**Target**: dryrun_package_path/README.md
**Rule**: Package directory must contain README.md with "dotnet run" instructions
**Severity**: ERROR

## W07 — DRYRUN_PACKAGE_HAS_OUTPUT_DIR
**Target**: dryrun_package_path/output/
**Rule**: Package must have an output/ directory
**Severity**: WARNING

## W08 — DRYRUN_PACKAGE_HAS_PROVENANCE
**Target**: dryrun_package_path/source-provenance.json
**Rule**: Package must contain source-provenance.json with canonical_url field
**Severity**: ERROR

## W09 — DRYRUN_OUTPUT_NOT_EMPTY
**Target**: dryrun_package_path/output-validation.json
**Rule**: output-validation.json must exist with verdict=PASS (or PASS_TRIAL)
**Severity**: ERROR

## W10 — DRYRUN_OUTPUT_FILES_PRODUCED
**Target**: dryrun_package_path/output/
**Rule**: output/ directory must contain at least one file with size > 0
**Severity**: ERROR

## W11 — NUGET_PACKAGE_MATCHES_TEMPLATE
**Target**: .csproj PackageReference
**Rule**: The NuGet package referenced in .csproj must match the family template's nuget_package
**Severity**: WARNING

## W12 — CANONICAL_URL_IN_PROVENANCE_MATCHES_REGISTRY
**Target**: source-provenance.json canonical_url vs registry canonical_url
**Rule**: provenance.canonical_url must match entry.canonical_url
**Severity**: ERROR

## W13 — PROGRAM_CS_HAS_CANONICAL_URL_COMMENT
**Target**: Program.cs (first 10 lines)
**Rule**: Program.cs must have a comment referencing the canonical URL
**Severity**: WARNING

## W14 — REGISTRY_YAML_PARSEABLE
**Target**: pipeline/plugin-code-registry/family/*.yaml
**Rule**: All YAML files must parse without errors
**Severity**: ERROR

---

## Regression Guards (from prior sprint)

- R01-R10: Registry readiness validator rules (carried forward)
- R02 updated: CANONICAL_URL_BEST_MATCH treated as WARNING (not ERROR)

## Passing State

All 12 Wave A packages satisfy W01–W14. Registry YAML files (repaired 2026-06-05) satisfy W14.
