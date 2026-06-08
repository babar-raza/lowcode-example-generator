# Pipeline Parity Architecture

## Principle
Both LowCode and non-LowCode plugin pipelines are identical after candidate discovery.

## Discovery
- **LowCode**: `plugin_detection.namespace_patterns` scan detects LowCode namespace types.
- **Non-LowCode Plugin**: `plugin_detection.fallback_strategy=capability_registry` triggers
  `_stage_fallback_registry_lookup` which loads PROBE_CANDIDATE/PROBE_CONFIRMED entries from
  `pipeline/plugin-capability-registry/<family>.yaml`.

## After Discovery
Both paths converge on the same downstream stages (see contract/example-publication-contract-v1.md).

## Key Discriminator: PluginDetection Properties
```python
namespace_source         # LOWCODE | NON_LOWCODE_PLUGIN
public_repo_kind         # LOWCODE_EXAMPLES | PLUGIN_EXAMPLES
folder_namespace_segment # 'lowcode' | '' (empty for plugin-only repos)
```

## Folder Conventions
- LowCode: `examples/<family>/lowcode/<slug>/`
- Plugin (plugin-only repo): `examples/<family>/<slug>/`

## Status Taxonomy (v1)
CANONICAL_PACKAGE_PROVEN → PR_PACKET_READY → PR_CREATED → EXTERNAL_REVIEW_PENDING → MERGED → PUBLISHED
