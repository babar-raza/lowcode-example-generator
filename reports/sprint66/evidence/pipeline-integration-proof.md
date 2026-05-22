# Pipeline Integration Proof — EvidenceValidator — Sprint 66

## Status: ACTIVE

EvidenceValidator is imported and called in `src/plugin_examples/__main__.py`.

## Call Path

```
plugin_examples release-status --validate-bundle <bundle_dir>
  -> __main__.main()
  -> EvidenceValidator(bundle_dir=Path(bundle_dir))
  -> validator.validate()
```

## Sprint 66 Confirmation

No changes to EV wiring in Sprint 66. Gate remained active.
42-rule EV suite with 2993 passing unit tests.
EV is NOT deferred. Gate is NOT standalone-only.
