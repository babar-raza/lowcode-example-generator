# ADR-009: Documentation Governance — Docs-as-Code Synchronization Policy

Status: Accepted
Date: 2026-06-17

## Context

By 2026-06-17, the documentation estate had drifted from source code in five ways:

1. **CLI command gap**: `docs/reference/cli.md` documented 20 commands while 27 were registered in source — a 7-command gap that had persisted for at least 3 weeks without detection.
2. **Stale onboarding claims**: `docs/getting-started/operator-quickstart.md` listed .NET SDK 8.0 (current: 10.0) and 6 families (current: 18+).
3. **Near-duplicate files**: Two post-merge-verification files existed (`docs/operations/` and `docs/publishing/`) covering the same operator action with ~30% content overlap.
4. **Audit artifacts not promoted**: `docs/_audit/` contained a complete 2026-05-30 migration plan and IA proposal that were never executed.
5. **Generated file staleness**: `docs/development/open-taskcard-closure-matrix.md` was 35 days stale with no detection mechanism.

No CI gate enforced documentation completeness, link integrity, or synchronization with source.

## Decision

Adopt a **docs-as-code synchronization policy** with three enforcement layers:

### Layer 1: Source-Verified Reference Files

Files in `docs/reference/` are **source-verified**. Each must carry a `Last verified:` metadata line updated whenever the referenced source changes. The following reference files require source verification:

| File | Source to verify against |
|---|---|
| `docs/reference/cli.md` | `src/plugin_examples/commands/__init__.py` |
| `docs/reference/config.md` | `pipeline/schemas/family-config.schema.json`, `src/plugin_examples/family_config/models.py` |
| `docs/reference/environment-variables.md` | `os.getenv()` / `os.environ.get()` calls in `src/plugin_examples/` |
| `docs/reference/gates-and-verdicts.md` | `src/plugin_examples/gates/`, `src/plugin_examples/evidence_validator/rules/` |
| `docs/reference/schemas-and-contracts.md` | `pipeline/schemas/*.json` |

### Layer 2: Automated Detection Scripts

Three scripts enforce synchronization:

| Script | Purpose | Location |
|---|---|---|
| `scripts/check_cli_docs_drift.py` | Detect CLI commands registered in source but not documented in `cli.md` | New (added this sprint) |
| `scripts/check_doc_freshness.py` | Detect generated files older than `max_age_days` | New (added this sprint) |

### Layer 3: CI Gates

| Gate | Tool | Enforcement |
|---|---|---|
| `docs-cli-drift` | `scripts/check_cli_docs_drift.py` | Advisory initially; blocking after baseline verification |
| `docs-freshness` | `scripts/check_doc_freshness.py` | Advisory initially; blocking after 1 sprint |
| `docs-link-check` | `markdown-link-check` | Advisory initially; blocking for local links |

### File Creation Policy

Before creating any new docs file:

1. Search `docs/` for existing coverage of the topic (`grep` the title/topic).
2. If a near-duplicate exists, extend it rather than creating a new file.
3. New files go in the correct folder per audience and purpose:
   - `docs/reference/` — exhaustive canonical reference (source-verified)
   - `docs/guides/` — step-by-step how-to guides
   - `docs/operations/` — operational runbooks (step-level procedures)
   - `docs/getting-started/` — onboarding content
   - `docs/architecture/` — system design and ADRs
   - `docs/development/` — contributor documentation

### `_audit/` Promotion Policy

Files placed in `docs/_audit/` must be resolved within one sprint:
- Promote to active docs OR
- Archive to `docs/_archive/plans/` with a date suffix

`_audit/` must contain only `README.md` after each sprint. It is a staging area, not a long-term location.

### `last_verified` Frontmatter Policy

All `docs/reference/` files must include a `Last verified:` line in the frontmatter. When source changes (new commands, new env vars, new schemas), the author must update both the source and `Last verified:`.

## Consequences

**Positive:**
- CLI command drift is caught automatically before merging new commands without docs.
- Generated file staleness is caught within 7 days.
- Operators find accurate, current documentation.
- `_audit/` is emptied on a predictable schedule.

**Negative:**
- Reference file updates add overhead to source changes — author must also update docs.
- CI gate maintenance cost (scripts must be updated if command registration changes structure).

**Neutral:**
- The docs folder structure is unchanged. No reorganization was needed.
- Archive files are immutable; no policies apply to `docs/_archive/`.

## Alternatives Considered

- **No automation** — rejected (RC-2 proved undocumented commands persist for weeks without detection)
- **External doc platform (Docusaurus, MkDocs)** — rejected (overkill for a static markdown estate with no public hosting)
- **Vale style linter** — deferred (adds config overhead; acceptable once style guide is enforced in pre-commit)
