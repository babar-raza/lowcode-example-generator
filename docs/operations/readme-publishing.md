# README Publishing

Audience: Operator

The pipeline can render, audit, and publish README-only changes for a family package.

## Render Locally

```powershell
python -m plugin_examples render-root-readme --family cells --promote-latest
```

## Simulate README PR

```powershell
python -m plugin_examples publish-readme --family cells --approval-token APPROVE_LIVE_PR --promote-latest
```

## Publish README PR

```powershell
python -m plugin_examples publish-readme --family cells --publish --approval-token APPROVE_LIVE_PR --promote-latest
```

## Evidence

README commands write render, audit, simulation, or live PR result evidence under `workspace/verification/latest/`.

See:

- [CLI Reference](../reference/cli.md)
- [Publishing and GitHub](../reference/publishing-and-github.md)
