# Configuration Reference

Audience: Operator, Contributor
Source of truth: `src/plugin_examples/family_config/`, `pipeline/schemas/family-config.schema.json`, `pipeline/configs/`

## Family Configs

Family configs live under:

- `pipeline/configs/families/*.yml`
- `pipeline/configs/families/disabled/*.yml`
- `pipeline/configs/families/_templates/family-template.yml`

Configs are loaded by `load_family_config()` and validated against `pipeline/schemas/family-config.schema.json`.

## Top-Level Keys

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `family` | yes | string | Family slug such as `cells`. |
| `display_name` | yes | string | Human-readable product name. |
| `enabled` | yes | boolean | `false` configs are rejected by the loader. |
| `status` | yes | `active`, `disabled`, `experimental`, `discovery_only` | `experimental` requires `--allow-experimental`; `discovery_only` cannot run generation. |
| `nuget` | yes | object | Package resolution. |
| `plugin_detection` | yes | object | Namespace patterns used for source-of-truth proof. |
| `github` | yes | object | Official examples repo and publish target. |
| `fixtures` | yes | object | Fixture discovery sources. |
| `existing_examples` | yes | object | Existing example mining sources. |
| `generation` | yes | object | Scenario generation limits and controls. |
| `validation` | yes | object | Restore/build/run/output/reviewer requirements. |
| `llm` | yes | object | Provider order. |
| `template_hints` | no | object | Defaults for template generation. |

## `nuget`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `package_id` | yes | string | Official NuGet package ID. |
| `version_policy` | yes | `latest-stable` or `pinned` | Controls version resolution. |
| `pinned_version` | no | string or null | Used with `pinned`. |
| `allow_prerelease` | no | false | Excludes prerelease versions by default. |
| `target_framework_preference` | yes | non-empty string array | First matching `lib/` folder wins. |
| `dependency_resolution.enabled` | no | true | Enables `.nuspec` dependency resolution. |
| `dependency_resolution.max_depth` | no | 2 | Maximum transitive dependency depth. |
| `dependency_resolution.extra_packages` | no | string array | Extra packages for reflection dependency resolution. |

## `plugin_detection`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `namespace_patterns` | yes | non-empty array | Examples: `Aspose.Cells.LowCode`, `Aspose.Cells.LowCode.*`. |

## `github`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `official_examples_repo.owner` | yes | string | Source repo owner for fixture/example mining. |
| `official_examples_repo.repo` | yes | string | Source repo name. |
| `official_examples_repo.branch` | yes | string | Source branch. |
| `published_plugin_examples_repo.owner` | yes | string | Publish target owner. |
| `published_plugin_examples_repo.repo` | yes | string | Publish target repo. |
| `published_plugin_examples_repo.branch` | yes | string | Publish target base branch. |
| `central_repo_allowed` | no | false | Allows shared central target only with explicit approval. |

## `fixtures` and `existing_examples`

Both use a `sources` array. Source entries commonly include:

| Key | Notes |
|---|---|
| `type` | Source type, such as `github`. |
| `owner` | GitHub owner. |
| `repo` | GitHub repo. |
| `branch` | Git branch. |
| `paths` | Paths searched for fixtures or examples. |

## `generation`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `min_examples_per_family` | yes | integer >= 1 | Lower bound for planned examples. |
| `max_examples_per_monthly_run` | yes | integer >= 1 | Upper bound per run. |
| `allow_new_fixtures` | no | boolean | Allows new fixture use. |
| `allow_generated_input_files` | no | true in model | Allows generated input fixtures. |
| `allowed_types` | no | string array | Optional short-name allowlist. |
| `preferred_methods_per_type` | no | object | Optional short-name to method map. |

## `validation`

| Key | Type/default | Notes |
|---|---|---|
| `require_restore` | boolean | Requires `dotnet restore`. |
| `require_build` | boolean | Requires `dotnet build`. |
| `require_run` | boolean | Requires `dotnet run`. |
| `require_output_validation` | boolean | Requires semantic output validation. |
| `require_example_reviewer` | boolean | Requires external reviewer when available/required. |
| `runtime_runner` | `linux`, `windows`, or `auto`; default `auto` | `auto` selects platform based on assembly/runtime constraints. |

## `llm`

| Key | Required | Type/default | Notes |
|---|---:|---|---|
| `provider_order` | yes | non-empty array | Examples: `llm_professionalize`, `ollama`. |

## Other Config Files

| File | Purpose |
|---|---|
| `pipeline/configs/llm-routing.yml` | Provider definitions, preflight prompt, env var names, retry/timeout values. |
| `pipeline/configs/metrics.yml` | Metrics defaults, mapping, allowed statuses/job types, env vars, ledger path. |
| `pipeline/configs/plugin-namespace-patterns.yml` | Global namespace pattern config. |
| `pipeline/configs/verifier.yml` | Verifier config. Runtime bridge also uses `EXAMPLE_REVIEWER_PATH`. |
| `pipeline/configs/github-publishing.yml` | Publishing config. Family configs still carry target repos used by publisher. |
| `pipeline/configs/denominators/*.json` | Family denominator models. |
| `pipeline/contracts/**/*.json` | Scenario contracts. |
