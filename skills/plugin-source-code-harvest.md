# Skill: Plugin Source Code Harvest

## Purpose
Fetch official source code (from GitHub repos, gists, or inline page snippets) for a given plugin.

## Inputs
- family_slug
- plugin_slug
- plugin_url (products.aspose.net page URL)
- source_links (from page harvest, may be empty)
- github_repo (from package-aliases or repo index)
- plugin_keywords (search terms for finding relevant files)

## Outputs
- Fetched C# code file(s) in .local/code-cache/{family}/{plugin_slug}/
- Code hash (SHA-256 of code text)
- Extracted symbols: namespaces, classes, methods, enums
- Updated: code-harvest/source-link-inventory.json
- Updated: code-harvest/code-symbol-inventory.json

## Prerequisites
- .local/code-cache/ directory exists
- GitHub repo identified (see pipeline/plugin-capability-registry/package-aliases.json)

## Step-by-Step Method

1. Check if source_links from page harvest contain GitHub/gist links
2. If direct source links exist: fetch raw file content
3. If no direct links: search GitHub repo file tree
   a. GET `https://api.github.com/repos/{org}/{repo}/git/trees/master?recursive=1`
   b. Filter C# files matching plugin_keywords (avoid Demo/UI/App_Start paths)
   c. Sort by path depth (prefer top-level examples)
   d. Select top 3 matches
4. Fetch raw file: `https://raw.githubusercontent.com/{org}/{repo}/master/{path}`
5. Compute SHA-256 hash of file content
6. Save to `.local/code-cache/{family}/{plugin_slug}/{filename}.cs`
7. Extract symbols via regex:
   - `using Aspose.*` → namespaces
   - `new ClassName(` → classes
   - `.MethodName(` → methods
   - `EnumType.Value` → enums
8. Classify result: CODE_FOUND_REPOSITORY / CODE_FOUND_GIST / NO_CODE_FOUND / CODE_FETCH_FAILED

## Checks
- [ ] Code hash recorded
- [ ] File saved to .local/code-cache/
- [ ] Symbols extracted
- [ ] Source type classified
- [ ] entry added to source-link-inventory.json

## Failure Modes
- GitHub 403: Rate limited — wait 60s, retry
- 404 for specific file: Try alternate path from tree search
- Empty match list: Record NO_CODE_FOUND
- Fetched wrong file (e.g., App.xaml.cs): Record as caveat; mark NEEDS_MANUAL_MAPPING

## Evidence Requirements
- code-harvest/source-link-inventory.json entry
- code-harvest/code-symbol-inventory.json entry
- .local/code-cache/{family}/{plugin_slug}/ directory with code file

## Example Entry
```json
{
  "family": "barcode",
  "plugin_slug": "generate-barcode",
  "source_type": "github_file",
  "raw_url": "https://raw.githubusercontent.com/aspose-barcode/Aspose.BarCode-for-.NET/master/.../StoreBarcodeOutputAsFile.cs",
  "code_hash": "bc77bfce202fa6f5c77b...",
  "fetch_status": "OK",
  "namespaces": ["Aspose.BarCode.Generation"],
  "classes": ["BarcodeGenerator"],
  "methods": ["Save", "Generate"]
}
```

## Stop Rules
- Stop if GitHub API rate limit hit; record CODE_FETCH_FAILED
- Do not invent code not found in official repos

## Continue Rules
- If no code found, record NO_CODE_FOUND and continue to next plugin
- NEEDS_MANUAL_MAPPING is acceptable outcome for this skill
