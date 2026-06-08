# Accepted Useful Work from Prior Sprints

## Sprint: lowcode-plugin-code-registry-20260604
## Date: 2026-06-04

---

## Accepted as Validation Infrastructure (Do Not Rebuild)

### 1. Package Aliases
- **Path**: `pipeline/plugin-capability-registry/package-aliases.json`
- **Status**: ACCEPTED — correct NuGet package IDs for 20 families
- **Usage**: Reference for registry entries to get correct package IDs
- **Note**: Do not rebuild; reference read-only

### 2. DllReflector and Dependency Resolution
- **Prior sprint**: Built pattern for downloading NuGet packages and reflecting DLLs
- **Evidence**: `reports/lowcode-non-lowcode-fallback-implementation-20260604/reflection/`
- **Reflection results**: 12/18 families reflected, namespace/type counts available
- **Usage**: Validation only — after code evidence establishes class/method intent
- **Note**: Aspose.Page.Plugins namespace is the only family with `.Plugins` namespace

### 3. Probe Generator Infrastructure
- **Prior sprint**: Probe .csproj templates and runner scripts created
- **Evidence**: `src/plugin_examples/probe_generator/`
- **Probes confirmed**: barcode, imaging, zip, tasks, cad, font
- **Usage**: Run probes after code evidence determines correct API pattern
- **Note**: Probes validate; they do not discover

### 4. Runner Fallback Stage
- **Path**: `src/plugin_examples/runner.py`
- **Status**: ACCEPTED — fallback stage for non-LowCode example running
- **Usage**: Can be used for running validated examples

### 5. Plugin Page URL Inventory (65 URLs)
- **Path**: `reports/lowcode-non-lowcode-plugin-universe-20260604/catalog/plugin-page-hashes.json`
- **Status**: ACCEPTED as starting URL list — 65 real products.aspose.net pages
- **Note**: These are real pages from prior crawl, but source-code content was NOT harvested
- **Usage**: This sprint will re-crawl to harvest source-code links, gists, snippets

### 6. Prior Feasibility Probes (6 families)
- barcode: generate-barcode — PROBE_CONFIRMED (BarcodeGenerator class)
- imaging: save-image — PROBE_CONFIRMED (Image.Load/Save pattern)
- zip: create-zip — PROBE_CONFIRMED (Archive class)
- tasks: convert-mpp-to-pdf — PROBE_CONFIRMED (Project.Save pattern)
- cad: convert-cad-to-pdf — PROBE_CONFIRMED (Image.Load/CadImage pattern)
- font: convert-font — PROBE_CONFIRMED (Font.Open/Save pattern, trial-restricted)
- **Usage**: Accepted as validation baselines; need code evidence to confirm they match official page snippets

### 7. NuGet Availability Matrix
- **Path**: `reports/lowcode-non-lowcode-plugin-universe-20260604/catalog/`
- **Status**: ACCEPTED — 20/20 families confirmed available on NuGet
- **Usage**: Reference for registry package_version fields

### 8. Website Catalog Crawler
- **Path**: `src/plugin_examples/website_catalog/crawler.py`
- **Status**: ACCEPTED — can crawl plugin pages
- **Improvement needed**: Must harvest source-code links, gists, inline snippets per page

---

## Summary

These 8 categories of prior work are accepted as valid infrastructure. This sprint will:
- Use them as validation/reference tools
- NOT treat them as discovery authority
- Build on top of them with page/code evidence
