# Local CI simulation — mirrors .gitlab-ci.yml + .github/workflows/build-and-test.yml
# Run from repo root: powershell -ExecutionPolicy Bypass -File scripts\local-ci.ps1
$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "src"

Write-Host "=== Stage: Lint ==="

Write-Host "--- Ruff (advisory — 16 pre-existing violations; see TC-H09) ---"
ruff check src/ tests/
if ($LASTEXITCODE -ne 0) {
  Write-Host "ADVISORY: ruff reported violations (non-blocking until TC-H09 resolved)"
}

Write-Host "--- Compile check ---"
python -m compileall src/
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "--- RISK-10: Gate isolation (advisory) ---"
$riskResult = Select-String -Path "src\plugin_examples\gates\*.py" -Pattern "from plugin_examples\.(llm_router|healing_intelligence|generator)|import plugin_examples\.(llm_router|healing_intelligence|generator)" -ErrorAction SilentlyContinue
if ($riskResult) {
  Write-Host "ADVISORY: RISK-10 findings detected:"
  $riskResult | ForEach-Object { Write-Host $_.ToString() }
  Write-Host "(non-blocking pending TC-H03 scope resolution)"
} else {
  Write-Host "Gate isolation check passed"
}

Write-Host "--- pip-audit (advisory) ---"
if (Get-Command pip-audit -ErrorAction SilentlyContinue) {
  pip-audit --strict
  if ($LASTEXITCODE -ne 0) { Write-Host "ADVISORY: pip-audit reported vulnerabilities" }
} else {
  Write-Host "SKIP: pip-audit not installed (pip install pip-audit to enable)"
}

Write-Host ""
Write-Host "=== Stage: Unit Tests (with coverage) ==="
python -m pytest tests/unit -v --timeout=60 `
  --cov=src/plugin_examples --cov-report=term-missing --cov-fail-under=60
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== Stage: Integration Tests ==="
python -m pytest tests/integration -v --timeout=120
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "=== Stage: .NET Build ==="
if (Get-Command dotnet -ErrorAction SilentlyContinue) {
  dotnet build tools/DllReflector/DllReflector.csproj -c Release
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} else {
  Write-Host "SKIP: dotnet SDK not found (install .NET 8.0 to run this check)"
}

Write-Host ""
Write-Host "=== All checks passed ==="
