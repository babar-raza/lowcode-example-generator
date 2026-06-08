# Environment Proof

Sprint: non-lowcode-fallback-implementation-20260604
Date: 2026-06-04

## Runtime Environment

- Platform: Windows 11 Pro 10.0.26200
- Python: 3.13 (C:/Python313/python.exe)
- .venv Python: .venv/Scripts/python.exe
- pytest version: confirmed via .venv
- dotnet: SDK 9.0 (dotnet build/run/restore available)
- DllReflector: tools/DllReflector/ (.NET tool)
- NuGet cache: .local/cache/

## Test Results

- Total tests: 3316 passed, 18 skipped, 0 failed
- New tests: 94 (88 unit + 6 integration)
- MFL minimum: 72

## Backward Compatibility

- cells.yml: unchanged (empty git diff)
- words.yml: unchanged
- pdf.yml: unchanged
- slides.yml: unchanged
- email.yml: unchanged
- diagram.yml: unchanged
- format-authority/: unchanged
