# Claim-to-Evidence Table

| README Claim | Evidence Source | Verified |
|---|---|---|
| Pipeline generates, validates, publishes C# examples for Aspose .NET plugin APIs | AGENTS.md:9 | Yes |
| Published examples live in separate repos | AGENTS.md:11 | Yes |
| Cells: 9 examples, POST_MERGE_VERIFIED | workspace/verification/latest/release-status.json | Yes |
| Words: 4 examples (pilot), POST_MERGE_VERIFIED | workspace/verification/latest/release-status.json | Yes |
| Both at version 26.4.0 | workspace/verification/latest/release-status.json | Yes |
| Cells PR #1 merged | workspace/verification/latest/release-status.json (last_pr_number: 1) | Yes |
| Words PR #1 merged | workspace/verification/latest/release-status.json (last_pr_number: 1) | Yes |
| PDF status: discovery_only (blocked) | pipeline/configs/families/pdf.yml:4 | Yes |
| Words allowed_types: 4 types only | pipeline/configs/families/words.yml:60-64 | Yes |
| Words preferred_methods_per_type defined | pipeline/configs/families/words.yml:65-69 | Yes |
| Python >= 3.12 required | pyproject.toml:8 | Yes |
| 4 runtime dependencies (jsonschema, Jinja2, pyyaml, requests) | pyproject.toml:9-14 | Yes |
| CI runs on ubuntu-latest, Python 3.12 and 3.13 | .github/workflows/build-and-test.yml:13 | Yes |
| DllReflector built with .NET 8.0 in CI | .github/workflows/build-and-test.yml:44 | Yes |
| Approved LLM providers: llm_professionalize, ollama | src/plugin_examples/llm_router/provider_policy.py:12 | Yes |
| Forbidden providers: gpt_oss, openai, azure_openai | src/plugin_examples/llm_router/provider_policy.py:13 | Yes |
| Forbidden model: gpt-4o-mini | src/plugin_examples/llm_router/provider_policy.py:14 | Yes |
| Env vars: GPT_OSS_ENDPOINT, GPT_OSS_API_KEY, GPT_OSS_MODEL | docs/ci/environment-variables.md:31-41 | Yes |
| APPROVE_LIVE_PR must equal exactly "APPROVE_LIVE_PR" | docs/ci/environment-variables.md:20 | Yes |
| APPROVE_MERGE_PR must equal exactly "APPROVE_MERGE_PR" | docs/ci/environment-variables.md:27 | Yes |
| GITHUB_TOKEN: never logged | docs/ci/environment-variables.md:11 | Yes |
| GPT_OSS_API_KEY: never logged | docs/ci/environment-variables.md:37 | Yes |
| CLI entry point: plugin-examples = plugin_examples.__main__:main | pyproject.toml:23 | Yes |
| Cells published_plugin_examples_repo: aspose-cells-net | pipeline/configs/families/cells.yml:37 | Yes |
| Words published_plugin_examples_repo: aspose-words-net | pipeline/configs/families/words.yml:34 | Yes |
| No direct push to main | AGENTS.md:35 | Yes |
| Monthly CI cron on 1st of month | MEMORY.md / agent report | Partial (workflow file not fully read) |
| 13 pipeline stages in runner.py | Agent report of runner.py | Partial (not read line-by-line) |
| 21+ verification gates | Agent report of gates/evaluator.py | Partial |
| 27 test files, 759 tests | Agent report, git status | Partial |
| DllReflector uses MetadataLoadContext exclusively (no code exec) | Agent report of tools/DllReflector/Program.cs | Partial |
| README backfill PRs #3 merged for Cells and Words | workspace/verification/latest/cells-readme-backfill-pr-verification.json (existence), MEMORY.md | Partial |
| Aspose.net link pattern: https://{subdomain}.aspose.net/{family_slug} | Agent report of publisher/aspose_links.py | Partial |

**Legend:**
- Yes = Read file directly and verified exact content
- Partial = Verified via Explore agent report; file not read line-by-line
