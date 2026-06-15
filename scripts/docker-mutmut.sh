#!/usr/bin/env bash
# Docker-based mutation testing runner for CI.
# Runs mutmut inside a Python 3.13 Linux container — no WSL dependency.
# Called from GitLab CI or locally: bash scripts/docker-mutmut.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Docker mutation testing ==="
echo "Project: $PROJECT_DIR"

# MSYS_NO_PATHCONV prevents Git Bash from mangling /c/Users/... paths.
# pwd produces /c/Users/... which Docker Desktop on Windows maps correctly.
MSYS_NO_PATHCONV=1 docker run --rm \
    -v "$PROJECT_DIR:/app" \
    -w /app \
    python:3.13-slim \
    bash -c '
        set -euo pipefail
        echo "=== Installing dependencies ==="
        pip install -q -e ".[dev]" 2>/dev/null

        echo "=== Running mutmut ==="
        mutmut run \
            --paths-to-mutate src/plugin_examples/gates/,src/plugin_examples/policy/loader.py,src/plugin_examples/reliability/slo_monitor.py,src/plugin_examples/compliance/reporter.py,src/plugin_examples/reliability/slo_remediator.py,src/plugin_examples/contracts/stage_contracts.py \
            --runner "python -m pytest tests/unit/ -x -q --timeout=30" \
            || true

        echo "=== Parsing results ==="
        mutmut results || true

        python3 -c "
import subprocess, re, json, sys

out = subprocess.run([\"mutmut\", \"results\"], capture_output=True, text=True).stdout
killed = len(re.findall(r\"Mutant .+ killed\", out)) + len(re.findall(r\"Mutant .+ timeout\", out))
survived = len(re.findall(r\"Mutant .+ survived\", out))
total = killed + survived
score = round((killed / total * 100), 1) if total else 0.0
result = {\"killed\": killed, \"survived\": survived, \"total\": total, \"score\": score}
with open(\"mutmut-summary.json\", \"w\") as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
"
        echo "=== Done ==="
    '
