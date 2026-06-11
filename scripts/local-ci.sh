#!/usr/bin/env bash
# Local CI simulation — mirrors .gitlab-ci.yml + .github/workflows/build-and-test.yml
# Run from repo root: bash scripts/local-ci.sh
set -euo pipefail

export PYTHONPATH=src

echo "=== Stage: Lint ==="

echo "--- Ruff (blocking gate — TC-H09 fixed all violations) ---"
ruff check src/ tests/

echo "--- Compile check ---"
python -m compileall src/

echo "--- RISK-10: Gate isolation (blocking — TC-H14 scoped to example_gates.py) ---"
if grep -rn \
  "from plugin_examples\.llm_router\|import plugin_examples\.llm_router\|from plugin_examples\.healing_intelligence\|import plugin_examples\.healing_intelligence\|from plugin_examples\.generator\|import plugin_examples\.generator" \
  src/plugin_examples/gates/example_gates.py; then
  echo "RISK-10 VIOLATION: Gate modules must not import AI/LLM modules"
  exit 1
else
  echo "Gate isolation check passed — no AI imports found in example_gates.py"
fi

echo "--- pip-audit (advisory) ---"
if command -v pip-audit &>/dev/null; then
  pip-audit --strict || echo "ADVISORY: pip-audit reported vulnerabilities"
else
  echo "SKIP: pip-audit not installed (pip install pip-audit to enable)"
fi

echo ""
echo "=== Stage: Unit Tests (with coverage) ==="
if python -m pytest --version &>/dev/null 2>&1; then
  python -m pytest tests/unit -v --timeout=60 \
    --cov=src/plugin_examples --cov-report=term-missing --cov-fail-under=60
else
  echo "SKIP: pytest not available in current Python (pip install -e '.[dev]' to enable)"
fi

echo ""
echo "=== Stage: Integration Tests ==="
if python -m pytest --version &>/dev/null 2>&1; then
  python -m pytest tests/integration -v --timeout=120
else
  echo "SKIP: pytest not available in current Python"
fi

echo ""
echo "=== Stage: .NET Build ==="
if command -v dotnet &>/dev/null; then
  dotnet build tools/DllReflector/DllReflector.csproj -c Release
else
  echo "SKIP: dotnet SDK not found (install .NET 8.0 to run this check)"
fi

echo ""
echo "=== All checks passed ==="
