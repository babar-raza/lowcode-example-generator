# Product Overview

Audience: User, Operator, Contributor

This repository is the pipeline repo for generating, validating, and publishing SDK-style C# examples for Aspose .NET plugin APIs, especially LowCode and Plugins namespaces.

The pipeline:

1. Resolves an official NuGet package.
2. Extracts DLL/XML assets.
3. Reflects public API symbols into an API catalog.
4. Detects plugin-capable namespaces.
5. Plans examples from reflected symbols.
6. Generates SDK-style C# console projects.
7. Runs restore, build, run, output validation, and optional example-reviewer checks.
8. Publishes accepted examples through GitHub pull requests.

Published examples do not live in this repository. They are published to configured family-specific example repositories.

## Source of Truth

The official NuGet package is the source of truth for API symbols. Documentation and existing examples are supporting inputs only.

See:

- [System Design](../architecture/system-design.md)
- [Pipeline Stages](../architecture/pipeline-stages.md)
- [Configuration Reference](../reference/config.md)
