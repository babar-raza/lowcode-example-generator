# Example-Reviewer Integration Surface

**TC-00X Discovery Report**
**Repo:** https://github.com/babar-raza/example-reviewer
**Owner:** babar-raza (same owner as lowcode-example-generator)
**Language:** Python (primary), C# (templates)
**Branch:** main

## Integration Modes

### 1. CLI (Recommended for TC-15)

**Entry point:** `python -m src.cli.main`

**Relevant commands for pipeline integration:**

| Command | Purpose | Flags |
|---------|---------|-------|
| `compile-verify --family <f>` | Compile extracted examples | `--max-examples N` |
| `runtime-verify --family <f>` | Run compiled examples | `--max-examples N` |
| `compile-fix --family <f>` | Fix compilation errors | `--max-examples N` |
| `runtime-fix --family <f>` | Fix runtime errors | `--max-examples N` |
| `final-review --family <f>` | LLM review of changes | |
| `status --family <f>` | Check pipeline status | `--json` |

**Global flags:** `--config-dir`, `--db-path`, `--workspace-dir`, `--verbose`, `--json`

### 2. MCP Server (Alternative)

**Entry point:** `src/mcp_tools/server.py`
**Transport:** stdio, JSON-RPC 2.0
**Tools:** 12 tools matching CLI commands
**Protocol:** `2024-11-05`

### 3. Direct Python Import (Not recommended)

Possible but creates tight coupling. CLI subprocess is preferred.

## Required Configuration

The example-reviewer expects:
- Family config JSON in `config/families/{family}.json`
- Database at `data/example_reviewer.db` (SQLite)
- Workspace directory for compilations
- .NET SDK installed for compile/runtime operations

## Integration Plan for TC-15

1. **Mode:** CLI subprocess via `python -m src.cli.main`
2. **Workflow:**
   - Copy generated examples to reviewer workspace
   - Run `compile-verify --family cells --json`
   - Parse JSON output for pass/fail
   - Run `runtime-verify --family cells --json` if compilation passes
   - Run `final-review --family cells --json` for LLM review
3. **Availability check:** Test `python -m src.cli.main status --json`
4. **Failure behavior:** If reviewer unavailable, block publishing (fail-closed)

## Dependencies

- Python 3.x with packages from requirements.txt
- SQLite database
- .NET SDK for compilation
- Optional: Ollama/LLM for compile-fix, runtime-fix, final-review

## Status

- Repo accessible: YES
- CLI documented: YES
- MCP documented: YES
- Family configs exist for: cad, cells, email, html, imaging, medical, page, pdf, slides, smoke, tasks, tex, words, zip
- Integration mode selected: CLI subprocess
