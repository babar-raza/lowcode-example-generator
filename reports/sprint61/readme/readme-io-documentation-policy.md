# README I/O Documentation Policy — Sprint 61

## Purpose

Defines what constitutes valid I/O format documentation in a plugin example README.
Closes Sprint 60 defect SD60-02: README audit claimed MATCH based on family/workflow/
package_id presence, without verifying that input and output formats were documented.

---

## Policy: Required README Content

Each example README **MUST** include an explicit "## I/O Formats" section documenting:

1. **Input format(s)**: The file extension(s) the example accepts (e.g., `.xlsx`, `.pdf`)
2. **Output format(s)**: The file extension(s) or output type the example produces

### Acceptable Forms

The I/O section may be any of:
- A structured `## I/O Formats` section with `**Input:**` and `**Output:**` labels
- A description sentence in the introduction (e.g., "Converts `.xlsx` spreadsheets to `.html`")
- A table with Input/Output rows

### NOT Acceptable

- API symbol names that happen to contain extension-like substrings (e.g., `PdfConverter`, `DocConverter`)
- Inferred from the scenario ID alone
- Present in code blocks but not in prose

---

## Detection Rule

The `readme_io_format_not_falsely_complete` EvidenceValidator rule enforces this policy.

Prose-context detection strips:
- Lines containing only backtick-enclosed API symbols
- Code blocks (triple-backtick sections)

Then scans for file extension patterns (`\.xlsx`, `\.pdf`, etc.) or explicit labels
(`Input:`, `Output:`, `accepts`, `produces`) in the remaining prose.

---

## Before State (Sprint 61 Audit)

All 42 auto-generated READMEs use the template:

```markdown
# {scenario-id}
Auto-generated example for **{Package}** (net8.0).
## API Symbols Used
`Aspose.X.LowCode.ClassName`, ...
## Run
dotnet run
```

**Result: 0/42 have I/O format documentation** (BOTH_DOC_MISSING for all 42).

---

## After State (Target — post correction)

After adding `## I/O Formats` sections derived from Program.cs:

| Status | Count |
|--------|-------|
| IO_DOC_MATCH | 38 |
| INPUT_DOC_MISSING | 3 (words-mail-merger, words-report-builder, pdf-pdf-aconverter) |
| BOTH_DOC_MISSING | 1 (pdf-text-extractor — no local package) |

The 3 INPUT_DOC_MISSING cases have no input.EXT literal in Program.cs (they use data sources
or runtime-generated inputs). These must be manually classified.

---

## Correction Template

For each example, add after the description line:

```markdown
## I/O Formats

**Input:** `.{input_ext}` file
**Output:** `.{output_ext}` file
```

Special cases:
- `pdf-text-extractor`: Output is stdout (string result)
- `email-converter`: Output is a directory of converted files
- `words-report-builder`: Input is a data source + template

---

## Publication Blocker

Adding I/O format documentation to published READMEs requires:
1. Pushing updated README.md to each target repo branch
2. Creating a PR for each family (or batching by family)
3. Requires `PLUGIN_EXAMPLES_README_PUSH_APPROVAL=APPROVE_README_PUSH`

This is a **publication operation** deferred from Sprint 61 to Sprint 62.
Sprint 61 delivers the audit evidence and correction plan — not the live push.

---

## Audit Evidence Files

| File | Description |
|------|-------------|
| `example-readme-io-audit-before.json` | Current state: 0/42 with I/O docs |
| `example-readme-io-audit-after.json` | Target state: 38/42 IO_DOC_MATCH post-correction |
| `readme-io-correction-plan.json` | Per-example correction text to add |
