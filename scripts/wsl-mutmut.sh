#!/usr/bin/env bash
# WSL-side mutation testing runner for CI.
# Called from GitLab CI via: wsl.exe -d Ubuntu-22.04 -- bash <this-script> <wsl-project-path>
set -euo pipefail

PROJECT_DIR="${1:?Usage: wsl-mutmut.sh <wsl-project-path>}"
VENV_DIR="/tmp/mutmut-venv"

echo "=== WSL mutation testing ==="
echo "Project: $PROJECT_DIR"
echo "Venv: $VENV_DIR"

# Create or reuse venv
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Install project with dev deps
pip install -e "$PROJECT_DIR[dev]" --quiet 2>/dev/null || pip install -e "$PROJECT_DIR[dev]"

cd "$PROJECT_DIR"

# Run mutmut (uses [tool.mutmut] from pyproject.toml)
echo "=== Running mutmut ==="
mutmut run \
    --paths-to-mutate src/plugin_examples/gates/,src/plugin_examples/policy/loader.py,src/plugin_examples/reliability/slo_monitor.py,src/plugin_examples/compliance/reporter.py,src/plugin_examples/reliability/slo_remediator.py,src/plugin_examples/contracts/stage_contracts.py \
    --runner "python -m pytest tests/unit/ -x -q --timeout=30" \
    || true  # mutmut exits non-zero when survivors exist

echo "=== Parsing results ==="
mutmut results || true

# Produce JSON summary
python3 -c "
import subprocess, re, json, sys

out = subprocess.run(['mutmut', 'results'], capture_output=True, text=True).stdout
killed = len(re.findall(r'Mutant .+ killed', out)) + len(re.findall(r'Mutant .+ timeout', out))
survived = len(re.findall(r'Mutant .+ survived', out))
total = killed + survived
score = round((killed / total * 100), 1) if total else 0.0
result = {'killed': killed, 'survived': survived, 'total': total, 'score': score}
with open('mutmut-summary.json', 'w') as f:
    json.dump(result, f, indent=2)
print(json.dumps(result, indent=2))
"
echo "=== Done ==="
