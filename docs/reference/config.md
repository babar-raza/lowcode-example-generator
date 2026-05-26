# Configuration Reference

Audience: Operator, Contributor

Source of truth: `src/plugin_examples/family_config/`, `pipeline/schemas/family-config.schema.json`, `pipeline/configs/`

Last verified from audit: 2026-05-25

## Family Config Files

Family configs live under:

- `pipeline/configs/families/*.yml`
- `pipeline/configs/families/disabled/*.yml`
- `pipeline/configs/families/_templates/family-template.yml`

The runner loads `pipeline/configs/families/{family}.yml`. If it finds a disabled fallback path, the loader rejects it because configs under `disabled/` are not processable.

Configs are schema-validated by `validate_family_config()` against `pipeline/schemas/family-config.schema.json`, then converted into dataclasses in `src/plugin_examples/family_config/models.py`.

## Top-Level Keys

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `family` | yes | string | Family slug, for example `cells`. |
| `display_name` | yes | string | Human-readable product name. |
| `enabled` | yes | boolean | `false` configs are rejected before full schema validation. |
| `status` | yes | string | `disabled` is rejected; `experimental` requires `--allow-experimental`; `discovery_only` cannot run generation. |
| `nuget` | yes | object | Package resolution and dependency behavior. |
| `plugin_detection` | yes | object | Namespace patterns for plugin source-of-truth detection. |
| `github` | yes | object | Official examples repo and publish target repo. |
| `fixtures` | yes | object | Fixture discovery sources. |
| `existing_examples` | yes | object | Existing example mining sources. |
| `generation` | yes | object | Scenario generation limits and constraints. |
| `validation` | yes | object | Restore/build/run/output/reviewer requirements. |
| `llm` | yes | object | Provider order. |
| `template_hints` | no | object | Template generation defaults. |
| `per_type_constraints` | no | object, default `{}` | Required/forbidden generation constraints by type. |

## `nuget`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `package_id` | yes | string | Official NuGet package ID. |
| `version_policy` | yes | string | Code supports `latest-stable` and pinned-version flows. |
| `pinned_version` | no | string or null | Used when a pinned package version is required. |
| `allow_prerelease` | no | boolean, default `false` | Excludes prerelease versions by default. |
| `target_framework_preference` | no | list, default `["netstandard2.0"]` | Framework preference order for extraction. |
| `dependency_resolution.enabled` | no | boolean, default `true` | Enables `.nuspec` dependency resolution. |
| `dependency_resolution.max_depth` | no | integer, default `2` | Maximum transitive dependency depth. |
| `dependency_resolution.extra_packages` | no | list, default `[]` | Extra packages for reflection dependency resolution. |

## `plugin_detection`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `namespace_patterns` | yes | non-empty list | Pattern list used against the reflected API catalog. Examples include `Aspose.Cells.LowCode` and `Aspose.Cells.LowCode.*`. |

## `github`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `official_examples_repo.owner` | yes | string | Source repo owner for fixture/example mining. |
| `official_examples_repo.repo` | yes | string | Source repo name. |
| `official_examples_repo.branch` | yes | string | Source branch. |
| `published_plugin_examples_repo.owner` | yes | string | Target repo owner for publication. |
| `published_plugin_examples_repo.repo` | yes | string | Target repo name for publication. |
| `published_plugin_examples_repo.branch` | yes | string | Target base branch. |
| `central_repo_allowed` | no | boolean, default `false` | Allows shared central target only when explicitly configured. |

## `fixtures` and `existing_examples`

Both sections use a `sources` array.

| Key | Required | Notes |
|---|---:|---|
| `type` | yes | Source type, commonly `github`. |
| `owner` | yes | GitHub owner. |
| `repo` | yes | GitHub repo. |
| `branch` | yes | Git branch. |
| `paths` | no | Paths searched for fixtures or examples. Defaults to `[]` in the dataclass. |

## `generation`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `min_examples_per_family` | yes | integer | Lower bound for planned examples. |
| `max_examples_per_monthly_run` | yes | integer | Upper bound per run. |
| `allow_new_fixtures` | no | boolean, default `true` | Allows new fixture use. |
| `allow_generated_input_files` | no | boolean, default `true` | Allows generated input fixtures. |
| `allowed_types` | no | list, default `[]` | Optional short-name allowlist. |
| `preferred_methods_per_type` | no | object, default `{}` | Optional short-name to method map. |

## `validation`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `require_restore` | no | boolean, default `true` | Requires `dotnet restore`. |
| `require_build` | no | boolean, default `true` | Requires `dotnet build`. |
| `require_run` | no | boolean, default `true` | Requires `dotnet run`. |
| `require_output_validation` | no | boolean, default `true` | Requires output validation. |
| `require_example_reviewer` | no | boolean, default `true` | Requires external reviewer when available/required. |
| `runtime_runner` | no | string, default `auto` | Runtime runner selection. |

## `llm`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `provider_order` | yes | non-empty list | Provider order used by the router preflight. Governance requires the professionalize endpoint; see [Environment Variables](environment-variables.md). |

## `template_hints`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `default_input_extension` | no | `.xlsx` | Default generated input extension. |
| `default_input_filename` | no | `input.xlsx` | Default generated input filename. |
| `array_input_filenames` | no | `["input1.xlsx", "input2.xlsx"]` | Default multiple-input filenames. |
| `input_creation_lines` | no | `[]` | C# lines used by template generation to create default input. |
| `merger_input_creation_lines` | no | `[]` | C# lines used to create merger inputs. |
| `additional_usings` | no | `[]` | Extra C# `using` statements for generated examples. |
| `default_output_extension` | no | `.out` | Default output extension. |
| `default_fixture_extension` | no | `.xlsx` | Default fixture extension. |

## Other Config and Data Inputs

| Path | Purpose |
|---|---|
| `pipeline/configs/denominators/*.json` | Family denominator models, source versions, and catalog hash checks. |
| `pipeline/contracts/**/*.json` | Scenario contracts consumed by planner/generator. |
| `pipeline/format-authority/manifest.json` | Format authority manifest. |
| `pipeline/format-authority/contracts/*.json` | Format authority contracts by family. |
| `pipeline/configs/metrics.yml` | Metrics defaults, environment variable names, and post ledger path. |
| `pipeline/configs/llm-routing.yml` | LLM routing config file. Current router code also contains defaults and policy checks. |
| `pipeline/configs/plugin-namespace-patterns.yml` | Global namespace pattern config. |
| `pipeline/configs/verifier.yml` | Verifier configuration. The runtime bridge also uses `EXAMPLE_REVIEWER_PATH`. |
| `pipeline/configs/github-publishing.yml` | Publishing config. Family configs still carry target repos used by publisher. |

## Related Guides

- [Add or Update a Family](../guides/add-or-update-family.md)
- [Run a Family Pipeline](../guides/run-family-pipeline.md)
- [Schemas and Contracts](schemas-and-contracts.md)
