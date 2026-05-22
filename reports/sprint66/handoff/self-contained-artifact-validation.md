# Sprint 66 — Self-Contained Artifact Validation

Generated: 2026-05-22
Sprint: sprint66-remote-truth-repair-self-contained-artifacts-readme-io-publication-proof

## Validation Rules

1. No `obj/` directories present
2. No `bin/` directories present
3. No hidden workspace references (no paths pointing outside bundle)
4. Every example has Program.cs, README.md, .csproj
5. Every README.md contains "## Input and Output" section
6. No audit record references a missing file

## Results

| Family | Examples | README Present | I/O Section | Program.cs | .csproj | obj/bin | Status |
|--------|----------|---------------|-------------|------------|---------|---------|--------|
| cells | 9 | 9/9 | 9/9 | 9/9 | 9/9 | 0 | PASS |
| words | 8 | 8/8 | 8/8 | 8/8 | 8/8 | 0 | PASS |
| pdf | 19 | 19/19 | 19/19 | 19/19 | 19/19 | 0 | PASS |
| diagram | 2 | 2/2 | 2/2 | 2/2 | 2/2 | 0 | PASS |
| email | 1 | 1/1 | 1/1 | 1/1 | 1/1 | 0 | PASS |
| slides | 3 | 3/3 | 3/3 | 3/3 | 3/3 | 0 | PASS |
| **TOTAL** | **42** | **42/42** | **42/42** | **42/42** | **42/42** | **0** | **ALL PASS** |

## Source Paths

All artifacts copied from:
- `reports/sprint64/destination-packages/per-family/{family}/` (standard examples)
- `reports/sprint64/destination-packages/special-cases/pdf-pdf-aconverter/` → `handoff/per-family/pdf/pdfa-converter/`
- `reports/sprint64/destination-packages/special-cases/pdf-text-extractor/` → `handoff/per-family/pdf/text-extractor/`

## Destination Layout

```
reports/sprint66/handoff/per-family/
├── cells/
│   ├── Directory.Packages.props
│   ├── html-converter/     (Program.cs, README.md, *.csproj)
│   ├── image-converter/    ...
│   ├── json-converter/
│   ├── pdf-converter/
│   ├── spreadsheet-converter/
│   ├── spreadsheet-locker/
│   ├── spreadsheet-merger/
│   ├── spreadsheet-splitter/
│   ├── text-converter/
│   └── handoff-index.json
├── words/    (8 examples + Directory.Packages.props)
├── pdf/      (19 examples including html/, pdfa-converter/, text-extractor/)
├── diagram/  (2 examples)
├── email/    (1 example)
└── slides/   (3 examples)
```

## Sprint 65 vs Sprint 66

| Dimension | Sprint 65 | Sprint 66 |
|-----------|-----------|-----------|
| handoff/per-family/ content | EMPTY | 42/42 examples present |
| README I/O in handoff | N/A | 42/42 present |
| obj/bin in handoff | N/A | 0 (none) |
| External package references | Yes (sprint64 paths) | None (all copied in) |

## Verdict

`SELF_CONTAINED_42_42_ALL_PASS`
