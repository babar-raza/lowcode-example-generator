# README Gate Flow Integration — Sprint 67

## Status: ACTIVE

The README audit gate is called in `publish-pr --publish` live mode.

## Call Path

```
plugin_examples publish-pr --publish --approval-token APPROVE_LIVE_PR
  -> __main__.main()
  -> batch_publisher.publish_batch()
  -> check_readme_audit_gate(audit_path, approval_token)
```

## Sprint 67 Confirmation

Gate is active and wired into the publication flow. All gate tests pass.
Sprint 62 hardening applies: APPROVE_README_PUSH no longer bypasses a failed audit.
Only APPROVE_README_AUDIT_OVERRIDE can bypass (records audit_override_used=True).
