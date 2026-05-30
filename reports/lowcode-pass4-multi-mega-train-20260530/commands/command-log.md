# Command Log — Pass 4 Multi-Mega-Train

Sprint: lowcode-pass4-multi-mega-train-20260530
Date: 2026-05-30

## Pass 4 Commands Executed

### Assembly — pdf-controlled-pilot-pr10
```
C:/Python313/python.exe scripts/assemble_pdf_pr10_pilot.py
```
- Source: workspace/runs/pilot-pdf-repair-20260530/generated/pdf/
- Destination: workspace/pr-dry-run/pdf-controlled-pilot-pr10/
- Result: 5 examples assembled, all build (dotnet build exit 0)

### E2E — Cells (from pilot run directory)
```
dotnet restore workspace/runs/pilot-cells-20260529-214911/generated/cells/<example> --nologo -v q
dotnet build ... --no-restore --nologo -v q
dotnet run --no-build --project ...
```
- Result: 9/9 PASS

### E2E — Words (from pilot run directory)
```
dotnet restore workspace/runs/pilot-words-20260529-220000/generated/words/<example> --nologo -v q
dotnet build ... --no-restore --nologo -v q
dotnet run --no-build --project ...
```
- Result: 8/8 PASS

### E2E — PDF, Diagram, Slides, Email (from pr-dry-run)
```
dotnet restore workspace/pr-dry-run/<pkg>/examples/<family>/lowcode/<slug>
dotnet build ... --no-restore --nologo -v q
dotnet run --no-build --project ...
```
- Result: 25/25 PASS

### NuGet package checks
```
dotnet restore (with Aspose.Epub reference) → NU1101 (package not found)
dotnet restore (with Aspose.OCR 26.5.0) → success
dotnet restore (with Aspose.PSD 26.5.0) → success
```

### LowCode reflection check
```
Assembly.LoadFrom(aspose.ocr.dll)  → 1257 types, 0 LowCode
Assembly.LoadFrom(aspose.psd.dll)  → 4432 types, 0 LowCode
```

### Pytest
```
.venv/Scripts/python.exe -m pytest tests/ -q --tb=no
```
- Result: captured in tests/ directory

### Validator count
```
grep -c "def _rule_" src/plugin_examples/evidence_validator.py
```
- Result: 147
