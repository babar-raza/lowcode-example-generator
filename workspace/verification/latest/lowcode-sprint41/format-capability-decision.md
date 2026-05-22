# Lane F — Format-Capability Concurrent Work Decision

**Status:** COMMIT_APPROVED

## Files Under Review

| File | Delta | Description |
|------|-------|-------------|
| `src/plugin_examples/format_capability/classifier.py` | +1/-1 | Move mailmerger pattern before generic merger for correct priority |
| `src/plugin_examples/publisher/readme_renderer.py` | +68 | Add operation_kind classification, input/output format display fields |
| `templates/root-readme/lowcode-family-readme.md.j2` | +1/-1 | Use new display fields in README table rendering |
| `tests/unit/test_format_capability.py` | +15 | 6 new tests: Html/Jpeg/Png/Tiff exact names + MailMerger classification |

## Coherence Assessment

1. **Self-contained:** YES — all 4 files relate to the format-display feature extension.
2. **No overlap with PDF merge files:** YES — these modify generator source, not target repo content.
3. **No new dependencies:** YES — uses existing infrastructure only.
4. **Backwards compatible:** YES — adds new optional fields (operation_kind, input_format_display, output_format_display) with empty defaults; template uses `| default('', true)` fallback.

## Test Evidence

- `test_format_capability.py`: 254/254 PASS (includes 6 new tests from dirty changes)
- `test_format_map_completeness.py`: PASS
- `test_gate_output_validation.py`: PASS
- `test_manifest_format_fields.py`: PASS
- `test_readme_facts_extraction.py`: PASS
- Full suite: 2187/2187 PASS (3 skipped)

## Decision

**COMMIT** these 4 files as Sprint 41 with message:
```
feat(format-lifecycle): finalize format display and classifier refinements
```

Rationale: Files are coherent, self-contained, fully tested, and do not contaminate any other lane's work.
